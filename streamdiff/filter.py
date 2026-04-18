"""Filter schema changes by field name, change type, or breaking status."""

from typing import List, Optional
from streamdiff.diff import DiffResult, SchemaChange, ChangeType


def filter_changes(
    result: DiffResult,
    *,
    field_name: Optional[str] = None,
    change_type: Optional[ChangeType] = None,
    breaking_only: bool = False,
) -> DiffResult:
    """Return a new DiffResult with changes filtered by the given criteria."""
    changes: List[SchemaChange] = result.changes

    if field_name is not None:
        changes = [c for c in changes if c.field_name == field_name]

    if change_type is not None:
        changes = [c for c in changes if c.change_type == change_type]

    if breaking_only:
        from streamdiff.diff import is_breaking
        changes = [c for c in changes if is_breaking(c)]

    return DiffResult(changes=changes)


def filter_by_field_names(result: DiffResult, names: List[str]) -> DiffResult:
    """Keep only changes whose field name is in the provided list."""
    changes = [c for c in result.changes if c.field_name in names]
    return DiffResult(changes=changes)


def exclude_field_names(result: DiffResult, names: List[str]) -> DiffResult:
    """Remove changes whose field name is in the provided list."""
    changes = [c for c in result.changes if c.field_name not in names]
    return DiffResult(changes=changes)


def filter_by_change_types(result: DiffResult, change_types: List[ChangeType]) -> DiffResult:
    """Keep only changes whose change type is in the provided list.

    Args:
        result: The DiffResult to filter.
        change_types: A list of ChangeType values to retain.

    Returns:
        A new DiffResult containing only changes with a matching change type.
    """
    changes = [c for c in result.changes if c.change_type in change_types]
    return DiffResult(changes=changes)
