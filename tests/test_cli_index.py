import argparse
import json
import pytest
from unittest.mock import patch, MagicMock
from streamdiff.cli_index import add_index_subparser, handle_index
from streamdiff.schema import StreamSchema, SchemaField, FieldType


def _schema(*fields):
    return StreamSchema(name="s", fields=list(fields))


def _field(name, ft=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ft, required=required)


def _parse(args):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    add_index_subparser(sub)
    return p.parse_args(["index"] + args)


def test_add_index_subparser_registers():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    add_index_subparser(sub)
    ns = p.parse_args(["index", "schema.json"])
    assert ns.schema == "schema.json"


def test_defaults():
    ns = _parse(["schema.json"])
    assert ns.search is None
    assert ns.field_type is None
    assert ns.required_only is False
    assert ns.as_json is False


def test_handle_index_bad_file_returns_two():
    ns = _parse(["nonexistent.json"])
    assert handle_index(ns) == 2


def test_handle_index_no_matches_prints_message(capsys):
    schema = _schema(_field("user_id"))
    ns = _parse(["s.json", "--search", "zzz"])
    with patch("streamdiff.cli_index.load_schema", return_value=schema):
        rc = handle_index(ns)
    assert rc == 0
    out = capsys.readouterr().out
    assert "No fields matched" in out


def test_handle_index_json_output(capsys):
    schema = _schema(_field("id", FieldType.STRING))
    ns = _parse(["s.json", "--json"])
    with patch("streamdiff.cli_index.load_schema", return_value=schema):
        rc = handle_index(ns)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert data[0]["name"] == "id"


def test_handle_index_unknown_type_returns_two():
    schema = _schema(_field("x"))
    ns = _parse(["s.json", "--type", "banana"])
    with patch("streamdiff.cli_index.load_schema", return_value=schema):
        rc = handle_index(ns)
    assert rc == 2


def test_handle_index_required_only(capsys):
    schema = _schema(_field("a", required=True), _field("b", required=False))
    ns = _parse(["s.json", "--required-only"])
    with patch("streamdiff.cli_index.load_schema", return_value=schema):
        handle_index(ns)
    out = capsys.readouterr().out
    assert "a" in out
    assert "b" not in out
