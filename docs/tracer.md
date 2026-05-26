# sqlsift.tracer

Track how individual row keys evolve across multiple `DiffResult` snapshots.

## Overview

When you run the same diff query at different points in time (e.g. after each
migration step), `tracer` lets you follow a specific row through those
snapshots and see whether it was `added`, `modified`, or `removed` at each
stage.

## API

### `trace(snapshots, key_columns=None) -> List[TraceEntry]`

Builds a trace index from an ordered list of `(label, DiffResult)` pairs.

```python
from sqlsift.tracer import trace

entries = trace(
    [("before", result_v1), ("after", result_v2)],
    key_columns=["id"],
)
```

`key_columns` specifies which columns form the row identity.  If omitted the
entire row dict is used as the key.

### `persistent_keys(entries, labels) -> List[TraceEntry]`

Returns entries that appear in **every** listed label — rows that were touched
in all snapshots.

```python
from sqlsift.tracer import persistent_keys

stable = persistent_keys(entries, ["before", "after"])
```

### `transient_keys(entries, labels) -> List[TraceEntry]`

Returns entries that appear in **some but not all** listed labels — rows that
appear or disappear between snapshots.

### `kind_changed(entries, from_label, to_label) -> List[TraceEntry]`

Returns entries whose diff `kind` (`added` / `modified` / `removed`) differs
between two specific labels.

```python
from sqlsift.tracer import kind_changed

flipped = kind_changed(entries, "before", "after")
for e in flipped:
    print(e.key, e.appearances)
```

## `TraceEntry`

| Attribute | Type | Description |
|-----------|------|-------------|
| `key` | `tuple` | Row identity derived from `key_columns` |
| `appearances` | `dict[str, str]` | Maps snapshot label → diff kind |

`TraceEntry.as_dict()` returns a plain dictionary suitable for JSON
serialization.

## Example

```python
from sqlsift.tracer import trace, kind_changed

entries = trace(
    [("step1", diff1), ("step2", diff2), ("step3", diff3)],
    key_columns=["order_id"],
)

# rows that changed kind between step1 and step3
for e in kind_changed(entries, "step1", "step3"):
    print(e.key, ":", e.appearances["step1"], "->", e.appearances["step3"])
```
