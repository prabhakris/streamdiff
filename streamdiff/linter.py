"""Lint schema fields for naming and style issues."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from streamdiff.schema import StreamSchema


@dataclass
class LintIssue:
    field_name: str
    message: str
    severity: str = "warning"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.field_name}: {self.message}"


_SNAKE_CASE = re.compile(r'^[a-z][a-z0-9_]*$')
_MAX_NAME_LEN = 64


def _check_naming_convention(field_name: str) -> List[LintIssue]:
    issues: List[LintIssue] = []
    if not _SNAKE_CASE.match(field_name):
        issues.append(LintIssue(
            field_name=field_name,
            message="Field name should be snake_case (lowercase letters, digits, underscores)",
        ))
    return issues


def _check_name_length(field_name: str) -> List[LintIssue]:
    issues: List[LintIssue] = []
    if len(field_name) > _MAX_NAME_LEN:
        issues.append(LintIssue(
            field_name=field_name,
            message=f"Field name exceeds maximum length of {_MAX_NAME_LEN} characters",
        ))
    if len(field_name) == 0:
        issues.append(LintIssue(
            field_name=field_name,
            message="Field name must not be empty",
            severity="error",
        ))
    return issues


def _check_reserved_words(field_name: str) -> List[LintIssue]:
    reserved = {"type", "schema", "id", "timestamp", "metadata"}
    issues: List[LintIssue] = []
    if field_name in reserved:
        issues.append(LintIssue(
            field_name=field_name,
            message=f"'{field_name}' is a reserved word and may conflict with stream metadata",
            severity="warning",
        ))
    return issues


def lint_schema(schema: StreamSchema) -> List[LintIssue]:
    """Run all lint checks against every field in the schema."""
    issues: List[LintIssue] = []
    for field_name in schema.field_map:
        issues.extend(_check_naming_convention(field_name))
        issues.extend(_check_name_length(field_name))
        issues.extend(_check_reserved_words(field_name))
    return issues


def has_errors(issues: List[LintIssue]) -> bool:
    return any(i.severity == "error" for i in issues)
