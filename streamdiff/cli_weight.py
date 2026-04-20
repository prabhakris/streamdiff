"""CLI subcommand: weight — show field importance weights for a schema."""
import argparse
import json
import sys
from streamdiff.loader import load_schema
from streamdiff.weighter import weight_schema


def add_weight_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("weight", help="Show field importance weights for a schema")
    p.add_argument("schema", help="Path to schema JSON file")
    p.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")
    p.add_argument(
        "--min-weight",
        dest="min_weight",
        type=float,
        default=None,
        metavar="W",
        help="Only show fields with weight >= W",
    )
    p.add_argument(
        "--top",
        dest="top",
        type=int,
        default=None,
        metavar="N",
        help="Show only the top N fields by weight",
    )
    p.set_defaults(func=handle_weight)


def handle_weight(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not load schema: {exc}", file=sys.stderr)
        return 2

    report = weight_schema(schema, min_weight=args.min_weight)
    weights = report.weights

    if args.top is not None:
        weights = weights[: args.top]

    if args.as_json:
        data = {
            "weights": [w.to_dict() for w in weights],
            "total": sum(w.weight for w in weights),
        }
        print(json.dumps(data, indent=2))
        return 0

    if not weights:
        print("No fields match the given criteria.")
        return 0

    print(f"{'Field':<30} {'Weight':>8}  Reasons")
    print("-" * 60)
    for w in weights:
        reasons = ", ".join(w.reasons)
        print(f"{w.field_name:<30} {w.weight:>8.2f}  {reasons}")
    print("-" * 60)
    print(f"{'Total':<30} {sum(w.weight for w in weights):>8.2f}")
    return 0
