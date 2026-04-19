"""cli_stencil.py — CLI subcommand for applying a field stencil to a schema."""
from __future__ import annotations
import argparse
import json
import sys
from streamdiff.loader import load_schema
from streamdiff.stenciler import apply_stencil, apply_stencil_prefix


def add_stencil_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("stencil", help="Mask a schema to a set of allowed fields")
    p.add_argument("schema", help="Path to schema file")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--fields",
        nargs="+",
        metavar="FIELD",
        help="Exact field names to keep",
    )
    group.add_argument(
        "--prefix",
        nargs="+",
        metavar="PREFIX",
        help="Keep fields whose names start with any prefix",
    )
    p.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")
    p.add_argument("--out", metavar="FILE", help="Write resulting schema to file")
    p.set_defaults(func=handle_stencil)


def handle_stencil(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.fields:
        result = apply_stencil(schema, set(args.fields))
    else:
        result = apply_stencil_prefix(schema, args.prefix)

    if args.as_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))
        print(f"  kept   : {[f.name for f in result.kept]}")
        print(f"  dropped: {[f.name for f in result.dropped]}")

    if args.out:
        out_schema = result.to_schema(schema.name)
        with open(args.out, "w") as fh:
            fields_data = [
                {"name": f.name, "type": f.field_type.value, "required": f.required}
                for f in out_schema.fields
            ]
            json.dump({"name": out_schema.name, "fields": fields_data}, fh, indent=2)

    return 0 if bool(result) else 1
