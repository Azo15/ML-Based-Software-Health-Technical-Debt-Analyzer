# Phase 4.1 — local API and durable jobs

Install the pinned dependencies and run from the repository root:

```text
python -m pip install -r requirements.lock
python -m web --port 8765
```

Open `http://127.0.0.1:8765/docs` for the interactive API reference. The user-facing
project/results pages are Phase 4.2 work. The launcher binds only to 127.0.0.1;
this is a local single-user service, not a public authenticated deployment.
Browser requests with a different Origin are rejected and Host values are checked.

## API journey

1. `GET /api/health` verifies the service is running.
2. `POST /api/scans` with a JSON body such as the one below returns HTTP 202 and a
   scan ID. Validation errors return 422 and a full queue returns 429.
3. `GET /api/scans/{id}` returns state, progress and any structured error.
4. `GET /api/scans/{id}/report?format=json` downloads the complete result;
   `format=csv` downloads analyzed-file summaries. Reports not ready return 409.
5. `GET /api/scans?limit=50` lists the latest jobs. Unknown scan IDs return 404.

```json
{
  "repo_path": "C:/path/to/repository",
  "max_commits": 100,
  "observation_commits": 10,
  "excludes": ["tests/*"]
}
```

States are `queued`, `running`, `succeeded` and `failed`. A succeeded job can have
a complete, partial or empty analysis report; consult its report `status` and
warnings. Missing model data does not prevent maintainability results.

## Storage and lifecycle

Windows stores the SQLite database under `%LOCALAPPDATA%/SoftwareHealthAnalyzer`.
Other platforms use `~/.local/share/SoftwareHealthAnalyzer`. Override with
`--database <path>`. Reports, requested local paths and progress persist across
restarts. No source files are copied into the database. There is no automatic
retention deletion in this version.

One worker serializes analysis jobs, with at most eight queued/running jobs.
One process owns each database via a file lock; a second instance using that
database is rejected. Run one web worker. The API does not expose arbitrary
commands, download repositories, or execute analyzed code.

Normal shutdown waits for queued/running work. Forced shutdown leaves unfinished
jobs marked failed with `interrupted` when the next instance opens the database;
they are not silently replayed. Cancellation, per-job hard timeouts and automatic
retention are not implemented yet. Unexpected errors are logged locally and
returned as a generic API error. A failed job does not stop subsequent jobs.

Tests exercise real Git analysis through HTTP, failure recovery, progress,
JSON/CSV downloads, restart persistence, interrupted-job recovery, queue capacity,
single-process ownership and origin/host rejection.
