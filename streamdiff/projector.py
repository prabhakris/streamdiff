"""Project a schema onto a subset of fields using dot-notation path expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set

from streamdiff.schema import SchemaField, StreamSchema


@dataclass
class ProjectResult:
    included: List[SchemaField]
    excluded: List[SchemaField]
    paths: Set[str]

    def __bool__(self) -> bool:
        return bool(self.included)

    def to_dict(self) -> dict:
        return {
            "included": [{"name": f.name, "type": f.type.value, "required": f.required} for f in self.included],
            "excluded": [{"name": f.name, "type": f.type.value, "required": f.required} for f in self.excluded],
            "paths": sorted(self.paths),
            "included_count": len(self.included),
            "excluded_count": len(self.excluded),
        }

    def __str__(self) -> str:
        lines = [f"ProjectResult: {len(self.included)} included, {len(self.excluded)} excluded"]
        for f in self.included:
            lines.append(f"  + {f.name} ({f.type.value})")
        return "\n".join(lines)

    def to_schema(self) -> StreamSchema:
        return StreamSchema(fields=list(self.included))


def _matches_path(field_name: str, paths: Set[str]) -> bool:
    """Return True if field_name matches any of the given dot-notation paths."""
    for path in paths:
        if field_name == path:
            return True
        if field_name.startswith(path + "."):
            return True
    return False


def project_schema(
    schema: StreamSchema,
    paths: Optional[List[str]] = None,
) -> ProjectResult:
    """Return only fields whose names match one of the given dot-notation paths."""
    path_set: Set[str] = set(paths or [])
    included: List[SchemaField] = []
    excluded: List[SchemaField] = []

    for f in schema.fields:
        if not path_set or _matches_path(f.name, path_set):
            included.append(f)
        else:
            excluded.append(f)

    return ProjectResult(included=included, excluded=excluded, paths=path_set)
