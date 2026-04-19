"""Schema stretcher: expand a schema by applying field multipliers or patterns."""
from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.schema import StreamSchema, SchemaField, FieldType


@dataclass
class StretchResult:
    original_count: int
    expanded_count: int
    added_fields: List[SchemaField] = field(default_factory=list)
    schema: Optional[StreamSchema] = None

    def __bool__(self) -> bool:
        return self.expanded_count > self.original_count

    def to_dict(self) -> dict:
        return {
            "original_count": self.original_count,
            "expanded_count": self.expanded_count,
            "added_fields": [f.name for f in self.added_fields],
        }

    def __str__(self) -> str:
        delta = self.expanded_count - self.original_count
        return f"StretchResult: +{delta} fields ({self.original_count} -> {self.expanded_count})"


def stretch_by_suffix(
    schema: StreamSchema,
    suffixes: List[str],
    required: bool = False,
) -> StretchResult:
    """For each existing field, add variants with each suffix if not already present."""
    original_fields = list(schema.fields)
    original_names = {f.name for f in original_fields}
    added: List[SchemaField] = []

    for base_field in original_fields:
        for suffix in suffixes:
            new_name = f"{base_field.name}_{suffix}"
            if new_name not in original_names:
                new_field = SchemaField(
                    name=new_name,
                    field_type=base_field.field_type,
                    required=required,
                )
                added.append(new_field)
                original_names.add(new_name)

    new_schema = StreamSchema(name=schema.name, fields=original_fields + added)
    return StretchResult(
        original_count=len(original_fields),
        expanded_count=len(new_schema.fields),
        added_fields=added,
        schema=new_schema,
    )


def stretch_by_types(
    schema: StreamSchema,
    extra_types: List[FieldType],
    required: bool = False,
) -> StretchResult:
    """Add a new field for each specified type not already present in the schema."""
    original_fields = list(schema.fields)
    existing_types = {f.field_type for f in original_fields}
    added: List[SchemaField] = []

    for ft in extra_types:
        if ft not in existing_types:
            new_field = SchemaField(
                name=ft.value,
                field_type=ft,
                required=required,
            )
            added.append(new_field)
            existing_types.add(ft)

    new_schema = StreamSchema(name=schema.name, fields=original_fields + added)
    return StretchResult(
        original_count=len(original_fields),
        expanded_count=len(new_schema.fields),
        added_fields=added,
        schema=new_schema,
    )
