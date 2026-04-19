"""Embed schema fields into a flat vector representation for similarity comparison."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from streamdiff.schema import StreamSchema, FieldType


TYPE_INDEX: Dict[str, int] = {
    t.value: i for i, t in enumerate(FieldType)
}


@dataclass
class EmbedVector:
    field_name: str
    values: List[float]

    def to_dict(self) -> dict:
        return {"field": self.field_name, "vector": self.values}

    def __str__(self) -> str:
        vals = ", ".join(f"{v:.2f}" for v in self.values)
        return f"EmbedVector({self.field_name}: [{vals}])"


@dataclass
class EmbedReport:
    schema_name: str
    vectors: List[EmbedVector] = field(default_factory=list)

    def by_field(self, name: str) -> EmbedVector | None:
        for v in self.vectors:
            if v.field_name == name:
                return v
        return None

    def to_dict(self) -> dict:
        return {
            "schema": self.schema_name,
            "vectors": [v.to_dict() for v in self.vectors],
        }


def _embed_field(name: str, required: bool, type_str: str) -> EmbedVector:
    n_types = len(TYPE_INDEX)
    vec: List[float] = [0.0] * (n_types + 1)
    vec[0] = 1.0 if required else 0.0
    idx = TYPE_INDEX.get(type_str, -1)
    if idx >= 0:
        vec[1 + idx] = 1.0
    return EmbedVector(field_name=name, values=vec)


def embed_schema(schema: StreamSchema) -> EmbedReport:
    report = EmbedReport(schema_name=schema.name)
    for f in schema.fields:
        vec = _embed_field(f.name, f.required, f.type.value)
        report.vectors.append(vec)
    return report


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vectors must have equal length")
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x ** 2 for x in a) ** 0.5
    mag_b = sum(x ** 2 for x in b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)
