"""Utilities for loading query result sets from various sources."""

from __future__ import annotations

import csv
import io
import json
from typing import Any, Iterable, Sequence

Row = dict[str, Any]


def from_dicts(rows: Iterable[dict[str, Any]]) -> list[Row]:
    """Load rows directly from an iterable of dicts."""
    return [dict(row) for row in rows]


def from_csv(source: str | io.TextIOBase, *, delimiter: str = ",") -> list[Row]:
    """Load rows from a CSV string or file-like object.

    Args:
        source: A CSV-formatted string or an open text stream.
        delimiter: Field delimiter character (default ',').

    Returns:
        List of row dicts with string values as read from the CSV.
    """
    if isinstance(source, str):
        source = io.StringIO(source)
    reader = csv.DictReader(source, delimiter=delimiter)
    return [dict(row) for row in reader]


def from_json(source: str | io.TextIOBase) -> list[Row]:
    """Load rows from a JSON array of objects.

    Args:
        source: A JSON string or file-like object containing an array of objects.

    Returns:
        List of row dicts.

    Raises:
        ValueError: If the top-level JSON value is not a list.
    """
    if not isinstance(source, str):
        source = source.read()
    data = json.loads(source)
    if not isinstance(data, list):
        raise ValueError("JSON source must be a top-level array of objects.")
    return [dict(row) for row in data]


def from_tuples(
    rows: Iterable[tuple[Any, ...]],
    columns: Sequence[str],
) -> list[Row]:
    """Load rows from an iterable of tuples paired with column names.

    Args:
        rows: Iterable of tuples where each tuple represents one row.
        columns: Ordered sequence of column names matching the tuple positions.

    Returns:
        List of row dicts.

    Raises:
        ValueError: If a tuple length does not match the number of columns.
    """
    result: list[Row] = []
    for tup in rows:
        if len(tup) != len(columns):
            raise ValueError(
                f"Row {tup!r} has {len(tup)} values but {len(columns)} columns were given."
            )
        result.append(dict(zip(columns, tup)))
    return result
