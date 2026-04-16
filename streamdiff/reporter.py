import sys
from typing import TextIO

from streamdiff.diff import DiffResult, ChangeType

COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_GREEN = "\033[32m"
COLOR_RESET = "\033[0m"

CHANGE_ICONS = {
    ChangeType.ADDED_OPTIONAL: (COLOR_GREEN, "+"),
    ChangeType.ADDED_REQUIRED: (COLOR_RED, "+!"),
    ChangeType.REMOVED: (COLOR_RED, "-"),
    ChangeType.TYPE_CHANGED: (COLOR_RED, "~"),
    ChangeType.NULLABILITY_CHANGED: (COLOR_YELLOW, "~"),
}


def _colorize(text: str, color: str, use_color: bool) -> str:
    if use_color:
        return f"{color}{text}{COLOR_RESET}"
    return text


def print_diff(result: DiffResult, stream: TextIO = sys.stdout, use_color: bool = True) -> None:
    if not result.changes:
        print(_colorize("No schema changes detected.", COLOR_GREEN, use_color), file=stream)
        return

    print(f"Found {len(result.changes)} change(s):", file=stream)

    for change in result.changes:
        color, icon = CHANGE_ICONS.get(change.change_type, (COLOR_RESET, "?"))
        prefix = _colorize(f"[{icon}]", color, use_color)
        print(f"  {prefix} {change.detail}", file=stream)

    print("", file=stream)
    if result.has_breaking_changes:
        msg = f"BREAKING: {len(result.breaking_changes)} breaking change(s) detected."
        print(_colorize(msg, COLOR_RED, use_color), file=stream)
    else:
        print(_colorize("All changes are non-breaking.", COLOR_GREEN, use_color), file=stream)


def exit_code(result: DiffResult) -> int:
    return 1 if result.has_breaking_changes else 0
