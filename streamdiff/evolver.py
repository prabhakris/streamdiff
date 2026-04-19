"""Schema evolution advisor: suggests next safe schema version."""
from dataclasses import dataclass, field
from typing import List
from streamdiff.schema import StreamSchema, SchemaField
from streamdiff.diff import DiffResult, ChangeType, SchemaChange


@dataclass
class EvolutionSuggestion:
    field_name: str
    action: str  # 'keep', 'deprecate', 'remove', 'promote'
    reason: str

    def to_dict(self) -> dict:
        return {"field": self.field_name, "action": self.action, "reason": self.reason}

    def __str__(self) -> str:
        return f"[{self.action.upper()}] {self.field_name}: {self.reason}"


@dataclass
class EvolutionPlan:
    suggestions: List[EvolutionSuggestion] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.suggestions)

    def to_dict(self) -> dict:
        return {"suggestions": [s.to_dict() for s in self.suggestions]}


def _suggest_for_change(change: SchemaChange) -> EvolutionSuggestion:
    if change.change_type == ChangeType.ADDED:
        req = getattr(change.new_field, "required", False)
        if req:
            return EvolutionSuggestion(
                change.field_name, "promote",
                "New required field may break existing consumers; consider optional first."
            )
        return EvolutionSuggestion(
            change.field_name, "keep",
            "Optional field addition is safe."
        )
    if change.change_type == ChangeType.REMOVED:
        return EvolutionSuggestion(
            change.field_name, "deprecate",
            "Mark field deprecated before removal to allow consumer migration."
        )
    if change.change_type == ChangeType.TYPE_CHANGED:
        return EvolutionSuggestion(
            change.field_name, "deprecate",
            f"Type change from {change.old_field.field_type} to {change.new_field.field_type} is breaking; introduce new field instead."
        )
    return EvolutionSuggestion(change.field_name, "keep", "No action needed.")


def build_evolution_plan(result: DiffResult) -> EvolutionPlan:
    suggestions = [_suggest_for_change(c) for c in result.changes]
    return EvolutionPlan(suggestions=suggestions)
