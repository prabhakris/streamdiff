"""Attach human-readable labels to schema changes based on context."""
from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.diff import SchemaChange, ChangeType


@dataclass
class LabeledChange:
    change: SchemaChange
    labels: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        label_str = ", ".join(self.labels) if self.labels else "(none)"
        return f"{self.change.field_name} [{label_str}]"

    def to_dict(self) -> dict:
        return {
            "field": self.change.field_name,
            "change_type": self.change.change_type.value,
            "labels": self.labels,
        }


def _default_labels(change: SchemaChange) -> List[str]:
    labels = []
    if change.change_type == ChangeType.ADDED:
        labels.append("additive")
        if change.new_field and change.new_field.required:
            labels.append("breaking")
        else:
            labels.append("safe")
    elif change.change_type == ChangeType.REMOVED:
        labels.append("destructive")
        labels.append("breaking")
    elif change.change_type == ChangeType.TYPE_CHANGED:
        labels.append("structural")
        labels.append("breaking")
    return labels


def label_change(change: SchemaChange, extra: Optional[List[str]] = None) -> LabeledChange:
    labels = _default_labels(change)
    if extra:
        labels.extend(extra)
    return LabeledChange(change=change, labels=labels)


def label_all(changes: List[SchemaChange], extra: Optional[List[str]] = None) -> List[LabeledChange]:
    return [label_change(c, extra) for c in changes]


@dataclass
class LabelReport:
    labeled: List[LabeledChange] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.labeled)

    def to_dict(self) -> dict:
        return {"labeled_changes": [lc.to_dict() for lc in self.labeled]}


def build_label_report(changes: List[SchemaChange], extra: Optional[List[str]] = None) -> LabelReport:
    return LabelReport(labeled=label_all(changes, extra))
