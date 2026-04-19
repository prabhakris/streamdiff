"""Classify schema changes into semantic categories."""
from dataclasses import dataclass
from typing import List
from streamdiff.diff import SchemaChange, ChangeType


CATEGORY_ADDITIVE = "additive"
CATEGORY_DESTRUCTIVE = "destructive"
CATEGORY_STRUCTURAL = "structural"
CATEGORY_UNKNOWN = "unknown"


@dataclass
class ClassifiedChange:
    change: SchemaChange
    category: str

    def __str__(self) -> str:
        return f"{self.change.field_name} [{self.category}]"

    def to_dict(self) -> dict:
        return {
            "field": self.change.field_name,
            "change_type": self.change.change_type.value,
            "category": self.category,
        }


def _classify(change: SchemaChange) -> str:
    if change.change_type == ChangeType.ADDED:
        return CATEGORY_ADDITIVE
    if change.change_type == ChangeType.REMOVED:
        return CATEGORY_DESTRUCTIVE
    if change.change_type == ChangeType.TYPE_CHANGED:
        return CATEGORY_STRUCTURAL
    if change.change_type == ChangeType.REQUIRED_CHANGED:
        old = change.old_field
        new = change.new_field
        if old is not None and new is not None:
            if not old.required and new.required:
                return CATEGORY_DESTRUCTIVE
            return CATEGORY_ADDITIVE
    return CATEGORY_UNKNOWN


def classify_all(changes: List[SchemaChange]) -> List[ClassifiedChange]:
    return [ClassifiedChange(change=c, category=_classify(c)) for c in changes]


def group_by_category(classified: List[ClassifiedChange]) -> dict:
    result: dict = {}
    for cc in classified:
        result.setdefault(cc.category, []).append(cc)
    return result


def category_summary(classified: List[ClassifiedChange]) -> dict:
    groups = group_by_category(classified)
    return {cat: len(items) for cat, items in groups.items()}
