# sqlsift.validator

The `validator` module provides lightweight schema and key-integrity checks
against a `DiffResult` before you act on its rows (e.g. apply a patch or
export a report).

## Functions

### `validate_keys(result, keys) -> ValidationReport`

Verifies that every row in *result* (across `added`, `removed`, and `modified`
buckets) contains **all** columns listed in `keys`.

```python
from sqlsift import diff, validate_keys

result = diff(old_rows, new_rows, keys=["id"])
report = validate_keys(result, keys=["id"])
if not report.is_valid:
    for issue in report.issues:
        print(issue.message)
```

### `validate_columns(result, expected_columns) -> ValidationReport`

Flags any column that appears in a diff row but is **not** listed in
`expected_columns`.  Useful for catching schema drift between environments.

```python
from sqlsift import validate_columns

report = validate_columns(result, expected_columns=["id", "name", "email"])
assert report.is_valid, report.as_dict()
```

### `validate_no_null_keys(result, keys) -> ValidationReport`

Ensures that none of the key columns hold a `None` value, which would make
row identity ambiguous.

```python
from sqlsift import validate_no_null_keys

report = validate_no_null_keys(result, keys=["id"])
```

## `ValidationReport`

| Attribute | Type | Description |
|-----------|------|-------------|
| `issues` | `List[ValidationIssue]` | All problems found |
| `is_valid` | `bool` | `True` when `issues` is empty |

### `.as_dict()`

Returns a JSON-serialisable dictionary:

```json
{
  "is_valid": false,
  "issue_count": 1,
  "issues": [
    {"kind": "missing_key", "message": "Key column 'id' missing from row at index 0", "row_index": 0}
  ]
}
```

## `ValidationIssue`

| Field | Values |
|-------|--------|
| `kind` | `"missing_key"`, `"unknown_column"`, `"null_key"` |
| `message` | Human-readable description |
| `row_index` | Position in the combined diff list (`-1` if not applicable) |
