"""Public demo serving the original dashboard and one precomputed report."""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from analysis.report_export import render_report

ROOT = Path(__file__).parent
STATIC = ROOT / "static"
REPORT = json.loads((ROOT / "demo-report.json").read_text(encoding="utf-8"))
JOB = {
    "id": "demo",
    "state": "succeeded",
    "created": "2026-11-25T00:00:00Z",
    "payload": {"repo_path": "Software Health Analyzer"},
}
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/assets", StaticFiles(directory=STATIC), name="assets")


@app.get("/", response_class=HTMLResponse)
def dashboard():
    banner = """<aside class="demo-notice">
      <strong>Salt okunur demo</strong> · Gerçek analiz raporunu inceleyebilirsiniz.
      Yeni taramalar kapalıdır.
      <a href="https://github.com/Azo15/ML-Based-Software-Health-Technical-Debt-Analyzer#readme">
        Kaynak kodunu ve kurulum adımlarını açın</a>.
    </aside>"""
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    html = html.replace("<body>", '<body class="public-demo">' + banner, 1)
    return HTMLResponse(html, headers={
        "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'",
    })


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "demo"}


@app.get("/api/scans")
def scans():
    return [JOB]


@app.get("/api/scans/demo")
def scan():
    return JOB


@app.get("/api/scans/demo/report")
def report(format: str = Query(default="json", pattern="^(json|csv)$")):
    return Response(render_report(REPORT, format), media_type=(
        "application/json" if format == "json" else "text/csv"
    ))


@app.post("/api/scans")
def reject_scan():
    raise HTTPException(403, "Yeni taramalar demo sürümünde kapalıdır.")
