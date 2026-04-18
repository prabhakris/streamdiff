"""CLI subcommand for field lineage tracing across schema versions."""
import argparse
import json
from streamdiff.loader import load_schema
from streamdiff.tracer import trace_all, trace_field


def add_trace_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("trace", help="Trace field history across schema versions")
    p.add_argument(
        "schemas",
        nargs="+",
        metavar="LABEL:FILE",
        help="Ordered schema versions as label:path pairs",
    )
    p.add_argument("--field", dest="field_name", default=None, help="Trace a single field")
    p.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")


def _parse_versions(specs):
    versions = []
    for spec in specs:
        if ":" not in spec:
            raise ValueError(f"Expected LABEL:FILE, got: {spec!r}")
        label, path = spec.split(":", 1)
        versions.append((label, load_schema(path)))
    return versions


def handle_trace(args: argparse.Namespace) -> int:
    try:
        versions = _parse_versions(args.schemas)
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}")
        return 2

    if args.field_name:
        traces = {args.field_name: trace_field(args.field_name, versions)}
    else:
        traces = trace_all(versions)

    if args.as_json:
        print(json.dumps([t.to_dict() for t in traces.values()], indent=2))
    else:
        for t in traces.values():
            status = []
            for e in t.entries:
                mark = "+" if e.present else "-"
                status.append(f"{e.version}({mark})")
            added = t.added_in() or "?"
            removed = t.removed_in() or "present"
            print(f"{t.field_name:30s}  added={added}  removed={removed}  " + "  ".join(status))
    return 0
