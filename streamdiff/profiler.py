"""Schema profiler: collect field-level statistics from a StreamSchema."""
from dataclasses import dataclass, field
from typing import Dict, List
from streamdiff.schema import StreamSchema, FieldType


@dataclass
class FieldStat:
    name: str
    field_type: FieldType
    required: bool
    depth: int  # nesting depth based on dot-separated name

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.field_type.value,
            "required": self.required,
            "depth": self.depth,
        }


@dataclass
class ProfileResult:
    schema_name: str
    total_fields: int
    required_count: int
    optional_count: int
    type_counts: Dict[str, int]
    max_depth: int
    stats: List[FieldStat] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "schema_name": self.schema_name,
            "total_fields": self.total_fields,
            "required_count": self.required_count,
            "optional_count": self.optional_count,
            "type_counts": self.type_counts,
            "max_depth": self.max_depth,
            "fields": [s.to_dict() for s in self.stats],
        }


def _depth(name: str) -> int:
    return name.count(".") + 1


def profile_schema(schema: StreamSchema) -> ProfileResult:
    stats: List[FieldStat] = []
    type_counts: Dict[str, int] = {}

    for f in schema.fields:
        d = _depth(f.name)
        stats.append(FieldStat(name=f.name, field_type=f.field_type, required=f.required, depth=d))
        key = f.field_type.value
        type_counts[key] = type_counts.get(key, 0) + 1

    required = sum(1 for s in stats if s.required)
    max_depth = max((s.depth for s in stats), default=0)

    return ProfileResult(
        schema_name=schema.name,
        total_fields=len(stats),
        required_count=required,
        optional_count=len(stats) - required,
        type_counts=type_counts,
        max_depth=max_depth,
        stats=stats,
    )
