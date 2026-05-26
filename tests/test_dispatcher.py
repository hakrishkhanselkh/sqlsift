"""Tests for sqlsift.dispatcher."""

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.dispatcher import Dispatcher


def _added(key):
    return RowDiff(kind="added", key=(key,), left=None, right={"id": key})


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs), key_columns=["id"])


def _routing():
    return {
        "new": _make_result(_added(1), _added(2)),
        "old": _make_result(_added(3)),
    }


# ---------------------------------------------------------------------------

def test_register_returns_self_for_chaining():
    d = Dispatcher()
    result = d.register("new", lambda n, dr: None)
    assert result is d


def test_len_reflects_registered_handlers():
    d = Dispatcher()
    assert len(d) == 0
    d.register("new", lambda n, dr: None)
    assert len(d) == 1


def test_dispatch_calls_handler_and_returns_value():
    d = Dispatcher()
    d.register("new", lambda name, dr: len(dr.diffs))
    results = d.dispatch({"new": _make_result(_added(1), _added(2))})
    assert results["new"] == 2


def test_dispatch_skips_bucket_with_no_handler():
    d = Dispatcher()
    d.register("new", lambda n, dr: "ok")
    results = d.dispatch(_routing())
    assert "old" not in results
    assert "new" in results


def test_dispatch_raise_on_missing():
    d = Dispatcher()
    d.register("new", lambda n, dr: None)
    with pytest.raises(KeyError, match="old"):
        d.dispatch(_routing(), raise_on_missing=True)


def test_default_handler_used_for_unregistered_bucket():
    collected = []
    d = Dispatcher(default_handler=lambda n, dr: collected.append(n))
    d.dispatch({"alpha": _make_result(), "beta": _make_result()})
    assert sorted(collected) == ["alpha", "beta"]


def test_explicit_handler_takes_priority_over_default():
    calls = []
    d = Dispatcher(default_handler=lambda n, dr: calls.append(("default", n)))
    d.register("new", lambda n, dr: calls.append(("explicit", n)))
    d.dispatch({"new": _make_result(_added(1)), "old": _make_result()})
    assert ("explicit", "new") in calls
    assert ("default", "old") in calls
    assert ("default", "new") not in calls


def test_unregister_removes_handler():
    d = Dispatcher()
    d.register("new", lambda n, dr: "ok")
    d.unregister("new")
    assert len(d) == 0


def test_unregister_nonexistent_is_noop():
    d = Dispatcher()
    d.unregister("ghost")  # should not raise


def test_registered_buckets_sorted():
    d = Dispatcher()
    d.register("z", lambda n, dr: None)
    d.register("a", lambda n, dr: None)
    d.register("m", lambda n, dr: None)
    assert d.registered_buckets() == ["a", "m", "z"]


def test_dispatch_empty_routing_returns_empty_dict():
    d = Dispatcher()
    d.register("new", lambda n, dr: "ok")
    assert d.dispatch({}) == {}
