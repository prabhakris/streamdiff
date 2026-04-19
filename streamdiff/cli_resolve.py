"""CLI subcommand: resolve — merge and validate fields across multiple schemas."""
import argparse
import json
from typing import List

from streamdiff.loader import load_schema
from streamdiff.resolver import resolve_schemas


def add_resolve_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "resolve",
        help="Resolve and merge fields from multiple schema files",
    )
    p.add_argument(
        "schemas",
        nargs="+",
        metavar="NAME:FILE",
        help="Named schema files in NAME:FILE format",
    )
    p.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        default=False,
        help="Output result as JSON",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 if any conflicts are found",
    )


def _parse_named_schemas(specs: List[str]) -> dict:
    schemas = {}
    for spec in specs:
        if ":" not in spec:
            raise ValueError(f"Invalid schema spec '{spec}': expected NAME:FILE")
        name, path = spec.split(":", 1)
        schemas[name] = load_schema(path)
    return schemas


def handle_resolve(args) -> int:
    try:
        schemas = _parse_named_schemas(args.schemas)
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}")
        return 2

    result = resolve_schemas(schemas)

    if args.output_json:
        out = {
            "resolved": [r.to_dict() for r in result.resolved],
            "conflicts": result.conflicts,
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"Resolved {len(result.resolved)} field(s) from {len(schemas)} schema(s).")
        for r in result.resolved:
            print(f"  {r}")
        if result.conflicts:
            print(f"\n{len(result.conflicts)} conflict(s) found:")
            for c in result.conflicts:
                print(f"  ! {c}")

    if args.strict and not result.ok:
        return 1
    return 0
