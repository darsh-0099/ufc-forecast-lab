import copy
import json
import math
import sqlite3
import unittest
from pathlib import Path
from ufc_forecast_lab.core import blend, devig, score, simulate, validate
from ufc_forecast_lab.ledger import Ledger

RAW = (Path(__file__).resolve().parents[1] / "examples" / "synthetic.json").read_bytes()


class LabTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(RAW)

    def test_math(self):
        self.assertAlmostEqual(devig(-110, -110), 0.5)
        self.assertAlmostEqual(blend(0.58, 0.66), 0.6)
        result = score(self.doc, {"demo-1": "a"})
        self.assertAlmostEqual(result["brier"], 0.16)
        self.assertAlmostEqual(result["log_loss"], -math.log(0.6))
        self.assertEqual(result["accuracy"], 1)

    def test_bad_inputs(self):
        for value in (float("nan"), float("inf"), -0.1, 1.1, True):
            bad = copy.deepcopy(self.doc)
            bad["fights"][0]["p_a"] = value
            with self.assertRaises(ValueError):
                validate(bad)
        self.doc["fights"][0]["methods"]["a_ko"] = 0.3
        with self.assertRaises(ValueError):
            validate(self.doc)

    def test_temporal_and_duplicate_validation(self):
        self.doc["forecast_at"] = self.doc["event_start"]
        with self.assertRaises(ValueError):
            validate(self.doc)
        self.doc = json.loads(RAW)
        self.doc["fights"].append(copy.deepcopy(self.doc["fights"][0]))
        with self.assertRaises(ValueError):
            validate(self.doc)

    def test_simulation(self):
        first = simulate(self.doc, 10000, 42)
        self.assertEqual(first, simulate(self.doc, 10000, 42))
        counts = first["counts"]["demo-1"]
        self.assertEqual(sum(counts.values()), 10000)
        self.assertLess(abs(counts["a_dec"]/10000 - 0.3), 0.02)

    def test_ledger_integrity(self):
        ledger = Ledger(":memory:")
        ledger.freeze(RAW)
        with self.assertRaises(sqlite3.IntegrityError):
            ledger.freeze(RAW)
        for sql in ("UPDATE forecasts SET sha256='bad'", "DELETE FROM forecasts"):
            with self.assertRaises(sqlite3.IntegrityError):
                ledger.db.execute(sql)
        ledger.amend("synthetic-demo", {"fight_id": "demo-1", "kind": "void", "note": "Cancelled"})
        self.assertEqual(ledger.get("synthetic-demo"), self.doc)
        self.assertEqual(score(self.doc, {}, ledger.voids("synthetic-demo"))["n_scored"], 0)

    def test_results_policy(self):
        self.assertEqual(score(self.doc, {"demo-1": "draw"})["n_scored"], 0)
        self.assertEqual(score(self.doc, {})["pending"], ["demo-1"])
        with self.assertRaises(ValueError):
            score(self.doc, {"unknown": "a"})
        with self.assertRaises(ValueError):
            score(self.doc, {"demo-1": "a"}, {"demo-1"})

    def test_endpoint_and_tie(self):
        del self.doc["fights"][0]["methods"]
        self.doc["fights"][0]["p_a"] = 0
        self.assertEqual(score(self.doc, {"demo-1": "a"})["log_loss"], "infinity")
        self.doc["fights"][0]["p_a"] = 0.5
        result = score(self.doc, {"demo-1": "a"})
        self.assertIsNone(result["accuracy"])
        self.assertEqual(result["brier"], 0.25)


if __name__ == "__main__":
    unittest.main()
