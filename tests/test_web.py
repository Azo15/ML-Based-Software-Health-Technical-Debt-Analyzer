import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
from threading import Event
import time
import unittest

from fastapi.testclient import TestClient
from filelock import Timeout

from analysis.service import AnalysisError
from web.app import create_app
from web.jobs import JobStore, QueueFull


def fake_analyzer(repo_path, progress, **options):
    progress({"stage": "current_files", "completed": 1, "total": 1})
    if repo_path == "bad":
        raise AnalysisError("missing_repository", "Repository directory does not exist")
    if repo_path == "crash":
        raise RuntimeError("private diagnostic must not reach API")
    return {"schema_version": 1, "status": "complete", "files": [{
        "path": "a.py", "metrics": {"loc": 1, "cyclomatic_complexity_max": 0},
        "result": {"risk_score": None, "risk_score_kind": "unavailable", "maintainability_findings": []},
    }]}


def wait_for(client, job_id):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        job = client.get(f"/api/scans/{job_id}").json()
        if job["state"] in {"succeeded", "failed"}:
            return job
        time.sleep(0.01)
    raise AssertionError("Job did not finish")


class WebTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "jobs.sqlite3"

    def tearDown(self):
        self.temp.cleanup()

    def client(self, analyzer=fake_analyzer):
        return TestClient(create_app(self.db, analyzer), base_url="http://127.0.0.1")

    def test_failure_then_success_and_both_report_formats(self):
        with self.client() as client:
            self.assertEqual(client.get("/api/health").status_code, 200)
            failed = client.post("/api/scans", json={"repo_path": "bad"}).json()["id"]
            self.assertEqual(wait_for(client, failed)["error"]["code"], "missing_repository")
            self.assertEqual(client.get(f"/api/scans/{failed}/report").status_code, 409)
            submitted = client.post("/api/scans", json={"repo_path": "good"})
            self.assertEqual(submitted.status_code, 202)
            job_id = submitted.json()["id"]
            job = wait_for(client, job_id)
            self.assertEqual(job["state"], "succeeded")
            self.assertEqual(job["progress"]["completed"], 1)
            self.assertEqual(client.get(f"/api/scans/{job_id}/report").json()["files"][0]["path"], "a.py")
            csv = client.get(f"/api/scans/{job_id}/report?format=csv")
            self.assertEqual(csv.status_code, 200)
            self.assertIn("a.py", csv.text)
            self.assertIn("attachment", csv.headers["content-disposition"])
        with self.client() as client:
            self.assertEqual(client.get(f"/api/scans/{job_id}/report").status_code, 200)
            self.assertEqual(len(client.get("/api/scans").json()), 2)

    def test_request_validation_and_browser_boundaries(self):
        with self.client() as client:
            self.assertEqual(client.post("/api/scans", json={"repo_path": "x", "max_commits": 0}).status_code, 422)
            self.assertEqual(client.post("/api/scans", json={"repo_path": "x", "extra": True}).status_code, 422)
            self.assertEqual(client.get("/api/scans/unknown").status_code, 404)
            self.assertEqual(client.post("/api/scans", json={"repo_path": "x"}, headers={"Origin": "https://evil.example"}).status_code, 403)
            self.assertEqual(client.get("/api/health", headers={"Host": "evil.example"}).status_code, 400)

    def test_dashboard_and_local_assets_are_served(self):
        with self.client() as client:
            page = client.get("/")
            self.assertEqual(page.status_code, 200)
            self.assertIn("Proje klasörü", page.text)
            self.assertIn("script-src 'self'", page.headers["content-security-policy"])
            self.assertEqual(client.get("/assets/app.js").status_code, 200)
            self.assertEqual(client.get("/assets/style.css").status_code, 200)
            self.assertEqual(client.get("/assets/unknown.js").status_code, 404)

    def test_unexpected_failure_is_redacted(self):
        with self.client() as client:
            job_id = client.post("/api/scans", json={"repo_path": "crash"}).json()["id"]
            job = wait_for(client, job_id)
            self.assertEqual(job["error"]["code"], "internal_error")
            self.assertNotIn("private diagnostic", str(job))

    def test_restart_marks_interrupted_job_failed(self):
        store = JobStore(self.db, fake_analyzer)
        store.close()
        with sqlite3.connect(self.db) as db:
            db.execute("INSERT INTO jobs(id,state,created,updated,payload) VALUES ('lost','running','now','now','{}')")
        db.close()
        with self.client() as client:
            job = client.get("/api/scans/lost").json()
            self.assertEqual(job["state"], "failed")
            self.assertEqual(job["error"]["code"], "interrupted")

    def test_queue_is_bounded_and_database_has_single_owner(self):
        gate = Event()
        entered = Event()

        def blocking(**kwargs):
            entered.set()
            gate.wait(5)
            return fake_analyzer(**kwargs)

        store = JobStore(self.db, blocking, capacity=1)
        try:
            store.submit({"repo_path": "good"})
            self.assertTrue(entered.wait(3))
            with self.assertRaises(QueueFull):
                store.submit({"repo_path": "good"})
            with self.assertRaises(Timeout):
                JobStore(self.db, fake_analyzer)
        finally:
            gate.set()
            store.close()

    def test_real_repository_scan_through_http(self):
        repo = Path(self.temp.name) / "repo"
        repo.mkdir()
        env = dict(os.environ, GIT_AUTHOR_NAME="Fixture", GIT_COMMITTER_NAME="Fixture",
                   GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_EMAIL="fixture@example.invalid")
        (repo / "sample.py").write_text("value = 1\n", encoding="utf-8")
        for args in [("init", "-q"), ("add", "sample.py"), ("commit", "-q", "-m", "initial")]:
            subprocess.run(["git", "-C", str(repo), *args], check=True, env=env)
        with self.client(analyzer=None) as client:
            job_id = client.post("/api/scans", json={"repo_path": str(repo), "max_commits": 1}).json()["id"]
            self.assertEqual(wait_for(client, job_id)["state"], "succeeded")
            report = client.get(f"/api/scans/{job_id}/report").json()
            self.assertEqual(report["files"][0]["path"], "sample.py")
            self.assertIsNone(report["files"][0]["result"]["risk_score"])
        import gc
        gc.collect()
