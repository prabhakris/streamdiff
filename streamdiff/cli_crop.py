"""CLI sub-command: crop — trim a schema to a maximum number of fields."""
from __future__ import annotations

import argparse
import json
import sys

from streamdiff.cropper import crop_schema
from streamdiff.loader import load_schema


def add_crop_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "crop",
        help="Trim a schema to at most N fields.",
    )
    p.add_argument("schema", help="Path to the schema JSON file.")
    p.add_argument(
        "--limit",
        type=int,
        required=True,
        metavar="N",
        help="Maximum number of fields to keep.",
    )
    p.add_argument(
        "--sort",
        dest="sort_key",
        choices=["name", "type"],
        default=None,
        help="Sort fields before cropping (default: preserve original order).",
    )
    p.add_argument(
        "--desc",
        dest="descending",
        action="store_true",
        default=False,
        help="Reverse the sort order.",
    )
    p.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        default=False,
        help="Emit the result as JSON.",
    )
    p.set_defaults(func=handle_crop)


def handle_crop(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not load schema: {exc}", file=sys.stderr)
        return 2

    try:
        result = crop_schema(
            schema,
            limit=args.limit,
            sort_key=args.sort_key,
            descending=args.descending,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.output_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))
        if result.dropped:
            print("Dropped fields:")
            for f in result.dropped:
                print(f"  - {f.name} ({f.field_type.value})")

    return 0
