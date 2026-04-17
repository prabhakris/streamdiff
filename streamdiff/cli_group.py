"""CLI helpers for --group-by option."""
from __future__ import annotations
import argparse
from typing import List
from streamdiff.diff import SchemaChange
from streamdiff.grouper import group_by_prefix, group_by_change_type, group_summary

VALID_GROUP_BY = ("prefix", "change_type")


def add_group_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--group-by",
        choices=VALID_GROUP_BY,
        default=None,
        help="Group output changes by 'prefix' or 'change_type'.",
    )
    parser.add_argument(
        "--group-separator",
        default=".",
        help="Field name separator used when grouping by prefix (default: '.').",
    )


def apply_grouping(args: argparse.Namespace, changes: List[SchemaChange]) -> None:
    """Print grouped summary to stdout if --group-by is set."""
    if not args.group_by:
        return
    if args.group_by == "prefix":
        groups = group_by_prefix(changes, separator=args.group_separator)
    else:
        groups = group_by_change_type(changes)
    summary = group_summary(groups)
    for key, count in sorted(summary.items()):
        print(f"  [{key}] {count} change(s)")
