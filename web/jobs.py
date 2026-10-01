"""Single-worker analysis queue with durable SQLite results."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sqlite3
from threading import Lock
from uuid import uuid4
from filelock import FileLock

from analysis.service import AnalysisError, analyze_repository


class QueueFull(Exception):
    pass


class JobStore:
    def __init__(self, database, analyzer=analyze_repository, capacity=8):
        self.database = Path(database).resolve()
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self.analyzer = analyzer
        self.capacity = capacity
        self.lock = Lock()
        self.closed = False
        self.process_lock = FileLock(str(self.database) + ".lock")
        self.process_lock.acquire(timeout=0)
        try:
            with self.connect() as db:
                db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, state TEXT NOT NULL, created TEXT NOT NULL, updated TEXT NOT NULL, payload TEXT NOT NULL, progress TEXT, result TEXT, error TEXT)")
                db.execute("UPDATE jobs SET state='failed', error=?, updated=? WHERE state IN ('queued','running')",
                           (json.dumps({"code": "interrupted", "message": "Application stopped before this scan completed. Start a new scan."}), self.now()))
            self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="analysis")
        except Exception:
            self.process_lock.release()
            raise

    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat()

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=30)
        try:
            with db:
                yield db
        finally:
            db.close()

    def submit(self, payload):
        with self.lock:
            if self.closed:
                raise QueueFull("Application is shutting down")
            with self.connect() as db:
                active = db.execute("SELECT count(*) FROM jobs WHERE state IN ('queued','running')").fetchone()[0]
                if active >= self.capacity:
                    raise QueueFull("Analysis queue is full; wait for a scan to finish")
                job_id = uuid4().hex
                now = self.now()
                db.execute("INSERT INTO jobs (id,state,created,updated,payload) VALUES (?,?,?,?,?)",
                           (job_id, "queued", now, now, json.dumps(payload)))
            self.executor.submit(self._run, job_id, payload)
            return job_id

    def _update(self, job_id, **values):
        values["updated"] = self.now()
        assignments = ",".join(f"{key}=?" for key in values)
        with self.connect() as db:
            db.execute(f"UPDATE jobs SET {assignments} WHERE id=?", [*values.values(), job_id])

    def _run(self, job_id, payload):
        self._update(job_id, state="running")
        try:
            result = self.analyzer(**payload, progress=lambda event: self._update(
                job_id, progress=json.dumps(event)))
            self._update(job_id, state="succeeded", result=json.dumps(result, allow_nan=False))
        except Exception as exc:
            logging.getLogger(__name__).exception("Analysis job %s failed", job_id)
            error = {"code": exc.code, "message": str(exc)} if isinstance(exc, AnalysisError) else {
                "code": "internal_error", "message": "Analysis failed unexpectedly. Check the application log and retry."
            }
            self._update(job_id, state="failed", error=json.dumps(error))

    def get(self, job_id, include_result=False):
        with self.connect() as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            return None
        result = dict(row)
        for field in ("payload", "progress", "error"):
            result[field] = json.loads(result[field]) if result[field] else None
        if include_result:
            result["result"] = json.loads(result["result"]) if result["result"] else None
        else:
            result.pop("result")
        return result

    def list(self, limit=50):
        with self.connect() as db:
            ids = [row[0] for row in db.execute("SELECT id FROM jobs ORDER BY created DESC LIMIT ?", (limit,))]
        return [self.get(job_id) for job_id in ids]

    def close(self):
        with self.lock:
            self.closed = True
        try:
            self.executor.shutdown(wait=True)
        finally:
            self.process_lock.release()
