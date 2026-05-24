"""sqlsift — diff query result sets and surface row-level discrepancies."""

from sqlsift.diff import DiffResult, RowDiff, diff
from sqlsift.exporter import (
    to_csv_file,
    to_csv_string,
    to_dict_list,
    to_json_file,
    to_json_string,
    to_text_file,
)
from sqlsift.filter import by_columns, by_kind, by_predicate
from sqlsift.loader import from_csv, from_dicts, from_json, from_tuples
from sqlsift.patcher import generate_patch
from sqlsift.reporter import format_csv, format_json, format_text, print_report
from sqlsift.sorter import by_column, by_key
from sqlsift.sorter import by_kind as sort_by_kind
from sqlsift.summarizer import DiffSummary, summarize

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
    # filter
    "by_kind",
    "by_columns",
    "by_predicate",
    # sorter
    "by_key",
    "by_column",
    "sort_by_kind",
    # summarizer
    "DiffSummary",
    "summarize",
    # reporter
    "format_text",
    "format_csv",
    "format_json",
    "print_report",
    # exporter
    "to_text_file",
    "to_csv_file",
    "to_json_file",
    "to_csv_string",
    "to_json_string",
    "to_dict_list",
    # patcher
    "generate_patch",
]
