"""Stable, machine-readable exports of a completed repository scan."""

import csv
from io import StringIO
import json
from pathlib import Path
from typing import Any


def _safe_csv_text(value: str) -> str:
    """Keep spreadsheet programs from interpreting repository names as formulas."""
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value


def write_report(path: Path, report: dict[str, Any]) -> None:
    """Export JSON or CSV without silently replacing an existing report."""
    suffix = path.suffix.lower()
    if suffix == ".json":
        contents = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    elif suffix == ".csv":
        buffer = StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=[
            "path", "risk_score", "risk_score_kind", "loc",
            "cyclomatic_complexity_max", "finding_count", "finding_rules",
        ])
        writer.writeheader()
        for item in report["files"]:
            metrics = item["metrics"]
            result = item["result"]
            writer.writerow({
                "path": _safe_csv_text(item["path"]),
                "risk_score": "" if result["risk_score"] is None else result["risk_score"],
                "risk_score_kind": result["risk_score_kind"],
                "loc": metrics["loc"],
                "cyclomatic_complexity_max": metrics["cyclomatic_complexity_max"],
                "finding_count": len(result["maintainability_findings"]),
                "finding_rules": ";".join(
                    finding["rule"] for finding in result["maintainability_findings"]
                ),
            })
        contents = buffer.getvalue()
    else:
        raise ValueError("Report filename must end in .json or .csv")

    with path.open("x", encoding="utf-8", newline="") as output:
        output.write(contents)
