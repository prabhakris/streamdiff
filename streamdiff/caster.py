"""Cast schema fields to a target type with conflict detection."""
from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.schema import StreamSchema, SchemaField, FieldType


@dataclass
class CastResult:
    original: StreamSchema
    casted: StreamSchema
    coerced: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.skipped) == 0

    def to_dict(self) -> dict:
        return {
            "coerced": self.coerced,
            "skipped": self.skipped,
            "ok": bool(self),
        }

    def __str__(self) -> str:
        lines = []
        for name in self.coerced:
            lines.append(f"  ~ {name}: coerced to {self.casted.field_map[name].field_type.value}")
        for name in self.skipped:
            lines.append(f"  ! {name}: skipped (incompatible)")
        return "\n".join(lines) if lines else "No casts applied."


# Types that can be safely widened
_SAFE_WIDEN: dict = {
    FieldType.INT: {FieldType.LONG, FieldType.DOUBLE, FieldType.STRING},
    FieldType.LONG: {FieldType.DOUBLE, FieldType.STRING},
    FieldType.FLOAT: {FieldType.DOUBLE, FieldType.STRING},
    FieldType.DOUBLE: {FieldType.STRING},
    FieldType.BOOLEAN: {FieldType.STRING},
}


def _can_cast(src: FieldType, dst: FieldType) -> bool:
    if src == dst:
        return True
    return dst in _SAFE_WIDEN.get(src, set())


def cast_schema(
    schema: StreamSchema,
    target_type: FieldType,
    only: Optional[List[str]] = None,
) -> CastResult:
    """Attempt to cast fields in *schema* to *target_type*.

    If *only* is provided, only those field names are considered.
    """
    new_fields: List[SchemaField] = []
    coerced: List[str] = []
    skipped: List[str] = []

    candidates = set(only) if only else None

    for f in schema.fields:
        if candidates is not None and f.name not in candidates:
            new_fields.append(f)
            continue
        if f.field_type == target_type:
            new_fields.append(f)
        elif _can_cast(f.field_type, target_type):
            new_fields.append(
                SchemaField(name=f.name, field_type=target_type, required=f.required)
            )
            coerced.append(f.name)
        else:
            new_fields.append(f)
            skipped.append(f.name)

    casted = StreamSchema(name=schema.name, fields=new_fields)
    return CastResult(original=schema, casted=casted, coerced=coerced, skipped=skipped)
