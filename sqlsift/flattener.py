"""sqlsift.flattener — flatten DiffResult rows into plain dicts for downstream use."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .diff import DiffResult, RowDiff


def _flatten_row(row_diff: RowDiff, include_meta: bool = True) -> Dict[str, Any]:
    """Convert a single RowDiff into a flat dictionary.

    For modified rows the *after* values are used; delta keys are optionally
    included with a ``_delta_`` prefix so they never clash with real columns.
    """
    flat: Dict[str, Any] = dict(row_diff.row)

    if include_meta:
        flat["__kind__"] = row_diff.kind
        flat["__key__"] = row_diff.key

        if row_diff.delta:
            for col, (before, after) in row_diff.delta.items():
                flat[f"_delta_{col}_before"] = before
                flat[f"_delta_{col}_after"] = after

    return flat


def flatten(
    result: DiffResult,
    kinds: Optional[List[str]] = None,
    include_meta: bool = True,
) -> List[Dict[str, Any]]:
    """Return all rows in *result* as a list of plain dicts.

    Parameters
    ----------
    result:
        The :class:`~sqlsift.diff.DiffResult` to flatten.
    kinds:
        Optional list of kinds to include (``'added'``, ``'removed'``,
        ``'modified'``).  When *None* all rows are included.
    include_meta:
        When ``True`` (default) each dict contains ``__kind__``, ``__key__``
        and ``_delta_<col>_before`` / ``_delta_<col>_after`` entries.
    """
    rows = result.diffs
    if kinds is not None:
        normalised = {k.lower() for k in kinds}
        rows = [r for r in rows if r.kind in normalised]

    return [_flatten_row(r, include_meta=include_meta) for r in rows]


def flatten_modified_delta(result: DiffResult) -> List[Dict[str, Any]]:
    """Return one dict per *modified* row containing only the changed columns.

    Each dict contains the row key columns plus ``before`` and ``after`` values
    for every column that changed.
    """
    output: List[Dict[str, Any]] = []
    for row_diff in result.diffs:
        if row_diff.kind != "modified" or not row_diff.delta:
            continue
        entry: Dict[str, Any] = {"__key__": row_diff.key}
        for col, (before, after) in row_diff.delta.items():
            entry[f"{col}_before"] = before
            entry[f"{col}_after"] = after
        output.append(entry)
    return output
