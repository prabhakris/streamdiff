"""CLI integration for schema digest comparison."""
from __future__ import annotations

import argparse
import json
import sys

from streamdiff.loader import load_schema
from streamdiff.digester import compare_digests


def add_digest_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "digest",
        help="Compare schema fingerprints without full diff",
    )
    p.add_argument("old", help="Path to old schema file")
    p.add_argument("new", help="Path to new schema file")
    p.add_argument(
        "--algorithm",
        default="sha256",
        choices=["sha256", "sha1", "md5"],
        help="Hash algorithm (default: sha256)",
    )
    p.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="Output result as JSON",
    )
    p.add_argument(
        "--exit-on-change",
        action="store_true",
        help="Exit with code 1 if schemas differ",
    )
    p.set_defaults(func=handle_digest)


def handle_digest(args: argparse.Namespace) -> int:
    try:
        old_schema = load_schema(args.old)
        new_schema = load_schema(args.new)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading schema: {exc}", file=sys.stderr)
        return 2

    result = compare_digests(old_schema, new_schema, algorithm=args.algorithm)

    if getattr(args, "output_json", False):
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))

    if getattr(args, "exit_on_change", False) and result.changed:
        return 1
    return 0
