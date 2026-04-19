"""CLI subcommand: trim fields from a schema."""
import argparse
import json
import sys
from streamdiff.loader import load_schema
from streamdiff.trimmer import trim_by_types, trim_by_pattern, trim_optional


def add_trim_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("trim", help="Remove fields from a schema by type, pattern, or optionality")
    p.add_argument("schema", help="Path to schema JSON file")
    p.add_argument("--types", nargs="+", metavar="TYPE", help="Remove fields with these types")
    p.add_argument("--pattern", metavar="PATTERN", help="Remove fields whose name contains this substring")
    p.add_argument("--optional", action="store_true", help="Remove all optional fields")
    p.add_argument("--json", dest="json_out", action="store_true", help="Output result as JSON")


def handle_trim(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:
        print(f"error: could not load schema: {exc}", file=sys.stderr)
        return 2

    result = None

    if args.optional:
        result = trim_optional(schema)
    elif args.pattern:
        result = trim_by_pattern(schema, args.pattern)
    elif args.types:
        result = trim_by_types(schema, set(args.types))
    else:
        print("error: specify --types, --pattern, or --optional", file=sys.stderr)
        return 2

    if args.json_out:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))
        if result:
            print(f"Remaining fields: {len(result.schema.fields)}")

    return 0
