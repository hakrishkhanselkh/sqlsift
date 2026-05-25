"""streaker.py — detect consecutive runs of the same diff kind for a given key."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .diff import DiffResult, RowDiff


@dataclass
class Streak:
    """A consecutive run of diffs sharing the same kind for one logical key."""

    key: Tuple
    kind: str
    rows: List[RowDiff] = field(default_factory=list)

    @property
    def length(self) -> int:
        return len(self.rows)

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "kind": self.kind,
            "length": self.length,
            "rows": [r.row for r in self.rows],
        }


def _row_key(row: RowDiff, key_columns: List[str]) -> Tuple:
    """Extract a hashable key tuple from a RowDiff."""
    src = row.row if row.kind != "modified" else row.row
    return tuple(src.get(c) for c in key_columns)


def find_streaks(result: DiffResult, key_columns: List[str], min_length: int = 2) -> List[Streak]:
    """Return streaks (consecutive same-kind diffs) per logical key.

    Rows are grouped by key; within each group the original result ordering is
    preserved and runs of the same *kind* longer than *min_length* are returned.
    """
    if not result.diffs:
        return []

    # Group diffs by key while preserving order
    from collections import defaultdict

    groups: dict = defaultdict(list)
    for diff in result.diffs:
        k = _row_key(diff, key_columns)
        groups[k].append(diff)

    streaks: List[Streak] = []
    for key, diffs in groups.items():
        current: Streak | None = None
        for diff in diffs:
            if current is None or diff.kind != current.kind:
                if current is not None and current.length >= min_length:
                    streaks.append(current)
                current = Streak(key=key, kind=diff.kind, rows=[diff])
            else:
                current.rows.append(diff)
        if current is not None and current.length >= min_length:
            streaks.append(current)

    return streaks


def longest_streak(result: DiffResult, key_columns: List[str]) -> Streak | None:
    """Return the single longest streak across all keys, or None if result is empty."""
    candidates = find_streaks(result, key_columns, min_length=1)
    if not candidates:
        return None
    return max(candidates, key=lambda s: s.length)


def streak_summary(result: DiffResult, key_columns: List[str]) -> dict:
    """Return a summary dict of streak statistics for the result."""
    all_streaks = find_streaks(result, key_columns, min_length=1)
    if not all_streaks:
        return {"total_streaks": 0, "max_length": 0, "by_kind": {}}

    by_kind: dict = {}
    for s in all_streaks:
        by_kind.setdefault(s.kind, 0)
        by_kind[s.kind] += 1

    return {
        "total_streaks": len(all_streaks),
        "max_length": max(s.length for s in all_streaks),
        "by_kind": by_kind,
    }
