# sqlsift.timeline

The `timeline` module lets you record a series of `DiffResult` snapshots over time and analyse how your data migration progresses across runs.

## Core types

### `Snapshot`

A single point-in-time capture of a `DiffResult`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `result` | `DiffResult` | The diff at this point in time |
| `label` | `str` | Human-readable name (e.g. `"run-42"`, `"2024-01-15"`) |
| `recorded_at` | `datetime` | UTC timestamp; defaults to *now* |

```python
snap.as_dict()
# {'label': 'run-1', 'recorded_at': '2024-01-01T00:00:00+00:00',
#  'added': 3, 'removed': 0, 'modified': 12, 'identical': 85}
```

### `Timeline`

An ordered list of `Snapshot` objects with helper methods.

## Usage

```python
from sqlsift.timeline import Timeline

tl = Timeline()

# Record snapshots as migration runs complete
tl.add(result_run1, label="run-1")
tl.add(result_run2, label="run-2")
tl.add(result_run3, label="run-3")

# Inspect the latest snapshot
print(tl.latest().as_dict())

# See how modified-row counts change across runs
print(tl.trend("modified"))   # e.g. [47, 21, 3]
print(tl.trend("added"))      # e.g. [0, 0, 0]
```

## API reference

### `Timeline.add(result, label, recorded_at=None) -> Snapshot`

Append a snapshot. If `recorded_at` is omitted the current UTC time is used.

### `Timeline.latest() -> Snapshot | None`

Return the most recently added snapshot, or `None` if the timeline is empty.

### `Timeline.trend(metric) -> list[int]`

Return a list of integer values for *metric* across all snapshots in insertion order.

Valid metrics: `"added"`, `"removed"`, `"modified"`, `"identical"`.

### `Timeline.as_dict_list() -> list[dict]`

Serialise every snapshot to a dict; useful for JSON export or DataFrame creation.

### `Timeline.between(start, end) -> Timeline`

Return a new `Timeline` containing only snapshots whose `recorded_at` falls within `[start, end]`.

```python
from datetime import datetime, timezone

start = datetime(2024, 6, 1, tzinfo=timezone.utc)
end   = datetime(2024, 6, 30, tzinfo=timezone.utc)
june_runs = tl.between(start, end)
```
