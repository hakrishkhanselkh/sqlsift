# sqlsift.mapper

The `mapper` module provides utilities for transforming column values across every
row in a `DiffResult` without altering the diff structure itself.

## Functions

### `map_rows(result, spec) -> DiffResult`

Apply a dictionary of `{column: callable}` mappings to every row.  For
`modified` diffs the mapping is also applied to both sides of the `delta`.

```python
from sqlsift.mapper import map_rows

result = map_rows(result, {"price": lambda v: round(v, 2)})
```

### `rename_key(result, old, new) -> DiffResult`

Rename a column across all rows and deltas.

```python
from sqlsift.mapper import rename_key

result = rename_key(result, "amt", "amount")
```

### `cast_column(result, column, dtype) -> DiffResult`

Convenience wrapper around `map_rows` that casts a single column to *dtype*.
`None` values are passed through unchanged.

```python
from sqlsift.mapper import cast_column

result = cast_column(result, "quantity", int)
```

## Notes

- All functions return a **new** `DiffResult`; the original is never mutated.
- Columns absent from a row are silently skipped.
- `map_rows` can be chained with `sqlsift.pipeline.Pipeline` for multi-step
  transformations.
