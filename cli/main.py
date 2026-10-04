"""Terminal presentation of the shared repository analysis service."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from analysis.service import AnalysisError, analyze_repository
from cli.report_export import write_report


app = typer.Typer(help="Analyze Python repositories for risk and maintainability")
console = Console()


@app.callback()
def main():
    """Analyze a Git repository without executing its source code."""


@app.command()
def analyze(
    repo_path: str = typer.Argument(..., help="Path to a local Git repository"),
    max_commits: int = typer.Option(100, "--max-commits", "-m", min=1),
    observation_commits: int = typer.Option(10, "--observation-commits", min=1),
    file_path: Optional[str] = typer.Option(None, "--file", "-f"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="New .json or .csv report path"),
    exclude: list[str] = typer.Option([], "--exclude", help="Repeatable current-file path glob, e.g. tests/*"),
):
    """Rank current files and report separate maintainability findings."""
    console.print(Panel.fit("Software risk and maintainability analysis"))
    try:
        report = analyze_repository(repo_path, max_commits=max_commits,
                                    observation_commits=observation_commits,
                                    file_path=file_path, excludes=exclude)
    except AnalysisError as exc:
        console.print(f"Analysis failed ({exc.code}): {exc}", markup=False)
        raise typer.Exit(code=1) from exc
    console.print(report["model_evaluation"], markup=False)
    table = Table(title=Text(f"Current files in {Path(report['repository']).name}"))
    for title in ("File", "Risk score", "LOC", "Max CC", "Findings"):
        table.add_column(title, overflow="fold")
    for item in report["files"]:
        metrics, result = item["metrics"], item["result"]
        score = result["risk_score"]
        table.add_row(Text(item["path"]), f"{score:.3f}" if score is not None else "unavailable",
                      f"{metrics['loc']:.0f}", f"{metrics['cyclomatic_complexity_max']:.0f}",
                      str(len(result["maintainability_findings"])))
    console.print(table)
    console.print("Risk rank score is relative and is not a calibrated defect probability.")
    for item in report["skipped_files"]:
        console.print(f"Skipped {item['path']}: {item['reason']}", markup=False)
    console.print(f"Scan status: {report['status']}")
    if output is not None:
        try:
            write_report(output, report)
        except (OSError, ValueError, TypeError) as exc:
            console.print(f"Could not write report: {exc}", markup=False)
            raise typer.Exit(code=1) from exc
        console.print(f"Report saved: {output}", markup=False)
    if file_path and report["files"]:
        for issue in report["files"][0]["result"]["maintainability_findings"]:
            console.print(f"{issue['rule']}: {issue['reason']} — {issue['suggestion']}", markup=False)
    if report["status"] == "empty":
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
