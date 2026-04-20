"""Mask sensitive field names in a schema by replacing their names with redacted placeholders."""
from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.schema import StreamSchema, SchemaField

_SENSITIVE_PATTERNS = ("password", "secret", "token", "key", "credential", "ssn", "cvv", "pin")


@dataclass
class MaskedField:
    original_name: str
    masked_name: str
    field: SchemaField

    def to_dict(self) -> dict:
        return {
            "original_name": self.original_name,
            "masked_name": self.masked_name,
            "type": self.field.type.value,
            "required": self.field.required,
        }

    def __str__(self) -> str:
        return f"{self.original_name} -> {self.masked_name}"


@dataclass
class MaskResult:
    schema: StreamSchema
    masked: List[MaskedField] = field(default_factory=list)
    original_count: int = 0

    def __bool__(self) -> bool:
        return len(self.masked) > 0

    def to_dict(self) -> dict:
        return {
            "stream": self.schema.name,
            "original_count": self.original_count,
            "masked_count": len(self.masked),
            "masked_fields": [m.to_dict() for m in self.masked],
        }

    def __str__(self) -> str:
        if not self.masked:
            return f"No fields masked in '{self.schema.name}'"
        lines = [f"Masked {len(self.masked)} field(s) in '{self.schema.name}':"]
        for m in self.masked:
            lines.append(f"  {m}")
        return "\n".join(lines)


def _is_sensitive(name: str) -> bool:
    lower = name.lower()
    return any(pat in lower for pat in _SENSITIVE_PATTERNS)


def _mask_name(name: str, placeholder: str = "***") -> str:
    return f"{placeholder}_{name[-3:]}" if len(name) > 3 else placeholder


def mask_schema(
    schema: StreamSchema,
    placeholder: str = "***",
    extra_patterns: Optional[List[str]] = None,
) -> MaskResult:
    patterns = list(_SENSITIVE_PATTERNS)
    if extra_patterns:
        patterns.extend(p.lower() for p in extra_patterns)

    masked_fields: List[MaskedField] = []
    new_fields: List[SchemaField] = []

    for f in schema.fields:
        lower = f.name.lower()
        if any(pat in lower for pat in patterns):
            new_name = _mask_name(f.name, placeholder)
            masked_fields.append(MaskedField(original_name=f.name, masked_name=new_name, field=f))
            new_fields.append(SchemaField(name=new_name, type=f.type, required=f.required))
        else:
            new_fields.append(f)

    new_schema = StreamSchema(name=schema.name, fields=new_fields)
    return MaskResult(schema=new_schema, masked=masked_fields, original_count=len(schema.fields))
