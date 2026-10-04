# Phase 4.2 — browser interface

## Studio refinement — 2026-10-04

The local dashboard now uses a graphite sidebar, warm paper surfaces and copper
accents. An original, decorative analysis-flow panel describes the pipeline;
it is not a live chart or a claim about model performance. The empty workspace
explains the three-step journey. All styling remains local with system fonts.
The external codescope.dev site was used only as a visual reference; no source,
logos, images, copy or globe animation were reused.

The file toolbar adds findings-only filtering and descending findings/complexity
sorting, plus alphabetical or original report order. Search combines with the
filter. The visible count announces the selection; these controls do not change
the saved report or exports. Selecting a different report resets the controls.
Keyboard focus styles, a skip link, reduced-motion support, an accessible native
dialog and horizontal table scrolling support keyboard and narrow-screen use.

Verification: 51 Python tests passed; frontend formatting passed. In the browser,
a real saved report filtered from 28 to 7 files, complexity sorted descending,
an unmatched search returned zero rows, and the filtered CSV still contained all
28 files. The detail dialog opened and Escape closed it at 390 x 844. The page
had no horizontal overflow (375px scroll width in a 390px viewport). Desktop
visual inspection and browser console checks passed. This is not a complete
assistive-technology audit. Public GitHub import remains the next Phase 5 step.

## Original interface scope

Start with `python -m web --port 8765`, then open `http://127.0.0.1:8765/`.
The local UI is branded CodeScope. It uses locally served HTML, CSS and JavaScript;
there are no CDN fonts, external scripts or separate frontend build requirements.

Enter the full local Git repository root in **Proje klasörü**, optionally change
the analysis settings, then select **Analizi başlat**. The page shows the current
analysis stage and per-stage counts. Completed reports include file/finding/skip
counts, a searchable file list, file detail dialogs, maintenance suggestions,
skipped-file reasons and model evaluation. JSON and CSV links download saved
reports. The sidebar lists the latest 50 scans, including failed scans. A scan
URL fragment can reopen an existing result after a page reload.

The folder path is entered as text; this version does not open an operating-system
folder picker. Search filters the displayed report only. Historical scans and
reports persist in the API database. Unknown or insufficient model output is
shown explicitly, without invented risk percentages. Findings are rule-based;
they are not automatic code fixes.

Repository paths, file names, messages and finding text are inserted as text
nodes, not interpreted as HTML. The dashboard's content policy only permits local
assets. API origin/host checks remain in effect. Switching scans invalidates old
poll results so a previously selected scan cannot replace the current report.

## Verification on 2026-10-02

- All 49 Python tests passed, including API/static asset delivery and prior job tests.
- Browser: started a real repository scan, observed progress and completed results.
- Browser: searched a file, opened its maintenance suggestions and closed the dialog.
- Browser: downloaded the JSON report and returned to a saved scan after testing a
  nonexistent folder's readable error message.
- Desktop visual inspection completed. Formal responsive/accessibility checks,
  startup instructions from a fresh installation and the full MVP acceptance
  checklist remain Phase 4.3 work. This is a usable preview, not that final gate.
