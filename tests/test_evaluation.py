import unittest

from model.evaluation import ranking_metrics


class RankingMetricsTests(unittest.TestCase):
    def test_known_ranking_and_threshold_metrics(self):
        result = ranking_metrics([1, 0, 1, 0, 0], [0.9, 0.8, 0.7, 0.2, 0.1], [1, 1, 1, 0, 0])
        self.assertAlmostEqual(result["average_precision"], (1 + 2 / 3) / 2)
        self.assertEqual(result["inspection_k"], 1)
        self.assertEqual(result["recall_at_k"], 0.5)
        self.assertAlmostEqual(result["precision"], 2 / 3)
        self.assertEqual(result["recall"], 1.0)

    def test_inspection_budget_rounds_up(self):
        result = ranking_metrics([1, 1, 0, 0, 0, 0], [6, 5, 4, 3, 2, 1])
        self.assertEqual(result["inspection_k"], 2)
        self.assertEqual(result["recall_at_k"], 1.0)

    def test_no_positives_has_no_recall_or_average_precision(self):
        result = ranking_metrics([0, 0], [1, 0])
        self.assertIsNone(result["recall_at_k"])
        self.assertIsNone(result["average_precision"])

    def test_invalid_scores_are_rejected(self):
        for labels, scores in [([], []), ([1], [0, 1]), ([1], [float("inf")]), ([2], [0])]:
            with self.assertRaises(ValueError):
                ranking_metrics(labels, scores)
