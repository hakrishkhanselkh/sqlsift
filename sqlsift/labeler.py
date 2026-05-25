"""sqlsift.labeler — attach human-readable labels to RowDiff objects."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

from sqlsift.diff import DiffResult, RowDiff

# A labeling rule is a callable that receives a RowDiff and returns a string
# label or None when the rule does not apply.
LabelRule = Callable[[RowDiff], Optional[str]]


def label_row(
    row: RowDiff,
    rules: List[LabelRule],
    default: str = "unlabeled",
) -> str:
    """Return the first non-None label produced by *rules*, or *default*."""
    for rule in rules:
        result = rule(row)
        if result is not None:
            return result
    return default


def label_result(
    result: DiffResult,
    rules: List[LabelRule],
    default: str = "unlabeled",
) -> Dict[str, str]:
    """Return a mapping of row-key string → label for every row in *result*."""
    labeled: Dict[str, str] = {}
    for row in result.diffs:
        key_str = str(row.key)
        labeled[key_str] = label_row(row, rules, default)
    return labeled


def rule_by_kind(kind: str, label: str) -> LabelRule:
    """Return a rule that assigns *label* when the row kind matches *kind*."""
    if kind not in ("added", "removed", "modified"):
        raise ValueError(f"Invalid kind {kind!r}. Must be 'added', 'removed', or 'modified'.")

    def _rule(row: RowDiff) -> Optional[str]:
        return label if row.kind == kind else None

    return _rule


def rule_by_column_value(
    column: str,
    value: object,
    label: str,
) -> LabelRule:
    """Return a rule that assigns *label* when *column* equals *value* in the row data."""

    def _rule(row: RowDiff) -> Optional[str]:
        data = row.new_row if row.new_row is not None else row.old_row
        if data is None:
            return None
        return label if data.get(column) == value else None

    return _rule


def rule_by_predicate(predicate: Callable[[RowDiff], bool], label: str) -> LabelRule:
    """Return a rule that assigns *label* when *predicate* returns True."""

    def _rule(row: RowDiff) -> Optional[str]:
        return label if predicate(row) else None

    return _rule
