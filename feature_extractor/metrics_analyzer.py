"""
Module for extracting software metrics from Python source code.
Uses radon and lizard libraries to calculate complexity and size metrics.
"""
import ast
import lizard
from radon.complexity import cc_visit
from radon.metrics import h_visit
from radon.raw import analyze as raw_analyze
from typing import Dict, Any
from utils.logger import logger

class MetricsAnalyzer:
    """
    Analyzes Python source code to extract various software metrics.
    Calculates McCabe Cyclomatic Complexity, Halstead Metrics, and size metrics.
    """

    def analyze_code(self, source_code: str) -> Dict[str, Any]:
        """
        Analyzes the given source code and returns a dictionary of metrics.

        Args:
            source_code (str): The Python source code to analyze.

        Returns:
            Dict[str, float]: Dictionary containing computed metrics.
                              Returns empty dict if parsing fails.
        """
        metrics = {
            'cyclomatic_complexity': 0.0,
            'cyclomatic_complexity_max': 0.0,
            'halstead_volume': 0.0,
            'halstead_difficulty': 0.0,
            'halstead_effort': 0.0,
            'loc': 0.0,
            'lloc': 0.0,
            'num_functions': 0.0,
            'valid': False,
            'parse_error': None,
        }

        if not source_code or not source_code.strip():
            return metrics

        try:
            ast.parse(source_code)
        except SyntaxError as exc:
            metrics['parse_error'] = f"line {exc.lineno}: {exc.msg}"
            logger.warning("Skipping Python source with syntax error: %s", metrics['parse_error'])
            return metrics

        metrics['valid'] = True

        try:
            # 1. Lizard Analysis for LOC and basic Cyclomatic Complexity
            lizard_analysis = lizard.analyze_file.analyze_source_code("temp.py", source_code)
            metrics['loc'] = float(lizard_analysis.nloc) # Non-comment lines of code
            metrics['num_functions'] = float(len(lizard_analysis.function_list))
            metrics['lloc'] = float(raw_analyze(source_code).lloc)
            
            # Average cyclomatic complexity of functions from lizard
            if metrics['num_functions'] > 0:
                avg_cc = sum(func.cyclomatic_complexity for func in lizard_analysis.function_list) / metrics['num_functions']
                metrics['cyclomatic_complexity'] = float(avg_cc)
                metrics['cyclomatic_complexity_max'] = float(max(func.cyclomatic_complexity for func in lizard_analysis.function_list))
            else:
                # If no functions, we use radon to calculate raw complexity
                try:
                    blocks = cc_visit(source_code)
                    if blocks:
                        metrics['cyclomatic_complexity'] = float(sum(b.complexity for b in blocks) / len(blocks))
                        metrics['cyclomatic_complexity_max'] = float(max(b.complexity for b in blocks))
                except Exception:
                    pass

            # 2. Radon Analysis for Halstead metrics
            try:
                halstead_report = h_visit(source_code)
                metrics['halstead_volume'] = float(halstead_report.total.volume)
                metrics['halstead_difficulty'] = float(halstead_report.total.difficulty)
                metrics['halstead_effort'] = float(halstead_report.total.effort)
            except Exception as e:
                logger.debug(f"Radon Halstead analysis failed for a file segment. {e}")

        except Exception as e:
            logger.debug(f"Metrics analysis encountered an error: {e}")
            metrics['valid'] = False
            metrics['parse_error'] = f"metric extraction failed: {e}"

        return metrics
