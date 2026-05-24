"""Tests for sqlsift.annotator."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.annotator import (
    annotate_result,
    annotate_row,
    rule_column_changed,
    rule_missing_value,
)


def _added(key, row):
    return RowDiff(key=key, kind="added", old_row=None, new_row=row, delta=None)


def _removed(key, row):
    return RowDiff(key=key, kind="removed", old_row=row, new_row=None, delta=None)


def _modified(key, old, new, delta):
    return RowDiff(key=key, kind="modified", old_row=old, new_row=new, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs), keys=["id"])


# ---------------------------------------------------------------------------
# annotate_row
# ---------------------------------------------------------------------------

def test_annotate_row_default_label_added():
    diff = _added((1,), {"id": 1, "name": "alice"})
    ann = annotate_row(diff, [])
    assert ann["label"] == "ADDED"
    assert ann["notes"] == []


def test_annotate_row_default_label_removed():
    diff = _removed((2,), {"id": 2})
    ann = annotate_row(diff, [])
    assert ann["label"] == "REMOVED"


def test_annotate_row_contains_key_and_kind():
    diff = _added((42,), {"id": 42})
    ann = annotate_row(diff, [])
    assert ann["key"] == (42,)
    assert ann["kind"] == "added"


# ---------------------------------------------------------------------------
# annotate_result
# ---------------------------------------------------------------------------

def test_annotate_result_empty():
    result = _make_result()
    assert annotate_result(result) == []


def test_annotate_result_length_matches_diffs():
    result = _make_result(
        _added((1,), {"id": 1}),
        _removed((2,), {"id": 2}),
    )
    annotations = annotate_result(result)
    assert len(annotations) == 2


def test_annotate_result_no_rules_empty_notes():
    result = _make_result(_added((1,), {"id": 1}))
    ann = annotate_result(result)[0]
    assert ann["notes"] == []


# ---------------------------------------------------------------------------
# rule_column_changed
# ---------------------------------------------------------------------------

def test_rule_column_changed_fires_on_modified():
    rule = rule_column_changed("price")
    diff = _modified((1,), {"id": 1, "price": 10}, {"id": 1, "price": 20}, {"price": (10, 20)})
    assert rule(diff) is not None


def test_rule_column_changed_silent_on_other_columns():
    rule = rule_column_changed("price")
    diff = _modified((1,), {"id": 1, "name": "a"}, {"id": 1, "name": "b"}, {"name": ("a", "b")})
    assert rule(diff) is None


def test_rule_column_changed_silent_on_added():
    rule = rule_column_changed("price")
    diff = _added((1,), {"id": 1, "price": 5})
    assert rule(diff) is None


def test_rule_column_changed_custom_message():
    rule = rule_column_changed("price", message="price drift detected")
    diff = _modified((1,), {"id": 1, "price": 10}, {"id": 1, "price": 20}, {"price": (10, 20)})
    assert rule(diff) == "price drift detected"


# ---------------------------------------------------------------------------
# rule_missing_value
# ---------------------------------------------------------------------------

def test_rule_missing_value_fires_when_null():
    rule = rule_missing_value("email")
    diff = _added((1,), {"id": 1, "email": None})
    assert rule(diff) is not None


def test_rule_missing_value_silent_when_present():
    rule = rule_missing_value("email")
    diff = _added((1,), {"id": 1, "email": "x@y.com"})
    assert rule(diff) is None


def test_rule_missing_value_custom_message():
    rule = rule_missing_value("email", message="email must not be null")
    diff = _added((1,), {"id": 1, "email": None})
    assert rule(diff) == "email must not be null"
