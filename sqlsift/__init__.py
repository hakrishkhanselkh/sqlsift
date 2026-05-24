"""sqlsift — diff query result sets and surface row-level discrepancies."""
from sqlsift.diff import DiffResult, RowDiff, diff
from sqlsift.loader import from_csv, from_dicts, from_json, from_tuples
from sqlsift.reporter import format_csv, format_json, format_text, print_report
from sqlsift.filter import by_columns, by_kind, by_predicate
from sqlsift.summarizer import DiffSummary, summarize
from sqlsift.sorter import by_column, by_key
from sqlsift.patcher import generate_patch
from sqlsift.exporter import (
    to_csv_file,
    to_csv_string,
    to_dict_list,
    to_json_file,
    to_text_file,
)
from sqlsift.validator import (
    ValidationReport,
    ValidationIssue,
    validate_columns,
    validate_keys,
    validate_no_null_keys,
)

__all__ = [
    # core
    "diff",
    "DiffResult",
    "RowDiff",
    # loader
    "from_dicts",
    "from_csv",
    "from_json",
    "from_tuples",
    # reporter
    "format_text",
    "format_csv",
    "format_json",
    "print_report",
    # filter
    "by_kind",
    "by_columns",
    "by_predicate",
    # summarizer
    "DiffSummary",
    "summarize",
    # sorter
    "by_key",
    "by_column",
    # patcher
    "generate_patch",
    # exporter
    "to_text_file",
    "to_csv_file",
    "to_json_file",
    "to_dict_list",
    "to_csv_string",
    # validator
    "ValidationReport",
    "ValidationIssue",
    "validate_keys",
    "validate_columns",
    "validate_no_null_keys",
]
