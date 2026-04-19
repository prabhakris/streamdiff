"""Pinpoint which fields changed between two versions and why."""
from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.diff import SchemaChange, ChangeType, DiffResult
from streamdiff.schema import SchemaField


@dataclass
class Pinpoint:
    field_name: str
    change_type: ChangeType
    reason: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "field": self.field_name,
            "change_type": self.change_type.value,
            "reason": self.reason,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }

    def __str__(self) -> str:
        base = f"{self.field_name} [{self.change_type.value}]: {self.reason}"
        if self.old_value and self.new_value:
            base += f" ({self.old_value} -> {self.new_value})"
        return base


@dataclass
class PinpointReport:
    pinpoints: List[Pinpoint] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.pinpoints) > 0

    def to_dict(self) -> dict:
        return {"pinpoints": [p.to_dict() for p in self.pinpoints]}


def _reason_for(change: SchemaChange) -> str:
    if change.change_type == ChangeType.ADDED:
        req = "required" if (change.new_field and change.new_field.required) else "optional"
        return f"Field added as {req}"
    if change.change_type == ChangeType.REMOVED:
        return "Field was removed from schema"
    if change.change_type == ChangeType.TYPE_CHANGED:
        return "Field type was modified"
    if change.change_type == ChangeType.REQUIRED_CHANGED:
        return "Field required flag changed"
    return "Unknown change"


def pinpoint_changes(result: DiffResult) -> PinpointReport:
    pinpoints = []
    for change in result.changes:
        old_val = None
        new_val = None
        if change.change_type == ChangeType.TYPE_CHANGED:
            old_val = change.old_field.field_type.value if change.old_field else None
            new_val = change.new_field.field_type.value if change.new_field else None
        elif change.change_type == ChangeType.REQUIRED_CHANGED:
            old_val = str(change.old_field.required) if change.old_field else None
            new_val = str(change.new_field.required) if change.new_field else None
        pinpoints.append(Pinpoint(
            field_name=change.field_name,
            change_type=change.change_type,
            reason=_reason_for(change),
            old_value=old_val,
            new_value=new_val,
        ))
    return PinpointReport(pinpoints=pinpoints)
