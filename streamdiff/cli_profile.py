"""CLI integration for schema profiler."""
import argparse
import json
from streamdiff.loader import load_schema
from streamdiff.profiler import profile_schema


def add_profile_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("profile", help="Display field-level statistics for a schema")
    p.add_argument("schema", help="Path to schema JSON file")
    p.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        default=False,
        help="Output as JSON",
    )
    p.add_argument(
        "--min-depth",
        type=int,
        default=0,
        help="Only show fields at or beyond this nesting depth",
    )


def handle_profile(args: argparse.Namespace) -> int:
    schema = load_schema(args.schema)
    result = profile_schema(schema)

    if args.min_depth > 0:
        result.stats = [s for s in result.stats if s.depth >= args.min_depth]

    if args.output_json:
        print(json.dumps(result.to_dict(), indent=2))
        return 0

    print(f"Schema : {result.schema_name}")
    print(f"Fields : {result.total_fields}")
    print(f"Required / Optional: {result.required_count} / {result.optional_count}")
    print(f"Max depth : {result.max_depth}")
    print("Type breakdown:")
    for t, count in sorted(result.type_counts.items()):
        print(f"  {t}: {count}")
    if result.stats:
        print("Fields:")
        for s in result.stats:
            req = "required" if s.required else "optional"
            print(f"  {s.name} ({s.field_type.value}, {req}, depth={s.depth})")
    return 0
