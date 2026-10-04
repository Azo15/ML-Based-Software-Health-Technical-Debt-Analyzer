# Initial label-evidence inspection — 2026-10-01

This is an exploratory agent inspection, not independent human validation. The
selection rule was the first positive labeled revision in each repository's
chronological audit export. Two examples cannot estimate label precision. Raw
machine-generated records remain `unreviewed`; no labels were rewritten.

## Click

Snapshot `c3535905c77a29afc84861b29d3ad366ce5451bd`, file
`tests/test_shell_completion.py`, is labeled positive through two later commits.
Inspection of `git show <hash> -- tests/test_shell_completion.py` showed:

- `b7e5fd4cc7de70280eccd39f2bb956df617e5519` changes expected fish-completion
  output and removes a multiline-help test in a regression-related commit.
- `ddf20d0673788ebe8ec28b6031a24a36cba92115` adds an import and a regression test.

Judgement: regression-related test maintenance, with insufficient evidence that
the earlier test file itself contained the product defect. A positive candidate
here should not be presented as a confirmed defective source file.

## Requests

Snapshot `c65c780849563c891f35ffc98d3198b71011c012`, file `tests/test_requests.py`,
is labeled positive by `7bc45877a86192af77645e156eb3744f95b47dae`. Inspection of
the commit message and file diff shows a new regression test and an import. The
message body matches the broad keyword heuristic (including patch/issue).

Judgement: added regression coverage, not evidence that the existing test file
was the defect location. The label correctly denotes later candidate-commit
participation but does not establish defect ground truth.

## Consequence

Commit participation and file defect location must remain distinct. A future
study should separate production and test files, audit negative examples too,
and use independent reviewers before adopting stronger labels. Do not silently
remove test files from the frozen pilot or tune the classifier on these results.

## Updated experiment

`experiments/results/pilot-history-2026-10-01.json` records both completed runs
from clean analyzer commit `d8637ed`, including per-revision evidence and a
past-only churn baseline. That baseline's average precision was 0.273 for Click
and 0.333 for Requests, equal to the constant baseline in these test samples.
Adding it does not demonstrate predictive improvement. The model feature sets
were unchanged. All 37 tests passed before this run.
