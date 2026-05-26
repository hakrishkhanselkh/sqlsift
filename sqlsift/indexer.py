"""sqlsift.indexer — build lookup indexes over DiffResult rows for fast key-based access."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .diff import DiffResult, RowDiff


def _row_key(row: RowDiff, key_columns: List[str]) -> Tuple:
    """Return a hashable tuple of key-column values from row.before or row.after."""
    source = row.after if row.after is not None else row.before
    if source is None:
        return ()
    return tuple(source.get(col) for col in key_columns)


def build(result: DiffResult, key_columns: List[str]) -> Dict[Tuple, RowDiff]:
    """Return a dict mapping key tuples to RowDiff objects.

    If multiple rows share the same key the last one wins.
    """
    index: Dict[Tuple, RowDiff] = {}
    for row in result.diffs:
        k = _row_key(row, key_columns)
        index[k] = row
    return index


def lookup(
    result: DiffResult,
    key_columns: List[str],
    key_values: Dict[str, Any],
) -> Optional[RowDiff]:
    """Return the first RowDiff whose key matches *key_values*, or None."""
    index = build(result, key_columns)
    needle = tuple(key_values.get(col) for col in key_columns)
    return index.get(needle)


def group_by_key(
    result: DiffResult, key_columns: List[str]
) -> Dict[Tuple, List[RowDiff]]:
    """Return a dict mapping key tuples to *lists* of RowDiff objects.

    Useful when duplicates are expected (e.g. after a merge).
    """
    groups: Dict[Tuple, List[RowDiff]] = {}
    for row in result.diffs:
        k = _row_key(row, key_columns)
        groups.setdefault(k, []).append(row)
    return groups


def key_set(result: DiffResult, key_columns: List[str]) -> set:
    """Return the set of all key tuples present in *result*."""
    return {_row_key(row, key_columns) for row in result.diffs}


def missing_keys(
    result: DiffResult,
    key_columns: List[str],
    expected_keys: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Return entries from *expected_keys* that are absent in *result*."""
    present = key_set(result, key_columns)
    missing = []
    for kv in expected_keys:
        needle = tuple(kv.get(col) for col in key_columns)
        if needle not in present:
            missing.append(kv)
    return missing
