"""sqlsift public API — auto-generated aggregation of all sub-modules."""

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.loader import from_csv, from_dicts, from_json, from_tuples
from sqlsift.reporter import format_csv, format_json, format_text, print_report
from sqlsift.filter import by_columns, by_kind, by_predicate
from sqlsift.summarizer import ColumnStats, DiffSummary
from sqlsift.sorter import by_column  # sorter.by_key conflicts with deduplicator
from sqlsift.patcher import generate_patch
from sqlsift.exporter import (
    to_csv_file,
    to_csv_string,
    to_dict_list,
    to_json_file,
    to_text_file,
)
from sqlsift.validator import ValidationIssue, ValidationReport
from sqlsift.sampler import head, random_sample, stratified_sample, tail
from sqlsift.grouper import counts_by_column
from sqlsift.pivot import by_column as pivot_by_column, change_frequency, most_changed_columns
from sqlsift.scorer import DiffScore, score
from sqlsift.merger import conflicts, merge
from sqlsift.highlighter import (
    changed_columns,
    columns_changed_in_result,
    highlight_result,
    highlight_row,
)
from sqlsift.annotator import annotate_result, annotate_row, rule_column_changed
from sqlsift.segmenter import by_column_value as segment_by_column_value, sizes
from sqlsift.ranker import top_n
from sqlsift.timeline import Snapshot, Timeline
from sqlsift.comparator import changed_in_column, column_delta, compare_column, values_equal
from sqlsift.threshold import above_value, by_absolute_change, by_relative_change
from sqlsift.deduplicator import duplicates
from sqlsift.normalizer import normalize_result, strip_whitespace, to_lowercase
from sqlsift.transformer import drop_columns, rename_columns, transform_rows
from sqlsift.pipeline import Pipeline
from sqlsift.splitter import by_predicate as split_by_predicate, by_size
from sqlsift.flattener import flatten, flatten_modified_delta
from sqlsift.truncator import by_count, by_fraction, drop_beyond
from sqlsift.aggregator import ColumnAggregate
from sqlsift.classifier import classify, rule_by_kind as classify_by_kind
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
from sqlsift.auditor import AuditEntry, audit_summary, build_audit_log
from sqlsift.replay import replay, replay_stats
from sqlsift.mapper import cast_column, map_rows, rename_key
from sqlsift.router import route
from sqlsift.dispatcher import Dispatcher
from sqlsift.windower import by_index, rolling_counts
from sqlsift.tracer import (
    TraceEntry,
    kind_changed,
    persistent_keys,
    trace,
    transient_keys,
)

__all__ = [
    # diff
    "DiffResult",
    "RowDiff",
    # loader
    "from_csv",
    "from_dicts",
    "from_json",
    "from_tuples",
    # reporter
    "format_csv",
    "format_json",
    "format_text",
    "print_report",
    # filter
    "by_columns",
    "by_kind",
    "by_predicate",
    # summarizer
    "ColumnStats",
    "DiffSummary",
    # sorter
    "by_column",
    # patcher
    "generate_patch",
    # exporter
    "to_csv_file",
    "to_csv_string",
    "to_dict_list",
    "to_json_file",
    "to_text_file",
    # validator
    "ValidationIssue",
    "ValidationReport",
    # sampler
    "head",
    "random_sample",
    "stratified_sample",
    "tail",
    # grouper
    "counts_by_column",
    # pivot
    "pivot_by_column",
    "change_frequency",
    "most_changed_columns",
    # scorer
    "DiffScore",
    "score",
    # merger
    "conflicts",
    "merge",
    # highlighter
    "changed_columns",
    "columns_changed_in_result",
    "highlight_result",
    "highlight_row",
    # annotator
    "annotate_result",
    "annotate_row",
    "rule_column_changed",
    # segmenter
    "segment_by_column_value",
    "sizes",
    # ranker
    "top_n",
    # timeline
    "Snapshot",
    "Timeline",
    # comparator
    "changed_in_column",
    "column_delta",
    "compare_column",
    "values_equal",
    # threshold
    "above_value",
    "by_absolute_change",
    "by_relative_change",
    # deduplicator
    "duplicates",
    # normalizer
    "normalize_result",
    "strip_whitespace",
    "to_lowercase",
    # transformer
    "drop_columns",
    "rename_columns",
    "transform_rows",
    # pipeline
    "Pipeline",
    # splitter
    "split_by_predicate",
    "by_size",
    # flattener
    "flatten",
    "flatten_modified_delta",
    # truncator
    "by_count",
    "by_fraction",
    "drop_beyond",
    # aggregator
    "ColumnAggregate",
    # classifier
    "classify",
    "classify_by_kind",
    # profiler
    "profile_column",
    "profile_result",
    # inspector
    "column_names",
    "has_column",
    "key_columns",
    "row_count",
    "sample_values",
    # matcher
    "exact_match",
    "find_by_key",
    "fuzzy_match",
    # streaker
    "find_streaks",
    # censor
    "redact",
    "redact_by_predicate",
    # labeler
    "label_result",
    "label_row",
    # auditor
    "AuditEntry",
    "audit_summary",
    "build_audit_log",
    # replay
    "replay",
    "replay_stats",
    # mapper
    "cast_column",
    "map_rows",
    "rename_key",
    # router
    "route",
    # dispatcher
    "Dispatcher",
    # windower
    "by_index",
    "rolling_counts",
    # tracer
    "TraceEntry",
    "kind_changed",
    "persistent_keys",
    "trace",
    "transient_keys",
]
