"""stenciler.py — apply a field mask (stencil) to a schema, keeping only selected fields."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Set
from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class StencilResult:
    original_count: int
    kept: List[SchemaField]
    dropped: List[SchemaField]

    def __bool__(self) -> bool:
        return len(self.dropped) == 0

    def to_dict(self) -> dict:
        return {
            "original_count": self.original_count,
            "kept": [f.name for f in self.kept],
            "dropped": [f.name for f in self.dropped],
        }

    def __str__(self) -> str:
        return (
            f"StencilResult(kept={len(self.kept)}, dropped={len(self.dropped)})"
        )

    def to_schema(self, name: str = "stenciled") -> StreamSchema:
        return StreamSchema(name=name, fields=list(self.kept))


def apply_stencil(schema: StreamSchema, allow: Set[str]) -> StencilResult:
    """Keep only fields whose names are in *allow*."""
    kept: List[SchemaField] = []
    dropped: List[SchemaField] = []
    for f in schema.fields:
        (kept if f.name in allow else dropped).append(f)
    return StencilResult(
        original_count=len(schema.fields),
        kept=kept,
        dropped=dropped,
    )


def apply_stencil_prefix(schema: StreamSchema, prefixes: List[str]) -> StencilResult:
    """Keep fields whose name starts with any of *prefixes*."""
    allow = {f.name for f in schema.fields if any(f.name.startswith(p) for p in prefixes)}
    return apply_stencil(schema, allow)
