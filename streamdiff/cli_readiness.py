"""CLI subcommand: streamdiff readiness — score schema production-readiness."""
import argparse
import json
import sys
from streamdiff.loader import load_schema
from streamdiff.scorer3 import score_readiness


def add_readiness_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "readiness",
        help="Score schema fields for production readiness",
    )
    p.add_argument("schema", help="Path to schema JSON file")
    p.add_argument("--json", dest="as_json", action="store_true", default=False,
                   help="Output as JSON")
    p.add_argument("--min-score", type=float, default=0.0,
                   help="Exit 1 if overall score is below this threshold")
    p.set_defaults(func=handle_readiness)


def handle_readiness(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = score_readiness(schema)

    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(f"Overall readiness score: {report.overall:.1f}/10")
        for fr in report.fields:
            note_str = f"  [{', '.join(fr.notes)}]" if fr.notes else ""
            print(f"  {fr}{note_str}")

    if report.overall < args.min_score:
        return 1
    return 0
