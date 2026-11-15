import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def module(self, name):
        self.assertIsNotNone(importlib.util.find_spec(name), f"Brakuje modułu {name}")
        return importlib.import_module(name)

    def source(self):
        path = self.root / "rockyou.txt"
        rows = [f"Haslo{i:03}".encode() for i in range(100)]
        path.write_bytes(b"\n".join(rows + [b"Haslo000"] * 5 + [b" haslo ", b"", b"\xff", b"a" * 65]) + b"\n")
        return path

    def prepare(self, source=None, output="processed", **kwargs):
        return self.module("src.prepare_data").prepare_data(
            source or self.source(), self.root / output, **kwargs
        )

    def targets(self, passwords):
        path = self.root / "targets.jsonl"
        with path.open("w", encoding="utf-8") as stream:
            for i, password in enumerate(passwords):
                salt = bytes([i + 1]) * 16
                digest = hashlib.sha256(salt + password.encode("ascii")).hexdigest()
                stream.write(json.dumps({"password": password, "salt": salt.hex(), "sha256": digest}) + "\n")
        return path

    def test_split_is_disjoint_and_keeps_spaces_and_original_counts(self):
        self.prepare()
        output = self.root / "processed"
        train = set(output.joinpath("train.txt").read_text().splitlines())
        val = set(output.joinpath("val.txt").read_text().splitlines())
        targets = [json.loads(line) for line in output.joinpath("evaluation/targets.jsonl").read_text().splitlines()]
        test = {row["password"] for row in targets}
        self.assertFalse(train & val or train & test or val & test)
        self.assertEqual((len(train), len(val), len(test)), (80, 10, 11))
        self.assertEqual(len(train | val | test), 101)
        self.assertIn(" haslo ", train | val | test)
        stats = json.loads(output.joinpath("stats.json").read_text())
        self.assertEqual(stats["records_read"], 109)
        self.assertEqual(stats["accepted_records"], 106)
        self.assertEqual(stats["duplicate_records"], 5)
        self.assertEqual(stats["rejected"], {"empty": 1, "length": 1, "characters": 1})
        for row in targets:
            actual = hashlib.sha256(bytes.fromhex(row["salt"]) + row["password"].encode("ascii")).hexdigest()
            self.assertEqual(actual, row["sha256"])
        self.assertEqual(output.joinpath("evaluation/hashes.txt").read_text().splitlines(), [r["sha256"] for r in targets])

    def test_same_seed_reproduces_split_and_baseline_uses_only_training(self):
        source = self.source()
        self.prepare(source, output="first", seed=17, baseline_size=5)
        self.prepare(source, output="second", seed=17, baseline_size=5)
        for filename in ["train.txt", "val.txt", "baseline.txt", "tokenizer.json"]:
            self.assertEqual((self.root / "first" / filename).read_bytes(), (self.root / "second" / filename).read_bytes())
        train = (self.root / "first/train.txt").read_text().splitlines()
        baseline = (self.root / "first/baseline.txt").read_text().splitlines()
        expected = sorted(train, key=lambda p: (-(6 if p == "Haslo000" else 1), p))[:5]
        self.assertEqual(baseline, expected)

    def test_invalid_or_insufficient_input_does_not_publish_partial_output(self):
        source = self.root / "small.txt"
        source.write_bytes(b"same\nsame\n")
        with self.assertRaises(ValueError):
            self.prepare(source)
        self.assertFalse((self.root / "processed").exists())

    def test_preparation_refuses_to_overwrite_existing_results(self):
        self.prepare()
        before = (self.root / "processed/train.txt").read_bytes()
        with self.assertRaises(FileExistsError):
            self.prepare()
        self.assertEqual((self.root / "processed/train.txt").read_bytes(), before)

    def test_limit_counts_source_records_and_crlf_does_not_change_passwords(self):
        source = self.root / "lines.txt"
        source.write_bytes(b" one \r\ntwo\r\nthree\r\nfour\r\n")
        self.prepare(source, limit=3)
        output = self.root / "processed"
        all_passwords = output.joinpath("train.txt").read_text().splitlines() + output.joinpath("val.txt").read_text().splitlines()
        all_passwords += [json.loads(line)["password"] for line in output.joinpath("evaluation/targets.jsonl").read_text().splitlines()]
        self.assertEqual(set(all_passwords), {" one ", "two", "three"})

    def test_sample_cap_limits_all_splits_but_counts_the_complete_source(self):
        source = self.source()
        output = self.root / "sample"
        result = subprocess.run(
            [sys.executable, "-m", "src.prepare_data", "--input", str(source),
             "--output", str(output), "--max-passwords", "10"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        stats = json.loads((output / "stats.json").read_text())
        self.assertEqual(stats["unique_passwords"], 101)
        self.assertEqual(stats["selected_passwords"], 10)
        self.assertEqual(stats["excluded_by_sample_limit"], 91)
        self.assertEqual(stats["split"], {"train": 8, "val": 1, "test": 1})
        self.assertEqual(len((output / "train.txt").read_text().splitlines()), 8)
        self.assertEqual(len((output / "val.txt").read_text().splitlines()), 1)
        self.assertEqual(len((output / "evaluation/targets.jsonl").read_text().splitlines()), 1)

    def test_tokenizer_roundtrip_padding_and_saved_contract(self):
        tokenizer = self.module("src.tokenizer").CharacterTokenizer()
        encoded = tokenizer.encode(" Ab9! ", pad_to=12)
        self.assertEqual(len(encoded), 12)
        self.assertEqual(encoded[0], tokenizer.bos_id)
        self.assertIn(tokenizer.eos_id, encoded)
        self.assertEqual(encoded[-1], tokenizer.pad_id)
        self.assertEqual(tokenizer.decode(encoded), " Ab9! ")
        path = self.root / "tokenizer.json"
        tokenizer.save(path)
        restored = type(tokenizer).load(path)
        self.assertEqual(restored.encode(" Ab9! "), tokenizer.encode(" Ab9! "))
        with self.assertRaises(ValueError):
            tokenizer.encode("żółw")
        with self.assertRaises(ValueError):
            tokenizer.encode("long", pad_to=2)
        with self.assertRaises(ValueError):
            tokenizer.decode([1000])

    def test_known_hit_rate_deduplicates_candidates_and_excludes_baseline(self):
        evaluate = self.module("src.evaluate").evaluate_candidates
        targets = self.targets(["alpha", "beta", "gamma", "delta"])
        candidates = self.root / "candidates.txt"
        candidates.write_bytes(b"alpha\nalpha\nbeta\n gamma \nmissing\n")
        baseline = self.root / "baseline.txt"
        baseline.write_text("alpha\n")
        result = evaluate(candidates, targets, baseline, budget=4)
        self.assertEqual(result["targets"], 4)
        self.assertEqual(result["eligible_targets"], 3)
        self.assertEqual(result["hits"], 2)
        self.assertEqual(result["new_hits"], 1)
        self.assertAlmostEqual(result["new_hit_rate"], 1 / 3)
        self.assertEqual(result["baseline_hits"], 1)
        self.assertEqual(result["unique_candidates"], 4)
        self.assertEqual(result["duplicate_candidates"], 1)
        self.assertTrue(result["budget_reached"])

    def test_budget_is_applied_before_matching_and_does_not_peek_at_targets(self):
        evaluate = self.module("src.evaluate").evaluate_candidates
        targets = self.targets(["answer", "other"])
        candidates = self.root / "candidates.txt"
        candidates.write_text("miss\nanswer\n")
        baseline = self.root / "baseline.txt"
        baseline.write_text("")
        result = evaluate(candidates, targets, baseline, budget=1)
        self.assertEqual(result["hits"], 0)
        self.assertEqual(result["unique_candidates"], 1)

    def test_empty_eligible_test_has_undefined_rate_and_incomplete_budget_is_reported(self):
        evaluate = self.module("src.evaluate").evaluate_candidates
        targets = self.targets(["alpha"])
        candidates = self.root / "candidates.txt"
        candidates.write_text("alpha\n")
        baseline = self.root / "baseline.txt"
        baseline.write_text("alpha\n")
        result = evaluate(candidates, targets, baseline, budget=100000)
        self.assertIsNone(result["new_hit_rate"])
        self.assertFalse(result["budget_reached"])
        self.assertFalse(result["goal_reached"])

    def test_evaluation_rejects_corrupt_targets(self):
        evaluate = self.module("src.evaluate").evaluate_candidates
        targets = self.targets(["answer"])
        row = json.loads(targets.read_text())
        row["sha256"] = "0" * 64
        targets.write_text(json.dumps(row) + "\n")
        candidates = self.root / "candidates.txt"
        candidates.write_text("answer\n")
        baseline = self.root / "baseline.txt"
        baseline.write_text("")
        with self.assertRaises(ValueError):
            evaluate(candidates, targets, baseline)

    def test_missing_input_cli_has_actionable_error_without_traceback(self):
        result = subprocess.run(
            [sys.executable, "-m", "src.prepare_data", "--input", str(self.root / "missing.txt")],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Brak pliku", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
