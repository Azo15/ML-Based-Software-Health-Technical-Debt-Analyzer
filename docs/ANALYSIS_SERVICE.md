# Shared analysis service and report contract

`analysis.service.analyze_repository(path, ...)` is the shared entry point for
the CLI and future local API. It accepts a Git repository root, positive commit
limits, an optional selected Python file, current-file exclusion globs and an
optional progress callback. It returns a JSON-safe dictionary and never imports
or executes the target project's code. Fatal input, Git, history or model failures
raise `AnalysisError`, whose `code` is suitable for a client error response.

Progress callbacks receive `stage`, `completed` and `total`. Stages are validating,
mining, historical_metrics, training, current_files and completed. A zero total
means no count is available for that stage, not an estimated overall percentage.
Callbacks are synchronous; clients should keep them fast. Cancellation, job
storage and HTTP access are Phase 4 responsibilities.

## Report version 1, additive fields

Existing `repository`, `scan`, `model_evaluation`, `evaluation_details` and `files`
remain compatible. Consumers should ignore unknown fields. Added fields are:

- `status`: `complete`, `partial` or `empty`. A partial result includes readable
  files but also invalid, missing, unreadable or out-of-repository files. An empty
  result has no analyzed files. Deliberate exclusions and empty modules alone do
  not make a nonempty scan partial.
- `repository_state`: starting and ending HEAD plus tracked-change state at start.
  Current metrics describe working-tree files, while training uses Git history.
  A changed HEAD during the scan produces a warning and a partial result. This is
  not an immutable filesystem snapshot; concurrent edits without a commit may
  still occur. Run against a quiet checkout for reproducible current-file metrics.
- `skipped_files`: relative path, stable reason and optional explanatory detail.
- `warnings`: code and readable message, including unavailable risk estimation.
- `summary`: analyzed/skipped file counts, usable training revisions and excluded
  invalid/empty historical revisions. Model evaluation reports the actual split.

Insufficient training data does not prevent maintainability analysis. Do not
interpret `complete` as evidence that a model is trained or calibrated.

## CLI usage and exit codes

```text
python -m cli.main analyze <repository-root> --exclude="tests/*" --exclude="examples/*" --output report.json
```

Globs match case-sensitive repository-relative paths with `/` separators. They
should use the `--exclude=pattern` spelling to avoid wildcard expansion by a
Windows shell/runtime before the CLI receives the pattern. They
filter current-file presentation only; historical labels/training retain their
existing population. Default analysis includes tracked Python files; `--file`
can explicitly select an existing untracked Python file within the repository.
Environment directories are always excluded.

Exit 0: complete or partial nonempty analysis. Exit 1: fatal error, empty result,
or report write failure. Invalid command syntax/options use Typer's exit 2.
Empty reports can still be exported for diagnosis. JSON retains skips/warnings;
CSV remains a summary of analyzed files and omits report-level metadata.
Existing output files are not overwritten. `analysis.report_export.write_report`
is the framework-independent exporter; the former CLI import remains compatible.

Phase 3 verification includes existing CLI/report checks, file-selection filters,
partial results, empty exports, typed input errors and progress completion. Phase
4.1 can now build background jobs around this service without duplicating logic.
