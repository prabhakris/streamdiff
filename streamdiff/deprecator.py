"""Mark and track deprecated fields in a schema."""
from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.schema import SchemaField
from streamdiff.diff import DiffResult, ChangeType


@dataclass
class DeprecationNotice:
    field_name: str
    reason: str
    since: Optional[str] = None

    def __str__(self) -> str:
        parts = [f"DEPRECATED: {self.field_name} — {self.reason}"]
        if self.since:
            parts.append(f"(since {self.since})")
        return " ".join(parts)

    def to_dict(self) -> dict:
        return {"field": self.field_name, "reason": self.reason, "since": self.since}


@dataclass
class DeprecationReport:
    notices: List[DeprecationNotice] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.notices) > 0

    def to_dict(self) -> dict:
        return {"deprecated": [n.to_dict() for n in self.notices]}


DEFAULT_PREFIXES = ("deprecated_", "old_", "legacy_", "obsolete_")
DEFAULT_SUFFIXES = ("_deprecated", "_old", "_legacy", "_v1", "_v2")


def _looks_deprecated(name: str) -> bool:
    lower = name.lower()
    return any(lower.startswith(p) for p in DEFAULT_PREFIXES) or \
           any(lower.endswith(s) for s in DEFAULT_SUFFIXES)


def detect_deprecated_fields(
    result: DiffResult,
    since: Optional[str] = None,
) -> DeprecationReport:
    """Scan diff result for fields that appear deprecated by naming convention."""
    notices: List[DeprecationNotice] = []
    for change in result.changes:
        if change.change_type in (ChangeType.ADDED, ChangeType.REMOVED):
            name = change.field_name
            if _looks_deprecated(name):
                reason = "field name matches deprecation naming convention"
                notices.append(DeprecationNotice(field_name=name, reason=reason, since=since))
    return DeprecationReport(notices=notices)


def format_deprecation_text(report: DeprecationReport) -> str:
    if not report:
        return "No deprecated fields detected."
    lines = [str(n) for n in report.notices]
    return "\n".join(lines)
