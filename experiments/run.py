"""Run independent temporal evaluations on commit-pinned local repositories."""

import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import re
import subprocess

from data_collector.dataset import build_future_fix_dataset
from data_collector.git_miner import GitMiner
from feature_extractor.metrics_analyzer import MetricsAnalyzer
from model.debt_estimator import DebtEstimator


def git(repo, *args):
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True, encoding="utf-8", timeout=30
    ).strip()


def validate_manifest(manifest):
    if manifest.get("schema_version") != 1 or not manifest.get("repositories"):
        raise ValueError("Expected schema_version 1 and a nonempty repositories list")
    for option in ("max_commits", "observation_commits"):
        if type(manifest.get(option)) is not int or manifest[option] < 1:
            raise ValueError(f"{option} must be a positive integer")
    names = set()
    for spec in manifest["repositories"]:
        name = spec.get("name", "")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", name) or name in names:
            raise ValueError("Repository names must be unique simple directory names")
        names.add(name)
        if not re.fullmatch(r"[0-9a-f]{40}", spec.get("commit", "")):
            raise ValueError("Every repository must be pinned to a full commit hash")


def evaluate_repository(spec, repos_dir, max_commits, observation_commits):
    root = repos_dir.resolve()
    repo = (root / spec["name"]).resolve()
    if not repo.is_relative_to(root):
        raise ValueError("Repository path escapes the repositories directory")
    if git(repo, "rev-parse", "HEAD") != spec["commit"]:
        raise ValueError("Checkout HEAD differs from the manifest pin")
    if git(repo, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Repository has tracked local changes")
    shallow = git(repo, "rev-parse", "--is-shallow-repository") == "true"
    available = int(git(repo, "rev-list", "--count", "HEAD"))
    if shallow and available <= max_commits:
        raise ValueError("Shallow history must extend beyond the mining window; fetch more commits")

    raw = GitMiner(str(repo)).mine_commits(max_commits)
    candidates = build_future_fix_dataset(raw, observation_commits)
    analyzer = MetricsAnalyzer()
    rows = []
    for row in candidates:
        metrics = analyzer.analyze_code(row["source_code"])
        if metrics["valid"] and metrics["loc"] > 0:
            rows.append({**row, **metrics})
    estimator = DebtEstimator()
    message = estimator.train(rows)
    # Hash the actual features and labels, excluding copied source text.
    provenance = [
        {key: row[key] for key in [
            "commit_hash", "path", "future_bug_fix", "commit_sequence",
            "label_observed_at_sequence", "change_churn", "prior_change_count",
            "prior_churn", "history_lookback_commits", *estimator.features_col,
        ]} for row in rows
    ]
    fingerprint = hashlib.sha256(json.dumps(
        provenance, sort_keys=True, allow_nan=False
    ).encode("utf-8")).hexdigest()
    return {
        **spec, "shallow": shallow, "available_commits": available,
        "mined_revisions": len(raw), "candidate_revisions": len(candidates),
        "excluded_invalid_or_empty": len(candidates) - len(rows),
        "dataset_sha256": fingerprint, "evaluation": estimator.evaluation,
        "label_audit": [{
            "commit_hash": row["commit_hash"], "path": row["path"],
            "candidate_label": row["future_bug_fix"], "evidence": row["label_evidence"],
            "observation_window_commits": row["observation_window_commits"],
            "review_status": "unreviewed",
        } for row in rows],
        "explanation": message,
    }


def run_experiment(manifest, repos_dir):
    validate_manifest(manifest)
    results = []
    for spec in manifest["repositories"]:
        try:
            results.append(evaluate_repository(
                spec, Path(repos_dir), manifest["max_commits"], manifest["observation_commits"]
            ))
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            results.append({**spec, "evaluation": {"status": "error"}, "explanation": str(exc)})
    source = Path(__file__).resolve().parents[1]
    return {
        "schema_version": 1,
        "protocol": "independent_within_repository_temporal_holdouts",
        "manifest": manifest,
        "analyzer_commit": git(source, "rev-parse", "HEAD"),
        "analyzer_dirty": bool(git(source, "status", "--porcelain")),
        "python": platform.python_version(),
        "dependencies": {name: version(name) for name in (
            "scikit-learn", "numpy", "pandas", "PyDriller", "radon", "lizard"
        )},
        "repositories": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--repos-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; choose a new filename")
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        report = run_experiment(manifest, args.repos_dir)
        with args.output.open("x", encoding="utf-8") as target:
            json.dump(report, target, ensure_ascii=False, indent=2, allow_nan=False)
            target.write("\n")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))
    for result in report["repositories"]:
        print(f"{result['name']}: {result['evaluation']['status']}")
    return int(any(row["evaluation"]["status"] == "error" for row in report["repositories"]))


if __name__ == "__main__":
    raise SystemExit(main())
