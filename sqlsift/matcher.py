"""matcher.py — fuzzy and exact row matching utilities for DiffResult sets."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlsift.diff import DiffResult, RowDiff


def _row_value(row: Dict[str, Any], columns: Sequence[str]) -> Tuple[Any, ...]:
    """Extract an ordered tuple of values for the given columns from a row."""
    return tuple(row.get(col) for col in columns)


def exact_match(
    result: DiffResult,
    columns: Sequence[str],
    target: Dict[str, Any],
) -> List[RowDiff]:
    """Return all RowDiff entries whose row data matches *target* exactly on *columns*.

    For modified rows the *before* snapshot is used for comparison.
    """
    if not columns:
        raise ValueError("columns must not be empty")

    target_values = _row_value(target, columns)
    matched: List[RowDiff] = []

    for diff in result.diffs:
        row = diff.before if diff.before is not None else diff.after
        if row is None:
            continue
        if _row_value(row, columns) == target_values:
            matched.append(diff)

    return matched


def fuzzy_match(
    result: DiffResult,
    column: str,
    value: str,
    threshold: float = 0.6,
) -> List[RowDiff]:
    """Return RowDiff entries whose *column* value is similar to *value*.

    Similarity is measured with a simple character-overlap ratio so that the
    module has no external dependencies.  Use ``threshold`` (0–1) to control
    the minimum required score.
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0.0 and 1.0")

    def _similarity(a: str, b: str) -> float:
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        a_chars = set(a.lower())
        b_chars = set(b.lower())
        overlap = len(a_chars & b_chars)
        return overlap / max(len(a_chars), len(b_chars))

    matched: List[RowDiff] = []
    for diff in result.diffs:
        row = diff.before if diff.before is not None else diff.after
        if row is None:
            continue
        cell = row.get(column)
        if cell is None:
            continue
        if _similarity(str(cell), str(value)) >= threshold:
            matched.append(diff)

    return matched


def find_by_key(
    result: DiffResult,
    key_columns: Sequence[str],
    key_values: Sequence[Any],
) -> Optional[RowDiff]:
    """Return the first RowDiff whose key columns match *key_values*, or None."""
    if len(key_columns) != len(key_values):
        raise ValueError("key_columns and key_values must have the same length")

    target = dict(zip(key_columns, key_values))
    matches = exact_match(result, list(key_columns), target)
    return matches[0] if matches else None
