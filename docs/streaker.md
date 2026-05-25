# sqlsift.streaker

The `streaker` module detects **consecutive runs** (streaks) of the same diff
kind for a given logical key. This is useful when a migration produces repeated
inserts, deletes, or modifications for the same entity across multiple result
sets or ordered snapshots.

## Core types

### `Streak`

```python
@dataclass
class Streak:
    key: Tuple          # key values that identify the entity
    kind: str           # "added" | "removed" | "modified"
    rows: List[RowDiff] # ordered diffs that form the streak

    @property
    def length(self) -> int: ...

    def as_dict(self) -> dict: ...
```

## Functions

### `find_streaks(result, key_columns, min_length=2) -> List[Streak]`

Scans `result.diffs`, groups rows by `key_columns`, and returns every run of
consecutive same-kind diffs whose length is at least `min_length`.

```python
from sqlsift.streaker import find_streaks

streaks = find_streaks(result, key_columns=["order_id"], min_length=3)
for s in streaks:
    print(s.key, s.kind, s.length)
```

### `longest_streak(result, key_columns) -> Streak | None`

Returns the single longest streak across all keys, or `None` when the result
contains no diffs.

```python
from sqlsift.streaker import longest_streak

s = longest_streak(result, key_columns=["user_id"])
if s:
    print(f"Longest streak: {s.kind} × {s.length} for key {s.key}")
```

### `streak_summary(result, key_columns) -> dict`

Returns a high-level summary dictionary:

```python
{
    "total_streaks": 4,
    "max_length": 7,
    "by_kind": {"added": 2, "removed": 1, "modified": 1}
}
```

## Example

```python
from sqlsift import diff
from sqlsift.streaker import find_streaks, streak_summary

result = diff.compare(source_rows, target_rows, key_columns=["id"])

streaks = find_streaks(result, key_columns=["id"], min_length=2)
print(streak_summary(result, key_columns=["id"]))
```
