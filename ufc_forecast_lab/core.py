"""Probability math, strict input validation and deterministic evaluation."""
import math
import random
from datetime import datetime

BRANCHES = ("a_ko", "a_sub", "a_dec", "b_ko", "b_sub", "b_dec")


def probability(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Probability must be a number")
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("Probability must be finite and between zero and one")
    return float(value)


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must include a timezone")
    return parsed


def implied(odds):
    if isinstance(odds, bool) or not isinstance(odds, (int, float)):
        raise ValueError("American odds must be numeric")
    if not math.isfinite(odds) or abs(odds) < 100:
        raise ValueError("American odds must be <= -100 or >= 100")
    return -odds / (-odds + 100) if odds < 0 else 100 / (odds + 100)


def devig(odds_a, odds_b):
    a, b = implied(odds_a), implied(odds_b)
    return a / (a + b)


def blend(m0, market, weight=0.25):
    m0, market, weight = map(probability, (m0, market, weight))
    return (1 - weight) * m0 + weight * market


def validate(document):
    if set(document) != {"schema_version", "event_id", "event_start", "forecast_at", "fights"}:
        raise ValueError("Unexpected or missing document fields")
    if document["schema_version"] != 1:
        raise ValueError("Unsupported schema version")
    if not isinstance(document["event_id"], str) or not document["event_id"].strip():
        raise ValueError("event_id must be nonempty")
    if timestamp(document["forecast_at"]) >= timestamp(document["event_start"]):
        raise ValueError("Forecast timestamp must precede the event")
    if not isinstance(document["fights"], list) or not document["fights"]:
        raise ValueError("At least one fight is required")
    ids = set()
    for fight in document["fights"]:
        required = {"fight_id", "fighter_a", "fighter_b", "p_a"}
        allowed = required | {"methods", "m0_a", "market_a"}
        if not required <= set(fight) or set(fight) - allowed:
            raise ValueError("Unexpected or missing fight fields")
        for key in ("fight_id", "fighter_a", "fighter_b"):
            if not isinstance(fight[key], str) or not fight[key].strip():
                raise ValueError(f"{key} must be nonempty")
        if fight["fighter_a"] == fight["fighter_b"] or fight["fight_id"] in ids:
            raise ValueError("Duplicate fight or identical fighters")
        ids.add(fight["fight_id"])
        p = probability(fight["p_a"])
        for key in ("m0_a", "market_a"):
            if key in fight:
                probability(fight[key])
        if "methods" in fight:
            methods = fight["methods"]
            if set(methods) != set(BRANCHES):
                raise ValueError("Exactly six method branches are required")
            values = [probability(methods[key]) for key in BRANCHES]
            if not math.isclose(sum(values), 1, abs_tol=1e-9):
                raise ValueError("Method branches must sum to one")
            if not math.isclose(sum(values[:3]), p, abs_tol=1e-9):
                raise ValueError("Method branches must match p_a")
    return document


def simulate(document, draws=100000, seed=0):
    validate(document)
    if draws <= 0:
        raise ValueError("Draw count must be positive")
    rng = random.Random(seed)
    output = {}
    for fight in document["fights"]:
        if "methods" not in fight:
            raise ValueError("Simulation requires method probabilities for every fight")
        counts = dict.fromkeys(BRANCHES, 0)
        for outcome in rng.choices(BRANCHES, weights=[fight["methods"][k] for k in BRANCHES], k=draws):
            counts[outcome] += 1
        output[fight["fight_id"]] = counts
    return {"seed": seed, "draws_per_fight": draws, "counts": output}


def score(document, results, voids=()):
    validate(document)
    fights = {f["fight_id"]: f for f in document["fights"]}
    if set(results) - fights.keys() or set(voids) - fights.keys():
        raise ValueError("Unknown fight ID")
    if set(results) & set(voids):
        raise ValueError("Voided fights cannot have results")
    rows, excluded = [], []
    for fight_id, result in results.items():
        if result not in {"a", "b", "draw", "no_contest"}:
            raise ValueError("Result must be a, b, draw or no_contest")
        if result in {"draw", "no_contest"}:
            excluded.append(fight_id)
            continue
        p, y = fights[fight_id]["p_a"], int(result == "a")
        actual = p if y else 1 - p
        # Exact endpoint probabilities give infinite loss on an impossible outcome.
        loss = -math.log(actual) if actual > 0 else math.inf
        rows.append({"fight_id": fight_id, "p_a": p, "y": y, "brier": (p-y)**2,
                     "log_loss": loss, "correct": None if p == 0.5 else (p > 0.5) == bool(y)})
    n = len(rows)
    picks = [r for r in rows if r["correct"] is not None]
    buckets = []
    for lo, hi in ((0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.01)):
        group = [r for r in picks if lo <= max(r["p_a"], 1-r["p_a"]) < hi]
        buckets.append({"lower": lo, "upper": min(hi, 1), "n": len(group),
                        "mean_confidence": sum(max(r["p_a"], 1-r["p_a"]) for r in group)/len(group) if group else None,
                        "accuracy": sum(r["correct"] for r in group)/len(group) if group else None})
    average_loss = sum(r["log_loss"] for r in rows)/n if n else None
    return {"n_scored": n, "n_picks": len(picks),
            "accuracy": sum(r["correct"] for r in picks)/len(picks) if picks else None,
            "brier": sum(r["brier"] for r in rows)/n if n else None,
            "log_loss": "infinity" if average_loss == math.inf else average_loss,
            "voids": sorted(voids), "excluded": excluded,
            "pending": sorted(fights.keys() - results.keys() - set(voids)), "calibration": buckets}
