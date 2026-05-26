"""joiner.py — join two DiffResult sets on shared key columns."""

from __future__ import annotations

from typing import List, Optional, Tuple

from sqlsift.diff import DiffResult, RowDiff


def _row_key(row: dict, keys: List[str]) -> Tuple:
    """Return a hashable key tuple from *row* using *keys*."""
    return tuple(row.get(k) for k in keys)


def inner(left: DiffResult, right: DiffResult, keys: List[str]) -> DiffResult:
    """Return rows whose key appears in *both* left and right results.

    The returned :class:`~sqlsift.diff.DiffResult` contains only the
    :class:`~sqlsift.diff.RowDiff` objects from *left* whose composite
    key is also present in *right*.
    """
    right_keys = {
        _row_key(rd.row, keys)
        for rd in right.diffs
        if rd.row is not None
    }
    matched = [
        rd for rd in left.diffs
        if rd.row is not None and _row_key(rd.row, keys) in right_keys
    ]
    return DiffResult(matched)


def left_only(left: DiffResult, right: DiffResult, keys: List[str]) -> DiffResult:
    """Return rows from *left* whose key is **not** present in *right*."""
    right_keys = {
        _row_key(rd.row, keys)
        for rd in right.diffs
        if rd.row is not None
    }
    unmatched = [
        rd for rd in left.diffs
        if rd.row is not None and _row_key(rd.row, keys) not in right_keys
    ]
    return DiffResult(unmatched)


def right_only(left: DiffResult, right: DiffResult, keys: List[str]) -> DiffResult:
    """Return rows from *right* whose key is **not** present in *left*."""
    return left_only(right, left, keys)


def outer(
    left: DiffResult,
    right: DiffResult,
    keys: List[str],
) -> Tuple[DiffResult, DiffResult, DiffResult]:
    """Full outer split: returns (inner, left_only, right_only) triple.

    Each element is a :class:`~sqlsift.diff.DiffResult`.
    """
    return (
        inner(left, right, keys),
        left_only(left, right, keys),
        right_only(left, right, keys),
    )
