"""Redact sensitive fields from schemas before diffing or exporting."""
from dataclasses import dataclass, field
from typing import List, Set
from streamdiff.schema import StreamSchema, SchemaField

SENSITIVE_PATTERNS = ["password", "secret", "token", "key", "ssn", "credit"]


@dataclass
class RedactResult:
    original_count: int
    redacted_fields: List[str]
    schema: StreamSchema

    def __bool__(self) -> bool:
        return len(self.redacted_fields) > 0

    def to_dict(self) -> dict:
        return {
            "original_count": self.original_count,
            "redacted_count": len(self.redacted_fields),
            "redacted_fields": self.redacted_fields,
        }


def _is_sensitive(name: str, patterns: List[str]) -> bool:
    lower = name.lower()
    return any(p in lower for p in patterns)


def redact_schema(
    schema: StreamSchema,
    patterns: List[str] = None,
    placeholder: str = "[REDACTED]",
) -> RedactResult:
    if patterns is None:
        patterns = SENSITIVE_PATTERNS

    kept: List[SchemaField] = []
    redacted: List[str] = []

    for f in schema.fields:
        if _is_sensitive(f.name, patterns):
            redacted.append(f.name)
        else:
            kept.append(f)

    new_schema = StreamSchema(name=schema.name, fields=kept)
    return RedactResult(
        original_count=len(schema.fields),
        redacted_fields=redacted,
        schema=new_schema,
    )


def redact_all(
    schemas: List[StreamSchema],
    patterns: List[str] = None,
) -> List[RedactResult]:
    return [redact_schema(s, patterns) for s in schemas]
