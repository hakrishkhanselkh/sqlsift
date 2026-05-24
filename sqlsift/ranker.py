"""ranker.py — rank rows in a DiffResult by a numeric column or computed score."""

from __future__ import annotations

from typing import Callable, List, Optional

from sqlsift.diff import DiffResult, RowDiff


def _get_value(row: dict, column: str) -> float:
    """Return a float value for *column* from *row*, defaulting to 0.0."""
    try:
        return float(row.get(column, 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def by_column(
    result: DiffResult,
    column: str,
    *,
    ascending: bool = False,
    limit: Optional[int] = None,
) -> List[RowDiff]:
    """Rank diffs by the absolute change in *column* between old and new.

    For added rows the new value is used; for removed rows the old value.
    For modified rows the absolute delta is used.
    """
    def _score(rd: RowDiff) -> float:
        if rd.kind == "modified":
            old_val = _get_value(rd.old_row or {}, column)
            new_val = _get_value(rd.new_row or {}, column)
            return abs(new_val - old_val)
        if rd.kind == "added":
            return _get_value(rd.new_row or {}, column)
        if rd.kind == "removed":
            return _get_value(rd.old_row or {}, column)
        return 0.0

    ranked = sorted(result.diffs, key=_score, reverse=not ascending)
    if limit is not None:
        ranked = ranked[:limit]
    return ranked


def by_score(
    result: DiffResult,
    score_fn: Callable[[RowDiff], float],
    *,
    ascending: bool = False,
    limit: Optional[int] = None,
) -> List[RowDiff]:
    """Rank diffs using an arbitrary *score_fn* callable.

    *score_fn* receives a :class:`~sqlsift.diff.RowDiff` and must return a
    numeric value.  Higher scores appear first when *ascending* is ``False``.
    """
    ranked = sorted(result.diffs, key=score_fn, reverse=not ascending)
    if limit is not None:
        ranked = ranked[:limit]
    return ranked


def top_n(
    result: DiffResult,
    column: str,
    n: int = 10,
) -> List[RowDiff]:
    """Convenience wrapper — return the top *n* diffs ranked by *column*."""
    return by_column(result, column, ascending=False, limit=n)


def bottom_n(
    result: DiffResult,
    column: str,
    n: int = 10,
) -> List[RowDiff]:
    """Convenience wrapper — return the bottom *n* diffs ranked by *column*."""
    return by_column(result, column, ascending=True, limit=n)
