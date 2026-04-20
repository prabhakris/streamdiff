"""CLI subcommand: graph — visualise field relationships in a schema."""
import argparse
import json
import sys
from streamdiff.loader import load_schema
from streamdiff.grapher import build_graph, isolated_fields


def add_graph_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("graph", help="Show field relationship graph for a schema")
    p.add_argument("schema", help="Path to schema JSON file")
    p.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")
    p.add_argument(
        "--isolated",
        action="store_true",
        help="Only show fields with no inferred neighbors",
    )


def handle_graph(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    graph = build_graph(schema)

    if args.isolated:
        names = isolated_fields(graph)
        if args.as_json:
            print(json.dumps({"isolated": names}, indent=2))
        else:
            if not names:
                print("No isolated fields.")
            else:
                for n in names:
                    print(f"  {n}")
        return 0

    if args.as_json:
        print(json.dumps(graph.to_dict(), indent=2))
    else:
        if not graph.nodes:
            print("No fields in schema.")
        else:
            for name, node in sorted(graph.nodes.items()):
                print(str(node))
    return 0
