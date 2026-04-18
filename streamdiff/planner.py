"""Migration plan generator: produces ordered action steps from a DiffResult."""
from dataclasses import dataclass, field
from typing import List
from streamdiff.diff import DiffResult, ChangeType, SchemaChange


@dataclass
class PlanStep:
    order: int
    action: str
    field_name: str
    detail: str
    breaking: bool

    def to_dict(self) -> dict:
        return {
            "order": self.order,
            "action": self.action,
            "field": self.field_name,
            "detail": self.detail,
            "breaking": self.breaking,
        }

    def __str__(self) -> str:
        flag = " [BREAKING]" if self.breaking else ""
        return f"{self.order}. [{self.action}] {self.field_name} — {self.detail}{flag}"


@dataclass
class MigrationPlan:
    steps: List[PlanStep] = field(default_factory=list)

    @property
    def has_breaking(self) -> bool:
        return any(s.breaking for s in self.steps)

    def to_dict(self) -> dict:
        return {"steps": [s.to_dict() for s in self.steps], "has_breaking": self.has_breaking}


_ACTION = {
    ChangeType.ADDED: "ADD_FIELD",
    ChangeType.REMOVED: "DROP_FIELD",
    ChangeType.TYPE_CHANGED: "ALTER_TYPE",
    ChangeType.REQUIRED_CHANGED: "ALTER_NULLABILITY",
}

_ORDER = {
    ChangeType.ADDED: 3,
    ChangeType.TYPE_CHANGED: 1,
    ChangeType.REQUIRED_CHANGED: 2,
    ChangeType.REMOVED: 4,
}


def _detail(change: SchemaChange) -> str:
    f = change.field
    if change.change_type == ChangeType.ADDED:
        req = "required" if f.required else "optional"
        return f"add {req} field of type {f.field_type.value}"
    if change.change_type == ChangeType.REMOVED:
        return f"drop field (was {f.field_type.value})"
    if change.change_type == ChangeType.TYPE_CHANGED:
        old = change.old_field.field_type.value if change.old_field else "?"
        return f"change type {old} -> {f.field_type.value}"
    if change.change_type == ChangeType.REQUIRED_CHANGED:
        now = "required" if f.required else "optional"
        return f"mark field as {now}"
    return ""


def build_plan(result: DiffResult) -> MigrationPlan:
    changes = sorted(result.changes, key=lambda c: _ORDER.get(c.change_type, 99))
    steps = [
        PlanStep(
            order=i + 1,
            action=_ACTION.get(c.change_type, "UNKNOWN"),
            field_name=c.field.name,
            detail=_detail(c),
            breaking=c.breaking,
        )
        for i, c in enumerate(changes)
    ]
    return MigrationPlan(steps=steps)
