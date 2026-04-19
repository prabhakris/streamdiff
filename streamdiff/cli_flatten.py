"""CLI subcommand: flatten — show a schema as flat dot-notation paths."""
import argparse
import json
import sys
from streamdiff.loader import load_schema
from streamdiff.flattener import flatten_schema, diff_flat_schemas


def add_flatten_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("flatten", help="Flatten schema fields to dot-notation paths")
    p.add_argument("schema", help="Path to schema file")
    p.add_argument("--compare", metavar="SCHEMA2", help="Compare against a second schema")
    p.add_argument("--separator", default=".", help="Path separator (default: '.')")
    p.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")
    p.set_defaults(func=handle_flatten)


def handle_flatten(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:
        print(f"Error loading schema: {exc}", file=sys.stderr)
        return 2

    flat = flatten_schema(schema, separator=args.separator)

    if args.compare:
        try:
            schema2 = load_schema(args.compare)
        except Exception as exc:
            print(f"Error loading compare schema: {exc}", file=sys.stderr)
            return 2
        flat2 = flatten_schema(schema2, separator=args.separator)
        diff = diff_flat_schemas(flat, flat2)
        if args.as_json:
            print(json.dumps(diff, indent=2))
        else:
            for key, paths in diff.items():
                if paths:
                    print(f"{key}:")
                    for p in paths:
                        print(f"  {p}")
        return 0

    if args.as_json:
        print(json.dumps(flat.to_dict(), indent=2))
    else:
        for f in flat.fields:
            print(str(f))
    return 0
