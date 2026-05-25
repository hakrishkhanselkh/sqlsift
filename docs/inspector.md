# sqlsift.inspector

The `inspector` module provides lightweight introspection utilities for a
`DiffResult`, letting you understand its structure and column metadata without
running a full summarization pass.

## Functions

### `column_names(result) -> list[str]`

Return a sorted list of every column name observed across all rows and delta
dictionaries in *result*.

```python
from sqlsift import inspector
cols = inspector.column_names(result)
print(cols)  # ['id', 'name', 'score']
```

### `key_columns(result) -> list[str]`

Return the key columns stored on *result* (if any), otherwise an empty list.

### `row_count(result) -> dict[str, int]`

Return a breakdown of diff rows by kind.

```python
counts = inspector.row_count(result)
# {'added': 3, 'removed': 1, 'modified': 7}
```

### `has_column(result, column) -> bool`

Quickly check whether *column* appears in any row of *result*.

### `sample_values(result, column, limit=5) -> list`

Return up to *limit* distinct values for *column* sampled from the result rows
in order.  Useful for a quick sanity-check of a column's contents.

```python
vals = inspector.sample_values(result, "status", limit=3)
print(vals)  # ['active', 'inactive', 'pending']
```

### `schema(result) -> dict[str, str]`

Infer a simple Python type name (`"int"`, `"str"`, `"float"`, …) for each
column based on the first non-`None` value found.  Columns where every
observed value is `None` are reported as `"unknown"`.

```python
s = inspector.schema(result)
# {'id': 'int', 'name': 'str', 'score': 'float'}
```

### `inspect(result) -> dict`

Convenience wrapper that returns all of the above in a single dictionary.

```python
info = inspector.inspect(result)
print(info["total"])    # total number of diff rows
print(info["columns"])  # sorted column list
print(info["schema"])   # inferred types
```
