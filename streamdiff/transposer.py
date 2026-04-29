"""Transpose a StreamSchema: swap field names and types to produce an inverted lookup map."""
from dataclasses import dataclass, field
from typing import Dict, List

from streamdiff.schema import StreamSchema, SchemaField, FieldType


@dataclass
class TransposeEntry:
    type_name: str
    field_names: List[str]

    def to_dict(self) -> dict:
        return {"type": self.type_name, "fields": sorted(self.field_names)}

    def __str__(self) -> str:
        return f"{self.type_name}: [{', '.join(sorted(self.field_names))}]"


@dataclass
class TransposeResult:
    entries: Dict[str, TransposeEntry] = field(default_factory=dict)
    original_field_count: int = 0

    def __bool__(self) -> bool:
        return bool(self.entries)

    def to_dict(self) -> dict:
        return {
            "original_field_count": self.original_field_count,
            "entries": {k: v.to_dict() for k, v in sorted(self.entries.items())},
        }

    def __str__(self) -> str:
        if not self.entries:
            return "TransposeResult(empty)"
        lines = [f"TransposeResult({self.original_field_count} fields)"]
        for key, entry in sorted(self.entries.items()):
            lines.append(f"  {entry}")
        return "\n".join(lines)

    def by_type(self, type_name: str) -> List[str]:
        """Return field names for a given type, or empty list."""
        entry = self.entries.get(type_name)
        return list(entry.field_names) if entry else []


def transpose_schema(schema: StreamSchema) -> TransposeResult:
    """Build a type -> [field_names] mapping from the given schema."""
    buckets: Dict[str, List[str]] = {}
    for f in schema.fields:
        type_key = f.type.value
        buckets.setdefault(type_key, []).append(f.name)

    entries = {
        type_key: TransposeEntry(type_name=type_key, field_names=names)
        for type_key, names in buckets.items()
    }
    return TransposeResult(entries=entries, original_field_count=len(schema.fields))
