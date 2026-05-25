"""sqlsift – diff query result sets and surface row-level discrepancies."""

from sqlsift.diff import RowDiff, DiffResult, diff  # noqa: F401
from sqlsift.loader import from_dicts, from_csv, from_json, from_tuples  # noqa: F401
from sqlsift.reporter import format_text, format_csv, format_json, print_report  # noqa: F401
from sqlsift.filter import by_kind, by_columns, by_predicate  # noqa: F401
from sqlsift.summarizer import DiffSummary, summarize  # noqa: F401
from sqlsift.sorter import by_key, by_column, by_kind as sort_by_kind  # noqa: F401
from sqlsift.patcher import generate_patch  # noqa: F401
from sqlsift.exporter import (  # noqa: F401
    to_text_file,
    to_csv_file,
    to_json_file,
    to_dict_list,
    to_csv_string,
)
from sqlsift.validator import ValidationReport, validate  # noqa: F401
from sqlsift.sampler import head, tail, random_sample, stratified_sample  # noqa: F401
from sqlsift.grouper import by_column as group_by_column  # noqa: F401
from sqlsift.pivot import by_column as pivot_by_column  # noqa: F401
from sqlsift.scorer import score  # noqa: F401
from sqlsift.merger import merge, conflicts  # noqa: F401
from sqlsift.highlighter import highlight_result  # noqa: F401
from sqlsift.annotator import annotate_result  # noqa: F401
from sqlsift.segmenter import by_column_value as segment_by_column_value  # noqa: F401
from sqlsift.ranker import by_column as rank_by_column  # noqa: F401
from sqlsift.timeline import Timeline  # noqa: F401
from sqlsift.comparator import compare_column  # noqa: F401
from sqlsift.threshold import by_absolute_change, by_relative_change  # noqa: F401
from sqlsift.deduplicator import by_key as dedup_by_key  # noqa: F401
from sqlsift.normalizer import normalize_result  # noqa: F401
from sqlsift.transformer import transform_rows, rename_columns, drop_columns  # noqa: F401
from sqlsift.pipeline import Pipeline  # noqa: F401
from sqlsift.splitter import by_size as split_by_size  # noqa: F401
from sqlsift.flattener import flatten  # noqa: F401
from sqlsift.truncator import by_count as truncate_by_count  # noqa: F401
from sqlsift.aggregator import aggregate  # noqa: F401
from sqlsift.classifier import (  # noqa: F401
    classify,
    label_counts,
    rule_by_kind,
    rule_by_column_value,
    rule_by_predicate,
)

__all__ = [
    # core
    "RowDiff",
    "DiffResult",
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
    "DiffSummary",
    "summarize",
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
    "ValidationReport",
    "validate",
    # sampler
    "head",
    "tail",
    "random_sample",
    "stratified_sample",
    # grouper
    "group_by_column",
    # pivot
    "pivot_by_column",
    # scorer
    "score",
    # merger
    "merge",
    "conflicts",
    # highlighter
    "highlight_result",
    # annotator
    "annotate_result",
    # segmenter
    "segment_by_column_value",
    # ranker
    "rank_by_column",
    # timeline
    "Timeline",
    # comparator
    "compare_column",
    # threshold
    "by_absolute_change",
    "by_relative_change",
    # deduplicator
    "dedup_by_key",
    # normalizer
    "normalize_result",
    # transformer
    "transform_rows",
    "rename_columns",
    "drop_columns",
    # pipeline
    "Pipeline",
    # splitter
    "split_by_size",
    # flattener
    "flatten",
    # truncator
    "truncate_by_count",
    # aggregator
    "aggregate",
    # classifier
    "classify",
    "label_counts",
    "rule_by_kind",
    "rule_by_column_value",
    "rule_by_predicate",
]
