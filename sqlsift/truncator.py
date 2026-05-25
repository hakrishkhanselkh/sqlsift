"""truncator.py – utilities for truncating DiffResult sets by count or fraction."""

from __future__ import annotations

from typing import Optional

from sqlsift.diff import DiffResult, RowDiff


def by_count(result: DiffResult, n: int, *, kind: Optional[str] = None) -> DiffResult:
    """Return a new DiffResult containing at most *n* rows.

    If *kind* is given (``'added'``, ``'removed'``, or ``'modified'``), only
    rows of that kind count toward the limit; other rows are kept as-is.
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")

    if kind is not None and kind not in ("added", "removed", "modified"):
        raise ValueError("kind must be 'added', 'removed', or 'modified'")

    kept: list[RowDiff] = []
    seen = 0
    for row in result.diffs:
        if kind is None or row.kind == kind:
            if seen >= n:
                continue
            seen += 1
        kept.append(row)

    return DiffResult(diffs=kept, key_columns=result.key_columns)


def by_fraction(result: DiffResult, fraction: float, *, kind: Optional[str] = None) -> DiffResult:
    """Return a new DiffResult keeping *fraction* of rows (0.0–1.0).

    If *kind* is given, the fraction applies only to rows of that kind.
    """
    if not (0.0 <= fraction <= 1.0):
        raise ValueError("fraction must be between 0.0 and 1.0")

    if kind is not None and kind not in ("added", "removed", "modified"):
        raise ValueError("kind must be 'added', 'removed', or 'modified'")

    if kind is None:
        total = len(result.diffs)
    else:
        total = sum(1 for r in result.diffs if r.kind == kind)

    n = int(total * fraction)
    return by_count(result, n, kind=kind)


def drop_beyond(result: DiffResult, limit: int) -> DiffResult:
    """Hard-cap the result to *limit* rows total, regardless of kind."""
    return by_count(result, limit)
