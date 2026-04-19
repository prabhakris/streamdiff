"""CLI subcommand: stretch — expand a schema with suffix or type variants."""
import argparse
import json
import sys
from streamdiff.loader import load_schema
from streamdiff.stretcher import stretch_by_suffix, stretch_by_types
from streamdiff.schema import FieldType


def add_stretch_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("stretch", help="Expand a schema with field variants")
    p.add_argument("schema", help="Path to schema JSON file")
    p.add_argument(
        "--suffix",
        nargs="+",
        metavar="SUFFIX",
        default=[],
        help="Suffixes to append to each field name",
    )
    p.add_argument(
        "--types",
        nargs="+",
        metavar="TYPE",
        default=[],
        help="Extra field types to inject (e.g. integer boolean)",
    )
    p.add_argument(
        "--required",
        action="store_true",
        default=False,
        help="Mark generated fields as required",
    )
    p.add_argument("--json", dest="json_output", action="store_true", default=False)
    p.set_defaults(func=handle_stretch)


def handle_stretch(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = None

    if args.suffix:
        result = stretch_by_suffix(schema, args.suffix, required=args.required)
        schema = result.schema

    if args.types:
        try:
            fts = [FieldType(t) for t in args.types]
        except ValueError as exc:
            print(f"error: unknown type — {exc}", file=sys.stderr)
            return 2
        result = stretch_by_types(schema, fts, required=args.required)
        schema = result.schema

    if result is None:
        print("No stretch operations specified.", file=sys.stderr)
        return 2

    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))
        for f in result.added_fields:
            req = "required" if f.required else "optional"
            print(f"  + {f.name} ({f.field_type.value}, {req})")

    return 0
