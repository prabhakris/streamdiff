"""Extract a subset of fields from a schema by pattern or list."""
from __future__ import annotations
import fnmatch
from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class ExtractResult:
    original_count: int
    extracted: List[SchemaField]
    dropped: List[SchemaField]

    def __bool__(self) -> bool:
        return len(self.extracted) > 0

    def to_dict(self) -> dict:
        return {
            "original_count": self.original_count,
            "extracted_count": len(self.extracted),
            "dropped_count": len(self.dropped),
            "extracted": [f.name for f in self.extracted],
            "dropped": [f.name for f in self.dropped],
        }

    def __str__(self) -> str:
        return (
            f"ExtractResult(extracted={len(self.extracted)}, "
            f"dropped={len(self.dropped)})"
        )

    def to_schema(self, name: str = "extracted") -> StreamSchema:
        return StreamSchema(name=name, fields=list(self.extracted))


def extract_by_names(schema: StreamSchema, names: List[str]) -> ExtractResult:
    name_set = set(names)
    extracted = [f for f in schema.fields if f.name in name_set]
    dropped = [f for f in schema.fields if f.name not in name_set]
    return ExtractResult(
        original_count=len(schema.fields),
        extracted=extracted,
        dropped=dropped,
    )


def extract_by_pattern(schema: StreamSchema, pattern: str) -> ExtractResult:
    extracted = [f for f in schema.fields if fnmatch.fnmatch(f.name, pattern)]
    dropped = [f for f in schema.fields if not fnmatch.fnmatch(f.name, pattern)]
    return ExtractResult(
        original_count=len(schema.fields),
        extracted=extracted,
        dropped=dropped,
    )


def extract_by_type(schema: StreamSchema, type_name: str) -> ExtractResult:
    extracted = [f for f in schema.fields if f.field_type.value == type_name]
    dropped = [f for f in schema.fields if f.field_type.value != type_name]
    return ExtractResult(
        original_count=len(schema.fields),
        extracted=extracted,
        dropped=dropped,
    )
