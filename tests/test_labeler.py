"""Tests for sqlsift.labeler."""

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.labeler import (
    label_result,
    label_row,
    rule_by_column_value,
    rule_by_kind,
    rule_by_predicate,
)


def _added(key, row):
    return RowDiff(key=key, kind="added", old_row=None, new_row=row, delta={})


def _removed(key, row):
    return RowDiff(key=key, kind="removed", old_row=row, new_row=None, delta={})


def _modified(key, old, new, delta):
    return RowDiff(key=key, kind="modified", old_row=old, new_row=new, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# rule_by_kind
# ---------------------------------------------------------------------------

def test_rule_by_kind_matches_added():
    rule = rule_by_kind("added", "new-row")
    row = _added(("id", 1), {"id": 1, "v": "a"})
    assert rule(row) == "new-row"


def test_rule_by_kind_no_match_returns_none():
    rule = rule_by_kind("removed", "gone")
    row = _added(("id", 1), {"id": 1})
    assert rule(row) is None


def test_rule_by_kind_invalid_raises():
    with pytest.raises(ValueError, match="Invalid kind"):
        rule_by_kind("unknown", "x")


# ---------------------------------------------------------------------------
# rule_by_column_value
# ---------------------------------------------------------------------------

def test_rule_by_column_value_matches():
    rule = rule_by_column_value("status", "active", "active-row")
    row = _added(("id", 1), {"id": 1, "status": "active"})
    assert rule(row) == "active-row"


def test_rule_by_column_value_no_match():
    rule = rule_by_column_value("status", "active", "active-row")
    row = _added(("id", 1), {"id": 1, "status": "inactive"})
    assert rule(row) is None


def test_rule_by_column_value_uses_old_row_for_removed():
    rule = rule_by_column_value("region", "EU", "eu-removed")
    row = _removed(("id", 2), {"id": 2, "region": "EU"})
    assert rule(row) == "eu-removed"


# ---------------------------------------------------------------------------
# rule_by_predicate
# ---------------------------------------------------------------------------

def test_rule_by_predicate_matches():
    rule = rule_by_predicate(lambda r: r.kind == "modified", "changed")
    row = _modified(("id", 3), {"id": 3, "v": 1}, {"id": 3, "v": 2}, {"v": (1, 2)})
    assert rule(row) == "changed"


def test_rule_by_predicate_no_match():
    rule = rule_by_predicate(lambda r: False, "never")
    row = _added(("id", 1), {"id": 1})
    assert rule(row) is None


# ---------------------------------------------------------------------------
# label_row
# ---------------------------------------------------------------------------

def test_label_row_uses_first_matching_rule():
    rules = [rule_by_kind("added", "first"), rule_by_kind("added", "second")]
    row = _added(("id", 1), {"id": 1})
    assert label_row(row, rules) == "first"


def test_label_row_falls_back_to_default():
    rules = [rule_by_kind("removed", "gone")]
    row = _added(("id", 1), {"id": 1})
    assert label_row(row, rules, default="other") == "other"


def test_label_row_empty_rules_returns_default():
    row = _added(("id", 1), {"id": 1})
    assert label_row(row, []) == "unlabeled"


# ---------------------------------------------------------------------------
# label_result
# ---------------------------------------------------------------------------

def test_label_result_keys_are_row_key_strings():
    result = _make_result(_added(("id", 1), {"id": 1}))
    labeled = label_result(result, [])
    assert "('id', 1)" in labeled


def test_label_result_all_rows_present():
    result = _make_result(
        _added(("id", 1), {"id": 1}),
        _removed(("id", 2), {"id": 2}),
    )
    labeled = label_result(result, [])
    assert len(labeled) == 2


def test_label_result_applies_rules():
    result = _make_result(
        _added(("id", 1), {"id": 1}),
        _removed(("id", 2), {"id": 2}),
    )
    rules = [rule_by_kind("added", "new"), rule_by_kind("removed", "old")]
    labeled = label_result(result, rules)
    assert labeled["('id', 1)"] == "new"
    assert labeled["('id', 2)"] == "old"


def test_label_result_empty_result():
    result = _make_result()
    assert label_result(result, []) == {}
