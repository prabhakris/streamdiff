"""Field indexer: build searchable index from a StreamSchema."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from streamdiff.schema import StreamSchema, SchemaField, FieldType


@dataclass
class IndexEntry:
    name: str
    field_type: FieldType
    required: bool
    depth: int

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.field_type.value,
            "required": self.required,
            "depth": self.depth,
        }

    def __str__(self) -> str:
        req = "required" if self.required else "optional"
        return f"{self.name} ({self.field_type.value}, {req}, depth={self.depth})"


@dataclass
class FieldIndex:
    entries: Dict[str, IndexEntry] = field(default_factory=dict)

    def get(self, name: str) -> Optional[IndexEntry]:
        return self.entries.get(name)

    def search(self, query: str) -> List[IndexEntry]:
        q = query.lower()
        return [e for e in self.entries.values() if q in e.name.lower()]

    def by_type(self, ft: FieldType) -> List[IndexEntry]:
        return [e for e in self.entries.values() if e.field_type == ft]

    def required_fields(self) -> List[IndexEntry]:
        return [e for e in self.entries.values() if e.required]

    def optional_fields(self) -> List[IndexEntry]:
        return [e for e in self.entries.values() if not e.required]

    def __len__(self) -> int:
        return len(self.entries)


def _depth(name: str, separator: str = ".") -> int:
    return name.count(separator)


def build_index(schema: StreamSchema, separator: str = ".") -> FieldIndex:
    idx = FieldIndex()
    for name, f in schema.field_map().items():
        entry = IndexEntry(
            name=name,
            field_type=f.field_type,
            required=f.required,
            depth=_depth(name, separator),
        )
        idx.entries[name] = entry
    return idx
