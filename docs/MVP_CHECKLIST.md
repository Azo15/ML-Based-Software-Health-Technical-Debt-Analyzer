# Web MVP acceptance checklist

The CLI prototype is available today. The first browser-based MVP is the Phase 4
milestone below. This is a local, single-user application for Python repositories.
Research validation continues separately; the UI must identify experimental risk
scores and still provide maintainability findings when no model can be trained.

## Delivery order

1. Phase 2 foundation: historical metrics and traceable labels, with tests.
   Initial pilot and reproducible evaluation are already implemented. Calibration,
   independent validation and label-quality studies remain research deliverables.
2. Phase 3 completion: extract a reusable analysis service from the CLI, record
   skipped files and errors, and stabilize the report structure for the UI.
3. Phase 4.1: local API and background jobs with progress, error states and saved
   reports; a failed scan must not prevent the next scan.
4. Phase 4.2: browser pages for adding a local project, starting a scan, viewing
   ranked files, opening file metrics/findings and downloading JSON/CSV reports.
5. Phase 4.3 — **MVP ready for user testing**: complete the full journey below on
   Windows, provide a repeatable launch command, and verify empty/invalid projects
   and small datasets show understandable messages.

## Acceptance journey

- Start the app using the documented command and open its local browser address.
- Select or enter a local Git repository folder and start an analysis.
- See progress, completion or a useful failure message.
- Inspect the file list and a selected file's metrics and maintenance suggestions.
- Understand when risk estimation is unavailable or experimental.
- Download a report and run another analysis successfully.

GitHub URL import and CI integration are Phase 5 additions and do not block this
local MVP. Multi-language support, accounts, private repository authentication and
automatic code changes are not part of the initial testing milestone. No calendar
date is committed until implementation and end-to-end checks establish readiness.
