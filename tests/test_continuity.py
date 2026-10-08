"""Optional recovered-archive checks; skipped explicitly when private files are absent."""
import hashlib
import importlib.util
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "private" / "continuity"


@unittest.skipUnless((ARCHIVE / "ufc_forecast_lab_2026-10-10_frozen.json").exists(),
                     "Private historical archive not present; historical verification not run")
class ContinuityTests(unittest.TestCase):
    def test_original_artifact_hashes(self):
        expected = {
            "ufc_forecast_lab_2026-10-10_frozen.json": "2417b78ed8852ad01b971d74f192eebd95834634bd441c9a98bd39edaa8b6944",
            "ufc_forecast_lab_2026-10-10_frozen.csv": "d6d9e82e077a4f8c8031b8a57666ab22fd46c4bfa30974c5c0f157d204234c7a",
        }
        for name, digest in expected.items():
            self.assertEqual(hashlib.sha256((ARCHIVE / name).read_bytes()).hexdigest(), digest)

    def test_audit_reproduction_and_read_only_behavior(self):
        files = [p for p in ARCHIVE.iterdir() if p.is_file()]
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        command = [sys.executable, str(ROOT / "tools" / "audit_continuity.py")]
        first = subprocess.check_output(command, cwd=ROOT)
        second = subprocess.check_output(command, cwd=ROOT)
        self.assertEqual(first, second)
        self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
        result = json.loads(first)
        self.assertEqual(result["new_audit_simulation"]["total_draws"], 1200000)
        self.assertEqual(result["cumulative_recomputed"]["correct"], 20)
        self.assertEqual(result["cumulative_recomputed"]["n"], 26)
        for event, brier, log_loss in (("rosas-barcelos", .2671, .7327), ("ufc-332", .1244, .4194)):
            metrics = result["historical_recomputed"][event]["metrics"]
            self.assertEqual(round(metrics["brier"], 4), brier)
            self.assertEqual(round(metrics["log_loss"], 4), log_loss)
        self.assertTrue(all(r["m1_matches_displayed"] for r in result["allen_duncan_arithmetic"]))


@unittest.skipUnless((ARCHIVE / "ufc_forecast_lab_2026-10-10.py").exists() and importlib.util.find_spec("numpy"),
                     "Original replay requires private script and NumPy")
class OriginalReplayTests(unittest.TestCase):
    def test_exact_original_execution_and_overwrite_protection(self):
        module = runpy.run_path(str(ROOT / "tools" / "replay_original.py"))
        with tempfile.TemporaryDirectory() as temp:
            report = module["replay"](Path(temp) / "outputs")
            self.assertEqual(report["exact_count_array_matches"], 12)
            self.assertTrue(report["same_fight_count"])
            self.assertTrue(report["json_structure_equal"])
            self.assertTrue(all(report["byte_equal"].values()))
            self.assertTrue(report["original_files_unchanged"])
            self.assertEqual(report["total_draws"], 1200000)
            with self.assertRaises(ValueError):
                module["replay"](Path(temp) / "outputs")
            with self.assertRaises(ValueError):
                module["replay"](ARCHIVE)


if __name__ == "__main__":
    unittest.main()
