"""CLI integration for the schema watchdog."""

import argparse
import sys

from streamdiff.reporter import print_diff, print_diff_json
from streamdiff.watchdog import WatchConfig, WatchEvent, watch


def add_watch_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("watch", help="Poll a schema file and report changes")
    p.add_argument("schema", help="Path to schema file to watch")
    p.add_argument(
        "--interval",
        type=float,
        default=5.0,
        metavar="SECONDS",
        help="Polling interval in seconds (default: 5)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="watch_format",
    )
    p.add_argument(
        "--break-on-breaking",
        action="store_true",
        default=False,
        help="Exit with code 1 on first breaking change",
    )


def handle_watch(args: argparse.Namespace) -> int:
    """Run the watch loop; returns exit code."""
    exit_on_breaking = getattr(args, "break_on_breaking", False)
    fmt = getattr(args, "watch_format", "text")

    def on_change(event: WatchEvent) -> None:
        print(f"[iteration {event.iteration}] Schema changed:", file=sys.stderr)
        if fmt == "json":
            print_diff_json(event.result)
        else:
            print_diff(event.result)

    def on_breaking(event: WatchEvent) -> None:
        if exit_on_breaking:
            sys.exit(1)

    cfg = WatchConfig(
        schema_path=args.schema,
        interval=args.interval,
        on_change=on_change,
        on_breaking=on_breaking,
    )

    try:
        watch(cfg)
    except KeyboardInterrupt:
        pass

    return 0
