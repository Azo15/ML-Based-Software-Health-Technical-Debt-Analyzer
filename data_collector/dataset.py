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
        path = row["path"]
        tracked_path = path
        evidence = []
        for commit_hash in future_hashes:
            for future_row in rows_by_commit[commit_hash]:
                if tracked_path not in (future_row["path"], future_row.get("old_path")):
                    continue
                tracked_path = future_row["path"]
                if future_row.get("is_bug_fix_candidate", future_row.get("is_bug_fix", 0)):
                    evidence.append({"commit_hash": commit_hash, "path": tracked_path,
                                     "subject": future_row.get("commit_subject", "")})
        labeled.append({
            "commit_hash": row["commit_hash"],
            "commit_date": row["commit_date"],
            "commit_sequence": index,
            "label_observed_at_sequence": index + observation_commits,
            "path": path,
            "source_code": row["source_code"],
            "future_bug_fix": int(bool(evidence)),
            "label_evidence": evidence,
            "observation_window_commits": future_hashes,
            **{key: row[key] for key in (
                "change_churn", "prior_change_count", "prior_churn", "history_lookback_commits"
            ) if key in row},
            "label_source": "commit_message_candidate",
            "observation_commits": observation_commits,
        })

    return labeled
