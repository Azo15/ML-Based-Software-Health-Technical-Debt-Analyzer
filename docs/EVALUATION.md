# Model comparison protocol

The CLI compares four fixed methods on the same chronological holdout:

- Random Forest: the predefined scoring model, with a fixed random seed.
- Logistic regression: standardization is fitted only on training data.
- Size baseline: ranks revisions by LOC without fitting a model.
- Constant baseline: assigns the training-set positive fraction to every revision.

The last 20% of labeled commits form the test period. Training examples whose
label observation window reaches that period are excluded. Evaluation includes
class counts, average precision, and precision/recall at an inspection budget of
20% of test revisions (rounded up). Classifier precision, recall, and F1 use the
classifiers' default decision thresholds. Baselines have no classification
threshold, so threshold metrics are omitted for them. Tied ranks retain input
order. Average precision is not trapezoidal integration of the PR curve.

`--output report.json` includes structured `evaluation_details` alongside the
human-readable evaluation. When evaluation is unavailable, its status is
`unavailable`; the explanation remains in `model_evaluation`. Scores are not
calibrated probabilities. Models are not selected or tuned using the test period.

These are within-repository revision comparisons. The same file can appear at
different times, so the results do not establish performance on unseen files or
repositories. Labels remain noisy commit-message candidates. Churn baselines,
calibration, multiple-repository experiments, confidence intervals, and independent
external validation remain Phase 2 work. No measured general accuracy is claimed.

Verification: `python -m unittest discover -s tests -q` exercises the holdout,
observation-window exclusion, comparison outputs, and manually checked metrics.
