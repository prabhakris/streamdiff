"""Score schema changes by risk level (0-100)."""
from dataclasses import dataclass
from typing import List
from streamdiff.diff import SchemaChange, ChangeType, DiffResult


_WEIGHTS = {
    ChangeType.REMOVED: 50,
    ChangeType.TYPE_CHANGED: 30,
    ChangeType.ADDED: 5,
}

_REQUIRED_MULTIPLIER = 2
_MAX_SCORE = 100


@dataclass
class RiskScore:
    score: int
    label: str
    breakdown: dict

    def __str__(self) -> str:
        return f"Risk: {self.label} ({self.score}/100)"


def _change_score(change: SchemaChange) -> int:
    base = _WEIGHTS.get(change.change_type, 0)
    if change.field.required:
        base *= _REQUIRED_MULTIPLIER
    return base


def score_changes(changes: List[SchemaChange]) -> RiskScore:
    if not changes:
        return RiskScore(score=0, label="none", breakdown={})

    breakdown = {ct.value: 0 for ct in ChangeType}
    total = 0
    for c in changes:
        pts = _change_score(c)
        breakdown[c.change_type.value] += pts
        total += pts

    score = min(total, _MAX_SCORE)
    if score == 0:
        label = "none"
    elif score < 20:
        label = "low"
    elif score < 50:
        label = "medium"
    else:
        label = "high"

    return RiskScore(score=score, label=label, breakdown=breakdown)


def score_result(result: DiffResult) -> RiskScore:
    return score_changes(result.changes)
