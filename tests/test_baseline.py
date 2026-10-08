import json
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest

from ufc_forecast_lab.baseline import evaluate, verify

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "baselines" / "continuity-v1"


class BaselineTests(unittest.TestCase):
    def test_independent_scoring_and_cohort(self):
        result = verify(BASELINE)
        self.assertEqual(result["combined"]["n"], 26)
        self.assertEqual(result["combined"]["correct"], 20)
        self.assertAlmostEqual(result["combined"]["brier"], .19022757692307693, places=14)
        self.assertAlmostEqual(result["combined"]["log_loss"], .5640163556358085, places=14)
        self.assertEqual(len(result["pending_fight_ids"]), 12)
        self.assertEqual(result["void_fight_ids"], ["rosas-barcelos:gall-dumas-void"])
        self.assertEqual(result["events"]["ufc-332"]["exact_method_correct"], 7)
        self.assertIsNone(result["events"]["rosas-barcelos"]["exact_method_correct"])
        self.assertEqual(len(result["rounded_method_issues"]), 5)

    def test_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp)/"baseline"
            shutil.copytree(BASELINE, copy)
            path = copy/"data/forecasts.json"
            data = json.loads(path.read_text())
            data["events"][0]["fights"][0]["p_a_pct"] = "99.9"
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "integrity failure"):
                verify(copy)

    def test_alias_is_required_and_results_are_independent(self):
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp)/"baseline"
            shutil.copytree(BASELINE, copy)
            # A fabricated historical aggregate cannot influence result-based scoring.
            (copy/"data/reported-benchmarks.json").write_text('{"correct": 26}')
            self.assertEqual(evaluate(copy)["combined"]["correct"], 20)
            path = copy/"data/outcomes.json"
            data = json.loads(path.read_text())
            data["aliases"] = [a for a in data["aliases"] if a["recorded_label"] != "Machado"]
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                evaluate(copy)

    def test_missing_result_cannot_silently_shrink_cohort(self):
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp)/"baseline"
            shutil.copytree(BASELINE, copy)
            path = copy/"data/outcomes.json"
            data = json.loads(path.read_text())
            data["rows"].pop()
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "no independently verified result"):
                evaluate(copy)

    @unittest.skipUnless((ROOT/"private/continuity/verified-outcomes-v2.json").exists(), "Private reconstruction inputs unavailable")
    def test_reconstruction_reproduces_versioned_data(self):
        build = runpy.run_path(str(ROOT/"tools/build_baseline.py"))["build"]
        with tempfile.TemporaryDirectory() as temp:
            path = build(Path(temp)/"rebuilt")
            for original in (BASELINE/"data").glob("*.json"):
                self.assertEqual(original.read_bytes(), (path/original.name).read_bytes())
            with self.assertRaisesRegex(ValueError, "already exists"):
                build(path)


if __name__ == "__main__":
    unittest.main()
