"""CLI helpers for severity filtering."""
import argparse
from streamdiff.severity import Severity, annotate_changes, filter_by_severity
from streamdiff.diff import DiffResult


def add_severity_args(parser: argparse.ArgumentParser) -> None:
    """Add --min-severity argument to a parser."""
    parser.add_argument(
        "--min-severity",
        choices=[s.value for s in Severity],
        default=None,
        help="Only show changes at or above this severity level (info, warning, error).",
    )


def apply_severity_filter(result: DiffResult, args: argparse.Namespace) -> DiffResult:
    """Filter DiffResult changes by min severity if specified."""
    min_sev = getattr(args, "min_severity", None)
    if not min_sev:
        return result
    severity = Severity(min_sev)
    annotated = annotate_changes(result.changes)
    filtered_pairs = filter_by_severity(annotated, severity)
    filtered_changes = [c for c, _ in filtered_pairs]
    return DiffResult(changes=filtered_changes)
