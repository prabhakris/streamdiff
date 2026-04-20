"""Crop a schema to a fixed number of fields, with optional ordering."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from streamdiff.schema import SchemaField, StreamSchema


@dataclass
class CropResult:
    original_count: int
    kept: List[SchemaField]
    dropped: List[SchemaField]

    def __bool__(self) -> bool:
        return len(self.dropped) > 0

    def to_dict(self) -> dict:
        return {
            "original_count": self.original_count,
            "kept_count": len(self.kept),
            "dropped_count": len(self.dropped),
            "kept": [f.name for f in self.kept],
            "dropped": [f.name for f in self.dropped],
        }

    def __str__(self) -> str:
        lines = [
            f"CropResult: {len(self.kept)}/{self.original_count} fields kept",
        ]
        if self.dropped:
            lines.append(f"  Dropped: {', '.join(f.name for f in self.dropped)}")
        return "\n".join(lines)

    def to_schema(self) -> StreamSchema:
        return StreamSchema(fields=list(self.kept))


def crop_schema(
    schema: StreamSchema,
    limit: int,
    sort_key: Optional[str] = None,
    descending: bool = False,
) -> CropResult:
    """Return at most *limit* fields from *schema*.

    Args:
        schema:     The source schema.
        limit:      Maximum number of fields to keep (non-negative).
        sort_key:   Optional pre-sort before cropping. One of
                    ``"name"`` or ``"type"``.
        descending: Reverse sort order when *sort_key* is set.
    """
    if limit < 0:
        raise ValueError(f"limit must be >= 0, got {limit}")

    fields: List[SchemaField] = list(schema.fields)

    if sort_key == "name":
        fields.sort(key=lambda f: f.name, reverse=descending)
    elif sort_key == "type":
        fields.sort(key=lambda f: f.field_type.value, reverse=descending)
    elif sort_key is not None:
        raise ValueError(f"Unknown sort_key: {sort_key!r}. Use 'name' or 'type'.")

    kept = fields[:limit]
    dropped = fields[limit:]

    return CropResult(
        original_count=len(fields),
        kept=kept,
        dropped=dropped,
    )
