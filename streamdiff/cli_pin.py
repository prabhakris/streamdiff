"""CLI subcommands for schema pinning."""
from __future__ import annotations

import argparse
import sys

from streamdiff.loader import load_schema
from streamdiff.pinner import save_pin, load_pin, list_pins, delete_pin, compare_to_pin
from streamdiff.diff import has_breaking_changes


def add_pin_subparser(subparsers: argparse._SubParsersAction) -> None:
    pin_p = subparsers.add_parser("pin", help="manage schema pins")
    pin_sub = pin_p.add_subparsers(dest="pin_cmd")

    # save
    save_p = pin_sub.add_parser("save", help="pin current schema as a named version")
    save_p.add_argument("name", help="pin name")
    save_p.add_argument("schema", help="schema file")
    save_p.add_argument("--pins-dir", default=".streamdiff_pins")

    # list
    list_p = pin_sub.add_parser("list", help="list saved pins")
    list_p.add_argument("--pins-dir", default=".streamdiff_pins")

    # delete
    del_p = pin_sub.add_parser("delete", help="delete a pin")
    del_p.add_argument("name")
    del_p.add_argument("--pins-dir", default=".streamdiff_pins")

    # compare
    cmp_p = pin_sub.add_parser("compare", help="compare schema against a pin")
    cmp_p.add_argument("name", help="pin name")
    cmp_p.add_argument("schema", help="current schema file")
    cmp_p.add_argument("--pins-dir", default=".streamdiff_pins")
    cmp_p.add_argument("--json", action="store_true", dest="as_json")


def handle_pin(args: argparse.Namespace) -> int:
    cmd = getattr(args, "pin_cmd", None)
    if cmd is None:
        print("Usage: streamdiff pin {save,list,delete,compare}", file=sys.stderr)
        return 2

    if cmd == "save":
        schema = load_schema(args.schema)
        path = save_pin(args.name, schema, pins_dir=args.pins_dir)
        print(f"Pinned '{args.name}' -> {path}")
        return 0

    if cmd == "list":
        pins = list_pins(pins_dir=args.pins_dir)
        if not pins:
            print("No pins saved.")
        else:
            for p in sorted(pins):
                print(p)
        return 0

    if cmd == "delete":
        removed = delete_pin(args.name, pins_dir=args.pins_dir)
        if removed:
            print(f"Deleted pin '{args.name}'.")
            return 0
        print(f"Pin '{args.name}' not found.", file=sys.stderr)
        return 1

    if cmd == "compare":
        schema = load_schema(args.schema)
        result = compare_to_pin(args.name, schema, pins_dir=args.pins_dir)
        if not result.found:
            print(f"Pin '{args.name}' not found.", file=sys.stderr)
            return 2
        if args.as_json:
            from streamdiff.reporter import print_diff_json
            print_diff_json(result.diff)
        else:
            from streamdiff.reporter import print_diff
            print_diff(result.diff)
        return 1 if has_breaking_changes(result.diff) else 0

    print(f"Unknown pin subcommand: {cmd}", file=sys.stderr)
    return 2
