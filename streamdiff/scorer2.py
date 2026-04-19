"""Field-level compatibility scorer using type compatibility rules."""
from dataclasses import dataclass
from typing import List
from streamdiff.diff import SchemaChange, ChangeType, DiffResult
from streamdiff.comparator import check_type_compatibility


@dataclass
class CompatibilityScore:
    field_name: str
    change_type: ChangeType
    score: float  # 0.0 = fully compatible, 1.0 = fully breaking
    reason: str

    def to_dict(self) -> dict:
        return {
            "field": self.field_name,
            "change_type": self.change_type.value,
            "score": self.score,
            "reason": self.reason,
        }

    def __str__(self) -> str:
        return f"{self.field_name}: score={self.score:.2f} ({self.reason})"


def _score_change(change: SchemaChange) -> CompatibilityScore:
    if change.change_type == ChangeType.ADDED:
        if change.new_field and change.new_field.required:
            return CompatibilityScore(change.field_name, change.change_type, 0.8, "required field added")
        return CompatibilityScore(change.field_name, change.change_type, 0.1, "optional field added")

    if change.change_type == ChangeType.REMOVED:
        return CompatibilityScore(change.field_name, change.change_type, 1.0, "field removed")

    if change.change_type == ChangeType.TYPE_CHANGED:
        if change.old_field and change.new_field:
            compat = check_type_compatibility(change.old_field.field_type, change.new_field.field_type)
            if compat:
                return CompatibilityScore(change.field_name, change.change_type, 0.2, "safe type widening")
            return CompatibilityScore(change.field_name, change.change_type, 0.9, "incompatible type change")

    return CompatibilityScore(change.field_name, change.change_type, 0.5, "unknown change")


def score_compatibility(result: DiffResult) -> List[CompatibilityScore]:
    return [_score_change(c) for c in result.changes]


def overall_score(scores: List[CompatibilityScore]) -> float:
    if not scores:
        return 0.0
    return max(s.score for s in scores)
