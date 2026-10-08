# Continuity baseline v1

This version preserves the existing M0/M1 experiment as recovered on October 8, 2026. It is not a new model. The Git tag `baseline-continuity-v1` identifies its code and documentation; `manifest.json` pins each dataset and metric file by SHA-256.

- 26 completed predictions are explicitly labeled `reconstructed_displayed_record`. Original displayed percentage strings are preserved; their original full-precision files and trusted freeze timestamps are unavailable.
- 12 pending Allen–Duncan predictions are labeled `extracted_from_recovered_original`. Their private original CSV, JSON and simulation script are hash-addressed in `data/sources.json`; exact file replay has been verified.
- Gall–Dumas remains a separate void record at 58.3%; Hernandez–Dumas is the scored replacement at 65.0%.
- Independently checked results are stored in `data/outcomes.json`. They are joined by event-scoped fight IDs; reported correctness flags and summary metrics are not used to determine winners.
- The Machado/Tina Black alias is supported by [UFC's athlete page](https://www.ufc.com/athlete/valesca-machado). Original forecast labels remain intact. All 26 completed matchup identities are resolved.
- UFC 332 rounded method values retain their original sums and GTD discrepancies. They are not renormalized. Missing Rosas method distributions remain null.

| Cohort | Correct | Brier | Log loss |
|---|---:|---:|---:|
| Rosas–Barcelos | 7/12 | 0.2670579167 | 0.7326953809 |
| UFC 332 | 13/14 | 0.1243730000 | 0.4194343340 |
| Combined | 20/26 | 0.1902275769 | 0.5640163556 |

UFC 332 exact winner/method accuracy independently recomputes to 7/14. The Rosas 2/12 method summary remains reported-only because complete method inputs are unavailable. Time discrepancies for Hernandez–Dumas have no effect on these metrics. The 13-fight historical market comparison still lacks a complete timestamped price snapshot and is retained only as a reported benchmark.

Verify from the repository root:

```sh
python3 -m ufc_forecast_lab.baseline baselines/continuity-v1
python3 -m unittest discover -s tests -v
```

Rebuilding requires the local private recovery archive. Run `python3 tools/build_baseline.py --output <fresh-directory>` to reproduce the four dataset files. The builder refuses an existing destination. Private raw evidence, prompts and source records are not included here.

Do not edit this baseline in place. Add corrected evidence and create a new version with explicit lineage. An integrity hash protects against unrecorded changes; it does not prove historic pre-event publication or establish that all earlier project records were recovered.

This version supports future evaluation against the preserved baseline. It is not an M2 training dataset: the 26 outcomes lack complete historical feature snapshots and constitute only two completed cards. M2 fitting and coefficient adoption require a separate chronological dataset and prospective evaluation protocol.
