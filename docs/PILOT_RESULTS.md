# Pilot results — 2026-10-01

The commit-pinned Click and Requests experiment completed using analyzer
`09ffb7e`. The committed JSON in `experiments/results/pilot-2026-10-01.json`
contains the exact repository pins, dependency versions, split commits and
dataset fingerprints. Two executions with identical source code (before and
after the runner commit) produced identical repository results and fingerprints.
The published execution used a clean analyzer checkout.

## Observations

- Click: 85 training and 33 test revisions, including 9 positive test candidates.
  Average precision: Random Forest 0.388, logistic regression 0.608, size 0.413,
  constant 0.273. In the top 7 revisions, Random Forest found 3 of 9 positive
  candidates; logistic regression found 5 of 9.
- Requests: 57 training and 33 test revisions, including 11 positive candidates.
  Average precision: Random Forest 0.450, logistic regression 0.415, size 0.542,
  constant 0.333. In the top 7 revisions, Random Forest found 1 of 11 positive
  candidates; size ranking found 4 of 11.

These values are not accuracy percentages. Labels indicate future fix-message
candidates, not independently verified defects. Random Forest did not beat the
size baseline on average precision in either sample, and its top-budget recall
was particularly low for Requests. The pilot therefore does not establish a
benefit from the current Random Forest feature set.

## Implications for the next experiment

Keep these outcomes as a recorded pilot. Do not select a winning production model
using this test period and then report the same period as independent validation.
Investigate change-history features and label quality, compare choices inside an
earlier validation period, and evaluate the frozen choice on a new untouched
period or repository. Current predictions remain uncalibrated ranking signals.

The small convenience sample, repeated versions of the same files, dependence
between neighboring outcomes, broad commit-message heuristic, short history,
and absence of confidence intervals limit generalization. Multi-repository runs
are now reproducible, but calibration, churn baselines, label auditing and
external validation are still outstanding Phase 2 acceptance work.

## Verification

All 32 unit/integration tests passed before the runner commit. Both real-repository
runs completed with status `evaluated`, and the comparison of per-repository
results across two runs passed. Reproduction commands are in `EXPERIMENTS.md`.
