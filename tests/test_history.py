import unittest

from data_collector.history import add_history_metrics


def row(commit, path="a.py", churn=1, old_path=None):
    return {"commit_hash": str(commit), "path": path, "old_path": old_path,
            "added_lines": churn, "deleted_lines": 0}


class HistoryTests(unittest.TestCase):
    def test_future_and_current_change_do_not_enter_prior_metrics(self):
        result = add_history_metrics([row(3, churn=100), row(2, churn=5), row(1, churn=2)])
        self.assertEqual([entry["prior_churn"] for entry in result], [7, 2, 0])
        changed_future = add_history_metrics([row(3, churn=900), row(2, churn=5), row(1, churn=2)])
        self.assertEqual(result[1:], changed_future[1:])

    def test_rename_retains_past_history(self):
        result = add_history_metrics([row(2, "new.py", old_path="a.py"), row(1, churn=4)])
        self.assertEqual(result[0]["prior_churn"], 4)

    def test_window_counts_commits_instead_of_files(self):
        result = add_history_metrics([
            row(3), row(2, "b.py"), row(2, "c.py"), row(1, churn=8)
        ], lookback_commits=1)
        self.assertEqual(result[0]["prior_churn"], 0)

    def test_invalid_window_is_rejected(self):
        with self.assertRaises(ValueError):
            add_history_metrics([], lookback_commits=0)
