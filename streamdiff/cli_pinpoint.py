"""CLI integration for pinpoint feature."""
import argparse
import json
from streamdiff.loader import load_schema
from streamdiff.diff import compute_diff
from streamdiff.pinpointer import pinpoint_changes


def add_pinpoint_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "pinpoint",
        help="Show detailed reasons for each schema change",
    )
    p.add_argument("old_schema", help="Path to old schema file")
    p.add_argument("new_schema", help="Path to new schema file")
    p.add_argument("--json", dest="as_json", action="store_true", default=False,
                   help="Output as JSON")
    p.set_defaults(func=handle_pinpoint)


def handle_pinpoint(args: argparse.Namespace) -> int:
    try:
        old = load_schema(args.old_schema)
        new = load_schema(args.new_schema)
    except Exception as e:
        print(f"Error loading schemas: {e}")
        return 2

    result = compute_diff(old, new)
    report = pinpoint_changes(result)

    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        if not report:
            print("No changes detected.")
        else:
            for p in report.pinpoints:
                print(str(p))

    return 0
