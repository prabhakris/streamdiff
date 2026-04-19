"""Clone (deep-copy) a StreamSchema, optionally remapping field types."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

from streamdiff.schema import StreamSchema, SchemaField, FieldType


@dataclass
class CloneResult:
    original: StreamSchema
    cloned: StreamSchema
    remapped: Dict[str, FieldType] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return True

    def to_dict(self) -> dict:
        return {
            "original_fields": len(self.original.fields),
            "cloned_fields": len(self.cloned.fields),
            "remapped": {k: v.value for k, v in self.remapped.items()},
        }

    def __str__(self) -> str:
        lines = [f"Cloned schema with {len(self.cloned.fields)} field(s)."]
        if self.remapped:
            for name, ft in self.remapped.items():
                lines.append(f"  remapped: {name} -> {ft.value}")
        return "\n".join(lines)


def clone_schema(
    schema: StreamSchema,
    type_map: Optional[Dict[str, FieldType]] = None,
    name_fn: Optional[Callable[[str], str]] = None,
) -> CloneResult:
    """Return a deep copy of *schema*.

    Args:
        schema:   Source schema to clone.
        type_map: Optional mapping of field-name -> new FieldType to apply
                  during cloning.
        name_fn:  Optional callable to transform each field name.
    """
    type_map = type_map or {}
    remapped: Dict[str, FieldType] = {}
    new_fields: list[SchemaField] = []

    for f in schema.fields:
        new_name = name_fn(f.name) if name_fn else f.name
        new_type = type_map.get(f.name, f.field_type)
        if new_type != f.field_type:
            remapped[new_name] = new_type
        new_fields.append(
            SchemaField(name=new_name, field_type=new_type, required=f.required)
        )

    cloned = StreamSchema(name=schema.name, fields=new_fields)
    return CloneResult(original=schema, cloned=cloned, remapped=remapped)
