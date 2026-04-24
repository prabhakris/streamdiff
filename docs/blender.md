# Schema Blender

The **blender** module merges two `StreamSchema` objects into a single unified schema.  Unlike the simpler `merger`, the blender accepts per-schema *weights* that control which schema wins when the same field exists in both with different types.

## Basic usage

```python
from streamdiff.blender import blend_schemas

result = blend_schemas(left_schema, right_schema)
print(result)  # BlendResult: N field(s), M conflict(s)
```

## Weighted blending

```python
result = blend_schemas(
    left_schema,
    right_schema,
    left_weight=1.0,
    right_weight=2.0,   # right schema is authoritative
)
```

When `right_weight > left_weight` and a field type conflict exists, the field definition from `right_schema` is kept.

## Conflict resolution rules

| Situation | Outcome |
|---|---|
| Field only in left | Kept as-is |
| Field only in right | Kept as-is |
| Same field, same type, both required | Kept required |
| Same field, same type, one optional | Required version wins |
| Same field, **different types**, equal weights | Left wins, conflict recorded |
| Same field, **different types**, `right_weight > left_weight` | Right wins, conflict recorded |

## BlendResult

```python
result.schema        # StreamSchema — the merged result
result.conflicts     # List[BlendConflict]
bool(result)         # True when no conflicts occurred
result.to_dict()     # JSON-serialisable summary
```

## BlendConflict

Each conflict carries:

- `field_name` — name of the conflicting field
- `left_type` / `right_type` — the competing types
- `chosen` — `"left"` or `"right"`, indicating which definition was kept

```python
for c in result.conflicts:
    print(c)  # conflict on 'count': integer vs string → chose left
    print(c.to_dict())
```

## When to use blender vs merger

| Use case | Module |
|---|---|
| Strict merge, fail on any conflict | `merger` |
| Weighted blend, tolerate conflicts | `blender` |
