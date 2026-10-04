# Historical metrics and candidate-label audit

Each mined revision records changed lines (added + deleted), prior change count,
and prior churn over the preceding 20 observed Python-changing commits. Current
and future changes do not enter prior metrics. Renames transfer the observed
history. The oldest observations have truncated history; these metrics describe
the bounded mining window, not a file's lifetime. Deleted files without retained
source are still absent from mining; delete/recreate histories and complex Git
branch topology require further validation.

The model comparison includes a prior-churn ranking baseline when these metrics
are available. Random Forest and logistic regression still use their existing
code metrics; the new baseline does not change their deployed feature set.

Dataset rows retain the future observation commit list and matching fix-candidate
commit hashes, paths and subjects. Rename chains within the observation window
are followed. These are label evidence, not model features. Experiment reports
export one audit record per usable labeled revision with `review_status` set to
`unreviewed`. No automated keyword match counts as a human-confirmed bug.

To audit a record, inspect each evidence commit with `git show <hash> -- <path>`,
check its parent version and issue/test context, and record a separate judgement:
confirmed behavioral fix, non-defect change, mixed/uncertain, or insufficient
evidence. Negative labels also need review: absence of a keyword candidate does
not prove absence of a defect. Record reviewer, evidence, judgement and rationale;
do not overwrite the raw labels or tune on the pilot test outcomes.

The next study must use a declared sampling method and independent reviewers
before claiming label precision or agreement. The audit export makes that study
possible; it does not complete the study by itself.
