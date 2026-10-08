# Continuity report — 2026-10-08

The existing experimental baseline is preserved as `continuity-v1`, tagged `baseline-continuity-v1`. Recovery, labeled reconstruction, independent outcome verification and reproducibility checks are complete for the available three-card scope. The full historical archive is still incomplete. M2 fitting requires a chronological as-of feature dataset; no coefficients have changed.

## Recovery inventory

| Material | Status |
|---|---|
| Allen–Duncan October 10 frozen CSV/JSON | Both downloaded artifacts recovered and copied byte-for-byte; 12 fights; all shared fields agree |
| Allen–Duncan M0, odds, M1, methods and simulation output | Present in JSON/CSV; seed 2026100801; 100,000 saved draws per fight; 1.2 million total |
| Allen–Duncan original simulation script and environment | Script recovered; exact replay succeeds under Python 3.12.14 / NumPy 2.3.5; historical environment version remains unrecorded |
| UFC 332 original forecast and scorecard | Displayed records recovered; 14 winner probabilities and six-branch method table transcribed; original files/script/counts missing |
| Rosas–Barcelos scorecard and final board | Displayed records recovered; 12 winner probabilities and result claims; replacement and void retained |
| Rosas original complete pre-event forecast | Missing; complete methods, independent inputs, prices, seed and script not recovered |
| Earlier research history | Partial; DWCS Week 7, Steveson-related revisions and initial architecture/version records missing |
| Prior-source archive | Six substantive assistant records retained locally outside the publication repository; accessible thread retrieval returned no attachment payloads and no older-page cursor |
| Other project conversations/files | No additional Forecast Lab conversation found in available recent/pinned or archived inventories; synced sources empty; filename searches covered project mirrors, Downloads and local Codex documents |
| GitHub source of truth | Established: reviewed software and sanitized continuity-v1 baseline published; private archive excluded |

Raw recovered records are kept private. Sanitized numerical reconstructions and independently checked outcomes are versioned in `baselines/continuity-v1/`; no private conversation content is included. Raw artifacts remain in `private/continuity/`, with original source records outside Git.

The repeated search covered the original forecasting chat, available recent/pinned conversation inventory and filename searches of Downloads, local Codex documents and project mirrors. No additional UFC 332/Rosas original artifacts were found. Current chat retrieval provides no older-page cursor or attachment payloads; previously recovered older records remain preserved locally. Reference-only messages cannot be expanded into missing files. The bounded reconstruction therefore uses the preserved displayed values, with provenance labels and null missing fields.

## Historical benchmark reconciliation

| Cohort | Reported winners | Recomputed Brier | Recomputed log loss | Conclusion |
|---|---:|---:|---:|---|
| Rosas–Barcelos, 12 reconstructed rows | 7/12 | 0.2670579167 | 0.7326953809 | Official-result scoring reproduces 0.2671 / 0.7327; Machado/Tina Black alias verified |
| UFC 332, 14 recorded rows | 13/14 | 0.1243730000 | 0.4194343340 | Reproduces 0.1244 / 0.4194 |
| Combined recorded cohort, 26 | 20/26 | 0.1902275769 | 0.5640163556 | Reproduces 0.1902 / 0.5640; does not establish completeness of the experiment |

Reported summaries, reconstructions and externally checked outcomes are separate files. The versioned evaluator calculates metrics from official winners, not recorded correctness flags. All 26 winners agree with the historical scorecard claims. The recovered Rosas confidence thresholds are 5/9 at 60%, 1/4 at 70%, 1/1 at 80%. UFC 332 has 10/11, 7/7 and 2/2 respectively. Neither card has a 90% forecast. The UFC 332 forecast narrative's statement of one 80% favorite conflicts with its table; the table has Pinas and Smith. Both the original claim and audit discrepancy are retained.

Historical exact-method summaries are 2/12 and 7/14, combined 9/26. The Rosas complete method inputs are missing, so that first exact-method benchmark cannot be independently reconstructed. UFC 332's displayed branches support the seven reported winner/method matches when KO and TKO are grouped. Its 9/14 decision-vs-finish summary is retained separately.

## External outcome checks

All 14 UFC 332 winners align with [UFC's official scorecard result text](https://www.ufc.com/news/ufc-332-silva-vs-wang-official-scorecards). All 12 Rosas scorecard matchups align with [UFC's official results](https://www.ufc.com/news/ufc-fight-night-rosas-jr-vs-barcelos-official-scorecards), with the alias resolution below. These are independently checked outcomes, not authenticated original prediction files. Web search supplied official page text; direct opens returned HTTP 403.

The historical Machado–Amaya row is now resolved. [UFC's athlete profile](https://www.ufc.com/athlete/valesca-machado) identifies Tina Black and lists Amaya vs Machado; [UFC's event profile](https://www.ufc.com.br/news/conheca-lutadores-brasileiros-ufc-vegas-121) names Valesca Machado with the nickname Tina Black. The baseline preserves Machado and 66.0% as originally recorded and adds a separate sourced alias. All 26 completed prediction matchups now have resolved outcome identity. The older unresolved flag remains preserved in the previous private verification snapshot.

KO versus TKO wording differs in some historical summaries but is equivalent under the preserved KO/TKO branch. Hernandez–Dumas time differs across UFC's event page (0:57) and main-card article (0:50); winner, method and round agree. Exact time remains unresolved.

## Reproducibility assessment

October 10 market normalization reproduces every stored market probability within its four-decimal percentage precision. The recovered original script confirms the 400-scale logistic Elo transform, captured adjustment and M0 clipping to [0.05, 0.95]. The 75/25 blend is frozen to 0.1 percentage point before stable largest-remainder method apportionment and simulation. All method totals, winner sums, GTD totals and saved count totals pass arithmetic checks.

This recovers the captured arithmetic, not the full source-to-feature-to-adjustment research process. Historical feature snapshots, rating snapshots, market observation times and analyst adjustment derivation are still needed for full model reproducibility.

The original script has now executed 100,000 draws per fight, 1.2 million total, using NumPy `default_rng` (PCG64), seed 2026100801 and sequential multinomial calls in the original fight order. Under Python 3.12.14 / NumPy 2.3.5, all 12 count arrays match exactly and regenerated CSV/JSON files are byte-for-byte identical to the supplied originals. Only the output path was redirected; the archived script and frozen artifacts were unchanged. The script SHA-256 is `78dbce559f8d40820b4e58850b8aee54de40d632fdee80880833498dd352c7ce`. Original runtime versions are still unknown, but a verified replay environment is now recorded.

The earlier audit using Python's `random.Random` remains saved as a different, deterministic protocol. It matches none of the original count arrays because it does not use the original NumPy multinomial sampler. It is not the original execution replay. Exact replay confirms execution reproducibility; it does not validate heuristic probabilities, source snapshots or pre-event authorship.

UFC 332 displayed method sums are 99.9% for Talbott and Ribovics and 100.1% for Wint. Displayed GTD differs from branch sums for Pinas (30.8 versus 30.7), Wint (29.9 versus 30.0) and Hernandez (56.1 versus 56.2). Preserve every displayed value; request the full-precision originals rather than renormalizing. The Hernandez replacement's reported simulated frequencies sum to 100.1%; they are rounded sample output, not input probabilities.

## Market benchmarks

UFC 332 reports a 13-fight comparison excluding Smith: M1 Brier 0.1331 versus market 0.1376; log loss 0.4433 versus 0.4480. Eight paired prices are visible, but the complete 13-pair dataset, source snapshot and exact timestamp are missing. The aggregate market advantage is preserved as a reported claim, not independently reproduced. Rosas has no complete consistent paired closing-market dataset. October 10 paired prices are recovered, but its event is pending and cannot be scored yet.

## Recovery requirements and development gate

The October 10 script gap is resolved, including exact output replay. Remaining requirements: original UFC 332 and Rosas frozen files/scripts with full-precision distributions; prior project conversation export or earlier research records; complete closing-market snapshots for the 13-fight comparison; and source/feature snapshots behind the captured October 10 analyst inputs. Preserve original filenames and bytes where possible. Full archive completeness remains unverified.

Run `python3 tools/audit_continuity.py` from the repository to reproduce the numerical audit when the private archive is present. For original execution replay, use Python with NumPy and `tools/replay_original.py --output <fresh-directory>`. Run `python3 -m unittest discover -s tests -v` for application and continuity tests; the original-replay test requires NumPy and the private script. Model improvements remain deferred while broader continuity gaps are resolved. Historical provenance gaps remain outstanding; remote persistence is established.

## Versioned baseline and reproducibility gate

`baselines/continuity-v1/` contains 26 labeled reconstructed completed forecasts, 12 original-derived pending forecasts, one void, separate official outcomes and aliases, reported historical summaries, recalculated metrics, source hashes and a manifest. `python3 -m ufc_forecast_lab.baseline baselines/continuity-v1` verifies integrity and independently reproduces scoring without private sources. The reconstruction builder reproduces the four dataset files exactly and refuses an existing destination. Changes to frozen probabilities are detected; missing outcomes fail rather than reducing the cohort silently. Original October 10 execution still reproduces both files byte-for-byte.

All 15 tests passed using Python 3.12.14 with NumPy 2.3.5. The available-data baseline gate is complete. Future M2 development must collect an as-of historical feature dataset, register walk-forward splits and compare against the preserved baseline. The 26 completed outcomes alone do not support training a new feature model or optimizing persistent weights. Local Git versioning and GitHub publication are established. The published snapshot exactly matches reviewed local files. Original local commits and the annotated baseline tag remain locally archived because command-line push authentication is unavailable.
