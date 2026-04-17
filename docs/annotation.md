# Change Annotation

The `--annotate` flag adds human-readable descriptions and actionable hints to each detected schema change.

## Usage

```bash
streamdiff diff old_schema.json new_schema.json --annotate
```

## Output

For each change, `streamdiff` prints:

- A **description** summarising what changed and how.
- A **hint** suggesting what to check or fix.

### Example

```
  [removed] Field 'user_id' was removed
    Hint: Consumers reading this field will break.
  [added] Field 'user_uuid' was added (required)
    Hint: Ensure consumers handle missing values if field is required.
```

## Change Types

| Change Type       | Description Template                                      |
|-------------------|-----------------------------------------------------------|
| `added`           | Field `{name}` was added (`required`/`optional`)          |
| `removed`         | Field `{name}` was removed                                |
| `type_changed`    | Field `{name}` type changed from `{old}` to `{new}`       |
| `required_changed`| Field `{name}` required flag changed to `{required}`      |

## Programmatic Use

```python
from streamdiff.annotator import annotate_all

annotated = annotate_all(diff_result.changes)
for a in annotated:
    print(a.description)
    print(a.hint)
```
