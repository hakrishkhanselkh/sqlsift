"""transformer.py – apply column-level transformations to rows within a DiffResult."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional

from sqlsift.diff import DiffResult, RowDiff

_Transform = Callable[[Any], Any]


def _apply_transforms(
    row: Dict[str, Any],
    transforms: Dict[str, _Transform],
) -> Dict[str, Any]:
    """Return a shallow copy of *row* with named transforms applied."""
    result = dict(row)
    for col, fn in transforms.items():
        if col in result:
            result[col] = fn(result[col])
    return result


def transform_rows(
    diff_result: DiffResult,
    transforms: Dict[str, _Transform],
) -> DiffResult:
    """Apply *transforms* to every row (and delta) in *diff_result*.

    Parameters
    ----------
    diff_result:
        The source :class:`~sqlsift.diff.DiffResult`.
    transforms:
        Mapping of column name → callable that receives the current value and
        returns the transformed value.

    Returns
    -------
    DiffResult
        A new result with transformed rows; the original is not mutated.
    """
    new_diffs: List[RowDiff] = []
    for rd in diff_result.diffs:
        new_row = _apply_transforms(rd.row, transforms)
        new_delta: Optional[Dict[str, Any]] = None
        if rd.delta is not None:
            new_delta = {}
            for col, (old, new) in rd.delta.items():
                fn = transforms.get(col)
                new_delta[col] = (
                    fn(old) if fn is not None else old,
                    fn(new) if fn is not None else new,
                )
        new_diffs.append(RowDiff(kind=rd.kind, key=rd.key, row=new_row, delta=new_delta))
    return DiffResult(diffs=new_diffs)


def rename_columns(
    diff_result: DiffResult,
    rename_map: Dict[str, str],
) -> DiffResult:
    """Return a new :class:`~sqlsift.diff.DiffResult` with columns renamed.

    Parameters
    ----------
    diff_result:
        The source result.
    rename_map:
        Mapping of old column name → new column name.
    """
    def _rename(row: Dict[str, Any]) -> Dict[str, Any]:
        return {rename_map.get(k, k): v for k, v in row.items()}

    new_diffs: List[RowDiff] = []
    for rd in diff_result.diffs:
        new_row = _rename(rd.row)
        new_delta: Optional[Dict[str, Any]] = None
        if rd.delta is not None:
            new_delta = {rename_map.get(k, k): v for k, v in rd.delta.items()}
        new_diffs.append(RowDiff(kind=rd.kind, key=rd.key, row=new_row, delta=new_delta))
    return DiffResult(diffs=new_diffs)


def drop_columns(
    diff_result: DiffResult,
    columns: Iterable[str],
) -> DiffResult:
    """Return a new result with the specified *columns* removed from every row."""
    drop = set(columns)
    new_diffs: List[RowDiff] = []
    for rd in diff_result.diffs:
        new_row = {k: v for k, v in rd.row.items() if k not in drop}
        new_delta = (
            {k: v for k, v in rd.delta.items() if k not in drop}
            if rd.delta is not None
            else None
        )
        new_diffs.append(RowDiff(kind=rd.kind, key=rd.key, row=new_row, delta=new_delta))
    return DiffResult(diffs=new_diffs)
