"""Expand a schema by duplicating fields with type promotions or variants."""
from dataclasses import dataclass, field
from typing import List, Optional

from streamdiff.schema import FieldType, SchemaField, StreamSchema

# Types that can be promoted to a wider type
_PROMOTIONS: dict = {
    FieldType.INT: FieldType.LONG,
    FieldType.FLOAT: FieldType.DOUBLE,
}


@dataclass
class ExpandResult:
    original: StreamSchema
    expanded: StreamSchema
    added_fields: List[SchemaField] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.added_fields) > 0

    def to_dict(self) -> dict:
        return {
            "original_count": len(self.original.fields),
            "expanded_count": len(self.expanded.fields),
            "added": [f.name for f in self.added_fields],
        }

    def __str__(self) -> str:
        if not self:
            return "ExpandResult: no fields added"
        names = ", ".join(f.name for f in self.added_fields)
        return f"ExpandResult: added {len(self.added_fields)} field(s): {names}"


def _make_promoted(f: SchemaField, suffix: str = "_wide") -> Optional[SchemaField]:
    """Return a promoted-type variant of *f*, or None if no promotion exists."""
    promoted_type = _PROMOTIONS.get(f.field_type)
    if promoted_type is None:
        return None
    return SchemaField(
        name=f"{f.name}{suffix}",
        field_type=promoted_type,
        required=False,
    )


def expand_schema(
    schema: StreamSchema,
    promote_types: bool = True,
    suffix: str = "_wide",
) -> ExpandResult:
    """Return a new schema with optional promoted-type variants appended."""
    new_fields: List[SchemaField] = list(schema.fields)
    added: List[SchemaField] = []

    if promote_types:
        existing_names = {f.name for f in schema.fields}
        for f in schema.fields:
            promoted = _make_promoted(f, suffix=suffix)
            if promoted and promoted.name not in existing_names:
                new_fields.append(promoted)
                added.append(promoted)
                existing_names.add(promoted.name)

    expanded = StreamSchema(name=schema.name, fields=new_fields)
    return ExpandResult(original=schema, expanded=expanded, added_fields=added)
