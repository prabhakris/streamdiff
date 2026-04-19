"""CLI subcommand: audit — view and manage the audit log."""
from __future__ import annotations

import argparse
import json
import sys

from streamdiff.auditor import load_entries, clear_audit

_DEFAULT_DIR = ".streamdiff/audit"


def add_audit_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("audit", help="View or clear the audit log")
    p.add_argument("--audit-dir", default=_DEFAULT_DIR, metavar="DIR")
    p.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")
    p.add_argument("--clear", action="store_true", help="Clear the audit log")
    p.add_argument("--only-breaking", action="store_true", help="Show only breaking changes")
    p.add_argument("--limit", type=int, default=0, metavar="N", help="Show last N entries (0=all)")


def handle_audit(args: argparse.Namespace) -> int:
    if args.clear:
        clear_audit(audit_dir=args.audit_dir)
        print("Audit log cleared.")
        return 0

    entries = load_entries(audit_dir=args.audit_dir)

    if args.only_breaking:
        entries = [e for e in entries if e.breaking]

    if args.limit and args.limit > 0:
        entries = entries[-args.limit :]

    if not entries:
        print("No audit entries found.")
        return 0

    if args.as_json:
        print(json.dumps([e.to_dict() for e in entries], indent=2))
    else:
        for e in entries:
            print(str(e))

    return 0
