"""Command-line entry point."""
import argparse
import json
import sqlite3
from pathlib import Path
from .core import blend, devig, score, simulate, validate
from .ledger import Ledger


def main():
    parser = argparse.ArgumentParser(description="Freeze, simulate and evaluate MMA probabilities")
    parser.add_argument("--db", default="forecast-lab.sqlite")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "freeze"):
        commands.add_parser(name).add_argument("file")
    sim = commands.add_parser("simulate")
    sim.add_argument("event_id")
    sim.add_argument("--draws", type=int, default=100000)
    sim.add_argument("--seed", type=int, default=0)
    scoring = commands.add_parser("score")
    scoring.add_argument("event_id")
    scoring.add_argument("results_file")
    amend = commands.add_parser("amend")
    amend.add_argument("event_id")
    amend.add_argument("file")
    export = commands.add_parser("export")
    export.add_argument("event_id")
    market = commands.add_parser("blend")
    market.add_argument("m0", type=float)
    market.add_argument("odds_a", type=float)
    market.add_argument("odds_b", type=float)
    market.add_argument("--weight", type=float, default=0.25)
    args = parser.parse_args()
    try:
        if args.command == "blend":
            market_a = devig(args.odds_a, args.odds_b)
            result = {"market_a": market_a, "m1_a": blend(args.m0, market_a, args.weight)}
        elif args.command == "validate":
            doc = validate(json.loads(Path(args.file).read_bytes()))
            result = {"valid": True, "event_id": doc["event_id"]}
        else:
            ledger = Ledger(args.db)
            if args.command == "freeze":
                result = {"sha256": ledger.freeze(Path(args.file).read_bytes())}
            elif args.command == "amend":
                ledger.amend(args.event_id, json.loads(Path(args.file).read_bytes()))
                result = {"recorded": True}
            elif args.command == "export":
                result = ledger.get(args.event_id)
            elif args.command == "simulate":
                result = simulate(ledger.get(args.event_id), args.draws, args.seed)
            else:
                result = score(ledger.get(args.event_id), json.loads(Path(args.results_file).read_bytes()), ledger.voids(args.event_id))
        print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, TypeError, KeyError, OSError, sqlite3.Error) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()
