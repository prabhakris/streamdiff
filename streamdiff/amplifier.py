"""Amplifier: expand a schema by duplicating fields with transformed names."""
from dataclasses import dataclass, field
from typing import List, Callable, Optional
from streamdiff.schema import StreamSchema, SchemaField, FieldType


@dataclass
class AmplifyResult:
    original_count: int
    added_count: int
    fields: List[SchemaField]

    def __bool__(self) -> bool:
        return self.added_count > 0

    def to_dict(self) -> dict:
        return {
            "original_count": self.original_count,
            "added_count": self.added_count,
            "total_count": self.original_count + self.added_count,
            "fields": [
                {"name": f.name, "type": f.field_type.value, "required": f.required}
                for f in self.fields
            ],
        }

    def __str__(self) -> str:
        return (
            f"AmplifyResult(original={self.original_count}, "
            f"added={self.added_count})"
        )

    def to_schema(self, name: str = "amplified") -> StreamSchema:
        from streamdiff.schema import StreamSchema
        return StreamSchema(name=name, fields=list(self.fields))


def _make_variant(f: SchemaField, suffix: str, new_type: Optional[FieldType] = None) -> SchemaField:
    return SchemaField(
        name=f"{f.name}{suffix}",
        field_type=new_type if new_type is not None else f.field_type,
        required=False,
    )


def amplify_schema(
    schema: StreamSchema,
    suffix: str = "_raw",
    type_filter: Optional[FieldType] = None,
    target_type: Optional[FieldType] = None,
) -> AmplifyResult:
    """Duplicate fields (optionally filtered by type) with a suffix appended to their names."""
    original = list(schema.fields)
    added: List[SchemaField] = []

    for f in original:
        if type_filter is not None and f.field_type != type_filter:
            continue
        variant = _make_variant(f, suffix, target_type)
        # avoid duplicating if name already exists
        existing_names = {x.name for x in original} | {x.name for x in added}
        if variant.name not in existing_names:
            added.append(variant)

    return AmplifyResult(
        original_count=len(original),
        added_count=len(added),
        fields=original + added,
    )
