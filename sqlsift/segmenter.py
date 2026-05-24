"""sqlsift.segmenter — slice a DiffResult into named segments based on column value ranges or buckets."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from .diff import DiffResult, RowDiff


def by_column_value(
    result: DiffResult,
    column: str,
    *,
    source: str = "left",
) -> Dict[Any, DiffResult]:
    """Partition *result* into sub-results keyed by the distinct values of *column*.

    Parameters
    ----------
    result:  The DiffResult to segment.
    column:  Column name whose value is used as the segment key.
    source:  Which side of a modified row to read the column from (``"left"``
             or ``"right"``).

    Returns
    -------
    A dict mapping each distinct column value to a DiffResult containing only
    the rows that carry that value.  Rows where the column is absent are
    collected under the key ``None``.
    """
    if source not in ("left", "right"):
        raise ValueError("source must be 'left' or 'right'")

    buckets: Dict[Any, List[RowDiff]] = {}

    for row in result.diffs:
        data = row.left if source == "left" else row.right
        if data is None:
            # Fall back to whichever side exists
            data = row.left or row.right or {}
        value = data.get(column)  # type: ignore[union-attr]
        buckets.setdefault(value, []).append(row)

    return {
        key: DiffResult(diffs=rows) for key, rows in buckets.items()
    }


def by_predicate(
    result: DiffResult,
    predicates: Dict[str, Callable[[RowDiff], bool]],
    *,
    default_segment: Optional[str] = "other",
) -> Dict[str, DiffResult]:
    """Segment *result* using a mapping of *name → predicate* functions.

    Each row is assigned to the **first** segment whose predicate returns
    ``True``.  If no predicate matches and *default_segment* is not ``None``,
    the row is placed in that catch-all segment.

    Parameters
    ----------
    result:           The DiffResult to segment.
    predicates:       Ordered mapping of segment name to a callable that
                      accepts a RowDiff and returns bool.
    default_segment:  Name for unmatched rows.  Pass ``None`` to discard them.
    """
    buckets: Dict[str, List[RowDiff]] = {name: [] for name in predicates}
    if default_segment is not None:
        buckets.setdefault(default_segment, [])

    for row in result.diffs:
        matched = False
        for name, pred in predicates.items():
            if pred(row):
                buckets[name].append(row)
                matched = True
                break
        if not matched and default_segment is not None:
            buckets[default_segment].append(row)

    return {name: DiffResult(diffs=rows) for name, rows in buckets.items()}


def sizes(segments: Dict[Any, DiffResult]) -> Dict[Any, int]:
    """Return a dict mapping each segment key to the number of diffs it contains."""
    return {key: len(seg.diffs) for key, seg in segments.items()}
