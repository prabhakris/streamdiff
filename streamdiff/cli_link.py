"""cli_link.py — CLI sub-command: link fields between two schema files."""
from __future__ import annotations

import argparse
import json
import sys

from streamdiff.loader import load_schema
from streamdiff.linker import link_schemas


def add_link_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "link",
        help="Link matching fields between two schema files.",
    )
    p.add_argument("left", help="Path to the left (old) schema file.")
    p.add_argument("right", help="Path to the right (new) schema file.")
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        default=False,
        help="Emit output as JSON.",
    )
    p.add_argument(
        "--exact-only",
        dest="exact_only",
        action="store_true",
        default=False,
        help="Only show exact (name + type) matches.",
    )
    p.set_defaults(func=handle_link)


def handle_link(args: argparse.Namespace) -> int:
    try:
        left = load_schema(args.left)
    except Exception as exc:  # noqa: BLE001
        print(f"error: cannot load left schema: {exc}", file=sys.stderr)
        return 2

    try:
        right = load_schema(args.right)
    except Exception as exc:  # noqa: BLE001
        print(f"error: cannot load right schema: {exc}", file=sys.stderr)
        return 2

    report = link_schemas(left, right)

    links = report.links
    if args.exact_only:
        links = [lk for lk in links if lk.exact]

    if args.as_json:
        out = {
            "links": [lk.to_dict() for lk in links],
            "unlinked_left": [f.name for f in report.unlinked_left],
            "unlinked_right": [f.name for f in report.unlinked_right],
        }
        print(json.dumps(out, indent=2))
    else:
        if links:
            print(f"Linked fields ({len(links)}):")
            for lk in links:
                print(f"  {lk}")
        else:
            print("No linked fields found.")

        if report.unlinked_left:
            print(f"\nOnly in left ({len(report.unlinked_left)}):")
            for f in report.unlinked_left:
                print(f"  {f.name}")

        if report.unlinked_right:
            print(f"\nOnly in right ({len(report.unlinked_right)}):")
            for f in report.unlinked_right:
                print(f"  {f.name}")

    return 0
