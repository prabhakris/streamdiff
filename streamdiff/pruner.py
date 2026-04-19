"""Prune deprecated or unwanted fields from a schema."""
from dataclasses import dataclass, field
from typing import List, Set
from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class PruneResult:
    pruned: List[SchemaField] = field(default_factory=list)
    kept: List[SchemaField] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.pruned) > 0

    def to_dict(self) -> dict:
        return {
            "pruned": [f.name for f in self.pruned],
            "kept": [f.name for f in self.kept],
            "pruned_count": len(self.pruned),
            "kept_count": len(self.kept),
        }

    def __str__(self) -> str:
        if not self.pruned:
            return "No fields pruned."
        names = ", ".join(f.name for f in self.pruned)
        return f"Pruned {len(self.pruned)} field(s): {names}"


def prune_by_names(schema: StreamSchema, names: Set[str]) -> PruneResult:
    """Remove fields whose names are in the given set."""
    pruned, kept = [], []
    for f in schema.fields:
        (pruned if f.name in names else kept).append(f)
    return PruneResult(pruned=pruned, kept=kept)


def prune_optional(schema: StreamSchema) -> PruneResult:
    """Remove all optional (non-required) fields."""
    pruned, kept = [], []
    for f in schema.fields:
        (kept if f.required else pruned).append(f)
    return PruneResult(pruned=pruned, kept=kept)


def apply_prune(schema: StreamSchema, result: PruneResult) -> StreamSchema:
    """Return a new StreamSchema containing only the kept fields."""
    return StreamSchema(name=schema.name, fields=list(result.kept))
