"""Assign importance weights to schema fields based on type, requiredness, and name patterns."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from streamdiff.schema import SchemaField, StreamSchema, FieldType


@dataclass
class FieldWeight:
    field_name: str
    weight: float
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"field": self.field_name, "weight": self.weight, "reasons": self.reasons}

    def __str__(self) -> str:
        return f"{self.field_name}: {self.weight:.2f}"


@dataclass
class WeightReport:
    weights: List[FieldWeight] = field(default_factory=list)

    def by_field(self) -> Dict[str, FieldWeight]:
        return {w.field_name: w for w in self.weights}

    def total(self) -> float:
        return sum(w.weight for w in self.weights)

    def to_dict(self) -> dict:
        return {
            "weights": [w.to_dict() for w in self.weights],
            "total": self.total(),
        }


_HIGH_IMPORTANCE_PATTERNS = ("id", "key", "timestamp", "created", "updated", "type", "status")
_HIGH_WEIGHT_TYPES = {FieldType.STRING, FieldType.INT, FieldType.LONG}


def _base_weight(f: SchemaField) -> float:
    return 2.0 if f.required else 1.0


def _type_bonus(f: SchemaField) -> tuple:
    if f.field_type in _HIGH_WEIGHT_TYPES:
        return 0.5, f"type {f.field_type.value} is high-importance"
    return 0.0, ""


def _name_bonus(f: SchemaField) -> tuple:
    lower = f.name.lower()
    for pattern in _HIGH_IMPORTANCE_PATTERNS:
        if pattern in lower:
            return 1.0, f"name contains '{pattern}'"
    return 0.0, ""


def weight_field(f: SchemaField) -> FieldWeight:
    reasons: List[str] = []
    w = _base_weight(f)
    reasons.append("required" if f.required else "optional")

    bonus, reason = _type_bonus(f)
    if bonus:
        w += bonus
        reasons.append(reason)

    bonus, reason = _name_bonus(f)
    if bonus:
        w += bonus
        reasons.append(reason)

    return FieldWeight(field_name=f.name, weight=round(w, 2), reasons=reasons)


def weight_schema(schema: StreamSchema, min_weight: Optional[float] = None) -> WeightReport:
    weights = [weight_field(f) for f in schema.fields]
    if min_weight is not None:
        weights = [w for w in weights if w.weight >= min_weight]
    weights.sort(key=lambda w: w.weight, reverse=True)
    return WeightReport(weights=weights)
