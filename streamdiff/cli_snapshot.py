"""CLI sub-commands for snapshot management."""
from __future__ import annotations

import argparse
import sys

from streamdiff.loader import load_schema
from streamdiff.snapshot import (
    save_snapshot,
    load_snapshot,
    list_snapshots,
    delete_snapshot,
)
from streamdiff.diff import diff_schemas
from streamdiff.reporter import print_diff, exit_code


def add_snapshot_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    sp = subparsers.add_parser("snapshot", help="Manage schema snapshots")
    ssub = sp.add_subparsers(dest="snapshot_cmd", required=True)

    save_p = ssub.add_parser("save", help="Save current schema as a snapshot")
    save_p.add_argument("schema", help="Path to schema file")
    save_p.add_argument("name", help="Snapshot name")
    save_p.add_argument("--dir", default=".streamdiff_snapshots")

    cmp_p = ssub.add_parser("compare", help="Compare schema against a snapshot")
    cmp_p.add_argument("schema", help="Path to current schema file")
    cmp_p.add_argument("name", help="Snapshot name to compare against")
    cmp_p.add_argument("--dir", default=".streamdiff_snapshots")
    cmp_p.add_argument("--json", action="store_true")

    ls_p = ssub.add_parser("list", help="List available snapshots")
    ls_p.add_argument("--dir", default=".streamdiff_snapshots")

    rm_p = ssub.add_parser("delete", help="Delete a snapshot")
    rm_p.add_argument("name", help="Snapshot name")
    rm_p.add_argument("--dir", default=".streamdiff_snapshots")


def handle_snapshot(args: argparse.Namespace) -> int:
    cmd = args.snapshot_cmd

    if cmd == "save":
        schema = load_schema(args.schema)
        path = save_snapshot(schema, args.name, directory=args.dir)
        print(f"Snapshot '{args.name}' saved to {path}")
        return 0

    if cmd == "compare":
        current = load_schema(args.schema)
        baseline = load_snapshot(args.name, directory=args.dir)
        result = diff_schemas(baseline, current)
        print_diff(result, use_json=getattr(args, "json", False))
        return exit_code(result)

    if cmd == "list":
        names = list_snapshots(args.dir)
        if not names:
            print("No snapshots found.")
        else:
            for n in names:
                print(n)
        return 0

    if cmd == "delete":
        removed = delete_snapshot(args.name, directory=args.dir)
        if removed:
            print(f"Snapshot '{args.name}' deleted.")
        else:
            print(f"Snapshot '{args.name}' not found.", file=sys.stderr)
            return 1
        return 0

    return 1
