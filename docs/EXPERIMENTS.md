# Reproducible pilot experiments

Run from the analyzer checkout with the pinned dependencies in `requirements.lock`.
The runner reads local Git data without executing the analyzed projects. It fits
a separate model for each repository; this is not cross-project validation.

`experiments/pilot.json` fixes two public projects, their commit hashes, the latest
200-commit mining budget, and a 10-observed-Python-commit outcome window. The
projects were chosen as small, established Python libraries before observing
scores. They are a convenience sample, not a representative benchmark.

Prepare a directory outside this checkout with subdirectories `click` and
`requests`. For each entry, initialize that subdirectory and fetch its exact pin:

```text
git init <directory>
git -C <directory> remote add origin <url-from-manifest>
git -C <directory> fetch --depth 250 origin <commit-from-manifest>
git -C <directory> checkout --detach FETCH_HEAD
```

The runner rejects a mismatched HEAD, tracked local changes, and shallow history
that does not extend past the mining budget. Repository URLs are provenance only;
the runner never downloads or checks out repositories automatically.

```text
python -m experiments.run --manifest experiments/pilot.json --repos-dir <parent-directory> --output <new-report.json>
```

The JSON records analyzer revision and dirty state, Python/dependency versions,
repository pins, data fingerprints, excluded revision counts, split membership,
class counts, comparison metrics, and unavailable/error explanations. Source code
is not copied into reports. Existing outputs are not overwritten. A failed
repository is retained in the report and causes exit status 1; an insufficient
dataset is an unavailable evaluation, not a program error.

Repeat with the same pins and environment and compare `dataset_sha256` and
`evaluation` for each repository. Full report equality is not required if analyzer
provenance changes. Historical labels are weak commit-message candidates, recent
windows are censored, and the same file can appear in both time periods. An
observation window is measured in commits with retained Python modifications,
not calendar time or all Git commits. No confidence interval, calibrated defect
probability, or claim of general accuracy is produced by this pilot.
