"""Group schema changes by namespace prefix or field path segment."""
from __future__ import annotations
from collections import defaultdict
from typing import Dict, List
from streamdiff.diff import SchemaChange


def group_by_prefix(changes: List[SchemaChange], separator: str = ".") -> Dict[str, List[SchemaChange]]:
    """Group changes by the first segment of the field name."""
    groups: Dict[str, List[SchemaChange]] = defaultdict(list)
    for change in changes:
        name = change.field_name
        prefix = name.split(separator)[0] if separator in name else name
        groups[prefix].append(change)
    return dict(groups)


def group_by_change_type(changes: List[SchemaChange]) -> Dict[str, List[SchemaChange]]:
    """Group changes by their ChangeType string value."""
    groups: Dict[str, List[SchemaChange]] = defaultdict(list)
    for change in changes:
        groups[change.change_type.value].append(change)
    return dict(groups)


def group_summary(groups: Dict[str, List[SchemaChange]]) -> Dict[str, int]:
    """Return a count summary for each group key."""
    return {key: len(items) for key, items in groups.items()}
