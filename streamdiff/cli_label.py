"""CLI integration for the labeler feature."""
import argparse
import json
from streamdiff.labeler import build_label_report
from streamdiff.diff import DiffResult


def add_label_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--label",
        action="store_true",
        default=False,
        help="Attach labels to each detected change.",
    )
    parser.add_argument(
        "--label-json",
        action="store_true",
        default=False,
        help="Output labels as JSON.",
    )
    parser.add_argument(
        "--extra-labels",
        nargs="*",
        default=None,
        metavar="LABEL",
        help="Additional labels to attach to every change.",
    )


def apply_labeling(args: argparse.Namespace, result: DiffResult) -> None:
    if not getattr(args, "label", False) and not getattr(args, "label_json", False):
        return

    extra = getattr(args, "extra_labels", None)
    report = build_label_report(result.changes, extra=extra)

    if getattr(args, "label_json", False):
        print(json.dumps(report.to_dict(), indent=2))
        return

    if not report:
        print("No changes to label.")
        return

    for lc in report.labeled:
        print(str(lc))
