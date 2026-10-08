# Model state

State date: 2026-10-08. Experimental baseline: existing Forecast Lab, continued unchanged. Versioned recovery baseline: `continuity-v1` (Git tag `baseline-continuity-v1`). Archive status: partial recovery with explicit reconstructions. Search, reconstruction, independent outcome scoring and baseline reproducibility checks are complete for the available three-card scope. M2 fitting still requires a suitable chronological feature dataset.

## Architecture

**M0 — independent heuristic forecast.** Matchup-based assessment uses opponent-adjusted statistics, age, durability and accumulated damage, recent form, grappling access and sequences, striking, strength of schedule and stylistic interactions. These are analyst estimates, not historically trained coefficients.

The recovered October 10 artifacts and original script capture public Elo ratings, additive analyst adjustments in percentage points, and independent M0 probabilities. The script confirms the 400-point logistic Elo transform, the recorded adjustments and M0 clipping to [0.05, 0.95]. Its conditional method estimates use stable largest-remainder apportionment into exact tenth-percent bins after M1 is rounded. The original script reproduces all stored outputs exactly. Original feature assessments and historical source snapshots remain incomplete. Do not generalize event-specific adjustments into persistent learned weights.

**M1 — market blend.** Preserve `M1 = 0.75 × M0 + 0.25 × de-vigged paired market probability`. All 12 October 10 final probabilities are reproduced to their published one-decimal percentage precision from the captured inputs. Do not change the 25% prior weight based on individual cards.

**M2 — future trained model.** Not implemented, not trained, and not validated. Require chronological walk-forward evaluation, historically available feature and price snapshots, training-only tuning and calibration, and identical out-of-sample cohorts for comparison against frozen M0/M1. Report leakage exclusions, sample counts and uncertainty.

After freezing continuity-v1, M2_VALIDATION_PLAN.md records the data eligibility, event-level chronological splits, candidate comparisons and adoption requirements. This is a design artifact; no training has begun because the as-of feature dataset is absent.

**Monte Carlo.** Six categorical winner/method branches, not detailed fight dynamics. Use at least 100,000 executed draws per fight when feasible; record seed, RNG/library version, stream ordering, input hashes, assumptions and raw counts. Simulation sampling error is separate from model uncertainty. Never replace a frozen probability with a rerun frequency.

## Current preserved baseline

- Allen–Duncan: recovered CSV/JSON and original script, 12 fights, declared freeze date October 8 and event date October 10, 2026; seed 2026100801 and 100,000 draws per fight. Verified replay with Python 3.12.14 / NumPy 2.3.5 reproduces all 12 count arrays and both files byte-for-byte. The originally used environment version is not recorded.
- UFC 332: 14 displayed frozen winner probabilities and six-branch distributions transcribed; completed scorecard preserved separately. No standalone CSV/JSON or script was supplied for this card. RNG protocol, unrounded distributions and counts are undocumented; execution replay is unavailable.
- Rosas–Barcelos: 12 displayed winner probabilities and completed scorecard reconstructed; Gall–Dumas void and Hernandez–Dumas replacement retained. No standalone CSV/JSON or script was supplied for this card. Full method distributions and forecast inputs are not present in the recovered displayed records. Machado is verified as Valesca Machado, also known as Tina Black; the original label is retained with a sourced alias mapping.

Raw recovered files and source records remain in the private archive. Sanitized forecast records, separate official outcomes, historical summary claims and recalculated metrics are versioned under `baselines/continuity-v1/`. All 26 completed prediction identities are resolved. The combined independently scored result is 20/26, Brier 0.19022757692307693 and log loss 0.5640163556358085. The baseline also preserves 12 pending October 10 predictions and one void record. The reviewed software and sanitized baseline are published to the project GitHub repository, which is now the source of truth for public project files. Private recovery material remains local. Publication used the connected GitHub account; the original local history and annotated baseline tag remain in the local archive. See CONTINUITY_REPORT.md for evidence levels and open gaps.

## Update protocol

After every forecast, amendment, scorecard or model change, update this file, MODEL_CHANGELOG.md, LEARNING_LOG.md and DATA_DICTIONARY.md as appropriate. Keep original artifacts immutable and hash-addressed. Record raw evidence separately from summaries and interpretations. Feature/source recovery and verification must precede model improvements.
