# Field-Level Compatibility Scorer

The `scorer2` module provides fine-grained compatibility scoring for individual
schema field changes, using type compatibility rules from `comparator`.

## Scores

Each change receives a score between `0.0` (fully compatible) and `1.0` (fully breaking).

| Change Type | Condition | Score |
|---|---|---|
| Added | optional field | 0.1 |
| Added | required field | 0.8 |
| Removed | any | 1.0 |
| Type changed | safe widening (e.g. int→long) | 0.2 |
| Type changed | incompatible (e.g. long→int) | 0.9 |

## Usage

```python
from streamdiff.scorer2 import score_compatibility, overall_score

scores = score_compatibility(diff_result)
worst = overall_score(scores)

for s in scores:
    print(s)  # field_name: score=1.00 (field removed)
```

## API

### `score_compatibility(result: DiffResult) -> List[CompatibilityScore]`

Returns a `CompatibilityScore` for each change in the diff result.

### `overall_score(scores: List[CompatibilityScore]) -> float`

Returns the maximum score across all changes. Returns `0.0` if there are no changes.

### `CompatibilityScore`

- `field_name: str`
- `change_type: ChangeType`
- `score: float`
- `reason: str`
- `.to_dict()` — serialise to plain dict
