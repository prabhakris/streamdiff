"""Retyper: bulk re-type fields in a schema according to a mapping."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from streamdiff.schema import FieldType, SchemaField, StreamSchema


@dataclass
class RetypeResult:
    original: StreamSchema
    updated: StreamSchema
    retyped: List[SchemaField] = field(default_factory=list)
    skipped: List[SchemaField] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.retyped) > 0

    def to_dict(self) -> dict:
        return {
            "retyped_count": len(self.retyped),
            "skipped_count": len(self.skipped),
            "retyped": [f.name for f in self.retyped],
            "skipped": [f.name for f in self.skipped],
        }

    def __str__(self) -> str:
        if not self.retyped:
            return "No fields retyped."
        lines = [f"Retyped {len(self.retyped)} field(s):"]
        for f in self.retyped:
            lines.append(f"  {f.name}: -> {f.field_type.value}")
        if self.skipped:
            lines.append(f"Skipped {len(self.skipped)} field(s) (type not in mapping).")
        return "\n".join(lines)


def retype_schema(
    schema: StreamSchema,
    type_map: Dict[FieldType, FieldType],
    names: Optional[List[str]] = None,
) -> RetypeResult:
    """Return a new schema with fields retyped according to type_map.

    Args:
        schema: The source schema.
        type_map: Mapping from old FieldType to new FieldType.
        names: If provided, only retype fields whose names are in this list.
    """
    new_fields: List[SchemaField] = []
    retyped: List[SchemaField] = []
    skipped: List[SchemaField] = []

    for f in schema.fields:
        if names is not None and f.name not in names:
            new_fields.append(f)
            continue
        if f.field_type in type_map:
            new_f = SchemaField(
                name=f.name,
                field_type=type_map[f.field_type],
                required=f.required,
            )
            new_fields.append(new_f)
            retyped.append(new_f)
        else:
            new_fields.append(f)
            skipped.append(f)

    updated = StreamSchema(name=schema.name, fields=new_fields)
    return RetypeResult(original=schema, updated=updated, retyped=retyped, skipped=skipped)
