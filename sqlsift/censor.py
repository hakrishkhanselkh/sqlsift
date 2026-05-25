"""censor.py — redact or mask sensitive column values in a DiffResult."""

from __future__ import annotations

from typing import Any, Callable, Collection, Dict, Optional

from sqlsift.diff import DiffResult, RowDiff

_MASK_DEFAULT = "***"


def _mask_row(
    row: Dict[str, Any],
    columns: Collection[str],
    mask: str,
) -> Dict[str, Any]:
    """Return a shallow copy of *row* with *columns* replaced by *mask*."""
    return {k: (mask if k in columns else v) for k, v in row.items()}


def _mask_delta(
    delta: Optional[Dict[str, Any]],
    columns: Collection[str],
    mask: str,
) -> Optional[Dict[str, Any]]:
    if delta is None:
        return None
    return {
        k: {"before": mask, "after": mask} if k in columns else v
        for k, v in delta.items()
    }


def redact(
    result: DiffResult,
    columns: Collection[str],
    mask: str = _MASK_DEFAULT,
) -> DiffResult:
    """Return a new DiffResult with *columns* replaced by *mask* in every row."""
    cols = set(columns)
    new_diffs = [
        RowDiff(
            kind=d.kind,
            key=d.key,
            row=_mask_row(d.row, cols, mask),
            delta=_mask_delta(d.delta, cols, mask),
        )
        for d in result.diffs
    ]
    return DiffResult(diffs=new_diffs)


def redact_by_predicate(
    result: DiffResult,
    predicate: Callable[[str, Any], bool],
    mask: str = _MASK_DEFAULT,
) -> DiffResult:
    """Redact any cell where *predicate(column_name, value)* returns True."""

    def _mask_row_pred(row: Dict[str, Any]) -> Dict[str, Any]:
        return {k: (mask if predicate(k, v) else v) for k, v in row.items()}

    def _mask_delta_pred(
        delta: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        if delta is None:
            return None
        return {
            k: {"before": mask, "after": mask}
            if predicate(k, v.get("after") if isinstance(v, dict) else v)
            else v
            for k, v in delta.items()
        }

    new_diffs = [
        RowDiff(
            kind=d.kind,
            key=d.key,
            row=_mask_row_pred(d.row),
            delta=_mask_delta_pred(d.delta),
        )
        for d in result.diffs
    ]
    return DiffResult(diffs=new_diffs)
