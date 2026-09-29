import gc
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from data_collector.git_miner import GitMiner


class GitMinerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self.env = dict(os.environ)
        self.env.update({
            "GIT_AUTHOR_NAME": "Fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "Fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        })
        self.git("init", "-q")

    def tearDown(self):
        gc.collect()
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.repo), *args], env=self.env, text=True
        ).strip()

    def commit_file(self, path, code, message):
        full_path = self.repo / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(code, encoding="utf-8")
        self.git("add", path)
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def test_limit_uses_newest_commit_and_preserves_prior_source(self):
        self.commit_file("src/a.py", "value = 1\n", "initial")
        self.commit_file("tests/a.py", "value = 2\n", "add tests")
        latest = self.commit_file("src/a.py", "value = 3\n", "fix bug")

        rows = GitMiner(str(self.repo)).mine_commits(max_commits=1)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["commit_hash"], latest)
        self.assertEqual(rows[0]["path"], "src/a.py")
        self.assertEqual(rows[0]["source_code_before"], "value = 1\n")
        self.assertEqual(rows[0]["source_code"], "value = 3\n")
        self.assertEqual(rows[0]["is_bug_fix_candidate"], 1)
        self.assertTrue(rows[0]["commit_date"])

    def test_same_filename_in_different_directories_keeps_identity(self):
        self.commit_file("src/a.py", "value = 1\n", "initial")
        self.commit_file("tests/a.py", "value = 2\n", "add tests")

        rows = GitMiner(str(self.repo)).mine_commits(max_commits=2)

        self.assertEqual({row["path"] for row in rows}, {"src/a.py", "tests/a.py"})

    def test_nonpositive_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            GitMiner(str(self.repo)).mine_commits(max_commits=0)


if __name__ == "__main__":
    unittest.main()
