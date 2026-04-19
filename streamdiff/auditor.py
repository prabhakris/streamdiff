"""Audit log: record who diffed what and when."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class AuditEntry:
    timestamp: str
    user: str
    old_schema: str
    new_schema: str
    breaking: bool
    change_count: int
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "user": self.user,
            "old_schema": self.old_schema,
            "new_schema": self.new_schema,
            "breaking": self.breaking,
            "change_count": self.change_count,
            "tags": self.tags,
        }

    def __str__(self) -> str:
        flag = " [BREAKING]" if self.breaking else ""
        return (
            f"{self.timestamp} {self.user}: {self.old_schema} -> {self.new_schema}"
            f" ({self.change_count} changes){flag}"
        )


def _audit_path(audit_dir: str) -> Path:
    return Path(audit_dir) / "audit.jsonl"


def record_entry(
    old_schema: str,
    new_schema: str,
    breaking: bool,
    change_count: int,
    audit_dir: str = ".streamdiff/audit",
    user: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> AuditEntry:
    Path(audit_dir).mkdir(parents=True, exist_ok=True)
    entry = AuditEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        user=user or os.environ.get("USER", "unknown"),
        old_schema=old_schema,
        new_schema=new_schema,
        breaking=breaking,
        change_count=change_count,
        tags=tags or [],
    )
    with open(_audit_path(audit_dir), "a") as fh:
        fh.write(json.dumps(entry.to_dict()) + "\n")
    return entry


def load_entries(audit_dir: str = ".streamdiff/audit") -> List[AuditEntry]:
    path = _audit_path(audit_dir)
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        entries.append(AuditEntry(**d))
    return entries


def clear_audit(audit_dir: str = ".streamdiff/audit") -> None:
    path = _audit_path(audit_dir)
    if path.exists():
        path.unlink()
