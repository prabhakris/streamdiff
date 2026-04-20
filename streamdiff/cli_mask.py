"""CLI subcommand: mask — redact sensitive field names in a schema."""
import argparse
import json
import sys
from streamdiff.loader import load_schema
from streamdiff.masker import mask_schema


def add_mask_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "mask",
        help="Redact sensitive field names in a schema file.",
    )
    p.add_argument("schema", help="Path to the schema JSON file.")
    p.add_argument(
        "--placeholder",
        default="***",
        help="Placeholder prefix used for masked field names (default: ***).",
    )
    p.add_argument(
        "--extra-patterns",
        nargs="*",
        dest="extra_patterns",
        metavar="PATTERN",
        help="Additional substrings to treat as sensitive.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output result as JSON.",
    )
    p.set_defaults(func=handle_mask)


def handle_mask(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not load schema: {exc}", file=sys.stderr)
        return 2

    result = mask_schema(
        schema,
        placeholder=args.placeholder,
        extra_patterns=args.extra_patterns or [],
    )

    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))
        if result:
            print(f"\n{len(result.masked)} field(s) masked out of {result.original_count}.")
        else:
            print(f"All {result.original_count} field(s) retained.")

    return 0
