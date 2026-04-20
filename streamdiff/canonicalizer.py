"""Canonicalize a StreamSchema into a stable, normalized representation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from streamdiff.schema import StreamSchema, SchemaField, FieldType


@dataclass
class CanonicalField:
    name: str
    type: str
    required: bool

    def to_dict(self) -> dict:
        return {"name": self.name, "type": self.type, "required": self.required}

    def __str__(self) -> str:
        req = "required" if self.required else "optional"
        return f"{self.name}: {self.type} ({req})"


@dataclass
class CanonicalSchema:
    name: str
    fields: List[CanonicalField] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "fields": [f.to_dict() for f in self.fields],
        }

    def __bool__(self) -> bool:
        return len(self.fields) > 0

    def __str__(self) -> str:
        lines = [f"Schema: {self.name}"]
        for f in self.fields:
            lines.append(f"  {f}")
        return "\n".join(lines)


def _normalize_type(ft: FieldType) -> str:
    """Return the lowercase string name of a FieldType."""
    return ft.value.lower() if hasattr(ft, "value") else str(ft).lower()


def canonicalize(schema: StreamSchema, sort: bool = True) -> CanonicalSchema:
    """Convert a StreamSchema into a CanonicalSchema.

    Args:
        schema: The source StreamSchema.
        sort: If True, fields are sorted alphabetically by name.

    Returns:
        A CanonicalSchema with normalized, optionally sorted fields.
    """
    fields: List[SchemaField] = list(schema.fields)
    if sort:
        fields = sorted(fields, key=lambda f: f.name)

    canonical_fields = [
        CanonicalField(
            name=f.name,
            type=_normalize_type(f.type),
            required=f.required,
        )
        for f in fields
    ]

    return CanonicalSchema(name=schema.name, fields=canonical_fields)


def diff_canonical(
    old: CanonicalSchema, new: CanonicalSchema
) -> dict:
    """Return a simple dict describing differences between two canonical schemas."""
    old_map = {f.name: f for f in old.fields}
    new_map = {f.name: f for f in new.fields}

    added = [n for n in new_map if n not in old_map]
    removed = [n for n in old_map if n not in new_map]
    changed = [
        n
        for n in old_map
        if n in new_map and old_map[n].to_dict() != new_map[n].to_dict()
    ]

    return {"added": added, "removed": removed, "changed": changed}
