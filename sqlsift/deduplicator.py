"""Deduplication utilities for DiffResult sets.

Provides functions to detect and remove duplicate RowDiff entries
based on key identity or full row equality.
"""

from __future__ import annotations

from typing import List, Tuple

from .diff import DiffResult, RowDiff


def _row_key(row: dict, key_columns: List[str]) -> Tuple:
    """Extract a hashable key tuple from a row dict."""
    return tuple(row.get(col) for col in key_columns)


def by_key(result: DiffResult, key_columns: List[str]) -> DiffResult:
    """Remove duplicate RowDiff entries that share the same key columns.

    When duplicates exist, the first occurrence is kept.

    Args:
        result: The DiffResult to deduplicate.
        key_columns: Column names that form the identity key.

    Returns:
        A new DiffResult with duplicate-key rows removed.
    """
    seen: set = set()
    unique: List[RowDiff] = []
    for diff in result.diffs:
        k = (diff.kind, _row_key(diff.row, key_columns))
        if k not in seen:
            seen.add(k)
            unique.append(diff)
    return DiffResult(unique)


def by_row(result: DiffResult) -> DiffResult:
    """Remove RowDiff entries that are completely identical (kind + row + delta).

    Args:
        result: The DiffResult to deduplicate.

    Returns:
        A new DiffResult with fully duplicate rows removed.
    """
    seen: set = set()
    unique: List[RowDiff] = []
    for diff in result.diffs:
        delta_key = tuple(sorted(diff.delta.items())) if diff.delta else ()
        row_key = tuple(sorted(diff.row.items()))
        fingerprint = (diff.kind, row_key, delta_key)
        if fingerprint not in seen:
            seen.add(fingerprint)
            unique.append(diff)
    return DiffResult(unique)


def duplicates(result: DiffResult, key_columns: List[str]) -> DiffResult:
    """Return only the RowDiff entries that are duplicates by key.

    The first occurrence of each key is excluded; subsequent occurrences
    are considered duplicates and are returned.

    Args:
        result: The DiffResult to inspect.
        key_columns: Column names that form the identity key.

    Returns:
        A new DiffResult containing only the duplicate rows.
    """
    seen: set = set()
    dupes: List[RowDiff] = []
    for diff in result.diffs:
        k = (diff.kind, _row_key(diff.row, key_columns))
        if k in seen:
            dupes.append(diff)
        else:
            seen.add(k)
    return DiffResult(dupes)
