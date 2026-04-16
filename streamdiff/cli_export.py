"""CLI helpers for the --export flag added to streamdiff."""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from streamdiff.diff import DiffResult
from streamdiff.exporter import write_export

SUPPORTED_FORMATS = ("json", "csv")


def add_export_args(parser: argparse.ArgumentParser) -> None:
    """Attach export-related arguments to *parser*."""
    parser.add_argument(
        "--export-format",
        choices=SUPPORTED_FORMATS,
        default=None,
        metavar="FMT",
        help="Export diff result to a file. Choices: %(choices)s.",
    )
    parser.add_argument(
        "--export-path",
        default=None,
        metavar="PATH",
        help="Destination file path for the exported diff (requires --export-format).",
    )


def handle_export(
    result: DiffResult,
    fmt: Optional[str],
    path: Optional[str],
) -> None:
    """Write *result* to *path* when both *fmt* and *path* are provided.

    Prints a confirmation message to stdout and exits with code 2 on error.
    """
    if fmt is None and path is None:
        return
    if fmt is None or path is None:
        print(
            "error: --export-format and --export-path must be used together.",
            file=sys.stderr,
        )
        sys.exit(2)
    try:
        write_export(result, fmt, path)
        print(f"Diff exported as {fmt.upper()} to {path}")
    except OSError as exc:
        print(f"error: could not write export file: {exc}", file=sys.stderr)
        sys.exit(2)
