"""Detect and handle field renames between two schemas."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from streamdiff.schema import SchemaField
from streamdiff.diff import DiffResult, SchemaChange, ChangeType


@dataclass
class RenameHint:
    old_name: str
    new_name: str
    confidence: float  # 0.0 - 1.0

    def __str__(self) -> str:
        pct = int(self.confidence * 100)
        return f"{self.old_name} -> {self.new_name} ({pct}% confidence)"


def _type_matches(a: SchemaField, b: SchemaField) -> bool:
    return a.field_type == b.field_type


def _name_similarity(a: str, b: str) -> float:
    """Simple character-overlap similarity."""
    if a == b:
        return 1.0
    set_a, set_b = set(a.lower()), set(b.lower())
    overlap = len(set_a & set_b)
    union = len(set_a | set_b)
    return overlap / union if union else 0.0


def detect_renames(
    result: DiffResult,
    min_confidence: float = 0.5,
) -> List[RenameHint]:
    """Cross-match removed and added fields to suggest renames."""
    removed: Dict[str, SchemaField] = {
        c.field_name: c.old_field
        for c in result.changes
        if c.change_type == ChangeType.REMOVED and c.old_field is not None
    }
    added: Dict[str, SchemaField] = {
        c.field_name: c.new_field
        for c in result.changes
        if c.change_type == ChangeType.ADDED and c.new_field is not None
    }

    hints: List[RenameHint] = []
    for old_name, old_field in removed.items():
        best_name: Optional[str] = None
        best_score = 0.0
        for new_name, new_field in added.items():
            if not _type_matches(old_field, new_field):
                continue
            score = _name_similarity(old_name, new_name)
            if score > best_score:
                best_score = score
                best_name = new_name
        if best_name is not None and best_score >= min_confidence:
            hints.append(RenameHint(old_name, best_name, round(best_score, 2)))
    return hints


def format_rename_hints(hints: List[RenameHint]) -> str:
    if not hints:
        return "No rename hints detected."
    lines = ["Possible renames:"]
    for h in hints:
        lines.append(f"  {h}")
    return "\n".join(lines)
