"""Tests for reporter output formatting."""
import io
import json

from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.reporter import print_diff, print_diff_json, exit_code, _colorize


def make_result(changes):
    return DiffResult(changes=changes)


def change(field, ctype, breaking=False, detail=None):
    return SchemaChange(field_name=field, change_type=ctype, breaking=breaking, detail=detail)


def test_no_changes_message():
    out = io.StringIO()
    print_diff(make_result([]), color=False, file=out)
    assert "No schema changes" in out.getvalue()


def test_added_field_shown():
    out = io.StringIO()
    result = make_result([change("age", ChangeType.ADDED)])
    print_diff(result, color=False, file=out)
    assert "age" in out.getvalue()
    assert "ADDED" in out.getvalue()


def test_breaking_marker_shown():
    out = io.StringIO()
    result = make_result([change("email", ChangeType.REMOVED, breaking=True)])
    print_diff(result, color=False, file=out)
    assert "BREAKING" in out.getvalue()


def test_json_output_structure():
    out = io.StringIO()
    result = make_result([change("id", ChangeType.MODIFIED, breaking=True, detail="type changed")])
    print_diff_json(result, file=out)
    data = json.loads(out.getvalue())
    assert data["breaking"] is True
    assert data["changes"][0]["field"] == "id"
    assert data["changes"][0]["detail"] == "type changed"


def test_exit_code_no_breaking():
    result = make_result([change("x", ChangeType.ADDED, breaking=False)])
    assert exit_code(result) == 0


def test_exit_code_breaking():
    result = make_result([change("x", ChangeType.REMOVED, breaking=True)])
    assert exit_code(result) == 1


def test_colorize_disabled():
    assert _colorize("hello", "red", enabled=False) == "hello"


def test_colorize_enabled():
    colored = _colorize("hello", "red", enabled=True)
    assert "hello" in colored
    assert colored != "hello"
