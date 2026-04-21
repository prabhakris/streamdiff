"""Pad a schema with default/placeholder fields up to a target count."""

from dataclasses import dataclass, field
from typing import List, Optional

from streamdiff.schema import FieldType, SchemaField, StreamSchema


@dataclass
class PadResult:
    original_count: int
    target_count: int
    added_fields: List[SchemaField]
    schema: StreamSchema

    def __bool__(self) -> bool:
        return len(self.added_fields) > 0

    def to_dict(self) -> dict:
        return {
            "original_count": self.original_count,
            "target_count": self.target_count,
            "added_count": len(self.added_fields),
            "added_fields": [f.name for f in self.added_fields],
            "schema_fields": [f.name for f in self.schema.fields],
        }

    def __str__(self) -> str:
        if not self:
            return "No padding needed."
        names = ", ".join(f.name for f in self.added_fields)
        return (
            f"Padded {len(self.added_fields)} field(s): {names} "
            f"({self.original_count} -> {self.target_count})"
        )


def _make_pad_field(
    index: int,
    prefix: str = "pad_field",
    field_type: FieldType = FieldType.STRING,
    required: bool = False,
) -> SchemaField:
    return SchemaField(
        name=f"{prefix}_{index}",
        field_type=field_type,
        required=required,
    )


def pad_schema(
    schema: StreamSchema,
    target: int,
    prefix: str = "pad_field",
    field_type: FieldType = FieldType.STRING,
    required: bool = False,
) -> PadResult:
    """Pad *schema* with placeholder fields until it has *target* fields."""
    original_count = len(schema.fields)
    added: List[SchemaField] = []

    if target <= original_count:
        return PadResult(
            original_count=original_count,
            target_count=original_count,
            added_fields=[],
            schema=schema,
        )

    existing_names = {f.name for f in schema.fields}
    new_fields = list(schema.fields)
    idx = 1
    while len(new_fields) < target:
        candidate = _make_pad_field(idx, prefix=prefix, field_type=field_type, required=required)
        if candidate.name not in existing_names:
            new_fields.append(candidate)
            added.append(candidate)
            existing_names.add(candidate.name)
        idx += 1

    padded_schema = StreamSchema(name=schema.name, fields=new_fields)
    return PadResult(
        original_count=original_count,
        target_count=len(new_fields),
        added_fields=added,
        schema=padded_schema,
    )
