"""Group DiffResult rows by column values for segmented analysis."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

from .diff import DiffResult, RowDiff


def by_column(result: DiffResult, column: str) -> Dict[str, DiffResult]:
    """Partition diffs into sub-results keyed by the value of *column*.

    Rows where the column is absent are grouped under the key ``"<missing>"``.

    Args:
        result: The source :class:`~sqlsift.diff.DiffResult`.
        column: Column name to group by.

    Returns:
        A dict mapping each distinct column value (as a string) to a
        :class:`~sqlsift.diff.DiffResult` containing only the matching rows.
    """
    buckets: Dict[str, List[RowDiff]] = defaultdict(list)
    for row in result.diffs:
        record = row.left or row.right or {}
        raw = record.get(column, "<missing>")
        buckets[str(raw)].append(row)
    return {
        key: DiffResult(diffs=rows) for key, rows in sorted(buckets.items())
    }


def by_columns(
    result: DiffResult, columns: List[str]
) -> Dict[Tuple[str, ...], DiffResult]:
    """Partition diffs by a *composite* set of column values.

    Args:
        result: The source :class:`~sqlsift.diff.DiffResult`.
        columns: Ordered list of column names forming the composite group key.

    Returns:
        A dict mapping each distinct value-tuple to a
        :class:`~sqlsift.diff.DiffResult`.
    """
    buckets: Dict[Tuple[str, ...], List[RowDiff]] = defaultdict(list)
    for row in result.diffs:
        record = row.left or row.right or {}
        key = tuple(str(record.get(col, "<missing>")) for col in columns)
        buckets[key].append(row)
    return {
        key: DiffResult(diffs=rows) for key, rows in sorted(buckets.items())
    }


def counts_by_column(result: DiffResult, column: str) -> Dict[str, int]:
    """Return the number of diffs per distinct value of *column*.

    Args:
        result: The source :class:`~sqlsift.diff.DiffResult`.
        column: Column name to count by.

    Returns:
        A dict mapping each column value string to its diff count.
    """
    return {
        key: len(sub.diffs)
        for key, sub in by_column(result, column).items()
    }
