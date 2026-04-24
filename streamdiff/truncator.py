"""Truncator: limit a schema to a maximum number of fields, with optional priority ordering."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from streamdiff.schema import SchemaField, StreamSchema


@dataclass
class TruncateResult:
    original_count: int
    kept: List[SchemaField]
    dropped: List[SchemaField]
    limit: int

    def __bool__(self) -> bool:
        return len(self.dropped) > 0

    def to_dict(self) -> dict:
        return {
            "original_count": self.original_count,
            "kept_count": len(self.kept),
            "dropped_count": len(self.dropped),
            "limit": self.limit,
            "kept": [f.name for f in self.kept],
            "dropped": [f.name for f in self.dropped],
        }

    def __str__(self) -> str:
        if not self:
            return f"TruncateResult: no fields dropped (limit={self.limit})"
        return (
            f"TruncateResult: kept {len(self.kept)}/{self.original_count} fields "
            f"(limit={self.limit}, dropped={[f.name for f in self.dropped]})"
        )

    def to_schema(self) -> StreamSchema:
        return StreamSchema(fields=list(self.kept))


def truncate_schema(
    schema: StreamSchema,
    limit: int,
    required_first: bool = True,
) -> TruncateResult:
    """Truncate *schema* to at most *limit* fields.

    When *required_first* is True (default), required fields are preserved
    before optional ones when deciding which fields to keep.
    """
    if limit < 0:
        raise ValueError(f"limit must be >= 0, got {limit}")

    fields: List[SchemaField] = list(schema.fields)
    original_count = len(fields)

    if required_first:
        ordered = [f for f in fields if f.required] + [f for f in fields if not f.required]
    else:
        ordered = list(fields)

    kept = ordered[:limit]
    dropped = ordered[limit:]

    return TruncateResult(
        original_count=original_count,
        kept=kept,
        dropped=dropped,
        limit=limit,
    )
