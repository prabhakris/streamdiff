"""delimiter.py — split a schema into chunks by a delimiter in field names."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from streamdiff.schema import SchemaField, StreamSchema


@dataclass
class DelimitResult:
    chunks: Dict[str, List[SchemaField]]
    unmatched: List[SchemaField]
    delimiter: str
    original_count: int

    def __bool__(self) -> bool:
        return bool(self.chunks)

    def to_dict(self) -> dict:
        return {
            "delimiter": self.delimiter,
            "original_count": self.original_count,
            "unmatched_count": len(self.unmatched),
            "chunks": {
                k: [{"name": f.name, "type": f.field_type.value, "required": f.required} for f in v]
                for k, v in self.chunks.items()
            },
            "unmatched": [
                {"name": f.name, "type": f.field_type.value, "required": f.required}
                for f in self.unmatched
            ],
        }

    def __str__(self) -> str:
        lines = [f"DelimitResult(delimiter={self.delimiter!r}, chunks={len(self.chunks)}, unmatched={len(self.unmatched)})"]
        for prefix, fields in self.chunks.items():
            lines.append(f"  [{prefix}]: {[f.name for f in fields]}")
        if self.unmatched:
            lines.append(f"  [unmatched]: {[f.name for f in self.unmatched]}")
        return "\n".join(lines)


def delimit_schema(
    schema: StreamSchema,
    delimiter: str = ".",
    depth: int = 1,
) -> DelimitResult:
    """Split schema fields into chunks based on a delimiter prefix up to *depth* segments."""
    chunks: Dict[str, List[SchemaField]] = {}
    unmatched: List[SchemaField] = []

    for f in schema.fields:
        parts = f.name.split(delimiter)
        if len(parts) > depth:
            key = delimiter.join(parts[:depth])
            chunks.setdefault(key, []).append(f)
        else:
            unmatched.append(f)

    return DelimitResult(
        chunks=chunks,
        unmatched=unmatched,
        delimiter=delimiter,
        original_count=len(schema.fields),
    )
