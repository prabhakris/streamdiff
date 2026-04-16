"""Reporting utilities for schema diffs."""
import json
import sys
from typing import Optional

from streamdiff.diff import DiffResult, ChangeType

_COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "reset": "\033[0m",
}


def _colorize(text: str, color: str, enabled: bool = True) -> str:
    if not enabled or color not in _COLORS:
        return text
    return f"{_COLORS[color]}{text}{_COLORS['reset']}"


_CHANGE_COLOR = {
    ChangeType.ADDED: "green",
    ChangeType.REMOVED: "red",
    ChangeType.MODIFIED: "yellow",
}


def print_diff(result: DiffResult, color: bool = True, file=None) -> None:
    file = file or sys.stdout
    if not result.changes:
        print("No schema changes detected.", file=file)
        return

    breaking_count = sum(1 for c in result.changes if c.breaking)
    print(f"Schema changes: {len(result.changes)} ({breaking_count} breaking)\n", file=file)

    for change in result.changes:
        tag = f"[{change.change_type.value.upper()}]"
        tag = _colorize(tag, _CHANGE_COLOR.get(change.change_type, "reset"), color)
        breaking_marker = _colorize(" [BREAKING]", "red", color) if change.breaking else ""
        print(f"  {tag} {change.field_name}{breaking_marker}", file=file)
        if change.detail:
            print(f"       {change.detail}", file=file)


def print_diff_json(result: DiffResult, file=None) -> None:
    file = file or sys.stdout
    payload = {
        "breaking": result.has_breaking,
        "changes": [
            {
                "field": c.field_name,
                "type": c.change_type.value,
                "breaking": c.breaking,
                "detail": c.detail,
            }
            for c in result.changes
        ],
    }
    print(json.dumps(payload, indent=2), file=file)


def exit_code(result: DiffResult) -> int:
    return 1 if result.has_breaking else 0
