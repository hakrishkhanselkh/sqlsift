# sqlsift.windower

The `windower` module provides **sliding-window** views over a `DiffResult`,
allowing you to inspect a subset of rows at a time — useful for paginating
large diffs, computing rolling statistics, or narrowing results to a key range.

## Functions

### `by_index(result, size, step=1)`

Yields successive `DiffResult` windows of `size` rows, advancing by `step`
rows between each window.

```python
from sqlsift.windower import by_index

for window in by_index(result, size=100, step=50):
    print(len(window.diffs))  # up to 100 rows per window
```

- `size` — number of rows per window (must be ≥ 1)
- `step` — number of rows to advance between windows (must be ≥ 1)
- The last window may contain fewer than `size` rows.

### `by_key_range(result, key_col, start, end)`

Returns a `DiffResult` containing only rows where the value of `key_col`
falls within the **inclusive** range `[start, end]`.

```python
from sqlsift.windower import by_key_range

slice_ = by_key_range(result, key_col="order_id", start=1000, end=1999)
```

For `removed` rows the lookup uses `old_row`; for all others `new_row` is used.

### `rolling_counts(result, size, step=1)`

Yields `(window_index, counts_dict)` tuples where `counts_dict` has keys
`added`, `removed`, and `modified`.

```python
from sqlsift.windower import rolling_counts

for idx, counts in rolling_counts(result, size=50):
    print(idx, counts)
# 0 {'added': 12, 'removed': 3, 'modified': 35}
# 1 {'added': 8,  'removed': 5, 'modified': 37}
```

This is convenient for spotting *where* in a large result set most changes
are concentrated.

## Error handling

| Condition | Exception |
|---|---|
| `size <= 0` | `ValueError` |
| `step <= 0` | `ValueError` |
