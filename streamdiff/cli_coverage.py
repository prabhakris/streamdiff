"""CLI subcommand: coverage — score how completely a schema is defined."""
import argparse
import json
import sys

from streamdiff.loader import load_schema
from streamdiff.scorer4 import score_coverage


def add_coverage_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "coverage",
        help="Score how completely a schema is defined",
    )
    p.add_argument("schema", help="Path to schema YAML/JSON file")
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        default=False,
        help="Output as JSON",
    )
    p.add_argument(
        "--min-percent",
        type=float,
        default=0.0,
        metavar="PCT",
        help="Exit non-zero if coverage percent is below this threshold",
    )
    p.set_defaults(func=handle_coverage)


def handle_coverage(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = score_coverage(schema)

    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(str(report))
        for cf in report.fields:
            flag = "*" if cf.has_complex_type else " "
            req = "required" if cf.required else "optional"
            print(f"  {flag} {cf.name} [{req}]  score={cf.score}")

    if report.percent < args.min_percent:
        print(
            f"coverage {report.percent}% is below threshold {args.min_percent}%",
            file=sys.stderr,
        )
        return 1

    return 0
