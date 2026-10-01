import gc
import csv
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from typer.testing import CliRunner

from cli.main import app
from analysis.service import AnalysisError, analyze_repository


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

    def test_json_export_preserves_findings_and_does_not_overwrite(self):
        output = self.repo / "analysis.json"
        args = ["analyze", str(self.repo), "--max-commits", "3",
                "--observation-commits", "1", "--output", str(output)]
        result = CliRunner().invoke(app, args)
        self.assertEqual(result.exit_code, 0, result.output)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual({item["path"] for item in report["files"]}, {"src/a.py", "tests/a.py"})
        self.assertTrue(all(item["result"]["risk_score"] is None for item in report["files"]))
        self.assertEqual(CliRunner().invoke(app, args).exit_code, 1)

    def test_csv_export_has_one_row_per_current_file(self):
        output = self.repo / "analysis.csv"
        result = CliRunner().invoke(app, [
            "analyze", str(self.repo), "--max-commits", "3",
            "--observation-commits", "1", "--output", str(output),
        ])
        self.assertEqual(result.exit_code, 0, result.output)
        with output.open(encoding="utf-8", newline="") as report_file:
            rows = list(csv.DictReader(report_file))
        self.assertEqual({row["path"] for row in rows}, {"src/a.py", "tests/a.py"})
        self.assertTrue(all(row["risk_score"] == "" for row in rows))

    def test_service_reports_invalid_empty_and_missing_files(self):
        self.commit_file("empty.py", "", "add empty module")
        (self.repo / "src/a.py").write_text("def broken(:\n", encoding="utf-8")
        (self.repo / "tests/a.py").unlink()
        self.commit_file("good.py", "raise RuntimeError('must never execute')\n", "add example")
        events = []
        report = analyze_repository(self.repo, max_commits=3, observation_commits=1, progress=events.append)
        self.assertEqual(report["status"], "partial")
        self.assertEqual({item["path"] for item in report["files"]}, {"good.py"})
        self.assertEqual({item["reason"] for item in report["skipped_files"]},
                         {"invalid_python", "empty_file", "missing_file"})
        self.assertEqual(report["summary"]["analyzed_files"], 1)
        self.assertTrue(report["repository_state"]["tracked_changes"])
        self.assertEqual(events[-1]["stage"], "completed")
        json.dumps(report, allow_nan=False)

    def test_filters_only_change_current_file_selection(self):
        normal = analyze_repository(self.repo, max_commits=3, observation_commits=1)
        filtered = analyze_repository(self.repo, max_commits=3, observation_commits=1, excludes=["tests/*"])
        self.assertEqual([row["path"] for row in filtered["files"]], ["src/a.py"])
        self.assertEqual(filtered["status"], "complete")
        self.assertEqual(filtered["summary"]["training_revisions"], normal["summary"]["training_revisions"])
        self.assertEqual(filtered["skipped_files"][0]["reason"], "excluded_by_filter")

    def test_empty_result_is_exported_with_nonzero_exit(self):
        output = self.repo / "empty.json"
        result = CliRunner().invoke(app, ["analyze", str(self.repo), "--exclude", "*", "--output", str(output)])
        self.assertEqual(result.exit_code, 1, result.output)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "empty")
        self.assertEqual(report["files"], [])
        self.assertEqual(len(report["skipped_files"]), 2)

    def test_service_rejects_nested_folder_and_invalid_options(self):
        with self.assertRaises(AnalysisError) as nested:
            analyze_repository(self.repo / "src")
        self.assertEqual(nested.exception.code, "repository_root_required")
        with self.assertRaises(AnalysisError) as options:
            analyze_repository(self.repo, max_commits=0)
        self.assertEqual(options.exception.code, "invalid_options")

    def test_non_git_directory_has_a_structured_error(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(AnalysisError) as error:
                analyze_repository(folder)
        self.assertEqual(error.exception.code, "git_error")


if __name__ == "__main__":
    unittest.main()
