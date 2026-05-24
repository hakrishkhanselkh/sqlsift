"""sqlsift — diff query result sets and surface row-level discrepancies."""

from sqlsift.diff import DiffResult, RowDiff, diff
from sqlsift.loader import from_dicts, from_csv, from_json, from_tuples
from sqlsift.reporter import format_text, format_csv, format_json, print_report
from sqlsift.filter import by_kind, by_columns, by_predicate
from sqlsift.summarizer import DiffSummary, summarize
from sqlsift.sorter import by_key, by_column, by_kind as sort_by_kind
from sqlsift.patcher import generate_patch
from sqlsift.exporter import (
    to_text_file,
    to_csv_file,
    to_json_file,
    to_dict_list,
    to_csv_string,
)
from sqlsift.validator import ValidationReport, validate
from sqlsift.sampler import head, tail, random_sample, stratified_sample

__all__ = [
    # core
    "DiffResult",
    "RowDiff",
    "diff",
    # loading
    "from_dicts",
    "from_csv",
    "from_json",
    "from_tuples",
    # reporting
    "format_text",
    "format_csv",
    "format_json",
    "print_report",
    # filtering
    "by_kind",
    "by_columns",
    "by_predicate",
    # summarising
    "DiffSummary",
    "summarize",
    # sorting
    "by_key",
    "by_column",
    "sort_by_kind",
    # patching
    "generate_patch",
    # exporting
    "to_text_file",
    "to_csv_file",
    "to_json_file",
    "to_dict_list",
    "to_csv_string",
    # validation
    "ValidationReport",
    "validate",
    # sampling
    "head",
    "tail",
    "random_sample",
    "stratified_sample",
]
