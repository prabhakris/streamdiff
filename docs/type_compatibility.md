# Type Compatibility

`streamdiff` evaluates whether a field's type change between two schema versions
is **safe** (non-breaking) or **breaking**.

## Safe Widening Promotions

The following type changes are considered safe because consumers can read the
new type without data loss:

| From    | To       |
|---------|----------|
| `int`   | `long`   |
| `int`   | `float`  |
| `int`   | `double` |
| `long`  | `double` |
| `float` | `double` |

All other type changes are treated as **breaking**.

## Usage

```python
from streamdiff.schema import FieldType
from streamdiff.comparator import check_type_compatibility

result = check_type_compatibility(FieldType.INT, FieldType.LONG)
if result:
    print("Safe:", result.reason)
else:
    print("Breaking:", result.reason)
```

## Programmatic Access

To list all registered safe promotions:

```python
from streamdiff.comparator import compatible_types
for from_t, to_t in compatible_types():
    print(f"{from_t.value} -> {to_t.value}")
```

The validator (`streamdiff/validator.py`) uses `check_type_compatibility`
internally when reporting type-change issues.
