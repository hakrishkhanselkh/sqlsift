"""sqlsift.profiler — compute per-column value profiles from a DiffResult."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .diff import DiffResult, RowDiff


@dataclass
class ColumnProfile:
    """Basic value profile for a single column across all diff rows."""

    column: str
    total: int = 0
    null_count: int = 0
    unique_values: int = 0
    top_values: List[tuple] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "column": self.column,
            "total": self.total,
            "null_count": self.null_count,
            "null_rate": round(self.null_count / self.total, 4) if self.total else 0.0,
            "unique_values": self.unique_values,
            "top_values": self.top_values,
        }


def _collect_values(rows: List[RowDiff], column: str) -> List[Any]:
    """Extract raw values for *column* from each row's 'row' dict."""
    values = []
    for rd in rows:
        if column in rd.row:
            values.append(rd.row[column])
    return values


def profile_column(result: DiffResult, column: str, top_n: int = 5) -> ColumnProfile:
    """Return a :class:`ColumnProfile` for *column* over all rows in *result*."""
    rows = result.diffs
    values = _collect_values(rows, column)
    counter: Counter = Counter()
    null_count = 0
    for v in values:
        if v is None:
            null_count += 1
        else:
            counter[v] += 1
    top = counter.most_common(top_n)
    return ColumnProfile(
        column=column,
        total=len(values),
        null_count=null_count,
        unique_values=len(counter),
        top_values=top,
    )


def profile_result(
    result: DiffResult,
    columns: Optional[List[str]] = None,
    top_n: int = 5,
) -> Dict[str, ColumnProfile]:
    """Return a mapping of column name → :class:`ColumnProfile` for every
    column found in *result* (or the explicit *columns* list)."""
    if not result.diffs:
        return {}
    if columns is None:
        seen: Dict[str, None] = {}
        for rd in result.diffs:
            for k in rd.row:
                seen[k] = None
        columns = list(seen)
    return {col: profile_column(result, col, top_n=top_n) for col in columns}
