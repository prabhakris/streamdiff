"""CLI integration for policy enforcement."""
import argparse
import json
import sys
from streamdiff.diff import ChangeType
from streamdiff.severity import Severity
from streamdiff.policy import PolicyRule, PolicyResult, evaluate_policy


def add_policy_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--policy-name", default="default", help="Name of the policy")
    parser.add_argument(
        "--allow-breaking", action="store_true", default=False,
        help="Allow breaking changes under this policy"
    )
    parser.add_argument(
        "--block-types", nargs="*", default=[],
        metavar="CHANGE_TYPE",
        help="Change types to block (e.g. removed type_changed)",
    )
    parser.add_argument(
        "--policy-json", action="store_true", default=False,
        help="Output policy result as JSON"
    )


def _parse_blocked_types(raw: list) -> list:
    result = []
    for name in raw:
        try:
            result.append(ChangeType(name))
        except ValueError:
            pass
    return result


def build_policy_rule(args: argparse.Namespace) -> PolicyRule:
    return PolicyRule(
        name=args.policy_name,
        description=f"CLI policy: {args.policy_name}",
        allow_breaking=args.allow_breaking,
        blocked_change_types=_parse_blocked_types(args.block_types or []),
    )


def handle_policy_output(policy_result: PolicyResult, use_json: bool) -> int:
    if use_json:
        data = {
            "passed": policy_result.passed,
            "violations": [
                {"rule": v.rule.name, "field": v.change.field_name, "reason": v.reason}
                for v in policy_result.violations
            ],
        }
        print(json.dumps(data, indent=2))
    else:
        if policy_result.passed:
            print("Policy passed: no violations.")
        else:
            print(f"Policy FAILED: {len(policy_result.violations)} violation(s)")
            for v in policy_result.violations:
                print(f"  {v}")
    return 0 if policy_result.passed else 1
