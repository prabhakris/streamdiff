"""CLI subcommand: embed — produce field vectors for a schema."""
from __future__ import annotations
import argparse
import json
import sys
from streamdiff.loader import load_schema
from streamdiff.embedder import embed_schema


def add_embed_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("embed", help="Embed schema fields as feature vectors")
    p.add_argument("schema", help="Path to schema JSON file")
    p.add_argument("--json", dest="as_json", action="store_true", default=False,
                   help="Output as JSON")
    p.add_argument("--field", dest="field_name", default=None,
                   help="Show vector for a single field only")
    p.set_defaults(func=handle_embed)


def handle_embed(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = embed_schema(schema)

    if args.field_name:
        vec = report.by_field(args.field_name)
        if vec is None:
            print(f"error: field '{args.field_name}' not found", file=sys.stderr)
            return 2
        if args.as_json:
            print(json.dumps(vec.to_dict(), indent=2))
        else:
            print(str(vec))
        return 0

    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        for vec in report.vectors:
            print(str(vec))

    return 0
