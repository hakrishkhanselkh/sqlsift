"""sqlsift.windower — sliding-window views over a DiffResult.

Functions
---------
by_index(result, size, step=1)
    Yield successive DiffResult windows of `size` rows.
by_key_range(result, key_col, start, end)
    Return rows whose key column value falls in [start, end].
rolling_counts(result, size, step=1)
    Yield (window_index, counts_dict) for each window.
"""

from __future__ import annotations

from typing import Generator, Any

from sqlsift.diff import DiffResult


def by_index(
    result: DiffResult,
    size: int,
    step: int = 1,
) -> Generator[DiffResult, None, None]:
    """Yield DiffResult windows of *size* rows, advancing by *step*."""
    if size <= 0:
        raise ValueError("size must be a positive integer")
    if step <= 0:
        raise ValueError("step must be a positive integer")

    rows = result.diffs
    i = 0
    while i < len(rows):
        window = rows[i : i + size]
        yield DiffResult(diffs=window)
        i += step


def by_key_range(
    result: DiffResult,
    key_col: str,
    start: Any,
    end: Any,
) -> DiffResult:
    """Return a DiffResult containing only rows where key_col is in [start, end]."""

    def _get(row_diff):
        row = row_diff.new_row if row_diff.new_row is not None else row_diff.old_row
        return row.get(key_col)

    filtered = [
        d
        for d in result.diffs
        if _get(d) is not None and start <= _get(d) <= end
    ]
    return DiffResult(diffs=filtered)


def rolling_counts(
    result: DiffResult,
    size: int,
    step: int = 1,
) -> Generator[tuple[int, dict[str, int]], None, None]:
    """Yield (window_index, {added, removed, modified}) for each window."""
    for idx, window in enumerate(by_index(result, size, step)):
        counts = {
            "added": len(window.added()),
            "removed": len(window.removed()),
            "modified": len(window.modified()),
        }
        yield idx, counts
