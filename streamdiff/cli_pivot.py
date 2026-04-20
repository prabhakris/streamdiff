"""CLI subcommand: pivot — display schema fields grouped by a dimension prefix."""
import argparse
import json
import sys
from streamdiff.loader import load_schema
from streamdiff.pivotter import pivot_schema


def add_pivot_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "pivot",
        help="Group schema fields by a prefix dimension.",
    )
    parser.add_argument("schema", help="Path to schema JSON file.")
    parser.add_argument(
        "--separator",
        default=".",
        help="Field name separator used to extract the dimension (default: '.').",
    )
    parser.add_argument(
        "--dimension-key",
        default="prefix",
        dest="dimension_key",
        help="Label for the grouping dimension in output (default: 'prefix').",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output result as JSON.",
    )
    parser.set_defaults(func=handle_pivot)


def handle_pivot(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not load schema: {exc}", file=sys.stderr)
        return 2

    result = pivot_schema(
        schema,
        separator=args.separator,
        dimension_key=args.dimension_key,
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result) if result else "No fields found.")

    return 0
