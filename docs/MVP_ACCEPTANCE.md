# Phase 4.3 — Local MVP acceptance

Completed 2026-10-04 on Windows with Python 3.12.14. This gate covers a local,
single-user Python repository analyzer. It does not establish commercial value,
production readiness or scientific predictive validity.

## Reproducibility

- Created a fresh `.venv` and installed `requirements.lock`; `pip check` passed.
- `python -m unittest discover -s tests -q`: **51 tests passed** on 2026-10-04.
- Launched the installed environment with `start.cmd`; the browser opened on
  `http://127.0.0.1:8765/`. Previously saved scan history remained available.
- Frontend formatting and `git diff --check` passed.

## Acceptance evidence

- Real project scan `4ef2775dc24a46b58edbae22518ffa1e`: 28 analyzed files,
  7 maintenance findings, 5 skipped files. Progress reached completion and a
  page reload reopened the saved report. These are this working-copy snapshot's
  counts, not fixed expected counts for future versions.
- File search selected `analysis/service.py`; its detail dialog displayed metrics
  and maintenance advice. Escape closed the dialog. The dialog now has an
  accessible name. This is a basic keyboard check, not a full accessibility audit.
- CSV downloaded through the browser; JSON download was checked in Phase 4.2.
- README-only fixture `3bf0a31ab0eb4ba0828200a6b344c8ac`: completed with explicit
  no-files messaging and zero counts; exported CSV contained only its header.
  A real project scan then completed successfully in the same application.
- A repository without commits produced the actionable Turkish `empty_history`
  message during the 2026-10-02 browser check. Regression tests cover that case
  and the README-only case. Missing/non-Git folder messages were also checked.
- At 390 x 844 the form and detail dialog remained usable, with the wide table
  scrolling inside its container rather than expanding the page (2026-10-02).
- Insufficient model data is explicitly reported without inventing a risk score.

## Fixes and limits

Added the Windows launcher and Turkish quickstart, distinguished missing commit
history from generic Git errors, named the file dialog, and cleared the previous
scan's state badge while a newly selected scan loads.

Only local Python Git repositories are supported. There is no hosted multi-user
service, authentication, public GitHub import or automatic code modification.
The basic browser checks are manual; cross-browser and assistive-technology
coverage remain future work. The test client emits an upstream httpx deprecation
warning, but the suite passes.

Phase 5 adds bounded public GitHub import and CI reports. Label quality,
calibration and independent model evaluation remain open research work in Phase 2.
Do not describe the experimental ranking as a calibrated bug probability or a
validated estimate of financial technical debt.
