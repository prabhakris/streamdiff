"""Severity levels for schema changes."""
from enum import Enum
from streamdiff.diff import SchemaChange, ChangeType


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


def get_severity(change: SchemaChange) -> Severity:
    """Return severity level for a given schema change."""
    if change.change_type == ChangeType.REMOVED:
        return Severity.ERROR
    if change.change_type == ChangeType.TYPE_CHANGED:
        return Severity.ERROR
    if change.change_type == ChangeType.ADDED:
        if change.field and change.field.required:
            return Severity.ERROR
        return Severity.INFO
    if change.change_type == ChangeType.REQUIRED_CHANGED:
        # optional -> required is breaking
        if change.field and change.field.required:
            return Severity.ERROR
        return Severity.WARNING
    return Severity.INFO


def annotate_changes(changes: list[SchemaChange]) -> list[tuple[SchemaChange, Severity]]:
    """Pair each change with its severity."""
    return [(c, get_severity(c)) for c in changes]


def filter_by_severity(
    annotated: list[tuple[SchemaChange, Severity]],
    min_severity: Severity,
) -> list[tuple[SchemaChange, Severity]]:
    """Return only changes at or above the given severity level."""
    order = [Severity.INFO, Severity.WARNING, Severity.ERROR]
    threshold = order.index(min_severity)
    return [(c, s) for c, s in annotated if order.index(s) >= threshold]
