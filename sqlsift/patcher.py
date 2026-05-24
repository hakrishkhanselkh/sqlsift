"""Generate SQL patch statements from diff results."""

from typing import Any, Dict, List, Optional
from sqlsift.diff import DiffResult, RowDiff


def _quote_value(value: Any) -> str:
    """Return a SQL-safe string representation of a value."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def _build_insert(table: str, row: Dict[str, Any]) -> str:
    columns = ", ".join(row.keys())
    values = ", ".join(_quote_value(v) for v in row.values())
    return f"INSERT INTO {table} ({columns}) VALUES ({values});"


def _build_delete(table: str, key_columns: List[str], row: Dict[str, Any]) -> str:
    conditions = " AND ".join(
        f"{col} = {_quote_value(row[col])}" for col in key_columns
    )
    return f"DELETE FROM {table} WHERE {conditions};"


def _build_update(
    table: str,
    key_columns: List[str],
    old_row: Dict[str, Any],
    new_row: Dict[str, Any],
) -> Optional[str]:
    changed = {
        col: new_row[col]
        for col in new_row
        if col not in key_columns and new_row.get(col) != old_row.get(col)
    }
    if not changed:
        return None
    set_clause = ", ".join(f"{col} = {_quote_value(val)}" for col, val in changed.items())
    conditions = " AND ".join(
        f"{col} = {_quote_value(old_row[col])}" for col in key_columns
    )
    return f"UPDATE {table} SET {set_clause} WHERE {conditions};"


def generate_patch(
    result: DiffResult,
    table: str,
    key_columns: Optional[List[str]] = None,
) -> List[str]:
    """Return a list of SQL statements that reconcile source -> target.

    Args:
        result:      The DiffResult produced by sqlsift.diff.diff().
        table:       Target table name used in generated SQL.
        key_columns: Columns that form the primary key. Defaults to
                     result.key_columns if not provided.

    Returns:
        A list of SQL statement strings (without a trailing newline).
    """
    keys = key_columns if key_columns is not None else list(result.key_columns)
    statements: List[str] = []

    for diff in result.diffs:
        if diff.kind == "added":
            statements.append(_build_insert(table, diff.right))  # type: ignore[arg-type]
        elif diff.kind == "removed":
            statements.append(_build_delete(table, keys, diff.left))  # type: ignore[arg-type]
        elif diff.kind == "modified":
            stmt = _build_update(table, keys, diff.left, diff.right)  # type: ignore[arg-type]
            if stmt:
                statements.append(stmt)

    return statements
