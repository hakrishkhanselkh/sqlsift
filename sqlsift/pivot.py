"""Pivot diff results into column-oriented summaries."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Any

from .diff import DiffResult, RowDiff


def by_column(result: DiffResult) -> Dict[str, Dict[str, List[Any]]]:
    """Return a mapping of column -> kind -> list of values seen in diffs.

    Only MODIFIED rows contribute changed values; ADDED/REMOVED rows
    contribute all their values under the respective kind key.
    """
    out: Dict[str, Dict[str, List[Any]]] = defaultdict(lambda: defaultdict(list))

    for diff in result.diffs:
        if diff.kind == "modified":
            for col, (old, new) in (diff.delta or {}).items():
                out[col]["old"].append(old)
                out[col]["new"].append(new)
        else:
            row = diff.row
            for col, val in row.items():
                out[col][diff.kind].append(val)

    return {col: dict(kinds) for col, kinds in out.items()}


def change_frequency(result: DiffResult) -> Dict[str, int]:
    """Return how many times each column appears in a modified diff's delta."""
    freq: Dict[str, int] = defaultdict(int)
    for diff in result.diffs:
        if diff.kind == "modified" and diff.delta:
            for col in diff.delta:
                freq[col] += 1
    return dict(freq)


def most_changed_columns(result: DiffResult, top_n: int = 5) -> List[str]:
    """Return the top-N column names most frequently changed across modified rows."""
    freq = change_frequency(result)
    return sorted(freq, key=lambda c: freq[c], reverse=True)[:top_n]
