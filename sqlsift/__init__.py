"""sqlsift — diff query result sets and surface row-level discrepancies."""

from sqlsift.diff import DiffResult, RowDiff, diff  # noqa: F401
from sqlsift.reporter import format_csv, format_json, format_text, print_report  # noqa: F401

__all__ = [
    "diff",
    "DiffResult",
    "RowDiff",
    "format_text",
    "format_csv",
    "format_json",
    "print_report",
]

__version__ = "0.1.0"
