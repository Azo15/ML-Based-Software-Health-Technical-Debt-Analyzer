import unittest

from feature_extractor.metrics_analyzer import MetricsAnalyzer


class MetricsAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = MetricsAnalyzer()

    def test_invalid_python_is_marked_invalid(self):
        metrics = self.analyzer.analyze_code("def broken(:\n    return 1\n")
        self.assertFalse(metrics["valid"])
        self.assertEqual(metrics["loc"], 0)
        self.assertIn("line 1", metrics["parse_error"])

    def test_max_complexity_survives_many_simple_functions(self):
        complex_function = "def branch(x):\n" + "".join(
            f"    if x == {i}:\n        return {i}\n" for i in range(15)
        ) + "    return -1\n"
        helpers = "".join(f"\ndef helper_{i}():\n    return 1\n" for i in range(19))
        solo = self.analyzer.analyze_code(complex_function)
        crowded = self.analyzer.analyze_code(complex_function + helpers)
        self.assertTrue(crowded["valid"])
        self.assertEqual(solo["cyclomatic_complexity_max"], 16)
        self.assertEqual(crowded["cyclomatic_complexity_max"], 16)
        self.assertLess(crowded["cyclomatic_complexity"], solo["cyclomatic_complexity"])

    def test_lloc_counts_logical_lines(self):
        metrics = self.analyzer.analyze_code("def add(a, b):\n    return a + b\n")
        self.assertTrue(metrics["valid"])
        self.assertEqual(metrics["lloc"], 2)


if __name__ == "__main__":
    unittest.main()
