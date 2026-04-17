import argparse
import pytest
from streamdiff.diff import SchemaChange, ChangeType, DiffResult
from streamdiff.schema import SchemaField, FieldType
from streamdiff.cli_severity import add_severity_args, apply_severity_filter


def _field(name="x", required=False):
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(ct, required=False):
    return SchemaChange(change_type=ct, field_name="x", field=_field(required=required))


def _parse(args):
    parser = argparse.ArgumentParser()
    add_severity_args(parser)
    return parser.parse_args(args)


def _result(*changes):
    return DiffResult(changes=list(changes))


def test_add_severity_args_accepts_info():
    ns = _parse(["--min-severity", "info"])
    assert ns.min_severity == "info"


def test_add_severity_args_default_none():
    ns = _parse([])
    assert ns.min_severity is None


def test_no_filter_returns_all():
    ns = _parse([])
    result = _result(_change(ChangeType.ADDED), _change(ChangeType.REMOVED))
    filtered = apply_severity_filter(result, ns)
    assert len(filtered.changes) == 2


def test_error_filter_removes_info_and_warning():
    ns = _parse(["--min-severity", "error"])
    result = _result(
        _change(ChangeType.ADDED, required=False),   # info
        _change(ChangeType.REQUIRED_CHANGED, required=False),  # warning
        _change(ChangeType.REMOVED),  # error
    )
    filtered = apply_severity_filter(result, ns)
    assert len(filtered.changes) == 1
    assert filtered.changes[0].change_type == ChangeType.REMOVED


def test_warning_filter_keeps_warning_and_error():
    ns = _parse(["--min-severity", "warning"])
    result = _result(
        _change(ChangeType.ADDED, required=False),
        _change(ChangeType.REQUIRED_CHANGED, required=False),
        _change(ChangeType.REMOVED),
    )
    filtered = apply_severity_filter(result, ns)
    assert len(filtered.changes) == 2
