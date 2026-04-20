"""Field coverage scorer: measures how completely a schema is defined."""
from dataclasses import dataclass, field
from typing import List
from streamdiff.schema import StreamSchema, SchemaField, FieldType

_COMPLEX_TYPES = {FieldType.ARRAY, FieldType.MAP, FieldType.BYTES}


@dataclass
class CoverageField:
    name: str
    required: bool
    has_complex_type: bool
    score: float

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "required": self.required,
            "has_complex_type": self.has_complex_type,
            "score": self.score,
        }

    def __str__(self) -> str:
        return f"{self.name}: {self.score:.2f}"


@dataclass
class CoverageReport:
    fields: List[CoverageField] = field(default_factory=list)
    total_score: float = 0.0
    max_score: float = 0.0

    @property
    def percent(self) -> float:
        if self.max_score == 0:
            return 0.0
        return round(self.total_score / self.max_score * 100, 2)

    def to_dict(self) -> dict:
        return {
            "fields": [f.to_dict() for f in self.fields],
            "total_score": self.total_score,
            "max_score": self.max_score,
            "percent": self.percent,
        }

    def __str__(self) -> str:
        return f"Coverage: {self.percent}% ({self.total_score}/{self.max_score})"


def _score_field(f: SchemaField) -> float:
    score = 1.0
    if not f.required:
        score -= 0.2
    if f.field_type in _COMPLEX_TYPES:
        score -= 0.1
    return round(max(score, 0.0), 2)


def score_coverage(schema: StreamSchema) -> CoverageReport:
    report = CoverageReport()
    for f in schema.fields:
        s = _score_field(f)
        cf = CoverageField(
            name=f.name,
            required=f.required,
            has_complex_type=f.field_type in _COMPLEX_TYPES,
            score=s,
        )
        report.fields.append(cf)
        report.total_score += s
        report.max_score += 1.0
    report.total_score = round(report.total_score, 2)
    report.max_score = round(report.max_score, 2)
    return report
