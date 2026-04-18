# Migration Planner

The `streamdiff.planner` module converts a `DiffResult` into an ordered
`MigrationPlan` — a concrete list of steps a team can follow to migrate
their Kafka or Kinesis stream schema safely.

## Steps

Each `PlanStep` contains:

| Field | Description |
|-------|-------------|
| `order` | Execution order (type changes first, drops last) |
| `action` | One of `ADD_FIELD`, `DROP_FIELD`, `ALTER_TYPE`, `ALTER_NULLABILITY` |
| `field` | Field name |
| `detail` | Human-readable description of the change |
| `breaking` | Whether this step is a breaking change |

## Ordering

Steps are ordered to minimise risk:

1. `ALTER_TYPE` — must happen before consumers are updated
2. `ALTER_NULLABILITY` — adjust required/optional constraints
3. `ADD_FIELD` — safe to add after type changes settle
4. `DROP_FIELD` — only remove after all consumers have migrated

## Usage

```python
from streamdiff.loader import load_schema
from streamdiff.diff import compute_diff
from streamdiff.planner import build_plan

old = load_schema("schemas/v1.json")
new = load_schema("schemas/v2.json")
result = compute_diff(old, new)
plan = build_plan(result)

for step in plan.steps:
    print(step)
```

## JSON output

```python
import json
print(json.dumps(plan.to_dict(), indent=2))
```

Example output:

```json
{
  "steps": [
    {"order": 1, "action": "ALTER_TYPE", "field": "amount",
     "detail": "change type int -> long", "breaking": true},
    {"order": 2, "action": "ADD_FIELD", "field": "currency",
     "detail": "add optional field of type string", "breaking": false}
  ],
  "has_breaking": true
}
```

## Breaking changes

Check `plan.has_breaking` to gate CI pipelines:

```python
if plan.has_breaking:
    sys.exit(1)
```
