"""Trim schemas by removing fields that match given criteria."""
from dataclasses import dataclass, field
from typing import List, Optional, Set
from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class TrimResult:
    original_count: int
    trimmed: List[SchemaField]
    schema: StreamSchema

    def __bool__(self) -> bool:
        return len(self.trimmed) > 0

    def to_dict(self) -> dict:
        return {
            "original_count": self.original_count,
            "trimmed_count": len(self.trimmed),
            "trimmed_fields": [f.name for f in self.trimmed],
            "remaining_count": len(self.schema.fields),
        }

    def __str__(self) -> str:
        if not self.trimmed:
            return "No fields trimmed."
        names = ", ".join(f.name for f in self.trimmed)
        return f"Trimmed {len(self.trimmed)} field(s): {names}"


def trim_by_types(schema: StreamSchema, type_names: Set[str]) -> TrimResult:
    """Remove fields whose type name is in type_names."""
    kept, removed = [], []
    for f in schema.fields:
        if f.field_type.value in type_names:
            removed.append(f)
        else:
            kept.append(f)
    new_schema = StreamSchema(name=schema.name, fields=kept)
    return TrimResult(original_count=len(schema.fields), trimmed=removed, schema=new_schema)


def trim_by_pattern(schema: StreamSchema, pattern: str) -> TrimResult:
    """Remove fields whose name contains the given substring."""
    kept, removed = [], []
    for f in schema.fields:
        if pattern.lower() in f.name.lower():
            removed.append(f)
        else:
            kept.append(f)
    new_schema = StreamSchema(name=schema.name, fields=kept)
    return TrimResult(original_count=len(schema.fields), trimmed=removed, schema=new_schema)


def trim_optional(schema: StreamSchema) -> TrimResult:
    """Remove all optional fields from the schema."""
    kept, removed = [], []
    for f in schema.fields:
        if not f.required:
            removed.append(f)
        else:
            kept.append(f)
    new_schema = StreamSchema(name=schema.name, fields=kept)
    return TrimResult(original_count=len(schema.fields), trimmed=removed, schema=new_schema)
