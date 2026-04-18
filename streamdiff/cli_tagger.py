"""CLI integration for tagging schema changes."""
import argparse
from typing import List, Optional
from streamdiff.tagger import tag_all, filter_by_tag, tags_summary, TaggedChange
from streamdiff.diff import SchemaChange


def add_tagger_args(parser: argparse.ArgumentParser) -> None:
    """Add tagging-related arguments to a parser."""
    parser.add_argument(
        "--tag-filter",
        metavar="TAG",
        default=None,
        help="Only show changes with this tag (e.g. destructive, additive, pii)",
    )
    parser.add_argument(
        "--tag-field",
        nargs=2,
        action="append",
        metavar=("FIELD", "TAG"),
        default=[],
        help="Assign a custom tag to a field: --tag-field email pii",
    )
    parser.add_argument(
        "--show-tag-summary",
        action="store_true",
        default=False,
        help="Print a summary of tag counts after diffing",
    )


def _build_extra_tags(tag_field_args: List) -> dict:
    extra: dict = {}
    for field_name, tag in (tag_field_args or []):
        extra.setdefault(field_name, []).append(tag)
    return extra


def apply_tagging(
    changes: List[SchemaChange],
    args: argparse.Namespace,
) -> List[TaggedChange]:
    """Tag changes and optionally filter by tag."""
    extra_tags = _build_extra_tags(getattr(args, "tag_field", []))
    tagged = tag_all(changes, extra_tags=extra_tags or None)
    tag_filter = getattr(args, "tag_filter", None)
    if tag_filter:
        tagged = filter_by_tag(tagged, tag_filter)
    return tagged


def format_tag_summary(tagged: List[TaggedChange]) -> str:
    summary = tags_summary(tagged)
    if not summary:
        return "Tags: none"
    parts = ", ".join(f"{tag}={count}" for tag, count in sorted(summary.items()))
    return f"Tags: {parts}"
