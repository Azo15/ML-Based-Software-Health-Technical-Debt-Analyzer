"""Past-only change metrics over a bounded, observed Python-commit window."""


def add_history_metrics(newest_first_rows, lookback_commits=20):
    if lookback_commits < 1:
        raise ValueError("lookback_commits must be positive")
    history = {}
    commits = {}
    enriched = []
    for row in reversed(newest_first_rows):
        sequence = commits.setdefault(row["commit_hash"], len(commits))
        path = row["path"]
        old_path = row.get("old_path")
        if old_path and old_path != path:
            history[path] = history.pop(old_path, [])
        previous = [(index, churn) for index, churn in history.get(path, [])
                    if sequence - lookback_commits <= index < sequence]
        churn = row["added_lines"] + row["deleted_lines"]
        enriched.append({**row, "change_churn": churn,
                         "prior_change_count": len(previous),
                         "prior_churn": sum(value for _, value in previous),
                         "history_lookback_commits": lookback_commits})
        history[path] = [*previous, (sequence, churn)]
    return list(reversed(enriched))
