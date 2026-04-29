"""rotator.py — rotate (cycle) field order in a schema by a given offset."""
from dataclasses import dataclass, field
from typing import List

from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class RotateResult:
    original: StreamSchema
    rotated: StreamSchema
    offset: int
    total: int

    def __bool__(self) -> bool:
        return self.offset % max(self.total, 1) != 0

    def to_dict(self) -> dict:
        return {
            "offset": self.offset,
            "total": self.total,
            "rotated": self.offset % max(self.total, 1) != 0,
            "fields": [
                {"name": f.name, "type": f.field_type.value, "required": f.required}
                for f in self.rotated.fields
            ],
        }

    def __str__(self) -> str:
        lines = [f"Rotate offset={self.offset} total={self.total}"]
        for f in self.rotated.fields:
            req = "required" if f.required else "optional"
            lines.append(f"  {f.name} ({f.field_type.value}, {req})")
        return "\n".join(lines)


def rotate_schema(schema: StreamSchema, offset: int = 1) -> RotateResult:
    """Return a new schema with fields rotated left by *offset* positions."""
    fields: List[SchemaField] = list(schema.fields)
    n = len(fields)
    if n == 0:
        rotated_fields: List[SchemaField] = []
    else:
        effective = offset % n
        rotated_fields = fields[effective:] + fields[:effective]

    rotated = StreamSchema(name=schema.name, fields=rotated_fields)
    return RotateResult(
        original=schema,
        rotated=rotated,
        offset=offset,
        total=n,
    )
