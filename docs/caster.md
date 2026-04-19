# Schema Caster

The `caster` module allows you to cast fields in a schema to a target type,
detecting which fields can be safely widened and which must be skipped.

## Usage

```python
from streamdiff.loader import load_schema
from streamdiff.caster import cast_schema
from streamdiff.schema import FieldType

schema = load_schema("my_schema.json")
result = cast_schema(schema, FieldType.STRING)

print(result)
print(result.to_dict())
```

## Selective casting

Pass an `only` list to restrict which fields are candidates:

```python
result = cast_schema(schema, FieldType.DOUBLE, only=["price", "amount"])
```

## Safe widening rules

| Source  | Safe targets                   |
|---------|--------------------------------|
| int     | long, double, string           |
| long    | double, string                 |
| float   | double, string                 |
| double  | string                         |
| boolean | string                         |

Any cast outside these rules is marked as **skipped** and the original field
is preserved unchanged.

## CastResult

| Attribute  | Description                              |
|------------|------------------------------------------|
| `coerced`  | List of field names successfully cast    |
| `skipped`  | List of field names that could not cast  |
| `casted`   | New `StreamSchema` with applied changes  |
| `original` | Unmodified source schema                 |

`bool(result)` is `True` when no fields were skipped.
