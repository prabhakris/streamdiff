import pytest
from streamdiff.schema import SchemaField, FieldType
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.deprecator import (
    DeprecationNotice,
    DeprecationReport,
    detect_deprecated_fields,
    format_deprecation_text,
    _looks_deprecated,
)


def _field(name: str, required: bool = False) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(name: str, change_type: ChangeType) -> SchemaChange:
    return SchemaChange(field_name=name, change_type=change_type, field=_field(name))


def _result(*changes: SchemaChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def test_looks_deprecated_prefix():
    assert _looks_deprecated("deprecated_user_id")
    assert _looks_deprecated("legacy_status")
    assert _looks_deprecated("old_name")


def test_looks_deprecated_suffix():
    assert _looks_deprecated("status_deprecated")
    assert _looks_deprecated("event_v1")
    assert _looks_deprecated("field_old")


def test_looks_deprecated_normal_name():
    assert not _looks_deprecated("user_id")
    assert not _looks_deprecated("event_type")
    assert not _looks_deprecated("timestamp")


def test_no_changes_returns_empty_report():
    report = detect_deprecated_fields(_result())
    assert not report
    assert report.notices == []


def test_added_deprecated_field_detected():
    report = detect_deprecated_fields(_result(_change("deprecated_email", ChangeType.ADDED)))
    assert report
    assert len(report.notices) == 1
    assert report.notices[0].field_name == "deprecated_email"


def test_removed_legacy_field_detected():
    report = detect_deprecated_fields(_result(_change("legacy_token", ChangeType.REMOVED)))
    assert len(report.notices) == 1


def test_since_is_set():
    report = detect_deprecated_fields(
        _result(_change("old_format", ChangeType.ADDED)), since="v2.3"
    )
    assert report.notices[0].since == "v2.3"


def test_normal_field_not_flagged():
    report = detect_deprecated_fields(_result(_change("user_id", ChangeType.ADDED)))
    assert not report


def test_to_dict():
    report = detect_deprecated_fields(_result(_change("legacy_id", ChangeType.REMOVED)), since="v1")
    d = report.to_dict()
    assert "deprecated" in d
    assert d["deprecated"][0]["field"] == "legacy_id"
    assert d["deprecated"][0]["since"] == "v1"


def test_format_no_deprecations():
    report = DeprecationReport(notices=[])
    assert format_deprecation_text(report) == "No deprecated fields detected."


def test_format_with_notices():
    report = DeprecationReport(notices=[
        DeprecationNotice(field_name="old_id", reason="naming convention", since="v3")
    ])
    text = format_deprecation_text(report)
    assert "old_id" in text
    assert "v3" in text
