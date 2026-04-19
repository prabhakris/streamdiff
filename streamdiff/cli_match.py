"""CLI subcommand: match fields between two schema versions."""
import argparse
import json
from streamdiff.loader import load_schema
from streamdiff.matcher import match_schemas


def add_match_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("match", help="Match fields between two schema files")
    p.add_argument("old", help="Path to old schema file")
    p.add_argument("new", help="Path to new schema file")
    p.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")
    p.add_argument(
        "--only-partial",
        action="store_true",
        help="Show only partial (non-exact) matches",
    )


def handle_match(args: argparse.Namespace) -> int:
    try:
        old_schema = load_schema(args.old)
        new_schema = load_schema(args.new)
    except Exception as exc:
        print(f"error: {exc}")
        return 2

    report = match_schemas(old_schema, new_schema)
    matches = report.matches
    if args.only_partial:
        matches = [m for m in matches if not m.exact]

    if args.as_json:
        out = {
            "matches": [m.to_dict() for m in matches],
            "unmatched_old": [f.name for f in report.unmatched_old],
            "unmatched_new": [f.name for f in report.unmatched_new],
        }
        print(json.dumps(out, indent=2))
    else:
        if matches:
            print("Matches:")
            for m in matches:
                print(f"  {m}")
        if report.unmatched_old:
            print("Removed (unmatched):")
            for f in report.unmatched_old:
                print(f"  - {f.name}")
        if report.unmatched_new:
            print("Added (unmatched):")
            for f in report.unmatched_new:
                print(f"  + {f.name}")
        if not matches and not report.unmatched_old and not report.unmatched_new:
            print("No fields to match.")

    return 0 if bool(report) else 1
