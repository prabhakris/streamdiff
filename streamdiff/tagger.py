"""Tag schema changes with user-defined labels for categorization."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from streamdiff.diff import SchemaChange, ChangeType


@dataclass
class TaggedChange:
    change: SchemaChange
    tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        tag_str = ", ".join(self.tags) if self.tags else "untagged"
        return f"{self.change.field_name} [{tag_str}]"


# Default tag rules: (ChangeType -> tag)
_DEFAULT_TAGS: Dict[ChangeType, str] = {
    ChangeType.ADDED: "additive",
    ChangeType.REMOVED: "destructive",
    ChangeType.TYPE_CHANGED: "destructive",
    ChangeType.REQUIRED_CHANGED: "compatibility",
}


def _default_tag(change: SchemaChange) -> Optional[str]:
    return _DEFAULT_TAGS.get(change.change_type)


def tag_change(change: SchemaChange, extra_tags: Optional[Dict[str, List[str]]] = None) -> TaggedChange:
    """Tag a single change with default and optional field-level tags."""
    tags: List[str] = []
    default = _default_tag(change)
    if default:
        tags.append(default)
    if extra_tags and change.field_name in extra_tags:
        tags.extend(extra_tags[change.field_name])
    return TaggedChange(change=change, tags=tags)


def tag_all(changes: List[SchemaChange], extra_tags: Optional[Dict[str, List[str]]] = None) -> List[TaggedChange]:
    """Tag all changes."""
    return [tag_change(c, extra_tags) for c in changes]


def filter_by_tag(tagged: List[TaggedChange], tag: str) -> List[TaggedChange]:
    """Return only changes that include the given tag."""
    return [t for t in tagged if tag in t.tags]


def tags_summary(tagged: List[TaggedChange]) -> Dict[str, int]:
    """Return a count of each tag across all tagged changes."""
    counts: Dict[str, int] = {}
    for t in tagged:
        for tag in t.tags:
            counts[tag] = counts.get(tag, 0) + 1
    return counts
