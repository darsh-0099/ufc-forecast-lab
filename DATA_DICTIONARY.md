# Data dictionary

## Provenance levels

Future M2 feature observations require both `observed_at` (when measured) and `available_at` (when knowable), alongside retrieval time and source hash. These fields are planned and are not fabricated for the recovered legacy data. See M2_VALIDATION_PLAN.md for temporal eligibility requirements.

| Level | Meaning |
|---|---|
| Recovered artifact | A downloaded CSV/JSON preserved byte-for-byte with SHA-256; historical authorship and freeze time are not proved by the hash |
| Transcribed record | A displayed historical value preserved exactly as text; the reconstructed label describes its machine-readable transcription and does not imply a standalone original file ever existed |
| Reported benchmark | Historical aggregate claim; stored separately from independent recomputation |
| Externally checked outcome | Winner/method/round checked against a named public source, with access method and conflicts recorded |
| New audit execution | A newly executed calculation or simulation with its own protocol; never labeled the historical execution |

## Recovered October 10 format

| Fields | Meaning and units |
|---|---|
| `event`, `event_date`, `freeze_date` | Event label and declared dates; dates lack clock time/timezone and must not be fabricated into exact timestamps |
| `fighter_a`, `fighter_b`, `division`, `rounds` | Original fighter ordering and bout metadata |
| `elo_a`, `elo_b`, `elo_prior_a_pct` | Captured public rating inputs and reported logistic prior in percent |
| `analyst_adjustment_pp` | Event-specific heuristic adjustment, percentage points |
| `independent_m0_a_pct` | Independent A-win estimate in percent; not trained ML |
| `odds_a`, `odds_b`, `devig_market_a_pct` | Paired American prices and normalized A probability in percent; snapshot date exists, exact time/book provenance is incomplete |
| `final_a_pct`, `final_b_pct` | Frozen blended winner probabilities; preserve exactly |
| `favorite`, `favorite_pct`, `favorite_fair_moneyline` | Display labels and derived fair price |
| `a_KO_TKO_pct`, `a_SUB_pct`, `a_DEC_pct`, B equivalents | Six unconditional winner-and-method percentages; KO and TKO share a branch |
| `GTD_pct` | Reported decision/distance branch total; not a complete treatment of exceptional time-limit outcomes |
| `uncertainty`, `drivers` | Analyst assessments and matchup explanations; preserve in private provenance archive |
| `mc_iterations`, `mc_seed` | Draws per fight and seed; recovered script uses NumPy `default_rng` and sequential multinomial sampling in original fight order |
| `mc_outcomes_aKO_aSUB_aDEC_bKO_bSUB_bDEC` | JSON-only integer count array in the named order; each array sums to 100,000 |

The CSV and JSON share all CSV fields; JSON additionally contains model text, source URLs and simulation metadata. Their captured numeric fields agree exactly. Source URLs do not substitute for immutable historical source snapshots.

The original October 10 script additionally preserves `cond_a` and `cond_b`: KO/TKO, submission and decision fractions conditional on each fighter winning. Stable largest-remainder apportionment transforms these into six unconditional branches using the frozen winner total in integer tenth-percent units. M0 is clipped to [0.05, 0.95], blended 75/25, then rounded to 0.1 percentage point before method apportionment or simulation. This script-derived ordering is confirmed by exact file replay; it is not inferred from rounded tables.

`original-script-replay/replay-report.json` stores script and output hashes, replay date, Python/NumPy versions, RNG protocol, seed, draw counts, byte-equality checks and original-file integrity. Only `OUT` is redirected using an AST transformation; no forecast or sampling operation changes. Verified replay environment: Python 3.12.14 and NumPy 2.3.5. The historical environment version remains unknown.

## Local runtime schema

The command-line scaffold accepts schema version 1, timezone-aware `forecast_at` and `event_start`, unique `event_id`/`fight_id`, and fractional `p_a`. Optional method fractions must sum to one and match `p_a`. The legacy October 10 artifacts are archived in their original format; they are not silently forced into this runtime schema. Any future adapter must preserve raw bytes, original date precision, metadata, method order and exact probabilities.

## Historical records and scoring

The immutable `baselines/continuity-v1/data/forecasts.json` stores 26 rows with `origin: reconstructed_displayed_record` and 12 rows with `origin: extracted_from_recovered_original`. `p_a_pct` and method percentages are original decimal strings. `trusted_freeze_timestamp` remains null. Missing method distributions remain null; rounded historical method sums are retained, flagged and excluded from probability simulation requiring exact normalized inputs. The Gall–Dumas void lives in `void_forecasts` and cannot join the scored cohort.

`data/outcomes.json` stores independently checked winners, method groups, rounds and source URLs. Event-scoped fight IDs define the joins. Its alias table resolves Machado to Tina Black and RDA to dos Anjos without overwriting source labels. `metrics.json` is calculated solely from those outcomes and forecast probabilities. `data/reported-benchmarks.json` remains a separate collection of historical claims; its contents do not influence scoring. `data/sources.json` records input hashes, and `manifest.json` pins every baseline data file and the metric output. Corrections require a new version rather than editing v1.

Transcriptions retain probability percentage strings, matchup labels and result text. Original labels remain unchanged even where identity conflicts exist. Canonical outcomes and alias decisions belong in a separate evidence layer. Unknown values remain null or explicitly missing.

Brier score is mean `(p-y)^2`; log loss uses natural logarithms. Confidence uses the picked fighter's frozen probability. Draws and no contests are excluded from binary metrics and counted separately; DQ winners are retained. Exactly 50% forecasts have no directional pick. Benchmarks based on unresolved rows stay labeled reported/transcribed rather than verified.

Raw artifacts, original assistant records, transcripts and complete audit outputs live outside tracked publication files or under ignored `private/`. Do not publish private source material. Frozen integrity tests use preserved hashes, duplicate rejection and update/delete protection; these do not establish externally trusted timestamps.
