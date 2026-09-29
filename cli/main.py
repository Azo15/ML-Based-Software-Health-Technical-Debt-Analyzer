"""Command line interface for local Python repository analysis."""

from pathlib import Path
import subprocess
import tokenize
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from data_collector.dataset import build_future_fix_dataset
from data_collector.git_miner import GitMiner
from feature_extractor.metrics_analyzer import MetricsAnalyzer
from model.debt_estimator import DebtEstimator
from cli.report_export import write_report
from utils.logger import logger


app = typer.Typer(help="Analyze Python repositories for risk and maintainability")
console = Console()


@app.callback()
def main():
    """Analyze a Git repository without executing its source code."""


def _current_python_files(repo_root: Path, selected: Optional[str]) -> list[Path]:
    if selected:
        path = (repo_root / selected).resolve()
        try:
            path.relative_to(repo_root)
        except ValueError as exc:
            raise ValueError("Selected file must be inside the repository") from exc
        if not path.is_file() or path.suffix != ".py":
            raise ValueError("Selected Python file does not exist")
        return [path]

    result = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "-z"],
        check=True, capture_output=True,
    )
    paths = []
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        relative = raw_path.decode("utf-8", errors="surrogateescape").replace("\\", "/")
        parts = Path(relative).parts
        if not relative.endswith(".py") or any(part in {"venv", ".venv", "__pycache__"} for part in parts):
            continue
        path = (repo_root / relative).resolve()
        try:
            path.relative_to(repo_root)
        except ValueError:
            logger.warning("Skipping a tracked file outside the repository: %s", relative)
            continue
        if path.is_file():
            paths.append(path)
    return sorted(paths)


@app.command()
def analyze(
    repo_path: str = typer.Argument(..., help="Path to a local Git repository"),
    max_commits: int = typer.Option(100, "--max-commits", "-m", min=1),
    observation_commits: int = typer.Option(10, "--observation-commits", min=1),
    file_path: Optional[str] = typer.Option(None, "--file", "-f", help="One Python file relative to the repository"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="New .json or .csv report path"),
):
    """Rank current Python files and report separate maintainability findings."""
    repo_root = Path(repo_path).resolve()
    if not repo_root.is_dir():
        logger.error("Repository directory does not exist: %s", repo_root)
        raise typer.Exit(code=1)

    try:
        current_files = _current_python_files(repo_root, file_path)
    except (ValueError, subprocess.CalledProcessError) as exc:
        logger.error("Cannot list current Python files: %s", exc)
        raise typer.Exit(code=1) from exc
    if not current_files:
        logger.error("No current Python files were selected")
        raise typer.Exit(code=1)

    console.print(Panel.fit("Software risk and maintainability analysis"))
    analyzer = MetricsAnalyzer()
    estimator = DebtEstimator()
    try:
        raw_history = GitMiner(str(repo_root)).mine_commits(max_commits=max_commits)
        candidate_rows = build_future_fix_dataset(raw_history, observation_commits)
        training_rows = []
        for row in candidate_rows:
            metrics = analyzer.analyze_code(row["source_code"])
            if metrics["valid"] and metrics["loc"] > 0:
                training_rows.append({**row, **metrics})
        report = estimator.train(training_rows)
    except (ValueError, OSError) as exc:
        logger.error("Historical analysis failed: %s", exc)
        raise typer.Exit(code=1) from exc

    console.print(f"\n[bold]Model evaluation[/bold]\n{report}")
    findings = []
    for path in current_files:
        try:
            with tokenize.open(path) as source_file:
                source = source_file.read()
        except (OSError, UnicodeError, SyntaxError) as exc:
            logger.warning("Skipping unreadable Python file %s: %s", path, exc)
            continue
        if not source.strip():
            continue
        metrics = analyzer.analyze_code(source)
        if not metrics["valid"]:
            logger.warning("Skipping invalid Python file %s: %s", path, metrics["parse_error"])
            continue
        findings.append({
            "path": path.relative_to(repo_root).as_posix(),
            "metrics": metrics,
            "result": estimator.estimate_debt(metrics),
        })
    if not findings:
        logger.error("No valid current Python files could be analyzed")
        raise typer.Exit(code=1)

    findings.sort(key=lambda row: (
        row["result"]["risk_score"] is None,
        -(row["result"]["risk_score"] or 0),
        -len(row["result"]["maintainability_findings"]),
        row["path"],
    ))
    table = Table(title=f"Current files in {repo_root.name}")
    table.add_column("File", overflow="fold", ratio=3)
    table.add_column("Risk score", justify="right")
    table.add_column("LOC", justify="right")
    table.add_column("Max CC", justify="right")
    table.add_column("Findings", justify="right")
    for item in findings:
        metrics = item["metrics"]
        result = item["result"]
        score = result["risk_score"]
        table.add_row(
            item["path"],
            f"{score:.3f}" if score is not None else "unavailable",
            f"{metrics['loc']:.0f}",
            f"{metrics['cyclomatic_complexity_max']:.0f}",
            str(len(result["maintainability_findings"])),
        )
    console.print(table)
    console.print("Risk rank score is relative and is not a calibrated defect probability.")

    if output is not None:
        export = {
            "schema_version": 1,
            "repository": str(repo_root),
            "scan": {"max_commits": max_commits, "observation_commits": observation_commits},
            "model_evaluation": report,
            "files": findings,
        }
        try:
            write_report(output, export)
        except (OSError, ValueError, TypeError) as exc:
            logger.error("Could not write report: %s", exc)
            raise typer.Exit(code=1) from exc
        console.print(f"Report saved: {output}")

    if file_path:
        item = findings[0]
        for issue in item["result"]["maintainability_findings"]:
            console.print(f"[bold]{issue['rule']}[/bold]: {issue['reason']} — {issue['suggestion']}")


if __name__ == "__main__":
    app()
