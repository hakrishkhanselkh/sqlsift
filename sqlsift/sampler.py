"""Sampling utilities for DiffResult — draw representative subsets of diffs."""

from __future__ import annotations

import random
from typing import Optional

from sqlsift.diff import DiffResult, RowDiff


def head(result: DiffResult, n: int) -> DiffResult:
    """Return the first *n* diffs from *result*, preserving order."""
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    return DiffResult(diffs=result.diffs[:n])


def tail(result: DiffResult, n: int) -> DiffResult:
    """Return the last *n* diffs from *result*, preserving order."""
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    return DiffResult(diffs=result.diffs[-n:] if n else [])


def random_sample(
    result: DiffResult,
    n: int,
    seed: Optional[int] = None,
) -> DiffResult:
    """Return a random sample of *n* diffs without replacement.

    Parameters
    ----------
    result:
        Source :class:`~sqlsift.diff.DiffResult`.
    n:
        Number of diffs to sample.  Clamped to ``len(result.diffs)``.
    seed:
        Optional RNG seed for reproducibility.
    """
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    rng = random.Random(seed)
    population = result.diffs
    k = min(n, len(population))
    sampled: list[RowDiff] = rng.sample(population, k)
    return DiffResult(diffs=sampled)


def stratified_sample(
    result: DiffResult,
    n_per_kind: int,
    seed: Optional[int] = None,
) -> DiffResult:
    """Return up to *n_per_kind* diffs for each diff kind (added/removed/modified).

    Parameters
    ----------
    result:
        Source :class:`~sqlsift.diff.DiffResult`.
    n_per_kind:
        Maximum diffs to include per kind.
    seed:
        Optional RNG seed for reproducibility.
    """
    if n_per_kind < 0:
        raise ValueError(f"n_per_kind must be >= 0, got {n_per_kind}")
    rng = random.Random(seed)
    buckets: dict[str, list[RowDiff]] = {}
    for diff in result.diffs:
        buckets.setdefault(diff.kind, []).append(diff)

    sampled: list[RowDiff] = []
    for kind in sorted(buckets):
        population = buckets[kind]
        k = min(n_per_kind, len(population))
        sampled.extend(rng.sample(population, k))
    return DiffResult(diffs=sampled)
