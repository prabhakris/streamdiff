# Schema Splitter

The `splitter` module partitions a `StreamSchema` into multiple sub-schemas
based on field name prefixes or explicit grouping rules.

## Use Cases

- Decompose a wide schema into domain-specific sub-schemas.
- Validate only a subset of fields relevant to a service.
- Prepare schemas for targeted diff comparisons.

## split_by_prefix

Groups fields by the first component of their name when split by a separator
(default `_`).

```python
from streamdiff.splitter import split_by_prefix

result = split_by_prefix(schema)
for group_name, sub_schema in result.groups.items():
    print(group_name, [f.name for f in sub_schema.fields])
```

Fields with no separator are placed in `result.unmatched`.

## split_by_names

Explicitly assigns fields to named groups.

```python
from streamdiff.splitter import split_by_names

result = split_by_names(schema, {
    "identity": ["user_id", "email"],
    "order":    ["order_id", "amount"],
})
```

Any field not listed in any group ends up in `result.unmatched`.

## SplitResult

| Attribute   | Type                        | Description                        |
|-------------|-----------------------------|------------------------------------|  
| `groups`    | `Dict[str, StreamSchema]`   | Named sub-schemas                  |
| `unmatched` | `StreamSchema`              | Fields not assigned to any group   |

`bool(result)` is `True` when at least one group was created.

`result.to_dict()` returns a JSON-serialisable summary.
