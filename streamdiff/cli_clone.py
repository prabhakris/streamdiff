"""CLI subcommand: clone — copy a schema file with optional type remapping."""
from __future__ import annotations
import argparse
import json
import sys

from streamdiff.loader import load_schema
from streamdiff.schema import FieldType
from streamdiff.cloner import clone_schema
from streamdiff.exporter import export_json


def add_clone_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("clone", help="Clone a schema with optional type remapping")
    p.add_argument("schema", help="Path to source schema JSON file")
    p.add_argument(
        "--remap",
        metavar="FIELD:TYPE",
        action="append",
        default=[],
        help="Remap a field type, e.g. count:long (repeatable)",
    )
    p.add_argument(
        "--upper",
        action="store_true",
        default=False,
        help="Uppercase all field names in the clone",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        default=False,
        help="Output cloned schema as JSON",
    )
    p.set_defaults(func=handle_clone)


def _parse_remap(specs: list[str]) -> dict:
    mapping = {}
    for spec in specs:
        if ":" not in spec:
            raise ValueError(f"Invalid remap spec '{spec}': expected FIELD:TYPE")
        name, type_str = spec.split(":", 1)
        try:
            mapping[name.strip()] = FieldType(type_str.strip().lower())
        except ValueError:
            raise ValueError(f"Unknown type '{type_str}' in remap spec '{spec}'")
    return mapping


def handle_clone(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:
        print(f"error: could not load schema: {exc}", file=sys.stderr)
        return 2

    try:
        type_map = _parse_remap(args.remap)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    name_fn = str.upper if args.upper else None
    result = clone_schema(schema, type_map=type_map, name_fn=name_fn)

    if args.as_json:
        print(json.dumps(export_json(result.cloned), indent=2))
    else:
        print(str(result))

    return 0
