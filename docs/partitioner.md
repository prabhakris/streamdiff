# Partitioner

The `partitioner` module splits schema fields into logical **buckets** based on a chosen strategy.
This is useful for understanding the structure of a schema at a glance or for downstream processing
that needs to operate on subsets of fields.

## Strategies

### `required` (default)

Splits fields into `required` and `optional` buckets.

```bash
streamdiff partition schema.json
```

### `type`

Groups fields by their data type (e.g., `string`, `int`, `boolean`).

```bash
streamdiff partition schema.json --strategy type
```

### `prefix`

Groups fields by the prefix of their name, using a configurable separator.

```bash
streamdiff partition schema.json --strategy prefix --separator _
```

Fields without the separator are placed in the `unpartitioned` list.

## JSON Output

Add `--json` to receive machine-readable output:

```bash
streamdiff partition schema.json --json
```

```json
{
  "strategy": "required",
  "partitions": {
    "required": [{"name": "id", "type": "string", "required": true}],
    "optional": [{"name": "label", "type": "string", "required": false}]
  },
  "unpartitioned": []
}
```

## Python API

```python
from streamdiff.partitioner import partition
from streamdiff.loader import load_schema

schema = load_schema("schema.json")
result = partition(schema, strategy="prefix", separator="_")
print(result)
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Success |
| 2    | Error loading schema or unknown strategy |
