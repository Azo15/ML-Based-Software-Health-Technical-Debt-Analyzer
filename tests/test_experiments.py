import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from experiments.run import evaluate_repository, run_experiment, validate_manifest


def manifest():
    return {"schema_version": 1, "max_commits": 20, "observation_commits": 2,
            "repositories": [{"name": "example", "commit": "a" * 40}]}


class ExperimentTests(unittest.TestCase):
    def test_manifest_rejects_unpinned_duplicate_and_escaping_repositories(self):
        for change in ({"commit": "main"}, {"name": "../outside"}):
            data = manifest()
            data["repositories"][0].update(change)
            with self.assertRaises(ValueError):
                validate_manifest(data)
        data = manifest()
        data["repositories"].append(copy.deepcopy(data["repositories"][0]))
        with self.assertRaises(ValueError):
            validate_manifest(data)

    @patch("experiments.run.GitMiner")
    @patch("experiments.run.git", return_value="b" * 40)
    def test_wrong_head_is_rejected_before_mining(self, git, miner):
        with self.assertRaisesRegex(ValueError, "HEAD"):
            evaluate_repository(manifest()["repositories"][0], Path.cwd(), 20, 2)
        miner.assert_not_called()

    @patch("experiments.run.GitMiner")
    @patch("experiments.run.git", side_effect=["a" * 40, "", "true", "20"])
    def test_shallow_boundary_is_rejected_before_mining(self, git, miner):
        with self.assertRaisesRegex(ValueError, "Shallow"):
            evaluate_repository(manifest()["repositories"][0], Path.cwd(), 20, 2)
        miner.assert_not_called()

    @patch("experiments.run.GitMiner")
    @patch("experiments.run.git", side_effect=["a" * 40, " M a.py"])
    def test_dirty_checkout_is_rejected_before_mining(self, git, miner):
        with self.assertRaisesRegex(ValueError, "local changes"):
            evaluate_repository(manifest()["repositories"][0], Path.cwd(), 20, 2)
        miner.assert_not_called()

    @patch("experiments.run.git", side_effect=["c" * 40, ""])
    @patch("experiments.run.evaluate_repository")
    def test_failed_repository_does_not_hide_other_results(self, evaluate, git):
        data = manifest()
        data["repositories"].append({"name": "second", "commit": "b" * 40})
        evaluate.side_effect = [ValueError("pin mismatch"), {"name": "second", "evaluation": {"status": "unavailable"}}]
        result = run_experiment(data, Path.cwd())
        self.assertEqual([row["evaluation"]["status"] for row in result["repositories"]], ["error", "unavailable"])
        self.assertFalse(result["analyzer_dirty"])
