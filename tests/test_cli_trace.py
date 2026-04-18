import json
import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.cli_trace import handle_trace, add_trace_subparser
import argparse


def _schema(*names):
    fields = [SchemaField(n, FieldType.STRING, True) for n in names]
    return StreamSchema(name="s", fields=fields)


def _args(schemas, field_name=None, as_json=False):
    return SimpleNamespace(schemas=schemas, field_name=field_name, as_json=as_json)


def test_add_trace_subparser_registers():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_trace_subparser(sub)
    ns = p.parse_args(["trace", "v1:a.json"])
    assert ns.schemas == ["v1:a.json"]


def test_handle_trace_bad_spec_returns_two():
    args = _args(["nocolon"])
    rc = handle_trace(args)
    assert rc == 2


def test_handle_trace_missing_file_returns_two():
    args = _args(["v1:/no/such/file.json"])
    rc = handle_trace(args)
    assert rc == 2


def test_handle_trace_text_output(capsys):
    schemas = {"v1:a": _schema("id", "name"), "v2:b": _schema("id")}

    def fake_load(path):
        return schemas[f"{path}"]

    with patch("streamdiff.cli_trace.load_schema", side_effect=lambda p: schemas.get(p, _schema())):
        with patch("streamdiff.cli_trace._parse_versions", return_value=[("v1", _schema("id", "name")), ("v2", _schema("id"))]):
            args = _args(["v1:a", "v2:b"])
            rc = handle_trace(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "id" in out


def test_handle_trace_json_output(capsys):
    with patch("streamdiff.cli_trace._parse_versions", return_value=[("v1", _schema("x")), ("v2", _schema("x", "y"))]):
        args = _args(["v1:a", "v2:b"], as_json=True)
        rc = handle_trace(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    names = [d["field"] for d in data]
    assert "x" in names
    assert "y" in names


def test_handle_trace_single_field(capsys):
    with patch("streamdiff.cli_trace._parse_versions", return_value=[("v1", _schema("a", "b"))]):
        args = _args(["v1:f"], field_name="a")
        rc = handle_trace(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "a" in out
