# Schema Composer

The **composer** module merges multiple `StreamSchema` objects into a single unified schema, surfacing field-level conflicts when the same field name appears in more than one source with incompatible types.

## Core API

```python
from streamdiff.composer import compose_schemas

result = compose_schemas(
    [("orders", schema_a), ("payments", schema_b)],
    on_conflict="fail",  # "fail" | "first" | "last"
)

if result:
    print(result.schema.fields)
else:
    for conflict in result.conflicts:
        print(conflict)
```

## `on_conflict` modes

| Mode | Behaviour |
|------|-----------|
| `fail` (default) | Returns `None` for `schema`; all conflicts reported. |
| `first` | Keeps the field type from the first schema that defined it. |
| `last` | Overwrites with the field type from the most recent schema. |

## Conflict resolution rules

- **Same name, same type** — no conflict; `required=True` wins if either source marks the field required.
- **Same name, different type** — conflict recorded regardless of mode; schema is only `None` in `fail` mode.

## `ComposeResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `schema` | `StreamSchema \| None` | Merged schema (`None` on unresolved conflict in `fail` mode). |
| `conflicts` | `list[ComposeConflict]` | All detected conflicts. |
| `source_names` | `list[str]` | Ordered list of source names passed in. |

`bool(result)` is `True` when there are no conflicts.

## `ComposeConflict`

```python
conflict.field_name   # str
conflict.sources      # ["schema_a", "schema_b"]
conflict.reason       # human-readable explanation
conflict.to_dict()    # serialisable dict
```

## CLI integration

The composer is used internally by `streamdiff merge` and `streamdiff resolve` when combining more than two schemas. It can also be invoked programmatically for pipeline use-cases where schemas from multiple Kafka topics must be unified before validation.
