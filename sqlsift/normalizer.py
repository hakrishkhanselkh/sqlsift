"""Normalizer: coerce and standardize values across DiffResult rows."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Optional

from sqlsift.diff import DiffResult, RowDiff


_Coercer = Callable[[Any], Any]


def _apply_coercers(
    row: Dict[str, Any],
    coercers: Dict[str, _Coercer],
) -> Dict[str, Any]:
    """Return a copy of *row* with coercers applied to matching columns."""
    result = dict(row)
    for col, fn in coercers.items():
        if col in result and result[col] is not None:
            try:
                result[col] = fn(result[col])
            except (ValueError, TypeError):
                pass  # leave original value on conversion failure
    return result


def normalize_row(row_diff: RowDiff, coercers: Dict[str, _Coercer]) -> RowDiff:
    """Return a new RowDiff with coercers applied to *left* and *right* dicts."""
    new_left = _apply_coercers(row_diff.left, coercers) if row_diff.left else row_diff.left
    new_right = _apply_coercers(row_diff.right, coercers) if row_diff.right else row_diff.right
    return RowDiff(
        key=row_diff.key,
        kind=row_diff.kind,
        left=new_left,
        right=new_right,
        delta=row_diff.delta,
    )


def normalize_result(
    result: DiffResult,
    coercers: Dict[str, _Coercer],
) -> DiffResult:
    """Apply *coercers* to every row in *result*, returning a new DiffResult."""
    normalized = [normalize_row(r, coercers) for r in result.rows]
    return DiffResult(rows=normalized, key_columns=result.key_columns)


def strip_whitespace(columns: Iterable[str]) -> Dict[str, _Coercer]:
    """Return a coercers dict that strips leading/trailing whitespace for *columns*."""
    return {col: str.strip for col in columns}


def to_lowercase(columns: Iterable[str]) -> Dict[str, _Coercer]:
    """Return a coercers dict that lowercases string values for *columns*."""
    return {col: lambda v: str(v).lower() for col in columns}


def to_numeric(
    columns: Iterable[str],
    cast: type = float,
) -> Dict[str, _Coercer]:
    """Return a coercers dict that casts *columns* to *cast* (default float)."""
    return {col: cast for col in columns}


def chain(*coercer_dicts: Dict[str, _Coercer]) -> Dict[str, _Coercer]:
    """Merge multiple coercer dicts; later dicts override earlier ones for the same column."""
    merged: Dict[str, _Coercer] = {}
    for d in coercer_dicts:
        merged.update(d)
    return merged
