# sqlsift.classifier

The `classifier` module lets you assign human-readable labels to rows in a
`DiffResult` based on a prioritised list of *rules*.  Rules are plain callables
that inspect a `RowDiff` and return a label string (or `None` to defer to the
next rule).  Rows that match no rule are placed in the `"unclassified"` bucket.

## Quick start

```python
from sqlsift.classifier import classify, rule_by_kind, rule_by_column_value, label_counts

rules = [
    rule_by_column_value("region", "EU", "european"),
    rule_by_kind("added",    "new_row"),
    rule_by_kind("removed",  "deleted"),
    rule_by_kind("modified", "changed"),
]

buckets = classify(result, rules)
print(label_counts(buckets))
# {'european': 3, 'new_row': 12, 'deleted': 5, 'changed': 8, 'unclassified': 1}
```

## API

### `classify(result, rules) -> dict[str, list[RowDiff]]`

Iterate over every `RowDiff` in `result` and apply each rule in order.  The
first rule that returns a non-`None` string wins.  Returns a dictionary mapping
label → list of matching rows.

### `rule_by_kind(kind, label) -> Rule`

Built-in rule factory.  Matches rows whose `kind` attribute equals `kind`
(`"added"`, `"removed"`, or `"modified"`).

### `rule_by_column_value(column, value, label) -> Rule`

Matches rows where `column` in the left (or right) row equals `value`.

### `rule_by_predicate(predicate, label) -> Rule`

Matches rows for which `predicate(row)` returns `True`.  Use this to express
arbitrary logic that the built-in factories cannot capture.

### `label_counts(classified) -> dict[str, int]`

Convenience helper that converts the output of `classify` into a simple
`{label: count}` mapping for reporting.

## Writing custom rules

A rule is any callable with the signature `(row: RowDiff) -> str | None`:

```python
def high_value_change(row):
    if row.kind == "modified":
        delta = row.delta.get("revenue", {})
        if abs(delta.get("right", 0) - delta.get("left", 0)) > 10_000:
            return "high_value_change"
    return None

buckets = classify(result, [high_value_change])
```
