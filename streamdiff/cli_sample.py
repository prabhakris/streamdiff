"""CLI subcommand: sample fields from a schema."""
from __future__ import annotations
import argparse
import json
import sys
from streamdiff.loader import load_schema
from streamdiff.sampler import sample_by_count, sample_by_fraction


def add_sample_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("sample", help="Sample fields from a schema")
    p.add_argument("schema", help="Path to schema file")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--count", type=int, metavar="N",
        help="Number of fields to sample",
    )
    group.add_argument(
        "--fraction", type=float, metavar="F",
        help="Fraction of fields to sample (0.0-1.0)",
    )
    p.add_argument("--seed", type=int, default=None, help="Random seed")
    p.add_argument("--json", dest="as_json", action="store_true", help="Output JSON")
    p.set_defaults(func=handle_sample)


def handle_sample(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        if args.count is not None:
            result = sample_by_count(schema, args.count, seed=args.seed)
        else:
            result = sample_by_fraction(schema, args.fraction, seed=args.seed)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(str(result))
        for f in result.sampled:
            req = "required" if f.required else "optional"
            print(f"  {f.name} ({f.field_type.value}, {req})")

    return 0
