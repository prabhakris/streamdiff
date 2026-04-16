"""Schema compatibility validation rules."""
from dataclasses import dataclass
from typing import List

from streamdiff.diff import DiffResult, ChangeType, SchemaChange


@dataclass
class ValidationIssue:
    change: SchemaChange
    rule: str
    message: str

    def __str__(self) -> str:
        return f"[{self.rule}] {self.message} (field: {self.change.field_name})"


def _check_required_added(change: SchemaChange) -> ValidationIssue | None:
    if change.change_type == ChangeType.ADDED and change.new_field and change.new_field.required:
        return ValidationIssue(
            change=change,
            rule="NO_REQUIRED_ADD",
            message=f"Adding required field '{change.field_name}' breaks existing consumers",
        )
    return None


def _check_type_changed(change: SchemaChange) -> ValidationIssue | None:
    if change.change_type == ChangeType.TYPE_CHANGED:
        old = change.old_field.field_type.value if change.old_field else "?"
        new = change.new_field.field_type.value if change.new_field else "?"
        return ValidationIssue(
            change=change,
            rule="NO_TYPE_CHANGE",
            message=f"Type change from '{old}' to '{new}' for field '{change.field_name}' is incompatible",
        )
    return None


def _check_removed(change: SchemaChange) -> ValidationIssue | None:
    if change.change_type == ChangeType.REMOVED:
        return ValidationIssue(
            change=change,
            rule="NO_REMOVAL",
            message=f"Removing field '{change.field_name}' may break existing consumers",
        )
    return None


_RULES = [_check_required_added, _check_type_changed, _check_removed]


def validate(result: DiffResult) -> List[ValidationIssue]:
    """Return all validation issues found in a diff result."""
    issues: List[ValidationIssue] = []
    for change in result.changes:
        for rule in _RULES:
            issue = rule(change)
            if issue:
                issues.append(issue)
    return issues


def is_valid(result: DiffResult) -> bool:
    return len(validate(result)) == 0
