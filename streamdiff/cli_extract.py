"""CLI subcommand for field extraction."""
from __future__ import annotations
import argparse
import json
import sys
from streamdiff.loader import load_schema
from streamdiff.extractor import extract_by_names, extract_by_pattern, extract_by_type


def add_extract_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("extract", help="Extract fields from a schema")
    p.add_argument("schema", help="Path to schema file")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--names",
        nargs="+",
        metavar="FIELD",
        help="Extract fields by exact name",
    )
    mode.add_argument(
        "--pattern",
        metavar="GLOB",
        help="Extract fields matching a glob pattern",
    )
    mode.add_argument(
        "--type",
        dest="field_type",
        metavar="TYPE",
        help="Extract fields of a specific type",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output result as JSON",
    )
    p.add_argument(
        "--output-schema",
        action="store_true",
        default=False,
        help="Output extracted fields as a schema JSON",
    )
    p.set_defaults(func=handle_extract)


def handle_extract(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.names:
        result = extract_by_names(schema, args.names)
    elif args.pattern:
        result = extract_by_pattern(schema, args.pattern)
    else:
        result = extract_by_type(schema, args.field_type)

    if args.output_schema:
        out = result.to_schema(name=schema.name + "_extracted")
        print(json.dumps({"name": out.name, "fields": [f.name for f in out.fields]}, indent=2))
        return 0

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))
        print(f"  extracted: {', '.join(f.name for f in result.extracted) or '(none)'}")
        print(f"  dropped:   {', '.join(f.name for f in result.dropped) or '(none)'}")

    return 0
