# sqlsift.normalizer

The `normalizer` module provides helpers to coerce and standardize column values
across the rows of a `DiffResult`. This is useful when source and target
databases store the same data in slightly different formats (e.g. trailing
spaces, mixed case, numeric strings) and you want to compare semantically
equivalent values rather than literal strings.

## Functions

### `normalize_row(row_diff, coercers) -> RowDiff`

Apply a dictionary of coercer functions to both `left` and `right` sides of a
`RowDiff`. Returns a new `RowDiff`; the original is not mutated.

```python
from sqlsift.normalizer import normalize_row, to_numeric

coercers = to_numeric(["price", "qty"])
new_row = normalize_row(row, coercers)
```

### `normalize_result(result, coercers) -> DiffResult`

Apply coercers to every row in a `DiffResult`, returning a new `DiffResult`.

```python
from sqlsift.normalizer import normalize_result, strip_whitespace

cleaned = normalize_result(result, strip_whitespace(["name", "email"]))
```

### `strip_whitespace(columns) -> dict`

Builds a coercers dict that strips leading and trailing whitespace from the
specified string columns.

### `to_lowercase(columns) -> dict`

Builds a coercers dict that converts the specified columns to lowercase strings.

### `to_numeric(columns, cast=float) -> dict`

Builds a coercers dict that casts the specified columns to a numeric type
(default `float`). Values that cannot be converted are left unchanged.

### `chain(*coercer_dicts) -> dict`

Merge multiple coercer dicts into one. Later dicts take precedence when the
same column appears in more than one dict.

```python
from sqlsift.normalizer import chain, strip_whitespace, to_lowercase

coercers = chain(
    strip_whitespace(["name", "city"]),
    to_lowercase(["name"]),
)
normalized = normalize_result(result, coercers)
```

## Notes

- `None` values in a column are skipped by all built-in coercers.
- Coercion errors (`ValueError`, `TypeError`) are silently ignored; the
  original value is preserved.
- `normalize_row` handles `added` rows (where `left` is `None`) and `removed`
  rows (where `right` is `None`) safely.
