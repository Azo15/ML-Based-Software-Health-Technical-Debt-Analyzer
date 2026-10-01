# Implementation plan

This project ranks Python files for future bug-fix risk and reports maintainability findings separately. The system is decision support: it must not present an untrained model output as a probability or equate bug risk with technical debt.

## Delivery rules

- Implement one coherent change per commit on `azo2`.
- Keep the original Desktop checkout and its staged `CONTRIBUTING.md` change untouched.
- Run relevant tests before each implementation commit and record the result in the commit message or change notes.
- Do not execute code from analyzed repositories. Preserve the provenance of every feature, label, model run, and prediction.
- Start with Python repositories. Multi-language analysis, private GitHub access, LLM explanations, and automatic code changes are later work.

## Phase 0 — Reproducible baseline

Remove the committed virtual environment from version control, add ignore rules, define reproducible installation, and correct the documented CLI invocation. Add a small regression suite that reproduces the known misleading outputs. Exit gate: fresh installation and smoke test on a tiny Git fixture work on Windows and Linux.

## Phase 1 — Trustworthy data and metrics

Mine recent commits deterministically, preserve repository-relative paths and renames, record commit dates, and extract features from the source state available at a given commit. Separate bug-fix *candidate* detection from the training label. Track the pre-fix version and label confidence. Reject syntax-invalid files explicitly. Add maximum and distributional function complexity alongside averages. Exit gate: fixture tests prove no post-fix source is labeled as pre-fix code and no future data enters a snapshot.

## Phase 2 — Model and evaluation

Create a file-version dataset with a declared future observation window. Compare size/churn baselines, logistic regression, and Random Forest. Split chronologically; check file- and repository-level leakage. Report class counts, precision, recall, PR AUC, Recall at K, and calibration. Do not output a probability unless the model and calibration are valid. Exit gate: repeatable experiment on multiple public Python repositories and an untouched later test period.

Progress (2026-10-01): fixed holdout comparisons and a reproducible, commit-pinned
Click/Requests pilot are implemented. Past-only churn metrics, a churn baseline
and traceable label evidence are available; `LABEL_AUDIT_PILOT.md` records an
initial two-example inspection. This phase remains open for a formal label audit,
calibration and independent validation. See `MVP_CHECKLIST.md` for the local web
MVP delivery order; the browser acceptance milestone is Phase 4.3.

## Phase 3 — CLI and reports

Analyze the current state of every selected Python file. Show separate bug-risk and maintainability results, explanations, and uncertainty. Support filters, JSON/CSV exports, clear exit codes, and useful errors for empty or small datasets. Exit gate: documented CLI commands and end-to-end fixture tests pass.

Completed on Windows (2026-10-01): a shared analysis service, current-file filters,
partial/empty report states, structured errors, skipped-file reasons, Git state,
progress events and compatible JSON/CSV exports. All 42 tests pass. The contract
and exit-code semantics are documented in `ANALYSIS_SERVICE.md`. Phase 4.1 is next.

## Phase 4 — API and web panel

Build a Python API around the analysis core and background scan jobs. Add project overview, ranked file list, file history, findings, and model evaluation screens. Keep data local by default. Exit gate: a user can add a local repository, run a scan, inspect a file, and download a report through the UI.

Phase 4.1 completed on Windows (2026-10-01): local FastAPI service, a bounded
single-worker queue, durable SQLite reports, progress/error endpoints and report
downloads. All 48 tests passed, including HTTP-to-analysis integration. See
`LOCAL_API.md`. User-facing pages (4.2) and MVP acceptance (4.3) remain outstanding.

## Phase 5 — GitHub and CI integration

Accept public GitHub repository URLs with bounded clone/scan size and time. Add a GitHub Actions example that publishes a machine-readable report and detects risk or maintainability regression. Exit gate: an example public repository and CI run produce the same report format as local analysis.

## Phase 6 — Thesis and demonstration

Document research question, data construction, label noise, baselines, experimental results, failure cases, threats to validity, architecture, installation, and demo steps. Exit gate: another person can reproduce the reported experiments and run the product from the documentation.

## Scope controls

Phases 0–3 establish the research and analysis foundation. If the schedule tightens, defer GitHub URL import and CI before weakening the data and evaluation gates. Final dates depend on the academic deadline and team size.
