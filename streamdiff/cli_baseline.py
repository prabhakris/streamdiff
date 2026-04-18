"""CLI helpers for baseline comparison."""
from __future__ import annotations

import argparse

from streamdiff.baseline import compare_to_baseline, latest_snapshot
from streamdiff.loader import load_schema
from streamdiff.reporter import print_diff, print_diff_json, exit_code


def add_baseline_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "baseline",
        help="Compare a schema file against a saved snapshot baseline.",
    )
    p.add_argument("schema", help="Path to the current schema file (JSON).")
    p.add_argument(
        "--name",
        default=None,
        help="Snapshot name to use as baseline (default: latest for stream).",
    )
    p.add_argument(
        "--snapshot-dir",
        default=".streamdiff",
        dest="snapshot_dir",
        help="Directory where snapshots are stored.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output diff as JSON.",
    )
    p.set_defaults(func=handle_baseline)


def handle_baseline(args: argparse.Namespace) -> int:
    current = load_schema(args.schema)
    name = args.name or latest_snapshot(current.name, args.snapshot_dir)
    if name is None:
        print(f"No baseline snapshot found for stream '{current.name}'.")
        return 1

    result = compare_to_baseline(current, name, args.snapshot_dir)
    if not result.found:
        print(f"Snapshot '{name}' not found; treating baseline as empty schema.")

    if args.json:
        print_diff_json(result.diff)
    else:
        print(f"Baseline: {result.baseline_path}")
        print_diff(result.diff)

    return exit_code(result.diff)
