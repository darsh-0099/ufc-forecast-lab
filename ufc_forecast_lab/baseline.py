"""Evaluate versioned frozen records against separately sourced outcomes."""
import hashlib
import json
import math
from decimal import Decimal
from pathlib import Path

BRANCHES = ("a_ko", "a_sub", "a_dec", "b_ko", "b_sub", "b_dec")


def summarize(rows):
    n = len(rows)
    picks = [r for r in rows if r["p"] != Decimal("0.5")]
    confidence = lambda r: max(r["p"], 1-r["p"])
    correct = lambda r: (r["p"] > Decimal("0.5")) == bool(r["y"])
    return {"n": n, "correct": sum(correct(r) for r in picks), "n_picks": len(picks),
            "accuracy": round(sum(correct(r) for r in picks)/len(picks), 12) if picks else None,
            "brier": float(sum((r["p"]-r["y"])**2 for r in rows)/n) if n else None,
            "log_loss": -sum(math.log(float(r["p"] if r["y"] else 1-r["p"])) for r in rows)/n if n else None,
            "thresholds": [{"minimum_pct": t, "n": sum(confidence(r)*100 >= t for r in picks),
                            "correct": sum(correct(r) for r in picks if confidence(r)*100 >= t)} for t in (60,70,80,90)],
            "calibration": [{"lower_pct": lo, "upper_pct": hi, "n": len(group),
                             "mean_confidence": float(sum(confidence(r) for r in group)/len(group)) if group else None,
                             "accuracy": sum(correct(r) for r in group)/len(group) if group else None}
                            for lo,hi in ((50,60),(60,70),(70,80),(80,90),(90,101))
                            for group in [[r for r in picks if lo <= confidence(r)*100 < hi]]]}


def evaluate(directory):
    directory = Path(directory)
    forecasts = json.loads((directory/"data/forecasts.json").read_text())
    evidence = json.loads((directory/"data/outcomes.json").read_text())
    outcomes = {r["fight_id"]: r for r in evidence["rows"]}
    if len(outcomes) != len(evidence["rows"]):
        raise ValueError("Duplicate outcome ID")
    aliases = {(a["event_id"],a["recorded_label"]):a["canonical_label"] for a in evidence["aliases"]}
    canon = lambda event, label: aliases.get((event,label),label)
    seen, matched, all_rows, pending = set(), set(), [], []
    event_scores, issues, joins = {}, [], []
    for event in forecasts["events"]:
        rows, method_correct, method_n = [], 0, 0
        for f in event["fights"]:
            fid = f["fight_id"]
            if fid in seen:
                raise ValueError("Duplicate forecast ID")
            seen.add(fid)
            p = Decimal(f["p_a_pct"])/100
            if not p.is_finite() or not 0 < p < 1:
                raise ValueError("Baseline probabilities must be finite and strictly between zero and one")
            methods = f["methods_pct"]
            if methods:
                if set(methods) != set(BRANCHES):
                    raise ValueError("Invalid method keys")
                values = [Decimal(methods[k]) for k in BRANCHES]
                if any(not v.is_finite() or not 0 <= v <= 100 for v in values):
                    raise ValueError("Invalid method probability")
                mismatch = sum(values) != 100 or sum(values[:3]) != p*100 or values[2]+values[5] != Decimal(f["gtd_pct"])
                if mismatch:
                    if f["origin"] != "reconstructed_displayed_record":
                        raise ValueError("Original probability distribution fails normalization")
                    issues.append({"fight_id":fid,"branch_sum_pct":str(sum(values)),
                                   "gtd_branch_sum_pct":str(values[2]+values[5]),
                                   "gtd_displayed_pct":f["gtd_pct"],"action":"preserved_without_normalization"})
            result = outcomes.get(fid)
            if event["status"] == "pending":
                if result:
                    raise ValueError("Pending forecast cannot receive a result in this baseline")
                pending.append(fid)
                continue
            if result is None:
                raise ValueError("Completed forecast has no independently verified result")
            a,b = canon(event["event_id"],f["fighter_a_as_recorded"]),canon(event["event_id"],f["fighter_b_as_recorded"])
            if result["event_id"] != event["event_id"] or {a,b} != {result["fighter_a"],result["fighter_b"]}:
                raise ValueError("Forecast/result identity mismatch")
            if result["winner"] not in (a,b):
                raise ValueError("Winner is not a bout participant")
            if result["verification"] != "independently_checked_official_results" or not result["source_url"]:
                raise ValueError("Missing independent result evidence")
            matched.add(fid)
            y = int(result["winner"] == a)
            rows.append({"p":p,"y":y})
            joins.append({"fight_id":fid,"p_a_pct":f["p_a_pct"],"actual_a_win":y,
                          "outcome_source_url":result["source_url"],"forecast_origin":f["origin"]})
            if methods:
                branch = max(BRANCHES,key=lambda k:Decimal(methods[k]))
                predicted_winner = a if branch.startswith("a_") else b
                predicted_method = {"ko":"KO_TKO","sub":"SUB","dec":"DEC"}[branch.split("_")[1]]
                method_correct += predicted_winner == result["winner"] and predicted_method == result["method"]
                method_n += 1
        if rows:
            event_scores[event["event_id"]] = {**summarize(rows),"exact_method_n":method_n,"exact_method_correct":method_correct if method_n else None}
            all_rows.extend(rows)
    voids = {f["fight_id"] for f in forecasts["void_forecasts"]}
    if voids & seen or voids & outcomes.keys():
        raise ValueError("Voided forecast entered the scored cohort")
    if outcomes.keys() - matched:
        raise ValueError("Unmatched outcome")
    return {"baseline_version":forecasts["baseline_version"],"scoring_source":"independently verified winners joined to preserved forecast probabilities",
            "events":event_scores,"combined":summarize(all_rows),"joined_rows":joins,
            "pending_fight_ids":pending,"void_fight_ids":sorted(voids),"rounded_method_issues":issues,
            "limitations":["Reconstructed predictions retain displayed precision; original underlying files and freeze timestamps remain unavailable for two cards.",
                           "Rosas complete method distribution is missing; its reported 2/12 exact-method score is not independently recomputed.",
                           "Historical market comparison remains reported-only without a complete timestamped market snapshot."]}


def verify(directory):
    directory = Path(directory)
    manifest = json.loads((directory/"manifest.json").read_text())
    expected = manifest["files"]
    for name,digest in expected.items():
        path = directory/name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Frozen baseline integrity failure: {name}")
    actual = {str(p.relative_to(directory)) for p in (directory/"data").glob("*.json")}
    if actual != {n for n in expected if n.startswith("data/")}:
        raise ValueError("Unexpected baseline data file")
    result = evaluate(directory)
    saved = json.loads((directory/"metrics.json").read_text())
    if result != saved:
        raise ValueError("Recomputed metrics differ from versioned baseline")
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    result = verify(args.directory)
    print(json.dumps({"version":result["baseline_version"],"verified":True,"combined":result["combined"]},indent=2))
