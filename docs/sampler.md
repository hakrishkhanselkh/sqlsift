# sqlsift.sampler

The `sampler` module provides utilities for drawing representative subsets
from a `DiffResult`.  This is useful when dealing with large migration diffs
where inspecting every row is impractical.

## Functions

### `head(result, n)`

Return the **first** `n` diffs from `result`, preserving the original order.

```python
from sqlsift.sampler import head

first_ten = head(diff_result, 10)
```

### `tail(result, n)`

Return the **last** `n` diffs from `result`, preserving the original order.

```python
from sqlsift.sampler import tail

last_ten = tail(diff_result, 10)
```

### `random_sample(result, n, seed=None)`

Return a **random sample** of `n` diffs without replacement.  Pass `seed` for
reproducible results.

```python
from sqlsift.sampler import random_sample

sample = random_sample(diff_result, 50, seed=42)
```

If `n` exceeds the number of available diffs the entire population is returned.

### `stratified_sample(result, n_per_kind, seed=None)`

Return up to `n_per_kind` diffs **for each diff kind** (`added`, `removed`,
`modified`).  This ensures every kind of change is represented even when one
kind dominates the result.

```python
from sqlsift.sampler import stratified_sample

# At most 5 added, 5 removed, 5 modified rows
sample = stratified_sample(diff_result, 5, seed=0)
```

## Error handling

All functions raise `ValueError` when `n` (or `n_per_kind`) is negative.

## Notes

- All functions return a **new** `DiffResult`; the original is never mutated.
- `random_sample` and `stratified_sample` accept an optional `seed` argument
  that is forwarded to `random.Random` for isolated, reproducible sampling.
