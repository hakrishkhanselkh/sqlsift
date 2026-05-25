"""Classify DiffResult rows into named categories based on user-defined rules."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

from sqlsift.diff import DiffResult, RowDiff


Rule = Callable[[RowDiff], Optional[str]]


def _apply_rules(row: RowDiff, rules: List[Rule]) -> str:
    """Return the label from the first matching rule, or 'unclassified'."""
    for rule in rules:
        label = rule(row)
        if label is not None:
            return label
    return "unclassified"


def classify(result: DiffResult, rules: List[Rule]) -> Dict[str, List[RowDiff]]:
    """Group every row in *result* into labelled buckets.

    Each rule is a callable that receives a :class:`~sqlsift.diff.RowDiff` and
    returns a string label when the row matches, or ``None`` to pass through to
    the next rule.  Rows that match no rule are placed under ``'unclassified'``.

    Returns a ``dict`` mapping label -> list of matching rows.
    """
    buckets: Dict[str, List[RowDiff]] = {}
    for row in result.diffs:
        label = _apply_rules(row, rules)
        buckets.setdefault(label, []).append(row)
    return buckets


def rule_by_kind(kind: str, label: str) -> Rule:
    """Return a rule that labels rows whose *kind* matches *kind*."""
    if kind not in ("added", "removed", "modified"):
        raise ValueError(f"kind must be 'added', 'removed', or 'modified'; got {kind!r}")

    def _rule(row: RowDiff) -> Optional[str]:
        return label if row.kind == kind else None

    return _rule


def rule_by_column_value(column: str, value: object, label: str) -> Rule:
    """Return a rule that labels rows where *column* in the source row equals *value*."""

    def _rule(row: RowDiff) -> Optional[str]:
        row_value = row.left.get(column) if row.left else None
        if row_value is None and row.right:
            row_value = row.right.get(column)
        return label if row_value == value else None

    return _rule


def rule_by_predicate(predicate: Callable[[RowDiff], bool], label: str) -> Rule:
    """Return a rule that labels rows for which *predicate* returns ``True``."""

    def _rule(row: RowDiff) -> Optional[str]:
        return label if predicate(row) else None

    return _rule


def label_counts(classified: Dict[str, List[RowDiff]]) -> Dict[str, int]:
    """Return a mapping of label -> row count from a classified result."""
    return {label: len(rows) for label, rows in classified.items()}
