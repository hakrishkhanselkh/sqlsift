"""comparator.py – column-level value comparison utilities for DiffResult rows."""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from sqlsift.diff import DiffResult, RowDiff


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _coerce(value: Any) -> Any:
    """Attempt lightweight numeric coercion so '1' == 1 comparisons work."""
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
    return value


def values_equal(a: Any, b: Any, *, coerce: bool = False) -> bool:
    """Return True when *a* and *b* should be considered equal."""
    if a == b:
        return True
    if coerce:
        return _coerce(a) == _coerce(b)
    return False


# ---------------------------------------------------------------------------
# Column-level comparison
# ---------------------------------------------------------------------------

def column_delta(row: RowDiff, column: str) -> Optional[Dict[str, Any]]:
    """Return {before, after} for *column* in a modified row, or None."""
    if row.kind != "modified" or row.delta is None:
        return None
    if column not in row.delta:
        return None
    return {"before": row.delta[column]["before"], "after": row.delta[column]["after"]}


def changed_in_column(result: DiffResult, column: str) -> List[RowDiff]:
    """Return all modified rows where *column* has changed."""
    out: List[RowDiff] = []
    for row in result.diffs:
        if row.kind == "modified" and row.delta and column in row.delta:
            out.append(row)
    return out


# ---------------------------------------------------------------------------
# Cross-row comparison
# ---------------------------------------------------------------------------

def compare_column(
    result: DiffResult,
    column: str,
    predicate: Optional[Callable[[Any, Any], bool]] = None,
) -> List[Dict[str, Any]]:
    """For every modified row return a record describing the column change.

    If *predicate* is given only rows where ``predicate(before, after)`` is
    True are included.
    """
    records: List[Dict[str, Any]] = []
    for row in changed_in_column(result, column):
        delta = column_delta(row, column)
        if delta is None:
            continue
        before, after = delta["before"], delta["after"]
        if predicate is not None and not predicate(before, after):
            continue
        records.append({"key": row.key, "column": column, "before": before, "after": after})
    return records


def numeric_drift(
    result: DiffResult, column: str, *, coerce: bool = True
) -> List[Dict[str, Any]]:
    """Return rows where *column* changed numerically, including the diff."""
    records: List[Dict[str, Any]] = []
    for row in changed_in_column(result, column):
        delta = column_delta(row, column)
        if delta is None:
            continue
        try:
            before = float(delta["before"]) if coerce else delta["before"]
            after = float(delta["after"]) if coerce else delta["after"]
            records.append({
                "key": row.key,
                "column": column,
                "before": before,
                "after": after,
                "diff": after - before,
            })
        except (TypeError, ValueError):
            continue
    return records
