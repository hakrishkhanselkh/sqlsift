"""replay.py – replay an audit log against a mutable row store.

Given a list of AuditEntry objects and a base dataset (list of dicts), apply
the recorded changes to reproduce the target state.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

from sqlsift.auditor import AuditEntry

RowStore = List[Dict[str, Any]]
KeyFunc = Callable[[Dict[str, Any]], Tuple]


def _default_key_func(row: Dict[str, Any]) -> Tuple:
    """Fallback: use the 'id' field as the key."""
    return (row.get("id"),)


def _index_store(store: RowStore, key_func: KeyFunc) -> Dict[Tuple, int]:
    return {key_func(row): idx for idx, row in enumerate(store)}


def replay(
    entries: List[AuditEntry],
    store: RowStore,
    *,
    key_func: Optional[KeyFunc] = None,
    row_source: Optional[Dict[Tuple, Dict[str, Any]]] = None,
) -> RowStore:
    """Apply audit entries to *store* and return the modified store.

    Parameters
    ----------
    entries:
        Ordered list of AuditEntry objects to replay.
    store:
        The baseline row store (list of dicts). A shallow copy is made.
    key_func:
        Callable that maps a row dict to a key tuple.  Defaults to ``id``.
    row_source:
        Mapping from key tuple to full row dict used for ``added`` entries.
        Required when the entries contain ``added`` kinds.
    """
    kf = key_func or _default_key_func
    result: RowStore = [dict(r) for r in store]
    rs = row_source or {}

    for entry in entries:
        idx_map = _index_store(result, kf)
        if entry.kind == "added":
            if entry.key in rs:
                result.append(dict(rs[entry.key]))
        elif entry.kind == "removed":
            pos = idx_map.get(entry.key)
            if pos is not None:
                result.pop(pos)
        elif entry.kind == "modified":
            pos = idx_map.get(entry.key)
            if pos is not None and entry.key in rs:
                result[pos] = dict(rs[entry.key])
    return result


def replay_stats(entries: List[AuditEntry]) -> Dict[str, int]:
    """Return counts of how many operations would be replayed by kind."""
    stats: Dict[str, int] = {"added": 0, "removed": 0, "modified": 0}
    for entry in entries:
        if entry.kind in stats:
            stats[entry.kind] += 1
    return stats
