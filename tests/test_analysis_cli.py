import gc
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from typer.testing import CliRunner

from cli.main import app


class AnalysisCliTests(unittest.TestCase):
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
        self.commit_file("src/a.py", "value = 1\n", "initial")
        self.commit_file("tests/a.py", "value = 2\n", "add tests")
        self.commit_file("src/a.py", "value = 3\n", "fix bug")

    def tearDown(self):
        gc.collect()
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.repo), *args], env=self.env, text=True
        ).strip()

    def commit_file(self, path, code, message):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(code, encoding="utf-8")
        self.git("add", path)
        self.git("commit", "-q", "-m", message)

    def test_default_analyzes_current_files_and_withholds_unsupported_risk(self):
        result = CliRunner().invoke(app, [
            "analyze", str(self.repo), "--max-commits", "3", "--observation-commits", "1"
        ])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("src/a.py", result.output)
        self.assertIn("tests/a.py", result.output)
        self.assertIn("unavailable", result.output)
        self.assertNotIn("Bug Probability", result.output)
        self.assertNotIn("Health Score", result.output)

    def test_file_option_rejects_paths_outside_repository(self):
        result = CliRunner().invoke(app, ["analyze", str(self.repo), "--file", "../outside.py"])
        self.assertEqual(result.exit_code, 1)


if __name__ == "__main__":
    unittest.main()
