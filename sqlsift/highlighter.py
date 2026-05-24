"""highlighter.py – highlight changed columns in modified rows."""
from __future__ import annotations

from typing import Dict, Iterable, List, Set

from sqlsift.diff import DiffResult, RowDiff


def changed_columns(diff: RowDiff) -> Set[str]:
    """Return the set of column names that differ in a modified row.

    For *added* or *removed* rows every column is considered changed.
    Returns an empty set when the row has no delta.
    """
    if diff.delta is None:
        if diff.kind in ("added", "removed"):
            return set(diff.row.keys())
        return set()
    return {col for col, (old, new) in diff.delta.items() if old != new}


def highlight_row(
    diff: RowDiff,
    marker: str = "**",
) -> Dict[str, str]:
    """Return a dict where changed column values are wrapped with *marker*.

    Unchanged values are returned as plain strings.  The result is always
    a ``str``-valued mapping suitable for display purposes.
    """
    cols = changed_columns(diff)
    return {
        k: f"{marker}{v}{marker}" if k in cols else str(v)
        for k, v in diff.row.items()
    }


def highlight_result(
    result: DiffResult,
    marker: str = "**",
    kinds: Iterable[str] = ("added", "removed", "modified"),
) -> List[Dict[str, str]]:
    """Apply :func:`highlight_row` to every diff in *result*.

    Only rows whose *kind* is in *kinds* are included; identical rows are
    skipped by default.
    """
    allowed = set(kinds)
    return [
        highlight_row(d, marker=marker)
        for d in result.diffs
        if d.kind in allowed
    ]


def columns_changed_in_result(result: DiffResult) -> Dict[str, int]:
    """Return a mapping of column name -> number of rows where it changed."""
    counts: Dict[str, int] = {}
    for diff in result.diffs:
        for col in changed_columns(diff):
            counts[col] = counts.get(col, 0) + 1
    return counts


def most_changed_columns(result: DiffResult, top_n: int = 5) -> List[str]:
    """Return the *top_n* column names most frequently changed across all diffs.

    Columns are ranked by how many rows they appear as changed in, descending.
    Useful for quickly surfacing which fields are most volatile between two
    versions of a dataset.

    Args:
        result: The diff result to analyse.
        top_n:  Maximum number of column names to return.  Defaults to 5.

    Returns:
        A list of column names sorted by change frequency, highest first.
    """
    counts = columns_changed_in_result(result)
    return sorted(counts, key=lambda col: counts[col], reverse=True)[:top_n]
