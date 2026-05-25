"""Tests for sqlsift.classifier."""

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.classifier import (
    classify,
    label_counts,
    rule_by_kind,
    rule_by_column_value,
    rule_by_predicate,
)


def _added(key, **kw):
    return RowDiff(kind="added", key=key, left=None, right={"id": key, **kw}, delta={})


def _removed(key, **kw):
    return RowDiff(kind="removed", key=key, left={"id": key, **kw}, right=None, delta={})


def _modified(key, delta, **kw):
    left = {"id": key, **kw}
    right = {**left, **{col: v["right"] for col, v in delta.items()}}
    return RowDiff(kind="modified", key=key, left=left, right=right, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# classify – basic bucketing
# ---------------------------------------------------------------------------

def test_classify_empty_result_returns_empty_dict():
    result = _make_result()
    assert classify(result, []) == {}


def test_classify_no_matching_rules_all_unclassified():
    result = _make_result(_added(1), _removed(2))
    out = classify(result, [])
    assert set(out.keys()) == {"unclassified"}
    assert len(out["unclassified"]) == 2


def test_classify_rule_by_kind_added():
    result = _make_result(_added(1), _removed(2), _added(3))
    rules = [rule_by_kind("added", "new_row")]
    out = classify(result, rules)
    assert len(out.get("new_row", [])) == 2
    assert len(out.get("unclassified", [])) == 1


def test_classify_rule_by_kind_removed():
    result = _make_result(_added(1), _removed(2))
    rules = [rule_by_kind("removed", "deleted")]
    out = classify(result, rules)
    assert "deleted" in out
    assert len(out["deleted"]) == 1


def test_classify_multiple_rules_first_match_wins():
    mod = _modified(1, {"score": {"left": 10, "right": 20}}, score=10)
    result = _make_result(mod)
    rules = [
        rule_by_kind("modified", "changed"),
        rule_by_kind("modified", "also_changed"),
    ]
    out = classify(result, rules)
    assert "changed" in out
    assert "also_changed" not in out


def test_classify_rule_by_column_value():
    r1 = _added(1, region="EU")
    r2 = _added(2, region="US")
    result = _make_result(r1, r2)
    rules = [rule_by_column_value("region", "EU", "european")]
    out = classify(result, rules)
    assert len(out["european"]) == 1
    assert out["european"][0].key == 1


def test_classify_rule_by_predicate():
    result = _make_result(_added(1), _added(2), _removed(3))
    rules = [rule_by_predicate(lambda r: r.kind == "added" and r.key == 2, "special")]
    out = classify(result, rules)
    assert len(out["special"]) == 1


# ---------------------------------------------------------------------------
# rule_by_kind – validation
# ---------------------------------------------------------------------------

def test_rule_by_kind_invalid_raises():
    with pytest.raises(ValueError, match="kind must be"):
        rule_by_kind("upserted", "label")


# ---------------------------------------------------------------------------
# label_counts
# ---------------------------------------------------------------------------

def test_label_counts_reflects_bucket_sizes():
    result = _make_result(_added(1), _added(2), _removed(3))
    rules = [rule_by_kind("added", "ins"), rule_by_kind("removed", "del")]
    out = classify(result, rules)
    counts = label_counts(out)
    assert counts == {"ins": 2, "del": 1}


def test_label_counts_empty():
    assert label_counts({}) == {}
