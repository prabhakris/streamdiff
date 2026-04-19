# Schema Pruner

The `pruner` module allows you to remove fields from a schema based on name lists or optionality.

## Use Cases

- Strip deprecated fields before publishing a cleaned schema
- Remove all optional fields to produce a minimal required-only schema
- Pre-process schemas before diffing to reduce noise

## API

### `prune_by_names(schema, names)`

Removes fields whose names appear in the provided set.

```python
from streamdiff.pruner import prune_by_names, apply_prune

result = prune_by_names(schema, {"legacy_field", "deprecated_id"})
cleaned = apply_prune(schema, result)
```

### `prune_optional(schema)`

Removes all fields where `required=False`.

```python
from streamdiff.pruner import prune_optional, apply_prune

result = prune_optional(schema)
required_only = apply_prune(schema, result)
```

### `apply_prune(schema, result)`

Returns a new `StreamSchema` containing only the kept fields. The original schema is not modified.

## `PruneResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `pruned`  | `List[SchemaField]` | Fields that were removed |
| `kept`    | `List[SchemaField]` | Fields that were retained |

```python
print(result)          # human-readable summary
print(result.to_dict()) # dict for JSON export
bool(result)           # True if any fields were pruned
```
