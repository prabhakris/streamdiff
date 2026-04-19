"""Field-level readiness scorer: estimates how 'production-ready' a schema is."""
from dataclasses import dataclass, field
from typing import List
from streamdiff.schema import StreamSchema, FieldType

_TYPE_SCORES = {
    FieldType.STRING: 10,
    FieldType.INT: 10,
    FieldType.LONG: 10,
    FieldType.FLOAT: 8,
    FieldType.DOUBLE: 8,
    FieldType.BOOLEAN: 10,
    FieldType.BYTES: 6,
    FieldType.ARRAY: 7,
    FieldType.MAP: 7,
    FieldType.RECORD: 9,
    FieldType.ENUM: 9,
    FieldType.NULL: 2,
}


@dataclass
class FieldReadiness:
    name: str
    score: int
    max_score: int
    notes: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "score": self.score,
            "max_score": self.max_score,
            "notes": self.notes,
        }

    def __str__(self):
        return f"{self.name}: {self.score}/{self.max_score}"


@dataclass
class ReadinessReport:
    fields: List[FieldReadiness] = field(default_factory=list)
    overall: float = 0.0

    def to_dict(self):
        return {
            "overall": round(self.overall, 2),
            "fields": [f.to_dict() for f in self.fields],
        }

    def __bool__(self):
        return self.overall >= 7.0


def _score_field(f) -> FieldReadiness:
    notes = []
    score = _TYPE_SCORES.get(f.field_type, 5)
    max_score = 10

    if not f.required:
        notes.append("optional field reduces confidence")
        score = max(0, score - 1)

    if len(f.name) < 3:
        notes.append("very short name")
        score = max(0, score - 2)

    return FieldReadiness(name=f.name, score=score, max_score=max_score, notes=notes)


def score_readiness(schema: StreamSchema) -> ReadinessReport:
    if not schema.fields:
        return ReadinessReport(fields=[], overall=0.0)

    scored = [_score_field(f) for f in schema.fields]
    overall = sum(r.score for r in scored) / (len(scored) * 10) * 10
    return ReadinessReport(fields=scored, overall=overall)
