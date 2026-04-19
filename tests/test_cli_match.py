import json
import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.cli_match import handle_match, add_match_subparser
import argparse


def _field(name, ftype=FieldType.STRING):
    return SchemaField(name=name, type=ftype, required=True)


def _schema(*fields):
    return StreamSchema(name="s", fields=list(fields))


def _args(**kwargs):
    defaults = {"old": "old.json", "new": "new.json", "as_json": False, "only_partial": False}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_add_match_subparser_registers():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    add_match_subparser(subs)
    args = parser.parse_args(["match", "a.json", "b.json"])
    assert args.old == "a.json"
    assert args.new == "b.json"
    assert args.as_json is False
    assert args.only_partial is False


def test_handle_match_load_error_returns_two():
    with patch("streamdiff.cli_match.load_schema", side_effect=FileNotFoundError("missing")):
        result = handle_match(_args())
    assert result == 2


def test_handle_match_exact_returns_zero(capsys):
    old = _schema(_field("id"))
    new = _schema(_field("id"))
    with patch("streamdiff.cli_match.load_schema", side_effect=[old, new]):
        result = handle_match(_args())
    assert result == 0


def test_handle_match_unmatched_returns_one(capsys):
    old = _schema(_field("a"))
    new = _schema(_field("b"))
    with patch("streamdiff.cli_match.load_schema", side_effect=[old, new]):
        result = handle_match(_args())
    assert result == 1
    captured = capsys.readouterr()
    assert "Removed" in captured.out
    assert "Added" in captured.out


def test_handle_match_json_output(capsys):
    old = _schema(_field("x"))
    new = _schema(_field("x"), _field("y"))
    with patch("streamdiff.cli_match.load_schema", side_effect=[old, new]):
        result = handle_match(_args(as_json=True))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "matches" in data
    assert "unmatched_new" in data
    assert data["unmatched_new"] == ["y"]


def test_handle_match_only_partial_filters(capsys):
    old = _schema(_field("id"), _field("count", FieldType.INT))
    new = _schema(_field("id"), _field("count", FieldType.STRING))
    with patch("streamdiff.cli_match.load_schema", side_effect=[old, new]):
        result = handle_match(_args(only_partial=True))
    captured = capsys.readouterr()
    assert "count" in captured.out
    assert "id" not in captured.out
