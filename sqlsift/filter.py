"""Filtering utilities for DiffResult sets."""

from typing import Callable, Iterable, List, Optional
from sqlsift.diff import DiffResult, RowDiff


def by_kind(result: DiffResult, kind: str) -> DiffResult:
    """Return a new DiffResult containing only diffs of the given kind.

    Args:
        result: The source DiffResult to filter.
        kind: One of 'added', 'removed', or 'modified'.

    Returns:
        A new DiffResult with only the matching RowDiff entries.

    Raises:
        ValueError: If kind is not a recognised value.
    """
    valid_kinds = {"added", "removed", "modified"}
    if kind not in valid_kinds:
        raise ValueError(f"kind must be one of {valid_kinds}, got {kind!r}")

    filtered = [d for d in result.diffs if d.kind == kind]
    return DiffResult(
        diffs=filtered,
        left_only=result.left_only if kind == "removed" else [],
        right_only=result.right_only if kind == "added" else [],
    )


def by_columns(result: DiffResult, columns: Iterable[str]) -> DiffResult:
    """Return a new DiffResult where modified diffs are filtered to only
    include changes in the specified columns.

    Diffs with no remaining column changes after filtering are dropped.
    Added and removed rows are passed through unchanged.

    Args:
        result: The source DiffResult.
        columns: Column names to keep in the diff delta.

    Returns:
        A new DiffResult with column-filtered modified diffs.
    """
    cols = set(columns)
    filtered: List[RowDiff] = []

    for d in result.diffs:
        if d.kind != "modified":
            filtered.append(d)
            continue
        narrowed_delta = {k: v for k, v in (d.delta or {}).items() if k in cols}
        if narrowed_delta:
            filtered.append(
                RowDiff(
                    kind=d.kind,
                    key=d.key,
                    left=d.left,
                    right=d.right,
                    delta=narrowed_delta,
                )
            )

    return DiffResult(
        diffs=filtered,
        left_only=result.left_only,
        right_only=result.right_only,
    )


def by_predicate(result: DiffResult, predicate: Callable[[RowDiff], bool]) -> DiffResult:
    """Return a new DiffResult containing only diffs for which predicate returns True.

    Args:
        result: The source DiffResult.
        predicate: A callable that accepts a RowDiff and returns bool.

    Returns:
        A new DiffResult with only matching RowDiff entries.
    """
    filtered = [d for d in result.diffs if predicate(d)]
    left_only = [r for r in result.left_only if predicate(RowDiff(kind="removed", key=None, left=r, right=None, delta=None))]
    right_only = [r for r in result.right_only if predicate(RowDiff(kind="added", key=None, left=None, right=r, delta=None))]
    return DiffResult(diffs=filtered, left_only=left_only, right_only=right_only)
