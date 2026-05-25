# sqlsift.transformer

The `transformer` module provides utilities for reshaping rows within a
`DiffResult` — renaming columns, dropping unwanted fields, and applying
arbitrary value transformations — without mutating the original data.

---

## Functions

### `transform_rows(diff_result, transforms)`

Apply one or more column-level callables to every row (and delta) in a
`DiffResult`.

```python
from sqlsift.transformer import transform_rows

result = transform_rows(diff_result, {
    "price": float,
    "name": str.strip,
})
```

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `diff_result` | `DiffResult` | Source result to transform. |
| `transforms` | `dict[str, Callable]` | Mapping of column → transform function. |

**Returns** a new `DiffResult`; the original is not mutated.

For `modified` rows the transform is applied to **both** the old and new
values stored in `delta`.

---

### `rename_columns(diff_result, rename_map)`

Return a new result with columns renamed according to *rename_map*.

```python
from sqlsift.transformer import rename_columns

result = rename_columns(diff_result, {"emp_name": "name", "emp_id": "id"})
```

Columns not present in *rename_map* are left unchanged.  Delta keys are
renamed alongside row keys.

---

### `drop_columns(diff_result, columns)`

Strip one or more columns from every row and delta entry.

```python
from sqlsift.transformer import drop_columns

result = drop_columns(diff_result, ["internal_id", "_checksum"])
```

Useful for removing audit columns or secrets before exporting a report.

---

## Chaining transformations

Because every function returns a new `DiffResult` you can chain calls
freely:

```python
from sqlsift.transformer import drop_columns, rename_columns, transform_rows

cleaned = (
    diff_result
    | (lambda r: drop_columns(r, ["_ts"]))
    | (lambda r: rename_columns(r, {"usr": "user"}))
    | (lambda r: transform_rows(r, {"salary": float}))
)
```

Or using plain function calls:

```python
step1 = drop_columns(diff_result, ["_ts"])
step2 = rename_columns(step1, {"usr": "user"})
final = transform_rows(step2, {"salary": float})
```
