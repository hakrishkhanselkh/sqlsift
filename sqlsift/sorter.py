"""Utilities for sorting DiffResult rows by key or column values."""

from typing import List, Optional, Sequence

from sqlsift.diff import DiffResult, RowDiff


def by_key(result: DiffResult, reverse: bool = False) -> DiffResult:
    """Return a new DiffResult with diffs sorted by their row key.

    Keys are compared lexicographically after converting each element to str
    so that mixed-type keys remain sortable.

    Args:
        result:  The source DiffResult.
        reverse: If True, sort in descending order.

    Returns:
        A new DiffResult whose ``diffs`` list is sorted by key.
    """
    sorted_diffs: List[RowDiff] = sorted(
        result.diffs,
        key=lambda d: tuple(str(k) for k in d.key),
        reverse=reverse,
    )
    return DiffResult(diffs=sorted_diffs)


def by_column(result: DiffResult, column: str, reverse: bool = False) -> DiffResult:
    """Return a new DiffResult sorted by the value of *column* in the old or
    new row snapshot.

    For *added* rows the new-row value is used; for *removed* rows the old-row
    value is used; for *modified* rows the old-row value is used.  Rows where
    the column is absent are sorted last (or first when *reverse* is True).

    Args:
        result: The source DiffResult.
        column: Column name to sort by.
        reverse: If True, sort in descending order.

    Returns:
        A new DiffResult whose ``diffs`` list is sorted by the given column.
    """

    _SENTINEL = object()

    def _sort_key(d: RowDiff):
        row = d.new_row if d.new_row is not None else d.old_row
        if row is None:
            return (1, None)
        val = row.get(column, _SENTINEL)
        if val is _SENTINEL:
            return (1, None)
        try:
            return (0, val)
        except TypeError:
            return (0, str(val))

    sorted_diffs: List[RowDiff] = sorted(
        result.diffs,
        key=_sort_key,
        reverse=reverse,
    )
    return DiffResult(diffs=sorted_diffs)


def by_kind(result: DiffResult, order: Optional[Sequence[str]] = None) -> DiffResult:
    """Return a new DiffResult grouped by diff kind.

    Args:
        result: The source DiffResult.
        order:  Sequence of kind strings defining the group order.  Defaults
                to ``["added", "removed", "modified"]``.

    Returns:
        A new DiffResult whose ``diffs`` list is grouped by kind.
    """
    if order is None:
        order = ["added", "removed", "modified"]

    rank = {kind: idx for idx, kind in enumerate(order)}
    default_rank = len(order)

    sorted_diffs: List[RowDiff] = sorted(
        result.diffs,
        key=lambda d: rank.get(d.kind, default_rank),
    )
    return DiffResult(diffs=sorted_diffs)
