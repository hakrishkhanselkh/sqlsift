"""threshold.py – filter DiffResult rows by numeric change magnitude."""
from __future__ import annotations

from typing import List, Optional

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.comparator import numeric_drift


def _extract_numeric(row: RowDiff, column: str) -> Optional[float]:
    """Return the numeric *after* value for *column* in an added/modified row."""
    if row.kind == "added" and row.after is not None:
        try:
            return float(row.after.get(column, 0))
        except (TypeError, ValueError):
            return None
    if row.kind == "modified" and row.delta and column in row.delta:
        try:
            return float(row.delta[column]["after"])
        except (TypeError, ValueError):
            return None
    return None


def by_absolute_change(
    result: DiffResult, column: str, min_change: float
) -> DiffResult:
    """Keep modified rows where |after - before| >= *min_change* for *column*."""
    kept: List[RowDiff] = []
    drift_map = {tuple(r["key"]): r["diff"] for r in numeric_drift(result, column)}
    for row in result.diffs:
        if row.kind != "modified":
            kept.append(row)
            continue
        diff_val = drift_map.get(tuple(row.key))
        if diff_val is not None and abs(diff_val) >= min_change:
            kept.append(row)
    return DiffResult(diffs=kept)


def by_relative_change(
    result: DiffResult, column: str, min_ratio: float
) -> DiffResult:
    """Keep modified rows where |change / before| >= *min_ratio* for *column*."""
    kept: List[RowDiff] = []
    for row in result.diffs:
        if row.kind != "modified":
            kept.append(row)
            continue
        if row.delta is None or column not in row.delta:
            continue
        try:
            before = float(row.delta[column]["before"])
            after = float(row.delta[column]["after"])
            if before == 0:
                continue
            if abs((after - before) / before) >= min_ratio:
                kept.append(row)
        except (TypeError, ValueError):
            continue
    return DiffResult(diffs=kept)


def above_value(
    result: DiffResult, column: str, threshold: float
) -> DiffResult:
    """Keep added/modified rows where the *after* value for *column* > *threshold*."""
    kept: List[RowDiff] = []
    for row in result.diffs:
        if row.kind == "removed":
            kept.append(row)
            continue
        val = _extract_numeric(row, column)
        if val is not None and val > threshold:
            kept.append(row)
    return DiffResult(diffs=kept)
