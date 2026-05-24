"""scorer.py – compute similarity and divergence scores for a DiffResult.

Scores are normalised to [0.0, 1.0] where 1.0 means the two result sets are
identical and 0.0 means they share nothing in common.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from .diff import DiffResult


@dataclass
class DiffScore:
    """Aggregated similarity metrics for a DiffResult."""

    total_rows: int
    identical_rows: int
    added_rows: int
    removed_rows: int
    modified_rows: int
    # per-column modification frequency (0.0 – 1.0 relative to modified_rows)
    column_change_rate: Dict[str, float] = field(default_factory=dict)

    @property
    def similarity(self) -> float:
        """Fraction of rows that are identical across both sets."""
        if self.total_rows == 0:
            return 1.0
        return self.identical_rows / self.total_rows

    @property
    def divergence(self) -> float:
        """Complement of similarity."""
        return 1.0 - self.similarity

    def as_dict(self) -> dict:
        return {
            "total_rows": self.total_rows,
            "identical_rows": self.identical_rows,
            "added_rows": self.added_rows,
            "removed_rows": self.removed_rows,
            "modified_rows": self.modified_rows,
            "similarity": round(self.similarity, 6),
            "divergence": round(self.divergence, 6),
            "column_change_rate": {
                col: round(rate, 6)
                for col, rate in self.column_change_rate.items()
            },
        }


def score(result: DiffResult) -> DiffScore:
    """Compute a :class:`DiffScore` from *result*.

    Parameters
    ----------
    result:
        A :class:`~sqlsift.diff.DiffResult` produced by :func:`~sqlsift.diff.diff`.

    Returns
    -------
    DiffScore
    """
    added = len(result.added)
    removed = len(result.removed)
    modified = len(result.modified)
    identical = len(result.identical) if hasattr(result, "identical") else 0

    total = added + removed + modified + identical

    # Build per-column change rates
    col_counts: Dict[str, int] = {}
    for row_diff in result.modified:
        for col in row_diff.delta:
            col_counts[col] = col_counts.get(col, 0) + 1

    col_rate: Dict[str, float] = {}
    if modified > 0:
        col_rate = {col: count / modified for col, count in col_counts.items()}

    return DiffScore(
        total_rows=total,
        identical_rows=identical,
        added_rows=added,
        removed_rows=removed,
        modified_rows=modified,
        column_change_rate=col_rate,
    )
