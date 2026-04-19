"""CLI helpers for --scope-include / --scope-exclude arguments."""
from __future__ import annotations
import argparse
from typing import List

from streamdiff.diff import DiffResult
from streamdiff.scoper import ScopeConfig, ScopeResult, apply_scope


def add_scope_args(parser: argparse.ArgumentParser) -> None:
    """Register scope filter arguments onto an existing parser."""
    parser.add_argument(
        "--scope-include",
        metavar="PATTERN",
        nargs="+",
        default=[],
        help="Glob patterns for field names to include (e.g. 'user.*').",
    )
    parser.add_argument(
        "--scope-exclude",
        metavar="PATTERN",
        nargs="+",
        default=[],
        help="Glob patterns for field names to exclude.",
    )


def build_scope_config(args: argparse.Namespace) -> ScopeConfig:
    return ScopeConfig(
        includes=list(args.scope_include or []),
        excludes=list(args.scope_exclude or []),
    )


def apply_scope_args(result: DiffResult, args: argparse.Namespace) -> ScopeResult:
    """Build a ScopeConfig from parsed args and apply it to a DiffResult."""
    cfg = build_scope_config(args)
    return apply_scope(result, cfg)


def format_scope_summary(scope_result: ScopeResult) -> str:
    lines: List[str] = []
    lines.append(f"Scoped changes: {scope_result.total_after} shown, {scope_result.dropped} dropped.")
    for c in scope_result.changes:
        lines.append(f"  [{c.change_type.value}] {c.field_name}")
    return "\n".join(lines)
