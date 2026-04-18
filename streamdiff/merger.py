"""Merge two StreamSchemas, with configurable conflict resolution."""
from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class MergeConflict:
    field_name: str
    base_field: SchemaField
    other_field: SchemaField

    def __str__(self) -> str:
        return (
            f"Conflict on '{self.field_name}': "
            f"base={self.base_field.field_type.value} "
            f"other={self.other_field.field_type.value}"
        )


@dataclass
class MergeResult:
    schema: Optional[StreamSchema]
    conflicts: List[MergeConflict] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.conflicts) == 0


def merge_schemas(
    base: StreamSchema,
    other: StreamSchema,
    prefer: str = "base",
) -> MergeResult:
    """Merge *other* into *base*.

    Args:
        base: The base schema.
        other: The schema to merge in.
        prefer: When a type conflict occurs, keep 'base' or 'other' field.
                Any other value leaves the conflict unresolved (schema=None).
    """
    if prefer not in ("base", "other"):
        raise ValueError("prefer must be 'base' or 'other'")

    base_map = base.field_map()
    other_map = other.field_map()
    conflicts: List[MergeConflict] = []
    merged: List[SchemaField] = []

    for name, base_field in base_map.items():
        if name in other_map:
            other_field = other_map[name]
            if base_field.field_type != other_field.field_type:
                conflicts.append(MergeConflict(name, base_field, other_field))
                merged.append(base_field if prefer == "base" else other_field)
            else:
                # keep required=True if either side requires it
                kept = SchemaField(
                    name=base_field.name,
                    field_type=base_field.field_type,
                    required=base_field.required or other_field.required,
                )
                merged.append(kept)
        else:
            merged.append(base_field)

    for name, other_field in other_map.items():
        if name not in base_map:
            merged.append(other_field)

    result_schema = StreamSchema(name=base.name, fields=merged)
    return MergeResult(schema=result_schema, conflicts=conflicts)
