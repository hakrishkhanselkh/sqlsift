"""Timeline utilities for tracking diff snapshots over time."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from sqlsift.diff import DiffResult
from sqlsift.summarizer import summarize


@dataclass
class Snapshot:
    """A labelled, timestamped DiffResult."""

    result: DiffResult
    label: str
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def as_dict(self) -> dict:
        summary = summarize(self.result)
        return {
            "label": self.label,
            "recorded_at": self.recorded_at.isoformat(),
            "added": summary.added_count,
            "removed": summary.removed_count,
            "modified": summary.modified_count,
            "identical": summary.identical_count,
        }


@dataclass
class Timeline:
    """Ordered collection of diff snapshots."""

    snapshots: List[Snapshot] = field(default_factory=list)

    def add(self, result: DiffResult, label: str, recorded_at: Optional[datetime] = None) -> Snapshot:
        """Append a new snapshot and return it."""
        snap = Snapshot(
            result=result,
            label=label,
            recorded_at=recorded_at or datetime.now(timezone.utc),
        )
        self.snapshots.append(snap)
        return snap

    def as_dict_list(self) -> List[dict]:
        """Return all snapshots serialised as dicts, in insertion order."""
        return [s.as_dict() for s in self.snapshots]

    def trend(self, metric: str = "modified") -> List[int]:
        """Return a list of *metric* values across snapshots in order.

        *metric* must be one of: added, removed, modified, identical.
        """
        valid = {"added", "removed", "modified", "identical"}
        if metric not in valid:
            raise ValueError(f"metric must be one of {sorted(valid)}, got {metric!r}")
        return [s.as_dict()[metric] for s in self.snapshots]

    def latest(self) -> Optional[Snapshot]:
        """Return the most recently added snapshot, or None if empty."""
        return self.snapshots[-1] if self.snapshots else None

    def between(
        self,
        start: datetime,
        end: datetime,
    ) -> "Timeline":
        """Return a new Timeline containing only snapshots within [start, end]."""
        filtered = [
            s for s in self.snapshots if start <= s.recorded_at <= end
        ]
        tl = Timeline()
        tl.snapshots = filtered
        return tl
