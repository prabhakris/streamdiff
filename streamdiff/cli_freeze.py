"""CLI subcommands for schema freezing."""
from __future__ import annotations

import argparse
import sys

from streamdiff.loader import load_schema
from streamdiff.diff import compute_diff
from streamdiff.freezer import save_freeze, load_freeze, check_freeze


def add_freeze_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("freeze", help="Freeze or check a frozen schema")
    sub = p.add_subparsers(dest="freeze_cmd", required=True)

    save_p = sub.add_parser("save", help="Save a freeze record for a schema")
    save_p.add_argument("schema", help="Path to schema file")
    save_p.add_argument("--name", required=True, help="Freeze record name")
    save_p.add_argument("--dir", default=".streamdiff/freezes", help="Directory for freeze records")

    check_p = sub.add_parser("check", help="Check schema against a freeze record")
    check_p.add_argument("old", help="Frozen (old) schema file")
    check_p.add_argument("new", help="New schema file")
    check_p.add_argument("--name", required=True, help="Freeze record name")
    check_p.add_argument("--dir", default=".streamdiff/freezes", help="Directory for freeze records")
    check_p.add_argument("--json", action="store_true", dest="as_json")


def handle_freeze(args: argparse.Namespace) -> int:
    if args.freeze_cmd == "save":
        try:
            schema = load_schema(args.schema)
        except Exception as e:
            print(f"Error loading schema: {e}", file=sys.stderr)
            return 2
        record = save_freeze(schema, args.name, args.dir)
        print(f"Frozen '{record.name}' with {len(record.fields)} fields -> {record.path}")
        return 0

    if args.freeze_cmd == "check":
        try:
            old_schema = load_schema(args.old)
            new_schema = load_schema(args.new)
        except Exception as e:
            print(f"Error loading schema: {e}", file=sys.stderr)
            return 2

        record = load_freeze(args.name, args.dir)
        if record is None:
            print(f"No freeze record '{args.name}' found in {args.dir}", file=sys.stderr)
            return 2

        diff = compute_diff(old_schema, new_schema)
        result = check_freeze(record, diff)

        if args.as_json:
            import json
            print(json.dumps(result.to_dict(), indent=2))
        else:
            if result.ok():
                print(f"OK: no violations against freeze '{args.name}'")
            else:
                for v in result.violations:
                    print(str(v))

        return 0 if result.ok() else 1

    return 2
