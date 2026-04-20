"""CLI integration for the reorder (field ordering diff) feature."""

import argparse
import json
import sys
from typing import Optional

from streamdiff.loader import load_schema
from streamdiff.reorder import detect_reorder


def add_reorder_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'reorder' subcommand."""
    parser = subparsers.add_parser(
        "reorder",
        help="Detect field ordering changes between two schema versions.",
    )
    parser.add_argument("old", help="Path to the old schema file.")
    parser.add_argument("new", help="Path to the new schema file.")
    parser.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        default=False,
        help="Output result as JSON.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if any reordering is detected.",
    )


def handle_reorder(args: argparse.Namespace) -> int:
    """Handle the 'reorder' subcommand. Returns an exit code."""
    try:
        old_schema = load_schema(args.old)
    except Exception as exc:
        print(f"Error loading old schema: {exc}", file=sys.stderr)
        return 2

    try:
        new_schema = load_schema(args.new)
    except Exception as exc:
        print(f"Error loading new schema: {exc}", file=sys.stderr)
        return 2

    result = detect_reorder(old_schema, new_schema)

    if args.output_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))

    if args.exit_code and result:
        return 1
    return 0
