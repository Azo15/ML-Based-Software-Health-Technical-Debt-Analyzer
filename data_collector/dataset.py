"""Build time-aware candidate labels from repository history.

Commit-message matches are weak labels, not confirmed defects. Each example is
the source available at its own commit; its label describes later commits.
"""

from typing import Any, Dict, List


def build_future_fix_dataset(
    mined_rows: List[Dict[str, Any]], observation_commits: int = 10
) -> List[Dict[str, Any]]:
    """Label snapshots using only later fix-candidate commits.

    ``mined_rows`` must be ordered newest-commit first, as emitted by GitMiner.
    The window counts observed commits that modified Python files. Rows in its
    newest portion are censored because their outcomes are not yet observable.
    """
    if observation_commits < 1:
        raise ValueError("observation_commits must be at least 1")

    chronological = list(reversed(mined_rows))
    commit_order = list(dict.fromkeys(row["commit_hash"] for row in chronological))
    commit_index = {commit_hash: i for i, commit_hash in enumerate(commit_order)}
    rows_by_commit: Dict[str, List[Dict[str, Any]]] = {}
    for row in chronological:
        rows_by_commit.setdefault(row["commit_hash"], []).append(row)

    labeled = []
    for row in chronological:
        index = commit_index[row["commit_hash"]]
        if index + observation_commits >= len(commit_order):
            continue

        future_hashes = commit_order[index + 1:index + observation_commits + 1]
        future_fixes = [
            future_row
            for commit_hash in future_hashes
            for future_row in rows_by_commit[commit_hash]
            if future_row.get("is_bug_fix_candidate", future_row.get("is_bug_fix", 0))
        ]
        path = row["path"]
        has_future_fix = any(
            path == future_row["path"] or path == future_row.get("old_path")
            for future_row in future_fixes
        )
        labeled.append({
            "commit_hash": row["commit_hash"],
            "commit_date": row["commit_date"],
            "path": path,
            "source_code": row["source_code"],
            "future_bug_fix": int(has_future_fix),
            "label_source": "commit_message_candidate",
            "observation_commits": observation_commits,
        })

    return labeled
