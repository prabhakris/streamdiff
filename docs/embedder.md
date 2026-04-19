# Embedder

The `embed` subcommand converts each field in a schema into a numeric feature vector. This is useful for downstream similarity comparisons or visualisation.

## Vector Format

Each vector has `1 + N` components where `N` is the number of supported `FieldType` values:

| Index | Meaning |
|-------|---------|
| 0 | `1.0` if the field is required, `0.0` otherwise |
| 1…N | One-hot encoding of the field type |

## Usage

```bash
# Print vectors for all fields (text)
streamdiff embed schema.json

# JSON output
streamdiff embed schema.json --json

# Single field
streamdiff embed schema.json --field user_id
```

## Example Output (text)

```
EmbedVector(user_id: [1.00, 1.00, 0.00, 0.00, 0.00, 0.00])
EmbedVector(score: [1.00, 0.00, 0.00, 1.00, 0.00, 0.00])
```

## Cosine Similarity

You can compare two field vectors programmatically:

```python
from streamdiff.embedder import embed_schema, cosine_similarity
from streamdiff.loader import load_schema

old = load_schema("old.json")
new = load_schema("new.json")

old_report = embed_schema(old)
new_report = embed_schema(new)

v_old = old_report.by_field("price")
v_new = new_report.by_field("price")

if v_old and v_new:
    sim = cosine_similarity(v_old.values, v_new.values)
    print(f"Similarity: {sim:.4f}")
```

A similarity of `1.0` means the fields are identical in type and requiredness. A value closer to `0.0` indicates structural divergence.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Input error (file not found, unknown field) |
