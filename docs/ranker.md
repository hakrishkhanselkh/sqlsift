# sqlsift.ranker

The `ranker` module orders the rows in a `DiffResult` by importance so you
can focus review effort on the most significant changes.

## Functions

### `by_column(result, column, *, ascending=False, limit=None)`

Rank every diff by the magnitude of change in a numeric *column*.

| Row kind   | Score used                          |
|------------|-------------------------------------|
| `modified` | `abs(new_value - old_value)`        |
| `added`    | `new_value`                         |
| `removed`  | `old_value`                         |

Returns a list of `RowDiff` objects sorted highest-score first (or
lowest-first when `ascending=True`).  Pass `limit` to cap the result.

```python
from sqlsift import ranker

top_changes = ranker.by_column(result, "revenue", limit=10)
for rd in top_changes:
    print(rd.key, rd.delta)
```

### `by_score(result, score_fn, *, ascending=False, limit=None)`

Rank diffs using an arbitrary callable `score_fn(row_diff) -> float`.

```python
ranked = ranker.by_score(
    result,
    score_fn=lambda rd: len(rd.delta),   # rows with most changed columns first
)
```

### `top_n(result, column, n=10)`

Convenience wrapper — returns the **n** diffs with the largest absolute
change in *column*.

```python
from sqlsift import ranker

biggest = ranker.top_n(result, "price", n=5)
```

### `bottom_n(result, column, n=10)`

Convenience wrapper — returns the **n** diffs with the smallest absolute
change in *column*.

```python
smallest = ranker.bottom_n(result, "price", n=5)
```

## Notes

- Missing or non-numeric column values are treated as `0.0`.
- All functions return plain `list[RowDiff]`; the original `DiffResult` is
  never mutated.
