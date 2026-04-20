"""CLI subcommand: retype — bulk retype schema fields."""

import argparse
import json
import sys
from typing import List, Optional

from streamdiff.loader import load_schema
from streamdiff.schema import FieldType
from streamdiff.retyper import retype_schema


def add_retype_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "retype",
        help="Bulk retype fields in a schema according to a type mapping.",
    )
    p.add_argument("schema", help="Path to the schema JSON file.")
    p.add_argument(
        "--map",
        metavar="OLD:NEW",
        action="append",
        dest="mappings",
        default=[],
        help="Type mapping in the form OLD:NEW (e.g. int:long). Repeatable.",
    )
    p.add_argument(
        "--fields",
        metavar="NAME",
        nargs="+",
        default=None,
        help="Limit retyping to these field names.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output result as JSON.",
    )
    p.set_defaults(func=handle_retype)


def _parse_type_map(mappings: List[str]) -> dict:
    type_map = {}
    for mapping in mappings:
        if ":" not in mapping:
            raise ValueError(f"Invalid mapping '{mapping}': expected OLD:NEW format.")
        old_str, new_str = mapping.split(":", 1)
        try:
            old_type = FieldType(old_str.lower())
            new_type = FieldType(new_str.lower())
        except ValueError as exc:
            raise ValueError(f"Unknown field type in mapping '{mapping}': {exc}") from exc
        type_map[old_type] = new_type
    return type_map


def handle_retype(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading schema: {exc}", file=sys.stderr)
        return 2

    try:
        type_map = _parse_type_map(args.mappings)
    except ValueError as exc:
        print(f"Error parsing type map: {exc}", file=sys.stderr)
        return 2

    result = retype_schema(schema, type_map, names=args.fields)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))

    return 0
