"""sqlsift — diff query result sets and surface row-level discrepancies."""

from .diff import DiffResult, RowDiff, diff  # noqa: F401
from .loader import from_dicts, from_csv, from_json, from_tuples  # noqa: F401
from .reporter import format_text, format_csv, format_json, print_report  # noqa: F401
from .filter import by_kind, by_columns as filter_by_columns, by_predicate  # noqa: F401
from .summarizer import DiffSummary, summarize  # noqa: F401
from .sorter import by_key, by_column as sort_by_column, by_kind as sort_by_kind  # noqa: F401
from .patcher import generate_patch  # noqa: F401
from .exporter import (
    to_text_file,
    to_csv_file,
    to_json_file,
    to_dict_list,
    to_csv_string,
)  # noqa: F401
from .validator import ValidationIssue, ValidationReport, validate  # noqa: F401
from .sampler import head, tail, random_sample, stratified_sample  # noqa: F401
from .grouper import (
    by_column as group_by_column,
    by_columns as group_by_columns,
    counts_by_column,
)  # noqa: F401

__version__ = "0.1.0"
__all__ = [
    # core
    "DiffResult",
    "RowDiff",
    "diff",
    # loaders
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
    "filter_by_columns",
    "by_predicate",
    # summarizer
    "DiffSummary",
    "summarize",
    # sorter
    "by_key",
    "sort_by_column",
    "sort_by_kind",
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
    # meta
    "__version__",
]
