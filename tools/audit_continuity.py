"""Read-only audit of the recovered archive. Never changes frozen probabilities.

Run from the repository: python3 tools/audit_continuity.py
Outputs JSON to stdout; archived data stays under the ignored private directory.
"""
import csv
import hashlib
import io
import json
import math
import platform
import random
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ufc_forecast_lab.core import devig, score

ARCHIVE = ROOT / "private" / "continuity"
HASHES = {
    "ufc_forecast_lab_2026-10-10_frozen.csv": "d6d9e82e077a4f8c8031b8a57666ab22fd46c4bfa30974c5c0f157d204234c7a",
    "ufc_forecast_lab_2026-10-10_frozen.json": "2417b78ed8852ad01b971d74f192eebd95834634bd441c9a98bd39edaa8b6944",
}
METHODS = ("a_KO_TKO_pct", "a_SUB_pct", "a_DEC_pct", "b_KO_TKO_pct", "b_SUB_pct", "b_DEC_pct")


def main():
    for name, digest in HASHES.items():
        assert hashlib.sha256((ARCHIVE / name).read_bytes()).hexdigest() == digest, name
    doc = json.loads((ARCHIVE / "ufc_forecast_lab_2026-10-10_frozen.json").read_text())
    csv_rows = list(csv.DictReader(io.StringIO((ARCHIVE / "ufc_forecast_lab_2026-10-10_frozen.csv").read_text())))
    assert len(csv_rows) == len(doc["fights"]) == 12
    comparisons = []
    counts = []
    # Explicit NEW audit protocol. It is not asserted to be the missing original script.
    seed = 2026100801
    rng = random.Random(seed)
    for csv_row, fight in zip(csv_rows, doc["fights"]):
        for key, value in csv_row.items():
            if isinstance(fight[key], (int, float)):
                assert Decimal(value) == Decimal(str(fight[key])), (fight["fighter_a"], key)
            else:
                assert value == fight[key], (fight["fighter_a"], key)
        values = [Decimal(str(fight[k])) for k in METHODS]
        assert sum(values) == 100
        assert sum(values[:3]) == Decimal(str(fight["final_a_pct"]))
        assert values[2] + values[5] == Decimal(str(fight["GTD_pct"]))
        assert Decimal(str(fight["final_a_pct"])) + Decimal(str(fight["final_b_pct"])) == 100
        assert sum(fight["mc_outcomes_aKO_aSUB_aDEC_bKO_bSUB_bDEC"]) == 100000
        elo = 100 / (1 + 10 ** ((fight["elo_b"] - fight["elo_a"]) / 400))
        m0 = elo + fight["analyst_adjustment_pp"]
        market = 100 * devig(fight["odds_a"], fight["odds_b"])
        m1 = .75 * fight["independent_m0_a_pct"] + .25 * market
        assert abs(m0 - fight["independent_m0_a_pct"]) < 0.000051
        assert abs(market - fight["devig_market_a_pct"]) < 0.000051
        assert round(m1, 1) == fight["final_a_pct"]
        sample = rng.choices(range(6), weights=[float(v) for v in values], k=100000)
        observed = [sample.count(k) for k in range(6)]
        counts.append({"fighter_a": fight["fighter_a"], "counts": observed,
                       "matches_original_counts": observed == fight["mc_outcomes_aKO_aSUB_aDEC_bKO_bSUB_bDEC"]})
        comparisons.append({"fighter_a": fight["fighter_a"], "m0_from_captured_inputs_pct": m0,
                            "market_from_captured_odds_pct": market,
                            "m1_unrounded_pct": m1, "m1_matches_displayed": True})
    historical = json.loads((ARCHIVE / "historical_transcriptions.json").read_text())["events"]
    scores = {}
    all_brier, all_log, all_correct = [], [], []
    for event, rows in historical.items():
        probabilities = [Decimal(r["frozen_probability_pct_text"])/100 for r in rows]
        winners = [int(r["pick_correct_as_recorded"]) for r in rows]
        # Only an evaluation adapter, with synthetic dates. Not a historic freeze record.
        evaluation = {"schema_version": 1, "event_id": "audit-evaluation",
                      "forecast_at": "2000-01-01T00:00:00Z", "event_start": "2000-01-02T00:00:00Z",
                      "fights": [{"fight_id": str(i), "fighter_a": "recorded-pick", "fighter_b": "recorded-opponent", "p_a": float(p)} for i, p in enumerate(probabilities)]}
        result = score(evaluation, {str(i): "a" if y else "b" for i, y in enumerate(winners)})
        briers = [(p-y)**2 for p, y in zip(probabilities, winners)]
        losses = [-math.log(float(p if y else 1-p)) for p, y in zip(probabilities, winners)]
        assert math.isclose(result["brier"], float(sum(briers)/len(rows)), abs_tol=1e-14)
        assert math.isclose(result["log_loss"], sum(losses)/len(rows), abs_tol=1e-14)
        all_brier.extend(briers); all_log.extend(losses); all_correct.extend(winners)
        scores[event] = {"provenance": "transcribed outcomes; identity resolution separate", "metrics": result,
                         "thresholds": [{"threshold": t, "n": sum(p >= Decimal(str(t)) for p in probabilities),
                                         "correct": sum(y for p,y in zip(probabilities,winners) if p >= Decimal(str(t)))} for t in (.6,.7,.8,.9)]}
    cumulative = {"n": len(all_correct), "correct": sum(all_correct),
                  "brier": float(sum(all_brier)/len(all_brier)), "log_loss": sum(all_log)/len(all_log)}
    tables = json.loads((ARCHIVE / "recorded-tables.json").read_text())["tables"]
    method_rows = []
    for line in tables["ufc-332-forecast"]:
        cells = [c.strip().replace("**", "") for c in line.strip("|").split("|")]
        if len(cells) == 10 and cells[1].endswith("%"):
            method_rows.append(cells)
    assert len(method_rows) == len(historical["ufc-332"]) == 14
    exact_method = distance_direction = 0
    rounding_issues = []
    for cells, row in zip(method_rows, historical["ufc-332"]):
        values = [Decimal(c.rstrip("%")) for c in cells[3:9]]
        branch = max(range(6), key=lambda k: values[k])
        result_text = row["result_as_recorded"]
        actual_method = "DEC" if ("UD" in result_text or "SD" in result_text) else "SUB" if "SUB" in result_text else "KO_TKO"
        predicted_method = ("KO_TKO", "SUB", "DEC")[branch % 3]
        exact_method += int((branch < 3) == row["pick_correct_as_recorded"] and predicted_method == actual_method)
        gtd = Decimal(cells[9].rstrip("%"))
        distance_direction += int((gtd > 50) == (actual_method == "DEC"))
        if sum(values) != 100 or values[2] + values[5] != gtd:
            rounding_issues.append({"matchup": cells[0], "branch_sum_pct": str(sum(values)),
                                    "distance_branch_sum_pct": str(values[2]+values[5]), "displayed_gtd_pct": str(gtd)})
    assert exact_method == 7 and distance_direction == 9
    report = {"audit_date": "2026-10-08", "original_checksums": HASHES,
              "csv_json_fields_agree": True, "allen_duncan_arithmetic": comparisons,
              "historical_recomputed": scores, "cumulative_recomputed": cumulative,
              "ufc_332_displayed_method_audit": {"exact_winner_method_correct": exact_method,
                                                "decision_vs_finish_correct": distance_direction,
                                                "rounded_table_issues": rounding_issues},
              "new_audit_simulation": {"protocol": "Python random.Random; single stream; fight order preserved; choices with displayed branch weights",
                                       "seed": seed, "draws_per_fight": 100000, "total_draws": 1200000,
                                       "python": platform.python_version(), "counts": counts,
                                       "status": "New execution, not restoration of original execution"},
              "missing_original_simulation_script": not (ARCHIVE / "ufc_forecast_lab_2026-10-10.py").exists(),
              "verified_original_replay_report_available": (ARCHIVE / "original-script-replay" / "replay-report.json").exists()}
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
