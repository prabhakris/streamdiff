"""CLI subcommand: project — project a schema onto a subset of dot-notation field paths."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from streamdiff.loader import load_schema
from streamdiff.projector import project_schema


def add_project_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "project",
        help="Project a schema onto a subset of fields using dot-notation paths.",
    )
    parser.add_argument("schema", help="Path to the schema JSON file.")
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        help="Dot-notation field paths to include (e.g. user.id user.name). "
             "If omitted, all fields are included.",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        default=False,
        help="Output result as JSON.",
    )
    parser.add_argument(
        "--show-excluded",
        action="store_true",
        default=False,
        help="Also list excluded fields in text output.",
    )
    parser.set_defaults(func=handle_project)


def handle_project(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = project_schema(schema, paths=args.paths or None)

    if args.as_json:
        print(json.dumps(result.to_dict(), indent=2))
        return 0

    print(f"Projected {len(result.included)} / {len(result.included) + len(result.excluded)} fields")
    for f in result.included:
        req = "required" if f.required else "optional"
        print(f"  {f.name}  ({f.type.value}, {req})")

    if args.show_excluded and result.excluded:
        print(f"Excluded ({len(result.excluded)}):")
        for f in result.excluded:
            print(f"  - {f.name}")

    return 0
