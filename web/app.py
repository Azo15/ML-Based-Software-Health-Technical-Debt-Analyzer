"""Loopback-only API for local single-user analysis jobs."""

from contextlib import asynccontextmanager
import os
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from starlette.middleware.trustedhost import TrustedHostMiddleware

from analysis.report_export import render_report
from web.jobs import JobStore, QueueFull


class ScanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    repo_path: str = Field(min_length=1, max_length=4096)
    max_commits: int = Field(default=100, ge=1, le=1000, strict=True)
    observation_commits: int = Field(default=10, ge=1, le=200, strict=True)
    file_path: str | None = Field(default=None, max_length=4096)
    excludes: list[Annotated[str, StringConstraints(max_length=512)]] = Field(default_factory=list, max_length=64)


def create_app(database=None, analyzer=None):
    if database is None:
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
        database = base / "SoftwareHealthAnalyzer" / "jobs.sqlite3"

    @asynccontextmanager
    async def lifespan(app):
        options = {} if analyzer is None else {"analyzer": analyzer}
        app.state.jobs = JobStore(database, **options)
        try:
            yield
        finally:
            app.state.jobs.close()

    app = FastAPI(title="Software Health Analyzer", version="0.4.1", lifespan=lifespan)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
    static = Path(__file__).parent / "static"
    app.mount("/assets", StaticFiles(directory=static), name="assets")

    @app.get("/", include_in_schema=False)
    def dashboard():
        return FileResponse(static / "index.html", headers={
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        })

    @app.middleware("http")
    async def local_browser_only(request: Request, call_next):
        origin = request.headers.get("origin")
        if origin and origin != f"{request.url.scheme}://{request.headers.get('host')}":
            return JSONResponse({"detail": "Cross-origin access is not allowed"}, status_code=403)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.get("/api/health")
    def health():
        return {"status": "ok", "version": "0.4.1"}

    @app.post("/api/scans", status_code=202)
    def submit_scan(payload: ScanRequest):
        try:
            job_id = app.state.jobs.submit(payload.model_dump())
        except QueueFull as exc:
            raise HTTPException(429, str(exc)) from exc
        return {"id": job_id, "status_url": f"/api/scans/{job_id}"}

    @app.get("/api/scans")
    def list_scans(limit: int = Query(default=50, ge=1, le=100)):
        return app.state.jobs.list(limit)

    @app.get("/api/scans/{job_id}")
    def scan_status(job_id: str):
        job = app.state.jobs.get(job_id)
        if job is None:
            raise HTTPException(404, "Scan not found")
        return job

    @app.get("/api/scans/{job_id}/report")
    def report(job_id: str, format: str = Query(default="json", pattern="^(json|csv)$")):
        job = app.state.jobs.get(job_id, include_result=True)
        if job is None:
            raise HTTPException(404, "Scan not found")
        if job["state"] != "succeeded":
            raise HTTPException(409, "Scan has no completed report")
        content = render_report(job["result"], format)
        return Response(content, media_type="application/json" if format == "json" else "text/csv",
                        headers={"Content-Disposition": f'attachment; filename="scan-{job["id"]}.{format}"'})

    return app
