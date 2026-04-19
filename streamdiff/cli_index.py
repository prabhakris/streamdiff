"""CLI subcommand: index — inspect and search schema fields."""
from __future__ import annotations
import argparse
import json
from streamdiff.loader import load_schema
from streamdiff.indexer import build_index
from streamdiff.schema import FieldType


def add_index_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("index", help="Index and search schema fields")
    p.add_argument("schema", help="Path to schema JSON file")
    p.add_argument("--search", default=None, help="Search fields by name substring")
    p.add_argument("--type", dest="field_type", default=None,
                   help="Filter by field type (e.g. string, int)")
    p.add_argument("--required-only", action="store_true", default=False)
    p.add_argument("--json", dest="as_json", action="store_true", default=False)


def handle_index(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:
        print(f"error: {exc}")
        return 2

    idx = build_index(schema)
    entries = list(idx.entries.values())

    if args.search:
        entries = idx.search(args.search)

    if args.field_type:
        try:
            ft = FieldType(args.field_type.lower())
        except ValueError:
            print(f"error: unknown type '{args.field_type}'")
            return 2
        entries = [e for e in entries if e.field_type == ft]

    if args.required_only:
        entries = [e for e in entries if e.required]

    if args.as_json:
        print(json.dumps([e.to_dict() for e in entries], indent=2))
    else:
        if not entries:
            print("No fields matched.")
        for e in entries:
            print(str(e))

    return 0
