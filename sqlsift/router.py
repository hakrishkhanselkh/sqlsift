"""sqlsift.router — route DiffResult rows into named buckets based on rules."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

from sqlsift.diff import DiffResult, RowDiff

# A rule is a callable that returns a bucket name (str) or None if no match.
Rule = Callable[[RowDiff], Optional[str]]


def _make_rule(name: str, predicate: Callable[[RowDiff], bool]) -> Rule:
    """Wrap a predicate into a named rule."""
    def _rule(row: RowDiff) -> Optional[str]:
        return name if predicate(row) else None
    return _rule


def rule_by_kind(kind: str, bucket: str) -> Rule:
    """Route rows whose kind matches *kind* into *bucket*."""
    if kind not in {"added", "removed", "modified", "unchanged"}:
        raise ValueError(f"Unknown kind: {kind!r}")
    return _make_rule(bucket, lambda r: r.kind == kind)


def rule_by_column_value(column: str, value: object, bucket: str) -> Rule:
    """Route rows where *column* equals *value* into *bucket*."""
    def _predicate(row: RowDiff) -> bool:
        data = row.left or row.right or {}
        return data.get(column) == value
    return _make_rule(bucket, _predicate)


def rule_by_predicate(predicate: Callable[[RowDiff], bool], bucket: str) -> Rule:
    """Route rows matching *predicate* into *bucket*."""
    return _make_rule(bucket, predicate)


def route(
    result: DiffResult,
    rules: List[Rule],
    default_bucket: str = "unmatched",
) -> Dict[str, DiffResult]:
    """Apply *rules* in order; the first matching rule wins.

    Returns a dict mapping bucket names to DiffResult objects.
    Rows that match no rule land in *default_bucket*.
    """
    buckets: Dict[str, List[RowDiff]] = {}

    for row in result.diffs:
        matched = False
        for rule in rules:
            bucket = rule(row)
            if bucket is not None:
                buckets.setdefault(bucket, []).append(row)
                matched = True
                break
        if not matched:
            buckets.setdefault(default_bucket, []).append(row)

    # Build DiffResult objects preserving key_columns
    return {
        name: DiffResult(diffs=rows, key_columns=result.key_columns)
        for name, rows in buckets.items()
    }


def bucket_names(routing: Dict[str, DiffResult]) -> List[str]:
    """Return sorted bucket names from a routing dict."""
    return sorted(routing.keys())


def sizes(routing: Dict[str, DiffResult]) -> Dict[str, int]:
    """Return a dict mapping bucket name to row count."""
    return {name: len(dr.diffs) for name, dr in routing.items()}
