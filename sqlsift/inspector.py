"""inspector.py — introspect DiffResult structure and column metadata."""

from __future__ import annotations

from typing import Any

from sqlsift.diff import DiffResult, RowDiff


def column_names(result: DiffResult) -> list[str]:
    """Return sorted list of all column names seen across all rows."""
    cols: set[str] = set()
    for row in result.diffs:
        cols.update(row.row.keys())
        if row.delta:
            cols.update(row.delta.keys())
    return sorted(cols)


def key_columns(result: DiffResult) -> list[str]:
    """Return the key columns inferred from result.key_columns, or [] if absent."""
    return list(getattr(result, "key_columns", []) or [])


def row_count(result: DiffResult) -> dict[str, int]:
    """Return counts broken down by diff kind."""
    counts: dict[str, int] = {"added": 0, "removed": 0, "modified": 0}
    for row in result.diffs:
        kind = row.kind
        if kind in counts:
            counts[kind] += 1
    return counts


def has_column(result: DiffResult, column: str) -> bool:
    """Return True if *column* appears in any row of *result*."""
    return column in column_names(result)


def sample_values(result: DiffResult, column: str, limit: int = 5) -> list[Any]:
    """Return up to *limit* distinct values for *column* from result rows."""
    seen: list[Any] = []
    for row in result.diffs:
        val = row.row.get(column)
        if val not in seen:
            seen.append(val)
        if len(seen) >= limit:
            break
    return seen


def schema(result: DiffResult) -> dict[str, str]:
    """Infer a simple type name for each column based on observed values."""
    type_map: dict[str, str] = {}
    for col in column_names(result):
        for row in result.diffs:
            val = row.row.get(col)
            if val is None and row.delta:
                pair = row.delta.get(col)
                val = pair[1] if isinstance(pair, (list, tuple)) and len(pair) == 2 else None
            if val is not None:
                type_map[col] = type(val).__name__
                break
        else:
            type_map[col] = "unknown"
    return type_map


def inspect(result: DiffResult) -> dict[str, Any]:
    """Return a full inspection summary of *result*."""
    return {
        "row_count": row_count(result),
        "total": len(result.diffs),
        "columns": column_names(result),
        "key_columns": key_columns(result),
        "schema": schema(result),
    }
