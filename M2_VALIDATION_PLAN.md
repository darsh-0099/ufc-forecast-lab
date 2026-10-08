# M2 validation plan

Status: design only, recorded after the `baseline-continuity-v1` tag. No trained M2 artifact or changed M0/M1 coefficients exist.

## Baseline and targets

Continue the established architecture. M0 remains the independent heuristic forecast; M1 remains 75% M0 and 25% de-vigged market. M2 will estimate winner probability from historically fitted features and must be evaluated against these preserved references. Winner/method modeling is a later, separately evaluated target; categorical Monte Carlo does not itself train or validate M2.

Continuity-v1 provides 26 reconstructed completed winner probabilities with independently verified outcomes and 12 pending original-derived predictions. It provides a reproducible comparison set, not a sufficient historical feature training dataset. The 26 completed outcomes have already been inspected during research and cannot be described as an untouched holdout. Original M0 inputs are unavailable for those two older cards; comparisons to M0 must use only events with preserved M0 inputs.

## Required as-of dataset

Every bout needs stable event/fighter identifiers, scheduled start time, official outcome and a source record. Every feature and market observation needs `observed_at`, `available_at`, source URL or dataset identifier, retrieval time and raw-content hash. A pre-fight feature is eligible only if its supporting information was available before the forecast cutoff. Retrieval after a fight does not establish pre-fight availability.

Candidate independent features follow the existing hypotheses: opponent-adjusted striking and grappling, age, past damage/durability, recent form, strength of schedule, phase access, short notice, weight-class changes and scheduled rounds. Historical weigh-in or injury features require contemporaneous evidence; do not backfill them from retrospective explanations. Missing features need an explicit missingness indicator and a documented policy, not invented values.

Keep result labels, feature observations and market snapshots separate. Resolve aliases through a versioned registry. DQ results retain the official winner for prospective scoring; no contests and draws follow a declared exclusion policy with counts reported. Do not silently drop inconvenient losses or retrospectively change frozen predictions.

## Chronological walk-forward protocol

1. Freeze the dataset version, target, feature list, missingness rules, market cutoff, candidate family and evaluation periods before inspecting candidate scores.
2. Split by entire event in chronological order. Training data and every feature contributing to it must precede the evaluation event. Never use another result from the same event to build that event's pre-card forecasts.
3. Fit transforms, imputation, opponent adjustments and calibration using training data only. Use inner chronological folds for regularization or other hyperparameters; do not tune against the outer evaluation events.
4. Begin with a regularized logistic winner model as the simplest fitted candidate. Any more complex model gets its own preregistered comparison. An untrained design is never reported as a working predictive model.
5. For each outer event, persist the training cutoff, eligible source hashes, model artifact, feature schema, code revision and frozen predictions before joining outcomes for scoring.
6. Add subsequent events prospectively. Do not replace the continuity baseline, tune coefficients to the two recovered cards, or describe already inspected outcomes as new out-of-sample evidence.

## Comparisons and adoption

Use matched fight sets and report coverage/exclusion reasons. Compare Brier score, natural-log loss and calibration with sample sizes; winner accuracy is secondary. Compare against M0 where captured, M1, a constant 50% reference and normalized market probabilities where paired timestamp-consistent prices exist. Use closing prices only as a clearly labeled post-forecast benchmark, not a pre-forecast feature.

Report paired score differences and uncertainty accounting for clustering by event. Choose evaluation duration and precision requirements before results are examined; a single strong card cannot justify adoption. Preserve each candidate and its failed evaluations. A candidate may be promoted only after chronological validation and a prospective evaluation period support an improvement without a material calibration or coverage regression.

M1 market weighting remains 25%. Any alternative market weight is a separate candidate with its own chronological tuning and validation. Do not silently fold a learned weight into the preserved baseline.

## Execution and next dependency

Record training seeds, runtime and dependency versions, data hashes, feature eligibility checks and artifacts for every fold. If method distributions are eventually supplied, execute at least 100,000 draws per fight when feasible and preserve the RNG protocol and raw counts. Count reproducibility remains distinct from predictive skill.

The next dependency is an acquired, licensed and audited as-of feature dataset spanning enough prior events for training and multiple later evaluation periods. That dataset is not currently present. Data acquisition and temporal provenance checks precede M2 fitting; no training result is claimed by this plan.
