"""CLI integration for risk scoring."""
import argparse
from streamdiff.scorer import score_result, RiskScore
from streamdiff.diff import DiffResult


def add_score_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--score",
        action="store_true",
        default=False,
        help="Print a risk score (0-100) for the diff.",
    )
    parser.add_argument(
        "--score-threshold",
        type=int,
        default=None,
        metavar="N",
        help="Exit with code 2 if risk score exceeds N.",
    )


def apply_score(args: argparse.Namespace, result: DiffResult) -> RiskScore:
    return score_result(result)


def handle_score_output(args: argparse.Namespace, risk: RiskScore) -> None:
    if getattr(args, "score", False):
        print(str(risk))
        print(f"  breakdown: {risk.breakdown}")


def score_exit_code(args: argparse.Namespace, risk: RiskScore) -> int:
    threshold = getattr(args, "score_threshold", None)
    if threshold is not None and risk.score > threshold:
        return 2
    return 0
