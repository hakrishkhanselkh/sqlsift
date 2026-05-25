"""Tests for sqlsift.censor."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.censor import redact, redact_by_predicate


def _added(key, row):
    return RowDiff(kind="added", key=key, row=row, delta=None)


def _removed(key, row):
    return RowDiff(kind="removed", key=key, row=row, delta=None)


def _modified(key, row, delta):
    return RowDiff(kind="modified", key=key, row=row, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# redact
# ---------------------------------------------------------------------------

def test_redact_empty_result():
    result = _make_result()
    out = redact(result, ["email"])
    assert out.diffs == []


def test_redact_masks_specified_column_in_added_row():
    row = {"id": 1, "email": "a@b.com", "name": "Alice"}
    result = _make_result(_added((1,), row))
    out = redact(result, ["email"])
    assert out.diffs[0].row["email"] == "***"
    assert out.diffs[0].row["name"] == "Alice"


def test_redact_does_not_mutate_original():
    row = {"id": 1, "email": "a@b.com"}
    result = _make_result(_added((1,), row))
    redact(result, ["email"])
    assert result.diffs[0].row["email"] == "a@b.com"


def test_redact_custom_mask_string():
    row = {"id": 2, "ssn": "123-45-6789"}
    result = _make_result(_added((2,), row))
    out = redact(result, ["ssn"], mask="REDACTED")
    assert out.diffs[0].row["ssn"] == "REDACTED"


def test_redact_masks_delta_before_and_after():
    row = {"id": 3, "salary": 9000}
    delta = {"salary": {"before": 8000, "after": 9000}}
    result = _make_result(_modified((3,), row, delta))
    out = redact(result, ["salary"])
    d = out.diffs[0].delta["salary"]
    assert d["before"] == "***"
    assert d["after"] == "***"


def test_redact_leaves_unmasked_delta_columns_intact():
    row = {"id": 4, "salary": 9000, "dept": "eng"}
    delta = {
        "salary": {"before": 8000, "after": 9000},
        "dept": {"before": "ops", "after": "eng"},
    }
    result = _make_result(_modified((4,), row, delta))
    out = redact(result, ["salary"])
    assert out.diffs[0].delta["dept"] == {"before": "ops", "after": "eng"}


def test_redact_none_delta_stays_none():
    row = {"id": 5, "token": "secret"}
    result = _make_result(_removed((5,), row))
    out = redact(result, ["token"])
    assert out.diffs[0].delta is None


def test_redact_multiple_columns():
    row = {"id": 6, "email": "x@y.com", "phone": "555", "name": "Bob"}
    result = _make_result(_added((6,), row))
    out = redact(result, ["email", "phone"])
    assert out.diffs[0].row["email"] == "***"
    assert out.diffs[0].row["phone"] == "***"
    assert out.diffs[0].row["name"] == "Bob"


# ---------------------------------------------------------------------------
# redact_by_predicate
# ---------------------------------------------------------------------------

def test_redact_by_predicate_masks_matching_cells():
    row = {"id": 7, "email": "user@example.com", "age": 30}
    result = _make_result(_added((7,), row))
    out = redact_by_predicate(result, lambda col, _: col == "email")
    assert out.diffs[0].row["email"] == "***"
    assert out.diffs[0].row["age"] == 30


def test_redact_by_predicate_value_based():
    row = {"id": 8, "score": 42, "label": "ok"}
    result = _make_result(_added((8,), row))
    # mask any integer value above 40
    out = redact_by_predicate(result, lambda _, v: isinstance(v, int) and v > 40)
    assert out.diffs[0].row["score"] == "***"
    assert out.diffs[0].row["label"] == "ok"


def test_redact_by_predicate_empty_result():
    result = _make_result()
    out = redact_by_predicate(result, lambda c, v: True)
    assert out.diffs == []
