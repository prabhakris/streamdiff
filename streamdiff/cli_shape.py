"""cli_shape.py — CLI subcommand for schema shaping."""
import argparse
import json
import sys
from typing import List

from streamdiff.loader import load_schema
from streamdiff.shaper import list_transforms, shape_schema


def add_shape_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "shape",
        help="Apply field transforms to a schema.",
    )
    p.add_argument("schema", help="Path to schema JSON file.")
    p.add_argument(
        "--transforms",
        nargs="+",
        default=[],
        metavar="TRANSFORM",
        help="Named transforms to apply in order.",
    )
    p.add_argument(
        "--list-transforms",
        action="store_true",
        default=False,
        help="List available transforms and exit.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output result as JSON.",
    )
    p.set_defaults(func=handle_shape)


def handle_shape(args: argparse.Namespace) -> int:
    if args.list_transforms:
        for name in list_transforms():
            print(name)
        return 0

    try:
        schema = load_schema(args.schema)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = shape_schema(schema, args.transforms)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))
        if result.applied:
            print(f"  changed fields : {', '.join(result.applied)}")
        if result.skipped:
            print(f"  unknown transforms: {', '.join(result.skipped)}")

    return 0
