# Forecast Lab maintenance

Continue the established experimental baseline. Read MODEL_STATE.md and CONTINUITY_REPORT.md before model work. Do not reset the project or present infrastructure changes as a new model.

Preserve M0 independent heuristic assessment, M1 75% M0 / 25% normalized market, and M2 as a future trained model requiring chronological walk-forward validation. Distinguish heuristic estimates, categorical outcome sampling and detailed dynamics simulation.

Never overwrite frozen probabilities, raw artifacts, original labels or result claims. Add corrections, source verification, replacements and voids in separate layers. Retain exact precision; do not normalize rounded historical tables to satisfy the runtime schema. Missing information must be documented and requested.

The available-data continuity audit is versioned as `continuity-v1`. Preserve this baseline and its tag; corrections require a new version with explicit provenance. Earlier cards were delivered as displayed forecasts; standalone CSV/JSON files and scripts were not supplied. Their machine-readable transcriptions must retain reconstructed labels. Do not describe unsupplied files as lost or require their recovery to preserve the displayed baseline. Before fitting M2 or adopting coefficient changes, obtain as-of historical feature data and use chronological walk-forward evaluation against this frozen baseline. Preserve the research hypotheses in LEARNING_LOG.md. Isolated results are insufficient for major persistent changes.

Update MODEL_STATE.md, MODEL_CHANGELOG.md, LEARNING_LOG.md and DATA_DICTIONARY.md alongside forecasts, scorecards and model changes. Execute at least 100,000 categorical draws per fight when feasible and preserve seeds, protocol, environment, assumptions, input hashes and outputs. Never claim original simulation replay from a new sampler.

Run numerical normalization, frozen integrity, reproducibility and scoring checks. Report optional private-archive tests as skipped when data is absent, not as successful historical verification.

Run `python3 -m ufc_forecast_lab.baseline baselines/continuity-v1` to verify hashes and independently recalculate scores. Historical correctness flags and reported benchmark summaries must never be used as ground-truth outcomes. Preserve pending and void accounting; missing outcomes must not silently shrink the evaluation cohort.

The recovered October 10 script has a verified exact replay. Use `tools/replay_original.py` with NumPy and a fresh output directory; it verifies the reviewed script hash and redirects only `OUT`. Do not execute the legacy script directly against its hard-coded output path or overwrite any supplied original. Keep the standard-library audit protocol distinct from the original NumPy multinomial protocol. Exact replay does not establish predictive validation or recover missing historical source snapshots.

Keep README and public files professional and software-focused. Exclude personal information, conversations, prompts, secrets, private data and raw source records. Stage files explicitly and inspect the full staged diff before publishing. Existing synced `sources/` and parent project instructions are read-only. GitHub is the intended source of truth; do not claim remote persistence until commits exist on the verified remote.
