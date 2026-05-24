"""Tests for sqlsift.sampler."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.sampler import head, tail, random_sample, stratified_sample


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _added(key: str) -> RowDiff:
    return RowDiff(kind="added", key={"id": key}, row={"id": key, "v": 1}, delta={})


def _removed(key: str) -> RowDiff:
    return RowDiff(kind="removed", key={"id": key}, row={"id": key, "v": 2}, delta={})


def _modified(key: str) -> RowDiff:
    return RowDiff(
        kind="modified",
        key={"id": key},
        row={"id": key, "v": 99},
        delta={"v": {"old": 1, "new": 99}},
    )


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# head
# ---------------------------------------------------------------------------

def test_head_returns_first_n():
    r = _make_result(_added("a"), _added("b"), _added("c"))
    assert len(head(r, 2).diffs) == 2
    assert head(r, 2).diffs[0].key == {"id": "a"}


def test_head_zero_returns_empty():
    r = _make_result(_added("a"), _added("b"))
    assert head(r, 0).diffs == []


def test_head_larger_than_size_returns_all():
    r = _make_result(_added("a"))
    assert len(head(r, 100).diffs) == 1


def test_head_negative_raises():
    with pytest.raises(ValueError):
        head(_make_result(), -1)


# ---------------------------------------------------------------------------
# tail
# ---------------------------------------------------------------------------

def test_tail_returns_last_n():
    r = _make_result(_added("a"), _added("b"), _added("c"))
    result = tail(r, 2)
    assert len(result.diffs) == 2
    assert result.diffs[-1].key == {"id": "c"}


def test_tail_zero_returns_empty():
    r = _make_result(_added("a"), _added("b"))
    assert tail(r, 0).diffs == []


def test_tail_negative_raises():
    with pytest.raises(ValueError):
        tail(_make_result(), -1)


# ---------------------------------------------------------------------------
# random_sample
# ---------------------------------------------------------------------------

def test_random_sample_length():
    r = _make_result(*[_added(str(i)) for i in range(20)])
    s = random_sample(r, 5, seed=42)
    assert len(s.diffs) == 5


def test_random_sample_reproducible():
    r = _make_result(*[_added(str(i)) for i in range(20)])
    s1 = random_sample(r, 5, seed=7)
    s2 = random_sample(r, 5, seed=7)
    assert [d.key for d in s1.diffs] == [d.key for d in s2.diffs]


def test_random_sample_clamped_to_population():
    r = _make_result(_added("a"), _added("b"))
    s = random_sample(r, 100, seed=0)
    assert len(s.diffs) == 2


def test_random_sample_negative_raises():
    with pytest.raises(ValueError):
        random_sample(_make_result(), -1)


# ---------------------------------------------------------------------------
# stratified_sample
# ---------------------------------------------------------------------------

def test_stratified_sample_per_kind():
    diffs = (
        [_added(str(i)) for i in range(5)]
        + [_removed(str(i)) for i in range(5)]
        + [_modified(str(i)) for i in range(5)]
    )
    r = _make_result(*diffs)
    s = stratified_sample(r, 2, seed=0)
    kinds = [d.kind for d in s.diffs]
    assert kinds.count("added") == 2
    assert kinds.count("removed") == 2
    assert kinds.count("modified") == 2


def test_stratified_sample_clamps_to_available():
    r = _make_result(_added("a"), _modified("b"))
    s = stratified_sample(r, 10, seed=0)
    assert len(s.diffs) == 2


def test_stratified_sample_negative_raises():
    with pytest.raises(ValueError):
        stratified_sample(_make_result(), -1)
