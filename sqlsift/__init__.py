"""sqlsift – diff query result sets and surface row-level discrepancies."""
from sqlsift.diff import DiffResult, RowDiff, diff  # noqa: F401
from sqlsift.loader import from_csv, from_dicts, from_json, from_tuples  # noqa: F401
from sqlsift.reporter import format_csv, format_json, format_text, print_report  # noqa: F401
from sqlsift.filter import by_columns, by_kind, by_predicate  # noqa: F401
from sqlsift.summarizer import DiffSummary, summarize  # noqa: F401
from sqlsift.sorter import by_column  # noqa: F401
from sqlsift.patcher import generate_patch  # noqa: F401
from sqlsift.exporter import (
    to_csv_file,
    to_csv_string,
    to_dict_list,
    to_json_file,
    to_text_file,
)  # noqa: F401
from sqlsift.validator import ValidationIssue, ValidationReport, validate  # noqa: F401
from sqlsift.sampler import head, random_sample, stratified_sample, tail  # noqa: F401
from sqlsift.grouper import by_column as group_by_column  # noqa: F401
from sqlsift.grouper import by_columns as group_by_columns  # noqa: F401
from sqlsift.grouper import counts_by_column  # noqa: F401
from sqlsift.pivot import by_column as pivot_by_column  # noqa: F401
from sqlsift.pivot import change_frequency, most_changed_columns  # noqa: F401
from sqlsift.scorer import DiffScore, score  # noqa: F401
from sqlsift.merger import conflicts, merge  # noqa: F401
from sqlsift.highlighter import (  # noqa: F401
    changed_columns,
    columns_changed_in_result,
    highlight_result,
    highlight_row,
)

__all__ = [
    # core
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
    # summarizer
    "DiffSummary",
    "summarize",
    # sorter
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
    "ValidationIssue",
    "ValidationReport",
    "validate",
    # sampler
    "head",
    "tail",
    "random_sample",
    "stratified_sample",
    # grouper
    "group_by_column",
    "group_by_columns",
    "counts_by_column",
    # pivot
    "pivot_by_column",
    "change_frequency",
    "most_changed_columns",
    # scorer
    "DiffScore",
    "score",
    # merger
    "merge",
    "conflicts",
    # highlighter
    "changed_columns",
    "highlight_row",
    "highlight_result",
    "columns_changed_in_result",
]
