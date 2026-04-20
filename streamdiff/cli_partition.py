"""CLI subcommand: partition — split schema fields into logical buckets."""

import argparse
import json
import sys
from typing import List

from streamdiff.loader import load_schema
from streamdiff.partitioner import partition


def add_partition_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "partition",
        help="Partition schema fields into logical buckets.",
    )
    p.add_argument("schema", help="Path to schema JSON file.")
    p.add_argument(
        "--strategy",
        choices=["required", "type", "prefix"],
        default="required",
        help="Partitioning strategy (default: required).",
    )
    p.add_argument(
        "--separator",
        default="_",
        help="Field name separator used by the prefix strategy (default: '_').",
    )
    p.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output result as JSON.",
    )
    p.set_defaults(func=handle_partition)


def handle_partition(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading schema: {exc}", file=sys.stderr)
        return 2

    kwargs = {}
    if args.strategy == "prefix":
        kwargs["separator"] = args.separator

    result = partition(schema, strategy=args.strategy, **kwargs)
    if result is None:
        print(f"Unknown strategy: {args.strategy}", file=sys.stderr)
        return 2

    if args.output_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))

    return 0
