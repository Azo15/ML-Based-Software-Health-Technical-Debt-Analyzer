"""Compatibility import; report export is shared by CLI and web clients."""

from analysis.report_export import write_report

__all__ = ["write_report"]
