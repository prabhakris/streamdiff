"""cli_delimit.py — CLI subcommand for schema field delimiting."""
from __future__ import annotations

import json
import sys
from argparse import ArgumentParser, Namespace, _SubParsersAction

from streamdiff.loader import load_schema
from streamdiff.delimiter import delimit_schema


def add_delimit_subparser(subparsers: _SubParsersAction) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "delimit",
        help="Split schema fields into groups by a delimiter in field names.",
    )
    p.add_argument("schema", help="Path to schema JSON file.")
    p.add_argument(
        "--delimiter",
        default=".",
        metavar="CHAR",
        help="Delimiter character to split on (default: '.').",
    )
    p.add_argument(
        "--depth",
        type=int,
        default=1,
        metavar="N",
        help="Number of prefix segments to group by (default: 1).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output result as JSON.",
    )
    p.set_defaults(func=handle_delimit)


def handle_delimit(args: Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not load schema: {exc}", file=sys.stderr)
        return 2

    result = delimit_schema(schema, delimiter=args.delimiter, depth=args.depth)

    if args.output_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))

    return 0
