"""CLI subcommand for changelog management."""
from __future__ import annotations

import argparse
from pathlib import Path

from streamdiff.changelog import load_changelog, append_changelog, build_entry
from streamdiff.loader import load_schema
from streamdiff.diff import compute_diff

_DEFAULT_PATH = ".streamdiff/changelog.json"


def add_changelog_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("changelog", help="Manage schema changelog")
    sub = p.add_subparsers(dest="changelog_cmd", required=True)

    rec = sub.add_parser("record", help="Record a diff into the changelog")
    rec.add_argument("old", help="Path to old schema file")
    rec.add_argument("new", help="Path to new schema file")
    rec.add_argument("--stream", default="unknown", help="Stream name label")
    rec.add_argument("--changelog", default=_DEFAULT_PATH, help="Changelog file path")

    show = sub.add_parser("show", help="Print changelog entries")
    show.add_argument("--changelog", default=_DEFAULT_PATH, help="Changelog file path")
    show.add_argument("--json", action="store_true", help="Output as JSON")
    show.add_argument("--breaking-only", action="store_true", help="Only show breaking entries")


def handle_changelog(args: argparse.Namespace) -> int:
    if args.changelog_cmd == "record":
        old = load_schema(args.old)
        new = load_schema(args.new)
        result = compute_diff(old, new)
        entry = build_entry(result, stream=args.stream)
        append_changelog(entry, Path(args.changelog))
        print(f"Recorded changelog entry for stream '{args.stream}'.")
        return 0

    if args.changelog_cmd == "show":
        entries = load_changelog(Path(args.changelog))
        if args.breaking_only:
            entries = [e for e in entries if e.breaking]
        if not entries:
            print("No changelog entries found.")
            return 0
        if args.json:
            import json
            print(json.dumps([e.to_dict() for e in entries], indent=2))
        else:
            for e in entries:
                print(e.to_text())
                print()
        return 0

    return 1
