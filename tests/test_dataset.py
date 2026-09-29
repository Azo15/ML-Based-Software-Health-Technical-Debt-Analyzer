import unittest

from data_collector.dataset import build_future_fix_dataset


def revision(commit, path, source, fix=False, old_path=None):
    return {
        "commit_hash": commit,
        "commit_date": f"2026-09-{int(commit):02d}T12:00:00+00:00",
        "path": path,
        "old_path": old_path,
        "source_code": source,
        "is_bug_fix_candidate": int(fix),
    }


class FutureFixDatasetTests(unittest.TestCase):
    def test_pre_fix_snapshot_gets_label_and_fix_snapshot_does_not(self):
        rows = [
            revision("3", "src/a.py", "corrected later", fix=False),
            revision("2", "src/a.py", "corrected", fix=True),
            revision("1", "src/a.py", "broken", fix=False),
        ]
        labeled = build_future_fix_dataset(rows, observation_commits=1)
        by_commit = {row["commit_hash"]: row for row in labeled}

        self.assertEqual(set(by_commit), {"1", "2"})
        self.assertEqual(by_commit["1"]["future_bug_fix"], 1)
        self.assertEqual(by_commit["1"]["source_code"], "broken")
        self.assertEqual(by_commit["2"]["future_bug_fix"], 0)
        self.assertEqual(by_commit["2"]["source_code"], "corrected")

    def test_unobserved_recent_snapshots_are_excluded(self):
        rows = [revision("2", "a.py", "new"), revision("1", "a.py", "old")]
        result = build_future_fix_dataset(rows, observation_commits=2)
        self.assertEqual(result, [])

    def test_rename_can_connect_a_future_fix_to_old_path(self):
        rows = [
            revision("2", "new.py", "fixed", fix=True, old_path="old.py"),
            revision("1", "old.py", "broken"),
        ]
        result = build_future_fix_dataset(rows, observation_commits=1)
        self.assertEqual(result[0]["future_bug_fix"], 1)

    def test_multiple_files_in_one_commit_do_not_expand_window(self):
        rows = [
            revision("2", "a.py", "fixed", fix=True),
            revision("2", "b.py", "other", fix=True),
            revision("1", "a.py", "broken"),
            revision("1", "b.py", "okay"),
        ]
        result = build_future_fix_dataset(rows, observation_commits=1)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(row["future_bug_fix"] == 1 for row in result))

    def test_invalid_window_is_rejected(self):
        with self.assertRaises(ValueError):
            build_future_fix_dataset([], observation_commits=0)


if __name__ == "__main__":
    unittest.main()
