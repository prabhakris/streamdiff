# Schema Stretcher

The **stretcher** module expands an existing schema by generating field variants
based on suffixes or by injecting fields of missing types.

## Use Cases

- Generate `_raw` / `_clean` / `_normalized` variants of every field for ETL pipelines.
- Ensure a schema covers all required primitive types before publishing.

## Python API

```python
from streamdiff.loader import load_schema
from streamdiff.stretcher import stretch_by_suffix, stretch_by_types
from streamdiff.schema import FieldType

schema = load_schema("events.json")

# Add _raw and _clean variants for every field
result = stretch_by_suffix(schema, ["raw", "clean"], required=False)
print(result)  # StretchResult: +4 fields (2 -> 6)

# Inject missing types
result2 = stretch_by_types(schema, [FieldType.BOOLEAN, FieldType.FLOAT])
for f in result2.added_fields:
    print(f"  + {f.name}")
```

## CLI

```bash
# Expand with suffixes
streamdiff stretch events.json --suffix raw clean

# Inject missing types
streamdiff stretch events.json --types boolean float

# Mark generated fields as required
streamdiff stretch events.json --suffix v2 --required

# JSON output
streamdiff stretch events.json --suffix raw --json
```

## Output (text)

```
StretchResult: +2 fields (2 -> 4)
  + user_id_raw (string, optional)
  + score_raw (integer, optional)
```

## Output (JSON)

```json
{
  "original_count": 2,
  "expanded_count": 4,
  "added_fields": ["user_id_raw", "score_raw"]
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Success |
| 2    | Bad input (missing file, unknown type, no operation) |
