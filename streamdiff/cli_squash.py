"""CLI subcommand: squash multiple schema diff results."""
import argparse
import json
import sys
from typing import List

from streamdiff.loader import load_schema
from streamdiff.diff import compute_diff
from streamdiff.squasher import squash


def add_squash_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "squash",
        help="Squash diffs across multiple schema pairs into one consolidated result.",
    )
    p.add_argument(
        "--pairs",
        nargs="+",
        metavar="OLD:NEW",
        required=True,
        help="Pairs of schema files as old:new.",
    )
    p.add_argument("--json", action="store_true", help="Output as JSON.")
    p.set_defaults(func=handle_squash)


def _parse_pairs(pairs: List[str]):
    parsed = []
    for pair in pairs:
        if ":" not in pair:
            return None, f"Invalid pair '{pair}': expected old:new format."
        old_path, new_path = pair.split(":", 1)
        parsed.append((old_path, new_path))
    return parsed, None


def handle_squash(args: argparse.Namespace) -> int:
    pairs, err = _parse_pairs(args.pairs)
    if err:
        print(f"Error: {err}", file=sys.stderr)
        return 2

    results = []
    for old_path, new_path in pairs:
        try:
            old = load_schema(old_path)
            new = load_schema(new_path)
        except Exception as exc:
            print(f"Error loading schemas: {exc}", file=sys.stderr)
            return 2
        results.append(compute_diff(old, new))

    squashed = squash(results)

    if args.json:
        print(json.dumps(squashed.to_dict(), indent=2))
    else:
        print(str(squashed))

    return 1 if any(c.breaking for c in squashed.changes) else 0
