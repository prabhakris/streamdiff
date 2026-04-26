"""Strip metadata or attributes from schema fields."""
from dataclasses import dataclass, field
from typing import List, Optional, Set

from streamdiff.schema import SchemaField, StreamSchema


@dataclass
class StripResult:
    original_count: int
    stripped_fields: List[SchemaField]
    removed_attrs: Set[str]

    def __bool__(self) -> bool:
        return bool(self.stripped_fields)

    def to_dict(self) -> dict:
        return {
            "original_count": self.original_count,
            "stripped_count": len(self.stripped_fields),
            "removed_attrs": sorted(self.removed_attrs),
            "fields": [
                {"name": f.name, "type": f.field_type.value, "required": f.required}
                for f in self.stripped_fields
            ],
        }

    def __str__(self) -> str:
        if not self.stripped_fields:
            return "StripResult(no fields)"
        attrs = ", ".join(sorted(self.removed_attrs))
        return (
            f"StripResult({len(self.stripped_fields)} fields, "
            f"removed attrs: {attrs})"
        )

    def to_schema(self) -> StreamSchema:
        return StreamSchema(fields=list(self.stripped_fields))


def strip_required(schema: StreamSchema) -> StripResult:
    """Return a copy of the schema where all fields are marked optional."""
    stripped = [
        SchemaField(name=f.name, field_type=f.field_type, required=False)
        for f in schema.fields
    ]
    return StripResult(
        original_count=len(schema.fields),
        stripped_fields=stripped,
        removed_attrs={"required"},
    )


def strip_by_names(
    schema: StreamSchema, names: Set[str]
) -> StripResult:
    """Remove fields whose names are in *names*."""
    kept = [f for f in schema.fields if f.name not in names]
    dropped_names = {f.name for f in schema.fields if f.name in names}
    return StripResult(
        original_count=len(schema.fields),
        stripped_fields=kept,
        removed_attrs=dropped_names,
    )
