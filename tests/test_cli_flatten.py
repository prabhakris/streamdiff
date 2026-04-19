import argparse
import json
import pytest
from unittest.mock import patch, MagicMock
from streamdiff.cli_flatten import add_flatten_subparser, handle_flatten
from streamdiff.schema import SchemaField, StreamSchema, FieldType
from streamdiff.flattener import FlatSchema, FlatField


def _schema(name, fields):
    s = StreamSchema(name=name)
    for f in fields:
        s.fields[f.name] = f
    return s


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


def _parse(args):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_flatten_subparser(sub)
    return parser.parse_args(["flatten"] + args)


def test_add_flatten_subparser_registers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_flatten_subparser(sub)
    args = parser.parse_args(["flatten", "schema.json"])
    assert args.schema == "schema.json"


def test_defaults():
    args = _parse(["schema.json"])
    assert args.separator == "."
    assert args.as_json is False
    assert args.compare is None


def test_handle_flatten_bad_file_returns_two():
    args = _parse(["nonexistent.json"])
    assert handle_flatten(args) == 2


def test_handle_flatten_text_output(capsys):
    s = _schema("s", [_field("user_id")])
    args = _parse(["schema.json"])
    with patch("streamdiff.cli_flatten.load_schema", return_value=s):
        rc = handle_flatten(args)
    assert rc == 0
    captured = capsys.readouterr()
    assert "user_id" in captured.out


def test_handle_flatten_json_output(capsys):
    s = _schema("s", [_field("event_time")])
    args = _parse(["schema.json", "--json"])
    with patch("streamdiff.cli_flatten.load_schema", return_value=s):
        rc = handle_flatten(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["name"] == "s"
    assert any(f["path"] == "event_time" for f in data["fields"])


def test_handle_flatten_compare(capsys):
    s1 = _schema("s", [_field("a")])
    s2 = _schema("s", [_field("a"), _field("b")])
    args = _parse(["s1.json", "--compare", "s2.json"])
    with patch("streamdiff.cli_flatten.load_schema", side_effect=[s1, s2]):
        rc = handle_flatten(args)
    assert rc == 0
    assert "b" in capsys.readouterr().out


def test_handle_flatten_compare_bad_second_file_returns_two():
    s1 = _schema("s", [_field("a")])
    args = _parse(["s1.json", "--compare", "missing.json"])
    with patch("streamdiff.cli_flatten.load_schema", side_effect=[s1, FileNotFoundError("no")]):
        rc = handle_flatten(args)
    assert rc == 2
