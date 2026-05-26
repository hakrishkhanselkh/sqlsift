"""tracer.py — track which rows changed between multiple DiffResult snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from sqlsift.diff import DiffResult, RowDiff


@dataclass
class TraceEntry:
    """Records a single row's presence across labelled snapshots."""

    key: Tuple[Any, ...]
    appearances: Dict[str, str] = field(default_factory=dict)  # label -> kind

    def as_dict(self) -> Dict[str, Any]:
        return {"key": self.key, "appearances": dict(self.appearances)}

    def __repr__(self) -> str:  # pragma: no cover
        return f"TraceEntry(key={self.key!r}, appearances={self.appearances!r})"


def trace(
    snapshots: List[Tuple[str, DiffResult]],
    key_columns: Optional[List[str]] = None,
) -> List[TraceEntry]:
    """Build a trace of how each row key moves across labelled DiffResults.

    Parameters
    ----------
    snapshots:
        Ordered list of (label, DiffResult) pairs.
    key_columns:
        Columns that form the row identity key.  When *None* the full
        ``row`` dict is used as the key (sorted items tuple).

    Returns
    -------
    List of :class:`TraceEntry` objects, one per unique row key seen.
    """
    if not snapshots:
        return []

    index: Dict[Tuple[Any, ...], TraceEntry] = {}

    for label, result in snapshots:
        for diff in result.diffs:
            row = diff.row
            if key_columns:
                key = tuple(row.get(c) for c in key_columns)
            else:
                key = tuple(sorted(row.items()))

            if key not in index:
                index[key] = TraceEntry(key=key)
            index[key].appearances[label] = diff.kind

    return list(index.values())


def persistent_keys(
    entries: List[TraceEntry], labels: List[str]
) -> List[TraceEntry]:
    """Return entries that appear in *every* supplied label."""
    label_set = set(labels)
    return [e for e in entries if label_set.issubset(e.appearances.keys())]


def transient_keys(entries: List[TraceEntry], labels: List[str]) -> List[TraceEntry]:
    """Return entries that appear in *some but not all* supplied labels."""
    label_set = set(labels)
    return [
        e
        for e in entries
        if e.appearances.keys() & label_set
        and not label_set.issubset(e.appearances.keys())
    ]


def kind_changed(
    entries: List[TraceEntry], from_label: str, to_label: str
) -> List[TraceEntry]:
    """Return entries whose diff *kind* differs between two labels."""
    result = []
    for e in entries:
        if from_label in e.appearances and to_label in e.appearances:
            if e.appearances[from_label] != e.appearances[to_label]:
                result.append(e)
    return result
