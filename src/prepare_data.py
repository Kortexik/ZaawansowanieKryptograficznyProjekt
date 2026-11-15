"""Prepare disjoint RockYou splits, a training-only baseline and evaluator data."""

import argparse
from contextlib import closing
import hashlib
from itertools import islice
import json
from pathlib import Path
import secrets
import sqlite3
import sys
import tempfile

from .tokenizer import CharacterTokenizer


def _collect_passwords(db, source, seed, limit, min_length, max_length, progress):
    db.execute("CREATE TABLE passwords (password TEXT PRIMARY KEY, frequency INTEGER NOT NULL, sort_key BLOB NOT NULL)")
    rejected = {"empty": 0, "length": 0, "characters": 0}
    stats = {"records_read": 0, "accepted_records": 0, "rejected": rejected}
    digest = hashlib.sha256()
    prefix = f"{seed}:".encode("ascii")
    batch = []
    insert = (
        "INSERT INTO passwords VALUES (?, 1, ?) "
        "ON CONFLICT(password) DO UPDATE SET frequency = frequency + 1"
    )
    with source.open("rb") as stream:
        for raw in islice(stream, limit):
            stats["records_read"] += 1
            digest.update(raw)
            password = raw.removesuffix(b"\n").removesuffix(b"\r")
            if not password:
                rejected["empty"] += 1
            elif not min_length <= len(password) <= max_length:
                rejected["length"] += 1
            elif any(char < 32 or char > 126 for char in password):
                rejected["characters"] += 1
            else:
                stats["accepted_records"] += 1
                batch.append((password.decode("ascii"), hashlib.sha256(prefix + password).digest()[:8]))
                if len(batch) == 5000:
                    db.executemany(insert, batch)
                    db.commit()
                    batch.clear()
            if progress and stats["records_read"] % 500000 == 0:
                print(f"Wczytano {stats['records_read']:,} wierszy...", file=sys.stderr, flush=True)
    db.executemany(insert, batch)
    db.commit()
    stats["sha256_of_read_bytes"] = digest.hexdigest()
    stats["unique_passwords"] = db.execute("SELECT COUNT(*) FROM passwords").fetchone()[0]
    stats["duplicate_records"] = stats["accepted_records"] - stats["unique_passwords"]
    db.execute("CREATE INDEX split_order ON passwords(sort_key, password)")
    return stats


def _export(db, destination, train_count, val_count, baseline_size, total):
    evaluation = destination / "evaluation"
    evaluation.mkdir()
    with (
        (destination / "train.txt").open("w", encoding="ascii", newline="\n") as train,
        (destination / "val.txt").open("w", encoding="ascii", newline="\n") as val,
        (evaluation / "targets.jsonl").open("w", encoding="ascii") as targets,
        (evaluation / "hashes.txt").open("w", encoding="ascii") as hashes,
    ):
        rows = db.execute("SELECT password FROM passwords ORDER BY sort_key, password LIMIT ?", (total,))
        for index, (password,) in enumerate(rows):
            if index < train_count:
                train.write(password + "\n")
            elif index < train_count + val_count:
                val.write(password + "\n")
            else:
                salt = secrets.token_bytes(16)
                digest = hashlib.sha256(salt + password.encode("ascii")).hexdigest()
                targets.write(json.dumps({"password": password, "salt": salt.hex(), "sha256": digest}) + "\n")
                hashes.write(digest + "\n")
    (evaluation / "targets.jsonl").chmod(0o600)
    query = (
        "SELECT password FROM ("
        "SELECT password, frequency FROM passwords ORDER BY sort_key, password LIMIT ?"
        ") ORDER BY frequency DESC, password LIMIT ?"
    )
    with (destination / "baseline.txt").open("w", encoding="ascii", newline="\n") as baseline:
        for (password,) in db.execute(query, (train_count, baseline_size)):
            baseline.write(password + "\n")
    CharacterTokenizer().save(destination / "tokenizer.json")


def prepare_data(source, output, *, seed=42, limit=None, min_length=1, max_length=64,
                 baseline_size=100000, max_passwords=1000000, progress=False):
    """Publish output only after a complete successful run. Never overwrite it."""
    source, output = Path(source), Path(output)
    if not source.is_file():
        raise FileNotFoundError(f"Brak pliku {source}. Dodaj rockyou.txt do folderu data.")
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Folder {output} już istnieje. Wybierz inny przez --output.")
    if min_length < 1 or max_length < min_length:
        raise ValueError("Długości muszą spełniać 1 <= min-length <= max-length.")
    if baseline_size < 1 or (limit is not None and limit < 1):
        raise ValueError("baseline-size i limit muszą być dodatnie.")
    if max_passwords < 3:
        raise ValueError("max-passwords musi wynosić co najmniej 3.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".prepare-", dir=output.parent) as temporary:
        work = Path(temporary)
        result = work / "result"
        result.mkdir()
        with closing(sqlite3.connect(work / "counts.sqlite3")) as db:
            stats = _collect_passwords(db, source, seed, limit, min_length, max_length, progress)
            total = min(stats["unique_passwords"], max_passwords)
            if total < 3:
                raise ValueError("Potrzeba co najmniej 3 różnych poprawnych haseł do podziału.")
            val_count = max(1, total // 10)
            train_count = min(max(1, total * 8 // 10), total - val_count - 1)
            _export(db, result, train_count, val_count, baseline_size, total)
        stats.update({
            "source": str(source.resolve()), "seed": seed, "limit": limit,
            "max_passwords": max_passwords, "selected_passwords": total,
            "excluded_by_sample_limit": stats["unique_passwords"] - total,
            "min_length": min_length, "max_length": max_length,
            "alphabet": "printable ASCII, codepoints 32..126",
            "split": {"train": train_count, "val": val_count, "test": total - train_count - val_count},
            "baseline_size": min(baseline_size, train_count),
            "hash_scheme": "SHA-256(salt_bytes + password_ascii), random 16-byte salt per target",
        })
        (result / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if output.exists() or output.is_symlink():
            raise FileExistsError(f"Folder {output} już istnieje. Wybierz inny przez --output.")
        result.rename(output)
    return stats


def main():
    parser = argparse.ArgumentParser(description="Przygotowanie danych i słownika bazowego dla M1/M2 Konrada.")
    parser.add_argument("--input", type=Path, default=Path("data/rockyou.txt"))
    parser.add_argument("--output", type=Path, default=Path("data/processed"))
    parser.add_argument("--limit", type=int, help="Czytaj tylko pierwsze N wierszy źródła, np. 10000 do próby.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--min-length", type=int, default=1)
    parser.add_argument("--max-length", type=int, default=64)
    parser.add_argument("--baseline-size", type=int, default=100000)
    parser.add_argument("--max-passwords", type=int, default=1000000,
                        help="Maksymalna próba unikalnych haseł do podziału, domyślnie milion.")
    args = parser.parse_args()
    try:
        stats = prepare_data(args.input, args.output, seed=args.seed, limit=args.limit,
                             min_length=args.min_length, max_length=args.max_length,
                             baseline_size=args.baseline_size, max_passwords=args.max_passwords,
                             progress=True)
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.error(str(error))
    print(f"Gotowe: {args.output}")
    print(f"Unikalne hasła: {stats['unique_passwords']:,}; wybrane: {stats['selected_passwords']:,}")
    print(f"Podział: {stats['split']}")
    print(f"Słownik bazowy: {stats['baseline_size']:,}; statystyki: {args.output / 'stats.json'}")


if __name__ == "__main__":
    main()
