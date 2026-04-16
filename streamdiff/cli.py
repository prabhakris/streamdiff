"""CLI entry point for streamdiff."""
import argparse
import sys
from pathlib import Path

from streamdiff.loader import load_schema
from streamdiff.diff import diff_schemas, has_breaking_changes
from streamdiff.reporter import print_diff, exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="streamdiff",
        description="Diff and validate schema changes in Kafka and Kinesis streams.",
    )
    parser.add_argument("old_schema", type=Path, help="Path to the old schema file (JSON/YAML).")
    parser.add_argument("new_schema", type=Path, help="Path to the new schema file (JSON/YAML).")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero code on any change, not just breaking ones.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.old_schema.exists():
        print(f"Error: old schema file not found: {args.old_schema}", file=sys.stderr)
        return 2
    if not args.new_schema.exists():
        print(f"Error: new schema file not found: {args.new_schema}", file=sys.stderr)
        return 2

    old = load_schema(args.old_schema)
    new = load_schema(args.new_schema)
    result = diff_schemas(old, new)

    if args.format == "json":
        from streamdiff.reporter import print_diff_json
        print_diff_json(result)
    else:
        print_diff(result, color=not args.no_color)

    if args.strict:
        return 1 if result.changes else 0
    return exit_code(result)


if __name__ == "__main__":
    sys.exit(main())
