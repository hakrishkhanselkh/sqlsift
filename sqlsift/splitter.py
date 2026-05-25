"""splitter.py — split a DiffResult into multiple DiffResults by a column value or a size limit."""

from __future__ import annotations

from typing import Dict, List, Optional

from sqlsift.diff import DiffResult, RowDiff


def by_column_value(result: DiffResult, column: str) -> Dict[str, DiffResult]:
    """Partition *result* into separate DiffResults keyed by the value of *column*.

    Rows where *column* is absent in both the left and right row are grouped
    under the string key ``"__missing__"``.

    Args:
        result: The source DiffResult to split.
        column: Column name to partition on.

    Returns:
        A dict mapping each distinct value (as a string) to a DiffResult.
    """
    buckets: Dict[str, List[RowDiff]] = {}

    for row_diff in result.diffs:
        row = row_diff.left or row_diff.right or {}
        if column in row:
            key = str(row[column])
        else:
            key = "__missing__"
        buckets.setdefault(key, []).append(row_diff)

    return {k: DiffResult(diffs=v) for k, v in buckets.items()}


def by_size(result: DiffResult, chunk_size: int) -> List[DiffResult]:
    """Split *result* into consecutive chunks of at most *chunk_size* diffs.

    Args:
        result: The source DiffResult to split.
        chunk_size: Maximum number of RowDiff entries per chunk.

    Returns:
        A list of DiffResult objects; the last chunk may be smaller than
        *chunk_size*.

    Raises:
        ValueError: If *chunk_size* is less than 1.
    """
    if chunk_size < 1:
        raise ValueError(f"chunk_size must be >= 1, got {chunk_size}")

    diffs = result.diffs
    return [
        DiffResult(diffs=diffs[i : i + chunk_size])
        for i in range(0, max(len(diffs), 1), chunk_size)
        if diffs[i : i + chunk_size]
    ] or [DiffResult(diffs=[])]


def by_predicate(result: DiffResult, predicate) -> tuple[DiffResult, DiffResult]:
    """Split *result* into two DiffResults: rows that satisfy *predicate* and those that do not.

    Args:
        result: The source DiffResult to split.
        predicate: A callable ``(RowDiff) -> bool``.

    Returns:
        A tuple ``(matched, unmatched)`` where *matched* contains rows for
        which *predicate* returned ``True``.
    """
    matched: List[RowDiff] = []
    unmatched: List[RowDiff] = []

    for row_diff in result.diffs:
        if predicate(row_diff):
            matched.append(row_diff)
        else:
            unmatched.append(row_diff)

    return DiffResult(diffs=matched), DiffResult(diffs=unmatched)
