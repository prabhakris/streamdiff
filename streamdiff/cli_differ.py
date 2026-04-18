"""CLI integration for the high-level differ."""
import argparse
from streamdiff.differ import DifferConfig, run_diff
from streamdiff.severity import Severity
from streamdiff.loader import load_schema
from streamdiff.reporter import print_diff, print_diff_json, exit_code


def add_differ_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("old", help="Path to old schema file")
    parser.add_argument("new", help="Path to new schema file")
    parser.add_argument("--score", action="store_true", default=False,
                        help="Include risk score in output")
    parser.add_argument("--min-severity", choices=[s.value for s in Severity],
                        default=None, help="Filter changes below this severity")
    parser.add_argument("--include", nargs="*", metavar="FIELD",
                        help="Only include these fields")
    parser.add_argument("--exclude", nargs="*", metavar="FIELD",
                        help="Exclude these fields")
    parser.add_argument("--json", action="store_true", default=False,
                        help="Output as JSON")


def handle_differ(args: argparse.Namespace) -> int:
    old = load_schema(args.old)
    new = load_schema(args.new)

    min_sev = Severity(args.min_severity) if args.min_severity else None

    config = DifferConfig(
        min_severity=min_sev,
        include_fields=args.include,
        exclude_fields=args.exclude,
        score=args.score,
    )

    result = run_diff(old, new, config)

    if args.json:
        print_diff_json(result.diff)
    else:
        print_diff(result.diff)
        if result.risk_score is not None:
            print(f"Risk score: {result.risk_score}")

    return exit_code(result.diff)
