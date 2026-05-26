"""Tests for sqlsift.router."""

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.router import (
    bucket_names,
    route,
    rule_by_column_value,
    rule_by_kind,
    rule_by_predicate,
    sizes,
)


def _added(key, **kw):
    return RowDiff(kind="added", key=key, left=None, right={"id": key, **kw})


def _removed(key, **kw):
    return RowDiff(kind="removed", key=key, left={"id": key, **kw}, right=None)


def _modified(key, left_kw, right_kw):
    delta = {k: (left_kw[k], right_kw[k]) for k in left_kw if left_kw[k] != right_kw.get(k)}
    return RowDiff(
        kind="modified",
        key=key,
        left={"id": key, **left_kw},
        right={"id": key, **right_kw},
        delta=delta,
    )


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs), key_columns=["id"])


# ---------------------------------------------------------------------------

def test_route_empty_result_returns_empty_dict():
    result = _make_result()
    routing = route(result, [rule_by_kind("added", "new")])
    assert routing == {} or all(len(v.diffs) == 0 for v in routing.values())


def test_route_by_kind_added():
    r = _make_result(_added(1), _removed(2))
    routing = route(r, [rule_by_kind("added", "new_rows")])
    assert "new_rows" in routing
    assert len(routing["new_rows"].diffs) == 1
    assert routing["new_rows"].diffs[0].kind == "added"


def test_route_by_kind_unmatched_goes_to_default():
    r = _make_result(_added(1), _removed(2))
    routing = route(r, [rule_by_kind("added", "new_rows")], default_bucket="rest")
    assert "rest" in routing
    assert len(routing["rest"].diffs) == 1
    assert routing["rest"].diffs[0].kind == "removed"


def test_route_first_rule_wins():
    r = _make_result(_added(1, region="US"))
    rules = [
        rule_by_kind("added", "all_added"),
        rule_by_column_value("region", "US", "us_added"),
    ]
    routing = route(r, rules)
    assert "all_added" in routing
    assert "us_added" not in routing


def test_route_by_column_value():
    r = _make_result(
        _added(1, region="US"),
        _added(2, region="EU"),
    )
    rules = [rule_by_column_value("region", "EU", "europe")]
    routing = route(r, rules, default_bucket="other")
    assert len(routing["europe"].diffs) == 1
    assert len(routing["other"].diffs) == 1


def test_route_by_predicate():
    r = _make_result(_modified(1, {"val": 10}, {"val": 50}), _modified(2, {"val": 1}, {"val": 2}))
    big_change = rule_by_predicate(
        lambda row: bool(row.delta and any(abs(v[1] - v[0]) > 20 for v in row.delta.values())),
        "big_changes",
    )
    routing = route(r, [big_change], default_bucket="small_changes")
    assert len(routing["big_changes"].diffs) == 1
    assert len(routing["small_changes"].diffs) == 1


def test_bucket_names_sorted():
    r = _make_result(_added(1), _removed(2), _modified(3, {"x": 1}, {"x": 2}))
    rules = [
        rule_by_kind("added", "z_bucket"),
        rule_by_kind("removed", "a_bucket"),
    ]
    routing = route(r, rules, default_bucket="m_bucket")
    assert bucket_names(routing) == sorted(routing.keys())


def test_sizes_returns_counts():
    r = _make_result(_added(1), _added(2), _removed(3))
    rules = [rule_by_kind("added", "added"), rule_by_kind("removed", "removed")]
    routing = route(r, rules)
    s = sizes(routing)
    assert s["added"] == 2
    assert s["removed"] == 1


def test_key_columns_preserved_in_buckets():
    r = DiffResult(diffs=[_added(1)], key_columns=["id", "region"])
    routing = route(r, [rule_by_kind("added", "new")])
    assert routing["new"].key_columns == ["id", "region"]


def test_rule_by_kind_invalid_raises():
    with pytest.raises(ValueError):
        rule_by_kind("invalid_kind", "bucket")
