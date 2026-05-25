"""sqlsift — diff query result sets and surface row-level discrepancies.

Public re-exports for the most commonly used symbols.
"""

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.loader import from_csv, from_dicts, from_json, from_tuples
from sqlsift.reporter import format_csv, format_json, format_text, print_report
from sqlsift.filter import by_columns, by_kind, by_predicate
from sqlsift.summarizer import DiffSummary, summarize
from sqlsift.sorter import by_column as sort_by_column
from sqlsift.sorter import by_key as sort_by_key
from sqlsift.sorter import by_kind as sort_by_kind
from sqlsift.patcher import generate_patch
from sqlsift.exporter import (
    to_csv_file,
    to_csv_string,
    to_dict_list,
    to_json_file,
    to_text_file,
)
from sqlsift.validator import ValidationReport, validate
from sqlsift.sampler import head, random_sample, stratified_sample, tail
from sqlsift.grouper import by_column as group_by_column
from sqlsift.grouper import by_columns as group_by_columns
from sqlsift.grouper import counts_by_column
from sqlsift.pivot import by_column as pivot_by_column
from sqlsift.pivot import change_frequency, most_changed_columns
from sqlsift.scorer import score
from sqlsift.merger import conflicts, merge
from sqlsift.highlighter import (
    changed_columns,
    columns_changed_in_result,
    highlight_result,
    highlight_row,
)
from sqlsift.annotator import annotate_result, annotate_row
from sqlsift.segmenter import by_column_value as segment_by_column_value
from sqlsift.segmenter import by_predicate as segment_by_predicate
from sqlsift.segmenter import sizes as segment_sizes
from sqlsift.ranker import by_column as rank_by_column
from sqlsift.ranker import by_score as rank_by_score
from sqlsift.ranker import top_n
from sqlsift.timeline import Timeline
from sqlsift.comparator import column_delta, compare_column, values_equal
from sqlsift.threshold import (
    above_value,
    by_absolute_change,
    by_relative_change,
)
from sqlsift.deduplicator import by_key as dedup_by_key
from sqlsift.deduplicator import by_row as dedup_by_row
from sqlsift.deduplicator import duplicates
from sqlsift.normalizer import (
    normalize_result,
    strip_whitespace,
    to_lowercase,
)
from sqlsift.transformer import drop_columns, rename_columns, transform_rows
from sqlsift.pipeline import Pipeline
from sqlsift.splitter import by_column_value as split_by_column_value
from sqlsift.splitter import by_predicate as split_by_predicate
from sqlsift.splitter import by_size as split_by_size
from sqlsift.flattener import flatten, flatten_modified_delta
from sqlsift.truncator import by_count as truncate_by_count
from sqlsift.truncator import by_fraction as truncate_by_fraction
from sqlsift.truncator import drop_beyond
from sqlsift.aggregator import aggregate
from sqlsift.classifier import classify
from sqlsift.profiler import profile_column, profile_result
from sqlsift.inspector import (
    column_names,
    has_column,
    key_columns,
    row_count,
    sample_values,
)
from sqlsift.matcher import exact_match, find_by_key, fuzzy_match
from sqlsift.streaker import find_streaks
from sqlsift.censor import redact, redact_by_predicate
from sqlsift.labeler import label_result, label_row
from sqlsift.auditor import build_audit_log, audit_summary
from sqlsift.replay import replay, replay_stats
from sqlsift.mapper import cast_column, map_rows, rename_key

__all__ = [
    # core
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
    "sort_by_key",
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
    "score",
    # merger
    "merge",
    "conflicts",
    # highlighter
    "changed_columns",
    "highlight_row",
    "highlight_result",
    "columns_changed_in_result",
    # annotator
    "annotate_row",
    "annotate_result",
    # segmenter
    "segment_by_column_value",
    "segment_by_predicate",
    "segment_sizes",
    # ranker
    "rank_by_column",
    "rank_by_score",
    "top_n",
    # timeline
    "Timeline",
    # comparator
    "values_equal",
    "column_delta",
    "compare_column",
    # threshold
    "by_absolute_change",
    "by_relative_change",
    "above_value",
    # deduplicator
    "dedup_by_key",
    "dedup_by_row",
    "duplicates",
    # normalizer
    "strip_whitespace",
    "to_lowercase",
    "normalize_result",
    # transformer
    "transform_rows",
    "rename_columns",
    "drop_columns",
    # pipeline
    "Pipeline",
    # splitter
    "split_by_column_value",
    "split_by_size",
    "split_by_predicate",
    # flattener
    "flatten",
    "flatten_modified_delta",
    # truncator
    "truncate_by_count",
    "truncate_by_fraction",
    "drop_beyond",
    # aggregator
    "aggregate",
    # classifier
    "classify",
    # profiler
    "profile_column",
    "profile_result",
    # inspector
    "column_names",
    "key_columns",
    "row_count",
    "has_column",
    "sample_values",
    # matcher
    "exact_match",
    "fuzzy_match",
    "find_by_key",
    # streaker
    "find_streaks",
    # censor
    "redact",
    "redact_by_predicate",
    # labeler
    "label_row",
    "label_result",
    # auditor
    "build_audit_log",
    "audit_summary",
    # replay
    "replay",
    "replay_stats",
    # mapper
    "map_rows",
    "rename_key",
    "cast_column",
]
