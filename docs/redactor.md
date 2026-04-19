# Redactor

The `redactor` module strips sensitive fields from schemas before diffing, exporting, or displaying results.

## Usage

```python
from streamdiff.redactor import redact_schema
from streamdiff.loader import load_schema

schema = load_schema("schema.json")
result = redact_schema(schema)

print(result.redacted_fields)  # ['password', 'api_key', ...]
print(result.schema)           # StreamSchema without sensitive fields
```

## Default Sensitive Patterns

The following substrings trigger redaction (case-insensitive):

- `password`
- `secret`
- `token`
- `key`
- `ssn`
- `credit`

## Custom Patterns

```python
result = redact_schema(schema, patterns=["internal", "private"])
```

## Bulk Redaction

```python
from streamdiff.redactor import redact_all

results = redact_all([schema_a, schema_b])
```

## RedactResult

| Attribute | Description |
|---|---|
| `original_count` | Total fields before redaction |
| `redacted_fields` | List of removed field names |
| `schema` | Cleaned `StreamSchema` |

`bool(result)` is `True` if any fields were redacted.

`result.to_dict()` returns a JSON-serialisable summary.
