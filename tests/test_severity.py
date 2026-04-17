import pytest
from streamdiff.diff import SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.severity import (
    Severity,
    get_severity,
    annotate_changes,
    filter_by_severity,
)


def _field(name="f", required=False, ftype=FieldType.STRING):
    return SchemaField(name=name, field_type=ftype, required=required)


def _change(change_type, required=False):
    return SchemaChange(change_type=change_type, field_name="f", field=_field(required=required))


def test_removed_is_error():
    assert get_severity(_change(ChangeType.REMOVED)) == Severity.ERROR


def test_type_changed_is_error():
    assert get_severity(_change(ChangeType.TYPE_CHANGED)) == Severity.ERROR


def test_added_required_is_error():
    assert get_severity(_change(ChangeType.ADDED, required=True)) == Severity.ERROR


def test_added_optional_is_info():
    assert get_severity(_change(ChangeType.ADDED, required=False)) == Severity.INFO


def test_required_changed_to_required_is_error():
    assert get_severity(_change(ChangeType.REQUIRED_CHANGED, required=True)) == Severity.ERROR


def test_required_changed_to_optional_is_warning():
    assert get_severity(_change(ChangeType.REQUIRED_CHANGED, required=False)) == Severity.WARNING


def test_annotate_changes_length():
    changes = [_change(ChangeType.ADDED), _change(ChangeType.REMOVED)]
    result = annotate_changes(changes)
    assert len(result) == 2
    assert result[1][1] == Severity.ERROR


def test_filter_by_severity_warning_excludes_info():
    changes = [
        _change(ChangeType.ADDED, required=False),   # INFO
        _change(ChangeType.REQUIRED_CHANGED, required=False),  # WARNING
        _change(ChangeType.REMOVED),  # ERROR
    ]
    annotated = annotate_changes(changes)
    result = filter_by_severity(annotated, Severity.WARNING)
    severities = [s for _, s in result]
    assert Severity.INFO not in severities
    assert Severity.WARNING in severities
    assert Severity.ERROR in severities


def test_filter_by_severity_error_only():
    changes = [
        _change(ChangeType.ADDED, required=False),
        _change(ChangeType.REMOVED),
    ]
    annotated = annotate_changes(changes)
    result = filter_by_severity(annotated, Severity.ERROR)
    assert len(result) == 1
    assert result[0][1] == Severity.ERROR
