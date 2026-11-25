# Public read-only demo

On Render, create a Docker Web Service from this repository and select the
`codex/read-only-demo` branch. Set the health check path to `/api/health`.
The demo serves the original UI and a report generated against this repository
using the CLI. It does not start the job worker or accept scan submissions.

To refresh the report, run the CLI locally, remove the local absolute
repository path from the exported JSON, then replace `web/demo-report.json`.
