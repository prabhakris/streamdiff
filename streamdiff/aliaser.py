"""Field alias mapping: map old field names to new ones for diff purposes."""
from dataclasses import dataclass, field
from typing import Dict, Optional
from streamdiff.diff import SchemaChange, ChangeType
from streamdiff.schema import SchemaField


@dataclass
class AliasMap:
    """Bidirectional mapping of old -> new field names."""
    mappings: Dict[str, str] = field(default_factory=dict)

    def add(self, old_name: str, new_name: str) -> None:
        if not old_name or not new_name:
            raise ValueError("Alias old_name and new_name must be non-empty strings.")
        self.mappings[old_name] = new_name

    def resolve(self, name: str) -> Optional[str]:
        return self.mappings.get(name)

    def reverse(self) -> Dict[str, str]:
        return {v: k for k, v in self.mappings.items()}


def apply_aliases(changes: list[SchemaChange], alias_map: AliasMap) -> list[SchemaChange]:
    """Suppress remove+add pairs that are covered by an alias mapping."""
    reverse = alias_map.reverse()
    removed = {c.field_name: c for c in changes if c.change_type == ChangeType.REMOVED}
    added = {c.field_name: c for c in changes if c.change_type == ChangeType.ADDED}
    suppressed = set()

    for old_name, new_name in alias_map.mappings.items():
        if old_name in removed and new_name in added:
            suppressed.add(old_name)
            suppressed.add(new_name)

    return [c for c in changes if c.field_name not in suppressed]


def load_alias_map(data: Dict[str, str]) -> AliasMap:
    """Build an AliasMap from a plain dict."""
    am = AliasMap()
    for old, new in data.items():
        am.add(old, new)
    return am
