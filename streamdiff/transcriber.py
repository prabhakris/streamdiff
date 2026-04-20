"""Transcribe schema fields into human-readable documentation strings."""
from dataclasses import dataclass, field
from typing import List, Optional

from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class TranscribedField:
    name: str
    type_name: str
    required: bool
    description: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type_name,
            "required": self.required,
            "description": self.description,
        }

    def __str__(self) -> str:
        req = "required" if self.required else "optional"
        return f"{self.name} ({self.type_name}, {req}): {self.description}"


@dataclass
class TranscribeReport:
    schema_name: str
    fields: List[TranscribedField] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.fields) > 0

    def to_dict(self) -> dict:
        return {
            "schema": self.schema_name,
            "fields": [f.to_dict() for f in self.fields],
        }

    def __str__(self) -> str:
        lines = [f"Schema: {self.schema_name}"]
        for f in self.fields:
            lines.append(f"  {f}")
        return "\n".join(lines)


def _describe_field(f: SchemaField) -> str:
    req = "Required" if f.required else "Optional"
    return f"{req} {f.field_type.value} field."


def transcribe_schema(
    schema: StreamSchema,
    name: Optional[str] = None,
) -> TranscribeReport:
    schema_name = name or schema.name
    transcribed = [
        TranscribedField(
            name=f.name,
            type_name=f.field_type.value,
            required=f.required,
            description=_describe_field(f),
        )
        for f in schema.fields
    ]
    return TranscribeReport(schema_name=schema_name, fields=transcribed)
