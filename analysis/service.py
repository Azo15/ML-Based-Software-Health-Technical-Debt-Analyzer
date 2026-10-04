"""Analyze repositories without depending on a terminal or web framework."""

from fnmatch import fnmatchcase
from pathlib import Path
import subprocess
import tokenize

from git.exc import GitCommandError
from data_collector.dataset import build_future_fix_dataset
from data_collector.git_miner import GitMiner
from feature_extractor.metrics_analyzer import MetricsAnalyzer
from model.debt_estimator import DebtEstimator


class AnalysisError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _git(root, *args):
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), *args], stderr=subprocess.PIPE, timeout=30
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise AnalysisError("git_error", "Git could not read the repository; check the folder and Git installation.") from exc


def _select_files(root, selected, excludes):
    skipped = []
    if selected:
        candidate = (root / selected).resolve()
        if not candidate.is_relative_to(root):
            raise AnalysisError("outside_repository", "Selected file must be inside the repository")
        if not candidate.is_file() or candidate.suffix != ".py":
            raise AnalysisError("invalid_file", "Selected Python file does not exist")
        names = [candidate.relative_to(root).as_posix()]
    else:
        names = [part.decode("utf-8", errors="surrogateescape").replace("\\", "/")
                 for part in _git(root, "ls-files", "-z").split(b"\0") if part]
    paths = []
    for name in sorted(names):
        if not name.endswith(".py"):
            continue
        reason = None
        path = (root / name).resolve()
        if any(part in {"venv", ".venv", "__pycache__"} for part in Path(name).parts):
            reason = "environment_directory"
        elif any(fnmatchcase(name, pattern) for pattern in excludes):
            reason = "excluded_by_filter"
        elif not path.is_relative_to(root):
            reason = "outside_repository"
        elif not path.is_file():
            reason = "missing_file"
        if reason:
            skipped.append({"path": name, "reason": reason})
        else:
            paths.append((name, path))
    return paths, skipped


def analyze_repository(repo_path, *, max_commits=100, observation_commits=10,
                       file_path=None, excludes=(), progress=None):
    """Return a JSON-safe report; progress receives stage, completed and total.

    Exclusions apply to current files, not the historical training population.
    No repository code is imported or executed.
    """
    def emit(stage, completed=0, total=0):
        if progress is not None:
            progress({"stage": stage, "completed": completed, "total": total})

    if type(max_commits) is not int or max_commits < 1 or type(observation_commits) is not int or observation_commits < 1:
        raise AnalysisError("invalid_options", "Commit limits must be positive integers")
    root = Path(repo_path).resolve()
    if not root.is_dir():
        raise AnalysisError("missing_repository", "Repository directory does not exist")
    emit("validating")
    top = Path(_git(root, "rev-parse", "--show-toplevel").decode("utf-8").strip()).resolve()
    if top != root:
        raise AnalysisError("repository_root_required", "Select the Git repository root folder")
    try:
        head = _git(root, "rev-parse", "--verify", "--quiet", "HEAD").decode().strip()
    except AnalysisError as exc:
        if isinstance(exc.__cause__, subprocess.CalledProcessError) and exc.__cause__.returncode == 1:
            raise AnalysisError("empty_history", "This Git repository has no commits yet. Create an initial commit before analyzing.") from exc
        raise
    dirty = bool(_git(root, "status", "--porcelain", "--untracked-files=no").strip())
    current, skipped = _select_files(root, file_path, excludes)
    analyzer = MetricsAnalyzer()
    estimator = DebtEstimator()
    warnings = []
    training_rows = []
    candidates = []
    model_message = "Model unavailable: no current Python files selected."
    if current:
        emit("mining")
        try:
            history = GitMiner(str(root)).mine_commits(max_commits=max_commits)
            candidates = build_future_fix_dataset(history, observation_commits)
        except (OSError, ValueError, GitCommandError) as exc:
            raise AnalysisError("history_failed", "Could not read repository history") from exc
        for index, row in enumerate(candidates):
            metrics = analyzer.analyze_code(row["source_code"])
            if metrics["valid"] and metrics["loc"] > 0:
                training_rows.append({**row, **metrics})
            emit("historical_metrics", index + 1, len(candidates))
        emit("training")
        try:
            model_message = estimator.train(training_rows)
        except ValueError as exc:
            raise AnalysisError("model_failed", "Historical features could not be evaluated") from exc
    if not estimator.is_trained:
        warnings.append({"code": "risk_unavailable", "message": model_message})
    findings = []
    for index, (name, path) in enumerate(current):
        try:
            with tokenize.open(path) as source_file:
                source = source_file.read()
        except (OSError, UnicodeError, SyntaxError) as exc:
            skipped.append({"path": name, "reason": "unreadable_file", "detail": str(exc)})
        else:
            if not source.strip():
                skipped.append({"path": name, "reason": "empty_file"})
            else:
                metrics = analyzer.analyze_code(source)
                if not metrics["valid"]:
                    skipped.append({"path": name, "reason": "invalid_python", "detail": metrics["parse_error"]})
                else:
                    findings.append({"path": name, "metrics": metrics,
                                     "result": estimator.estimate_debt(metrics)})
        emit("current_files", index + 1, len(current))
    findings.sort(key=lambda row: (
        row["result"]["risk_score"] is None, -(row["result"]["risk_score"] or 0),
        -len(row["result"]["maintainability_findings"]), row["path"],
    ))
    problems = {"unreadable_file", "invalid_python", "missing_file", "outside_repository"}
    status = "empty" if not findings else (
        "partial" if any(item["reason"] in problems for item in skipped) else "complete"
    )
    end_head = _git(root, "rev-parse", "HEAD").decode().strip()
    if end_head != head:
        warnings.append({"code": "repository_changed", "message": "HEAD changed during the scan; rerun for a consistent result."})
        if findings:
            status = "partial"
    report = {
        "schema_version": 1, "status": status, "repository": str(root),
        "repository_state": {"head": head, "head_at_completion": end_head, "tracked_changes": dirty},
        "scan": {"max_commits": max_commits, "observation_commits": observation_commits,
                 "file": file_path, "excludes": list(excludes)},
        "model_evaluation": model_message, "evaluation_details": estimator.evaluation,
        "files": findings, "skipped_files": skipped, "warnings": warnings,
        "summary": {"analyzed_files": len(findings), "skipped_files": len(skipped),
                    "training_revisions": len(training_rows),
                    "excluded_training_revisions": len(candidates) - len(training_rows)},
    }
    emit("completed", len(current), len(current))
    return report
