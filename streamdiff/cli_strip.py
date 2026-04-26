"""CLI sub-command: strip — remove or neutralise field attributes."""
import argparse
import json
import sys
from typing import List

from streamdiff.loader import load_schema
from streamdiff.stripper import strip_by_names, strip_required


def add_strip_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    parser = subparsers.add_parser(
        "strip",
        help="Strip attributes or fields from a schema.",
    )
    parser.add_argument("schema", help="Path to schema JSON file.")
    parser.add_argument(
        "--required",
        action="store_true",
        default=False,
        help="Mark all fields as optional (strip required flag).",
    )
    parser.add_argument(
        "--fields",
        nargs="+",
        metavar="NAME",
        default=None,
        help="Remove fields with these names.",
    )
    parser.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        default=False,
        help="Output result as JSON.",
    )
    parser.set_defaults(func=handle_strip)


def handle_strip(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:  # noqa: BLE001
        print(f"error: cannot load schema: {exc}", file=sys.stderr)
        return 2

    if args.required:
        result = strip_required(schema)
    elif args.fields:
        result = strip_by_names(schema, set(args.fields))
    else:
        print("error: specify --required or --fields", file=sys.stderr)
        return 2

    if args.output_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))
        for f in result.stripped_fields:
            flag = "required" if f.required else "optional"
            print(f"  {f.name} ({f.field_type.value}, {flag})")

    return 0
