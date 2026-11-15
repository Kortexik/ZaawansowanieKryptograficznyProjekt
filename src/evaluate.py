"""Evaluator only: freeze the candidate dictionary before opening target data."""

import argparse
import hashlib
import json
from pathlib import Path


def _read_candidates(path, budget):
    candidates = set()
    duplicates = invalid = read = 0
    with Path(path).open("rb") as stream:
        for raw in stream:
            read += 1
            raw = raw.removesuffix(b"\n").removesuffix(b"\r")
            if not raw or any(char < 32 or char > 126 for char in raw):
                invalid += 1
                continue
            password = raw.decode("ascii")
            if password in candidates:
                duplicates += 1
                continue
            candidates.add(password)
            if len(candidates) == budget:
                break
    return candidates, {"candidate_lines_read": read, "unique_candidates": len(candidates),
                        "duplicate_candidates": duplicates, "invalid_candidates": invalid}


def evaluate_candidates(candidates_path, targets_path, baseline_path, *, budget=100000):
    """Match unique passwords; exclude baseline hits from the main denominator."""
    if budget < 1:
        raise ValueError("Budżet musi być dodatni.")
    candidates, stats = _read_candidates(candidates_path, budget)
    with Path(baseline_path).open("r", encoding="ascii", newline="") as stream:
        baseline = {line.removesuffix("\n").removesuffix("\r") for line in stream}
    baseline.discard("")
    targets = set()
    with Path(targets_path).open("r", encoding="ascii") as stream:
        for number, line in enumerate(stream, start=1):
            try:
                row = json.loads(line)
                password = row["password"]
                digest = hashlib.sha256(bytes.fromhex(row["salt"]) + password.encode("ascii")).hexdigest()
                if digest != row["sha256"]:
                    raise ValueError("Niezgodny hash.")
                if password in targets:
                    raise ValueError("Powtórzone hasło testowe.")
                targets.add(password)
            except (ValueError, KeyError, TypeError, AttributeError) as error:
                raise ValueError(f"Nieprawidłowy rekord testowy w wierszu {number}.") from error
    if not targets:
        raise ValueError("Zbiór testowy jest pusty.")
    eligible = targets - baseline
    hits = len(targets & candidates)
    new_hits = len(eligible & candidates)
    rate = new_hits / len(eligible) if eligible else None
    stats.update({
        "budget": budget, "budget_reached": len(candidates) == budget,
        "targets": len(targets), "eligible_targets": len(eligible),
        "baseline_hits": len(targets & baseline), "hits": hits, "new_hits": new_hits,
        "hit_rate": hits / len(targets), "new_hit_rate": rate,
        "combined_hits": len(targets & (baseline | candidates)),
        "goal_reached": budget == 100000 and len(candidates) == budget and rate is not None and rate >= 0.15,
    })
    return stats


def main():
    parser = argparse.ArgumentParser(description="Ocena zamkniętego słownika kandydatów. Tylko dla oceniającego.")
    parser.add_argument("--candidates", type=Path, required=True, help="Plik tekstowy, jedno hasło w wierszu.")
    parser.add_argument("--targets", type=Path, default=Path("data/processed/evaluation/targets.jsonl"))
    parser.add_argument("--baseline", type=Path, default=Path("data/processed/baseline.txt"))
    parser.add_argument("--budget", type=int, default=100000)
    parser.add_argument("--output", type=Path, help="Zapisz raport JSON do nowego pliku.")
    args = parser.parse_args()
    try:
        stats = evaluate_candidates(args.candidates, args.targets, args.baseline, budget=args.budget)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
