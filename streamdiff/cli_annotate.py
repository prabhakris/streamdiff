"""CLI integration for annotation output."""

import argparse
from typing import List

from streamdiff.annotator import annotate_all, AnnotatedChange
from streamdiff.diff import SchemaChange


def add_annotate_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--annotate",
        action="store_true",
        default=False,
        help="Include descriptions and hints for each change.",
    )


def apply_annotation(
    args: argparse.Namespace,
    changes: List[SchemaChange],
) -> List[AnnotatedChange] | None:
    """Return annotated changes if --annotate flag is set, else None."""
    if getattr(args, "annotate", False):
        return annotate_all(changes)
    return None


def format_annotations(annotated: List[AnnotatedChange]) -> str:
    if not annotated:
        return "No changes to annotate."
    lines = []
    for a in annotated:
        lines.append(f"  [{a.change.change_type.value}] {a.description}")
        lines.append(f"    Hint: {a.hint}")
    return "\n".join(lines)
