import unittest

from model.debt_estimator import DebtEstimator


def metrics(value=2):
    return {
        "cyclomatic_complexity": float(value),
        "cyclomatic_complexity_max": float(value),
        "halstead_volume": float(value * 2),
        "halstead_difficulty": float(value),
        "halstead_effort": float(value * 4),
        "loc": float(value * 5),
        "num_functions": 1.0,
    }


class DebtEstimatorTests(unittest.TestCase):
    def test_untrained_model_does_not_invent_risk_or_health_percentage(self):
        result = DebtEstimator().estimate_debt(metrics())
        self.assertIsNone(result["risk_score"])
        self.assertNotIn("bug_probability", result)
        self.assertNotIn("health_score", result)

    def test_maintainability_is_separate_from_risk(self):
        result = DebtEstimator().estimate_debt(metrics(16))
        self.assertIsNone(result["risk_score"])
        self.assertEqual(result["maintainability_findings"][0]["rule"], "complex_function")

    def test_chronological_train_test_holdout(self):
        data = []
        for i in range(20):
            data.append({
                **metrics(i + 1),
                "commit_hash": f"commit-{i:02d}",
                "commit_date": f"2026-09-{i+1:02d}T12:00:00+00:00",
                "commit_sequence": i,
                "label_observed_at_sequence": i + 2,
                "path": "src/a.py",
                "future_bug_fix": int(i % 3 == 0),
            })
        estimator = DebtEstimator()
        report = estimator.train(list(reversed(data)))
        self.assertTrue(estimator.is_trained, report)
        self.assertEqual(estimator.train_commits, [f"commit-{i:02d}" for i in range(14)])
        self.assertEqual(estimator.test_commits, [f"commit-{i:02d}" for i in range(16, 20)])
        self.assertNotIn("commit-14", estimator.train_commits)
        self.assertNotIn("commit-15", estimator.train_commits)
        self.assertIn("Average precision", report)
        result = estimator.estimate_debt(metrics(21))
        self.assertIsNotNone(result["risk_score"])
        self.assertEqual(result["risk_score_kind"], "relative_ranking_not_calibrated_probability")

    def test_one_class_cannot_train(self):
        data = []
        for i in range(20):
            data.append({
                **metrics(i + 1),
                "commit_hash": f"commit-{i:02d}",
                "commit_date": f"2026-09-{i+1:02d}T12:00:00+00:00",
                "commit_sequence": i,
                "label_observed_at_sequence": i + 2,
                "path": "a.py",
                "future_bug_fix": 0,
            })
        estimator = DebtEstimator()
        self.assertIn("unavailable", estimator.train(data))
        self.assertFalse(estimator.is_trained)
        self.assertIsNone(estimator.estimate_debt(metrics())["risk_score"])

    def test_late_observation_window_can_make_training_unavailable(self):
        data = []
        for i in range(20):
            data.append({
                **metrics(i + 1),
                "commit_hash": f"commit-{i:02d}",
                "commit_date": f"2026-09-{i+1:02d}T12:00:00+00:00",
                "commit_sequence": i,
                "label_observed_at_sequence": i + 14,
                "path": "a.py",
                "future_bug_fix": i % 2,
            })
        estimator = DebtEstimator()
        self.assertIn("unavailable", estimator.train(data))
        self.assertFalse(estimator.is_trained)


if __name__ == "__main__":
    unittest.main()
