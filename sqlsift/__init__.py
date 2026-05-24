"""sqlsift — diff query result sets and surface row-level discrepancies."""

from sqlsift.diff import diff, DiffResult, RowDiff
from sqlsift.loader import from_dicts, from_csv, from_json, from_tuples
from sqlsift.reporter import format_text, format_csv, format_json, print_report
from sqlsift.filter import by_kind, by_columns, by_predicate

__all__ = [
    # core diff
    "diff",
    "DiffResult",
    "RowDiff",
    # loaders
    "from_dicts",
    "from_csv",
    "from_json",
    "from_tuples",
    # reporters
    "format_text",
    "format_csv",
    "format_json",
    "print_report",
    # filters
    "by_kind",
    "by_columns",
    "by_predicate",
]

__version__ = "0.1.0"
