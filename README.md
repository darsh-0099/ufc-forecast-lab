# UFC Forecast Lab

UFC Forecast Lab is a Python toolkit for continuing prospective MMA probability experiments. It stores forecast snapshots in a local SQLite ledger, samples winner-and-method outcomes, and evaluates predictions against independently supplied results. The software supports the existing heuristic experimental baseline; infrastructure changes do not reset that baseline. It makes no claim of predictive superiority.

## Architecture

- `core.py`: input validation, American-odds conversion, market normalization, blending, simulation and evaluation.
- `ledger.py`: original forecast bytes, SHA-256 checksums, import timestamps and append-only amendments.
- `cli.py`: commands for validating, freezing, exporting, simulating and scoring.
- `examples/`: synthetic inputs for demonstrating the workflow.
- `tests/`: numerical, validation and ledger integrity tests.
- `baselines/continuity-v1/`: versioned historical reconstructions, separate official outcomes, source hashes and independently recalculated benchmarks.

The package uses the Python standard library at runtime. It does not fetch fighter statistics, scrape markets, schedule monitoring, or train an Elo or machine-learning model. Data acquisition and independent M0 estimates must be supplied by a separate, documented research process.

## Installation

Requires Python 3.11 or newer. From the repository directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Alternatively, run `python3 -m ufc_forecast_lab.cli` directly from the repository without installation.

## Usage

```sh
ufc-forecast validate examples/synthetic.json
ufc-forecast --db demo.sqlite freeze examples/synthetic.json
ufc-forecast --db demo.sqlite export synthetic-demo
ufc-forecast --db demo.sqlite simulate synthetic-demo --draws 100000 --seed 42
ufc-forecast --db demo.sqlite score synthetic-demo examples/results.json
ufc-forecast blend 0.58 -150 130 --weight 0.25
```

To record a cancellation, use `amend synthetic-demo examples/void.json`. A void permanently excludes that fight from scoring. Do not supply a result for a voided fight. Notes use the same amendment structure with `kind: "note"`. Replacement forecasts should be separate snapshots with distinct event IDs; do not overwrite earlier entries. Results are supplied at scoring time and are not persisted by this version.

## Input contract

The synthetic forecast demonstrates schema version 1. Probabilities are fractions in `[0, 1]`. Each forecast requires an event ID, timezone-aware event start and forecast timestamps, and unique fight IDs. Each fight requires fighter names and `p_a`, the probability that the first listed fighter wins. Optional `m0_a` and `market_a` values preserve independent and market estimates.

Optional method distributions require exactly six unconditional branches: `a_ko`, `a_sub`, `a_dec`, `b_ko`, `b_sub`, and `b_dec`. They must sum to one, and the three A branches must sum to `p_a`. Simulation requires these branches for every fight. Rounded tables may fail these consistency checks; obtain the original exact forecast rather than silently renormalizing it.

Result JSON maps fight IDs to `a`, `b`, `draw`, or `no_contest`. Draws and no contests are excluded from binary scoring and reported separately. Missing results remain pending. Disqualifications can be encoded by the official winner as `a` or `b`; this version does not score method predictions.

## Methodology

For American odds, implied probability is `abs(odds)/(abs(odds)+100)` for negative odds and `100/(odds+100)` for positive odds. The two implied probabilities are divided by their sum to remove the quoted overround. Use paired prices from the same source and time; normalization does not remove all market bias.

The default blend is `M1 = 0.75 × M0 + 0.25 × market`. The blend command computes it explicitly; importing a forecast never recalculates its probabilities. Analyst adjustments to M0 are heuristic unless fitted and evaluated on a separate historical dataset. This package does not validate their quality.

M0 uses independent matchup assessment of opponent-adjusted statistics, age, durability, recent form, grappling, striking, strength of schedule and stylistic interactions. M2 is reserved for a future historically trained model evaluated through chronological walk-forward validation. It has not been trained or implemented. MODEL_STATE.md describes the preserved architecture and maintenance requirements.

Seeded categorical Monte Carlo samples the supplied six branches. It measures sampling variation under those assumptions and does not model individual exchanges or quantify model uncertainty. Decision branches describe decision outcomes; they are not a complete treatment of every way a fight may reach its scheduled time limit.

## Validation

```sh
python3 -m unittest discover -s tests -v
```

The optional original-script replay tool requires NumPy and the private recovered archive. Run `python3 tools/replay_original.py --output <fresh-directory>` in a compatible environment. Its verified replay environment uses NumPy 2.3.5. The tool preserves originals and redirects generated files into the new directory. Historical replay tests explicitly skip when their private inputs or NumPy are unavailable.

Verify the sanitized historical baseline without private files using `python3 -m ufc_forecast_lab.baseline baselines/continuity-v1`. It checks pinned file hashes and joins preserved probabilities to independently sourced outcomes. Reconstructed forecasts remain labeled as reconstructions; missing metadata stays missing. See the baseline README for its evidence limits.

Binary evaluation reports mean Brier score `(p-y)^2`, natural-log loss, winner accuracy and favorite-confidence calibration buckets with sample counts. Exact 50% predictions contribute to probability metrics but are excluded from winner-pick accuracy. Impossible outcomes assigned zero probability produce `"infinity"` log loss rather than being silently clipped.

Use chronological, prospective evaluation. Preserve the original snapshot, record amendments separately, and compare independent M0, blended M1 and timestamp-consistent markets on identical fight sets. This release scores the supplied `p_a` only; baseline comparisons require separate input snapshots. Recovered historical data has a separate continuity audit and is not included as a public training dataset. Small calibration buckets cannot establish predictive skill.

## Integrity and limitations

Duplicate event IDs are rejected. Database triggers reject updates and deletes, and reads verify the original input checksum. These protect against accidental application changes, not a database administrator or filesystem attacker. Declared forecast time is supplied by the importer; the separate import time does not prove that an older forecast was actually recorded before an event. Authentic prospective evidence requires contemporaneous publication or an independently timestamped archive.

The runtime schema does not yet capture source URLs, market observation times, feature snapshots or model versions; maintain those in a separate controlled research archive. Raw historical formats may need an explicit adapter. Preserve original date precision and raw bytes; do not invent timestamps or normalize rounded historical tables. There is no automatic reconstruction of missing forecasts, no automatic coefficient tuning and no betting-return evaluation.

Local databases, environments and `private/` or root `data/` directories are ignored by Git. The examples directory contains synthetic data; the versioned baseline contains sanitized research records. Review any new files before publishing: ignore rules do not sanitize content or protect files already tracked. UFC Forecast Lab is independent of the UFC and provides research tools, not guaranteed outcomes or betting recommendations.
