"""Reconstruct a labeled baseline from archived evidence into a fresh directory.

Private sources are required for rebuilding, but the sanitized baseline can be
verified without them. Existing version directories are never overwritten.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "private" / "continuity"
BRANCHES = ("a_ko", "a_sub", "a_dec", "b_ko", "b_sub", "b_dec")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(output):
    output = Path(output)
    if output.exists():
        raise ValueError("Baseline destination already exists; use a fresh version directory")
    transcriptions = json.loads((ARCHIVE / "historical_transcriptions.json").read_text())["events"]
    tables = json.loads((ARCHIVE / "recorded-tables.json").read_text())["tables"]
    outcomes = json.loads((ARCHIVE / "verified-outcomes-v2.json").read_text())
    methods = []
    for line in tables["ufc-332-forecast"]:
        cells = [c.strip().replace("**", "") for c in line.strip("|").split("|")]
        if len(cells) == 10 and cells[1].endswith("%"):
            methods.append(cells)
    if len(methods) != 14:
        raise ValueError("Expected fourteen reconstructed method rows")
    forecast_events = []
    dates = {"rosas-barcelos": "2026-09-26", "ufc-332": "2026-10-03"}
    for event, rows in transcriptions.items():
        expected = 12 if event == "rosas-barcelos" else 14
        if len(rows) != expected:
            raise ValueError("Incomplete historical board")
        fights = []
        for index, row in enumerate(rows):
            a, b = row["matchup_as_recorded"].split("–")
            f = {"fight_id": f"{event}:{index+1:02d}", "fighter_a_as_recorded": a,
                 "fighter_b_as_recorded": b, "p_a_pct": row["frozen_probability_pct_text"],
                 "origin": "reconstructed_displayed_record", "methods_pct": None,
                 "gtd_pct": None, "source_id": f"{event}-recorded-board"}
            if a != row["pick_as_recorded"]:
                raise ValueError("Historical probability orientation differs from fighter A")
            if event == "ufc-332":
                cells = methods[index]
                if cells[0].split("–")[0] != a or cells[1].rstrip("%") != f["p_a_pct"]:
                    raise ValueError("Pre-event table and scorecard disagree")
                f["methods_pct"] = dict(zip(BRANCHES, [c.rstrip("%") for c in cells[3:9]]))
                f["gtd_pct"] = cells[9].rstrip("%")
                f["methods_origin"] = "reconstructed_rounded_frozen_simulation_frequencies"
            fights.append(f)
        forecast_events.append({"event_id": event, "event_date": dates[event],
                                "declared_freeze_date": None, "trusted_freeze_timestamp": None,
                                "status": "completed", "fights": fights})
    original_path = ARCHIVE / "ufc_forecast_lab_2026-10-10_frozen.json"
    original = json.loads(original_path.read_text())
    names = ("a_KO_TKO_pct", "a_SUB_pct", "a_DEC_pct", "b_KO_TKO_pct", "b_SUB_pct", "b_DEC_pct")
    fights = []
    for index, row in enumerate(original["fights"]):
        fights.append({"fight_id": f"allen-duncan:{index+1:02d}",
                       "fighter_a_as_recorded": row["fighter_a"], "fighter_b_as_recorded": row["fighter_b"],
                       "p_a_pct": str(row["final_a_pct"]), "origin": "extracted_from_recovered_original",
                       "source_id": "allen-duncan-original-json", "methods_pct": dict(zip(BRANCHES, [str(row[k]) for k in names])),
                       "methods_origin": "original_frozen_unconditional_probabilities",
                       "gtd_pct": str(row["GTD_pct"]), "m0_a_pct": str(row["independent_m0_a_pct"]),
                       "market_a_pct": str(row["devig_market_a_pct"]), "odds_a": row["odds_a"], "odds_b": row["odds_b"],
                       "simulation_counts": row["mc_outcomes_aKO_aSUB_aDEC_bKO_bSUB_bDEC"],
                       "simulation_seed": row["mc_seed"], "simulation_draws": row["mc_iterations"]})
    forecast_events.append({"event_id": "allen-duncan", "event_date": "2026-10-10",
                            "declared_freeze_date": "2026-10-08", "trusted_freeze_timestamp": None,
                            "status": "pending", "fights": fights})
    forecast = {"schema_version": 1, "baseline_version": "continuity-v1", "reconstructed_on": "2026-10-08",
                "probability_units": "percent stored as original displayed decimal strings",
                "events": forecast_events,
                "void_forecasts": [{"fight_id": "rosas-barcelos:gall-dumas-void", "fighter_a_as_recorded": "Gall",
                                     "fighter_b_as_recorded": "Dumas", "p_a_pct": "58.3",
                                     "origin": "reconstructed_displayed_record", "status": "void",
                                     "replacement_fight_id": "rosas-barcelos:03"}]}
    reported = json.loads((ARCHIVE / "reported-benchmarks.json").read_text())
    reports = {key: reported[key] for key in ("rosas_barcelos", "ufc_332", "cumulative")}
    reports["provenance"] = "reported_historical_summaries; not independently scored results"
    sources = {
        "rosas-barcelos-recorded-board": {"kind": "reconstruction", "original_file_available": False,
                                          "input_sha256": sha(ARCHIVE / "historical_transcriptions.json")},
        "ufc-332-recorded-board": {"kind": "reconstruction", "original_file_available": False,
                                   "input_sha256": sha(ARCHIVE / "historical_transcriptions.json"),
                                   "method_table_sha256": sha(ARCHIVE / "recorded-tables.json")},
        "allen-duncan-original-json": {"kind": "recovered_original", "input_sha256": sha(original_path)},
        "private_originals": {name: sha(ARCHIVE / name) for name in (
            "ufc_forecast_lab_2026-10-10_frozen.csv", "ufc_forecast_lab_2026-10-10_frozen.json", "ufc_forecast_lab_2026-10-10.py")}}
    output.mkdir(parents=True)
    for name, content in (("forecasts.json", forecast), ("outcomes.json", outcomes),
                          ("reported-benchmarks.json", reports), ("sources.json", sources)):
        (output / name).write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(build(args.output))
