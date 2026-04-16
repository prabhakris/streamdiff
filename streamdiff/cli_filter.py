"""CLI helpers for applying filters to a DiffResult."""

import argparse
from typing import Optional
from streamdiff.diff import DiffResult, ChangeType
from streamdiff.filter import filter_changes, filter_by_field_names, exclude_field_names


def add_filter_args(parser: argparse.ArgumentParser) -> None:
    """Register filter-related CLI arguments on *parser*."""
    grp = parser.add_argument_group("filtering")
    grp.add_argument(
        "--field",
        metavar="NAME",
        help="Show only changes for this field name.",
    )
    grp.add_argument(
        "--change-type",
        choices=[ct.value for ct in ChangeType],
        metavar="TYPE",
        help="Show only changes of this type (added, removed, type_changed).",
    )
    grp.add_argument(
        "--breaking-only",
        action="store_true",
        default=False,
        help="Show only breaking changes.",
    )
    grp.add_argument(
        "--include-fields",
        metavar="NAMES",
        help="Comma-separated list of field names to include.",
    )
    grp.add_argument(
        "--exclude-fields",
        metavar="NAMES",
        help="Comma-separated list of field names to exclude.",
    )


def apply_filter_args(args: argparse.Namespace, result: DiffResult) -> DiffResult:
    """Apply filter arguments from parsed *args* to *result*."""
    change_type: Optional[ChangeType] = None
    if args.change_type:
        change_type = ChangeType(args.change_type)

    result = filter_changes(
        result,
        field_name=args.field or None,
        change_type=change_type,
        breaking_only=args.breaking_only,
    )

    if args.include_fields:
        names = [n.strip() for n in args.include_fields.split(",") if n.strip()]
        result = filter_by_field_names(result, names)

    if args.exclude_fields:
        names = [n.strip() for n in args.exclude_fields.split(",") if n.strip()]
        result = exclude_field_names(result, names)

    return result
