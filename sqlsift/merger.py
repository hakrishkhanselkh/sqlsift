"""merger.py — utilities for merging multiple DiffResult objects into one."""

from typing import List
from sqlsift.diff import DiffResult, RowDiff


def merge(*results: DiffResult) -> DiffResult:
    """Merge two or more DiffResult objects into a single DiffResult.

    Rows with the same key and kind are deduplicated; the first occurrence wins.
    Rows with the same key but conflicting kinds are included once per distinct
    (key, kind) pair so that callers can detect conflicts with ``conflicts()``.

    Args:
        *results: Two or more DiffResult instances to merge.

    Returns:
        A new DiffResult containing the combined rows.

    Raises:
        ValueError: If fewer than two results are supplied.
    """
    if len(results) < 2:
        raise ValueError("merge() requires at least two DiffResult arguments.")

    seen: dict = {}  # (key_tuple, kind) -> RowDiff
    ordered: List[RowDiff] = []

    for result in results:
        for row in result.diffs:
            key_tuple = tuple(sorted(row.key.items()))
            dedup_key = (key_tuple, row.kind)
            if dedup_key not in seen:
                seen[dedup_key] = row
                ordered.append(row)

    return DiffResult(diffs=ordered)


def conflicts(result: DiffResult) -> List[RowDiff]:
    """Return rows whose key appears with more than one diff kind.

    This is useful after calling ``merge()`` to detect rows that were
    classified differently across the source result sets.

    Args:
        result: A DiffResult, typically produced by ``merge()``.

    Returns:
        A list of RowDiff objects that share a key with at least one other
        RowDiff of a different kind.
    """
    from collections import defaultdict

    key_to_kinds: dict = defaultdict(set)
    key_to_rows: dict = defaultdict(list)

    for row in result.diffs:
        key_tuple = tuple(sorted(row.key.items()))
        key_to_kinds[key_tuple].add(row.kind)
        key_to_rows[key_tuple].append(row)

    conflicting: List[RowDiff] = []
    for key_tuple, kinds in key_to_kinds.items():
        if len(kinds) > 1:
            conflicting.extend(key_to_rows[key_tuple])

    return conflicting
