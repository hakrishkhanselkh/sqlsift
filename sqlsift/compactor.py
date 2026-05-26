"""compactor.py – collapse a DiffResult by merging rows that share the same key.

Useful when multiple diff passes produce overlapping results and you want a
single canonical view: the last-seen change for each key wins.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from sqlsift.diff import DiffResult, RowDiff


def _row_key(row: RowDiff, key_columns: Sequence[str]) -> Tuple:
    """Return a hashable key extracted from *row.before* or *row.after*."""
    source = row.after if row.after is not None else row.before
    if source is None:
        return ()
    return tuple(source.get(col) for col in key_columns)


def compact(
    result: DiffResult,
    key_columns: Sequence[str],
    *,
    keep: str = "last",
) -> DiffResult:
    """Deduplicate *result* so each logical key appears at most once.

    Parameters
    ----------
    result:
        Source :class:`~sqlsift.diff.DiffResult`.
    key_columns:
        Columns that together form the logical primary key.
    keep:
        ``"last"`` (default) retains the final occurrence of each key;
        ``"first"`` retains the first occurrence.

    Returns
    -------
    DiffResult
        A new result containing only the winning row per key.
    """
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")

    seen: dict[Tuple, RowDiff] = {}
    for row in result.diffs:
        k = _row_key(row, key_columns)
        if keep == "first" and k in seen:
            continue
        seen[k] = row

    return DiffResult(diffs=list(seen.values()))


def merge_results(
    results: Iterable[DiffResult],
    key_columns: Sequence[str],
    *,
    keep: str = "last",
) -> DiffResult:
    """Combine multiple :class:`~sqlsift.diff.DiffResult` objects then compact.

    Parameters
    ----------
    results:
        Iterable of results to combine before compaction.
    key_columns:
        Columns that form the logical primary key.
    keep:
        ``"last"`` or ``"first"`` – which occurrence wins when a key repeats.

    Returns
    -------
    DiffResult
        Merged and compacted result.
    """
    all_diffs: List[RowDiff] = []
    for r in results:
        all_diffs.extend(r.diffs)
    combined = DiffResult(diffs=all_diffs)
    return compact(combined, key_columns, keep=keep)
