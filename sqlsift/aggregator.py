"""sqlsift.aggregator — aggregate numeric columns across a DiffResult."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

from sqlsift.diff import DiffResult, RowDiff


def _numeric(value: Any) -> Optional[float]:
    """Return *value* as float, or None if it cannot be converted."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass
class ColumnAggregate:
    """Aggregate statistics for a single column across all diff rows."""

    column: str
    count: int = 0
    total: float = 0.0
    minimum: Optional[float] = None
    maximum: Optional[float] = None

    @property
    def mean(self) -> Optional[float]:
        return self.total / self.count if self.count else None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "column": self.column,
            "count": self.count,
            "sum": self.total,
            "mean": self.mean,
            "min": self.minimum,
            "max": self.maximum,
        }


def _value_for_row(row_diff: RowDiff, column: str) -> Optional[float]:
    """Extract the *after* value for *column* from a RowDiff."""
    if row_diff.kind == "added":
        return _numeric(row_diff.row.get(column))
    if row_diff.kind == "removed":
        return _numeric(row_diff.row.get(column))
    if row_diff.kind == "modified":
        # prefer the new (right-hand) value stored in delta
        delta = row_diff.delta or {}
        if column in delta:
            return _numeric(delta[column][1])
        return _numeric(row_diff.row.get(column))
    return None


def aggregate(
    result: DiffResult,
    columns: Sequence[str],
    *,
    kinds: Sequence[str] = ("added", "removed", "modified"),
) -> Dict[str, ColumnAggregate]:
    """Compute per-column numeric aggregates over *result*.

    Parameters
    ----------
    result:
        The :class:`~sqlsift.diff.DiffResult` to inspect.
    columns:
        Column names to aggregate.
    kinds:
        Restrict aggregation to rows whose kind is in this sequence.

    Returns
    -------
    dict mapping each column name to a :class:`ColumnAggregate`.
    """
    stats: Dict[str, ColumnAggregate] = {col: ColumnAggregate(column=col) for col in columns}

    for row_diff in result.diffs:
        if row_diff.kind not in kinds:
            continue
        for col in columns:
            val = _value_for_row(row_diff, col)
            if val is None:
                continue
            agg = stats[col]
            agg.count += 1
            agg.total += val
            agg.minimum = val if agg.minimum is None else min(agg.minimum, val)
            agg.maximum = val if agg.maximum is None else max(agg.maximum, val)

    return stats


def summary_table(result: DiffResult, columns: Sequence[str]) -> List[Dict[str, Any]]:
    """Return a list of aggregate dicts, one per column."""
    return [agg.as_dict() for agg in aggregate(result, columns).values()]
