# sqlsift.router

The `router` module routes rows from a `DiffResult` into named **buckets** based on ordered rules. The first matching rule wins, making it easy to build priority-based triage workflows.

## Quick Start

```python
from sqlsift.router import route, rule_by_kind, rule_by_column_value, sizes

routing = route(
    result,
    rules=[
        rule_by_kind("added", "new_rows"),
        rule_by_kind("removed", "deleted_rows"),
        rule_by_column_value("region", "US", "us_changes"),
    ],
    default_bucket="other",
)

print(sizes(routing))
# {'new_rows': 12, 'deleted_rows': 4, 'us_changes': 7, 'other': 31}
```

## API

### `route(result, rules, default_bucket="unmatched") -> Dict[str, DiffResult]`

Apply *rules* in order against every `RowDiff` in *result*. Returns a mapping of bucket name → `DiffResult`. Rows that match no rule are placed in *default_bucket*.

### `rule_by_kind(kind, bucket) -> Rule`

Route rows whose `.kind` equals *kind* (`"added"`, `"removed"`, `"modified"`, `"unchanged"`) into *bucket*.

### `rule_by_column_value(column, value, bucket) -> Rule`

Route rows where the given column equals *value* into *bucket*. Uses `left` if available, otherwise `right`.

### `rule_by_predicate(predicate, bucket) -> Rule`

Route rows for which `predicate(row)` returns `True` into *bucket*.

### `bucket_names(routing) -> List[str]`

Return sorted bucket names from a routing dict.

### `sizes(routing) -> Dict[str, int]`

Return a mapping of bucket name → row count.

## Notes

- Rules are evaluated **in order**; the first match wins.
- `key_columns` from the source `DiffResult` are preserved in every bucket.
- Buckets are only created when at least one row matches.
