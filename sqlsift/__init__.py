"""sqlsift — diff query result sets and surface row-level discrepancies."""

from sqlsift.diff import DiffResult, RowDiff, diff  # noqa: F401
from sqlsift.loader import from_dicts, from_csv, from_json, from_tuples  # noqa: F401
from sqlsift.reporter import format_text, format_csv, format_json, print_report  # noqa: F401
from sqlsift.filter import by_kind, by_columns, by_predicate  # noqa: F401
from sqlsift.summarizer import summarize, DiffSummary, ColumnStats  # noqa: F401
from sqlsift.sorter import by_key, by_column, by_kind as sort_by_kind  # noqa: F401
from sqlsift.patcher import generate_patch  # noqa: F401
from sqlsift.exporter import (  # noqa: F401
    to_text_file,
    to_csv_file,
    to_json_file,
    to_dict_list,
    to_csv_string,
)
from sqlsift.validator import validate, ValidationReport, ValidationIssue  # noqa: F401
from sqlsift.sampler import head, tail, random_sample, stratified_sample  # noqa: F401
from sqlsift.grouper import by_column as group_by_column  # noqa: F401
from sqlsift.pivot import by_column as pivot_by_column, change_frequency, most_changed_columns  # noqa: F401
from sqlsift.scorer import score, DiffScore  # noqa: F401
from sqlsift.merger import merge, conflicts  # noqa: F401
from sqlsift.highlighter import highlight_result, changed_columns  # noqa: F401
from sqlsift.annotator import annotate_result, annotate_row  # noqa: F401
from sqlsift.segmenter import by_column_value, by_predicate as segment_by_predicate, sizes  # noqa: F401
from sqlsift.ranker import by_column as rank_by_column, by_score as rank_by_score, top_n  # noqa: F401
from sqlsift.timeline import Timeline, Snapshot  # noqa: F401

__all__ = [
    # core
    "DiffResult",
    "RowDiff",
    "diff",
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
    "summarize",
    "DiffSummary",
    "ColumnStats",
    # sorter
    "by_key",
    "by_column",
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
    "validate",
    "ValidationReport",
    "ValidationIssue",
    # sampler
    "head",
    "tail",
    "random_sample",
    "stratified_sample",
    # grouper
    "group_by_column",
    # pivot
    "pivot_by_column",
    "change_frequency",
    "most_changed_columns",
    # scorer
    "score",
    "DiffScore",
    # merger
    "merge",
    "conflicts",
    # highlighter
    "highlight_result",
    "changed_columns",
    # annotator
    "annotate_result",
    "annotate_row",
    # segmenter
    "by_column_value",
    "segment_by_predicate",
    "sizes",
    # ranker
    "rank_by_column",
    "rank_by_score",
    "top_n",
    # timeline
    "Timeline",
    "Snapshot",
]
