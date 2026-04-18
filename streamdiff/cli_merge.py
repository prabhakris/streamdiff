"""CLI subcommand: merge two schema files."""
import argparse
import json
import sys
from streamdiff.loader import load_schema
from streamdiff.merger import merge_schemas


def add_merge_subparser(subparsers) -> None:
    p = subparsers.add_parser("merge", help="Merge two schema files")
    p.add_argument("base", help="Base schema file")
    p.add_argument("other", help="Schema file to merge in")
    p.add_argument(
        "--prefer",
        choices=["base", "other"],
        default="base",
        help="Which side wins on type conflict (default: base)",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        default=False,
        help="Output merged schema as JSON",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit non-zero if any conflicts were found",
    )


def handle_merge(args) -> int:
    base = load_schema(args.base)
    other = load_schema(args.other)
    result = merge_schemas(base, other, prefer=args.prefer)

    if result.conflicts:
        for c in result.conflicts:
            print(f"[CONFLICT] {c}", file=sys.stderr)

    if args.as_json:
        fields = [
            {"name": f.name, "type": f.field_type.value, "required": f.required}
            for f in result.schema.fields
        ]
        print(json.dumps({"name": result.schema.name, "fields": fields}, indent=2))
    else:
        print(f"Merged schema '{result.schema.name}': {len(result.schema.fields)} fields")
        if result.ok:
            print("No conflicts.")
        else:
            print(f"{len(result.conflicts)} conflict(s) resolved with prefer='{args.prefer}'.")

    if args.strict and result.conflicts:
        return 1
    return 0
