"""mapper.py — transform DiffResult rows by applying column-level mapping functions."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Optional

from sqlsift.diff import DiffResult, RowDiff

_MapSpec = Dict[str, Callable[[Any], Any]]


def _apply_map(row: Dict[str, Any], spec: _MapSpec) -> Dict[str, Any]:
    """Return a copy of *row* with mapped values applied."""
    result = dict(row)
    for col, fn in spec.items():
        if col in result:
            result[col] = fn(result[col])
    return result


def map_rows(result: DiffResult, spec: _MapSpec) -> DiffResult:
    """Apply *spec* mapping functions to every row in *result*.

    Both ``row`` and, for modified diffs, each side of ``delta`` are mapped.
    """
    mapped: list[RowDiff] = []
    for diff in result.diffs:
        new_row = _apply_map(diff.row, spec)
        new_delta: Optional[Dict[str, Any]] = None
        if diff.delta is not None:
            new_delta = {
                col: (
                    _apply_map({col: before}, spec)[col],
                    _apply_map({col: after}, spec)[col],
                )
                for col, (before, after) in diff.delta.items()
            }
        mapped.append(RowDiff(kind=diff.kind, key=diff.key, row=new_row, delta=new_delta))
    return DiffResult(diffs=mapped)


def rename_key(result: DiffResult, old: str, new: str) -> DiffResult:
    """Rename column *old* to *new* in every row and delta."""
    def _rename(row: Dict[str, Any]) -> Dict[str, Any]:
        r = dict(row)
        if old in r:
            r[new] = r.pop(old)
        return r

    renamed: list[RowDiff] = []
    for diff in result.diffs:
        new_row = _rename(diff.row)
        new_delta: Optional[Dict[str, Any]] = None
        if diff.delta is not None:
            new_delta = {
                (new if col == old else col): val
                for col, val in diff.delta.items()
            }
        renamed.append(RowDiff(kind=diff.kind, key=diff.key, row=new_row, delta=new_delta))
    return DiffResult(diffs=renamed)


def cast_column(result: DiffResult, column: str, dtype: type) -> DiffResult:
    """Cast *column* values to *dtype* across all rows."""
    return map_rows(result, {column: lambda v: dtype(v) if v is not None else v})
