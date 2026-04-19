import json
import pytest
from unittest.mock import patch, MagicMock
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.cli_template import handle_template, add_template_subparser
import argparse


def _schema(*names):
    return StreamSchema(fields=[SchemaField(name=n, type=FieldType.STRING, required=True) for n in names])


def _args(**kwargs):
    defaults = {"schema": "s.json", "template": "event", "check": False, "as_json": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_template_subparser_registers(capsys):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_template_subparser(sub)
    # just ensure no exception


def test_handle_template_bad_file_returns_two():
    args = _args(schema="/no/such/file.json")
    with patch("streamdiff.cli_template.load_schema", side_effect=FileNotFoundError("not found")):
        assert handle_template(args) == 2


def test_handle_template_unknown_template_returns_two():
    args = _args(template="ghost")
    with patch("streamdiff.cli_template.load_schema", return_value=_schema()):
        with patch("streamdiff.cli_template.get_template", return_value=None):
            assert handle_template(args) == 2


def test_handle_template_check_no_missing_returns_zero(capsys):
    schema = _schema("event_id", "event_type", "timestamp")
    args = _args(check=True)
    with patch("streamdiff.cli_template.load_schema", return_value=schema):
        code = handle_template(args)
    assert code == 0
    out = capsys.readouterr().out
    assert "satisfies" in out


def test_handle_template_check_missing_returns_one(capsys):
    schema = _schema("event_id")
    args = _args(check=True)
    with patch("streamdiff.cli_template.load_schema", return_value=schema):
        code = handle_template(args)
    assert code == 1
    out = capsys.readouterr().out
    assert "event_type" in out


def test_handle_template_check_json(capsys):
    schema = _schema("event_id")
    args = _args(check=True, as_json=True)
    with patch("streamdiff.cli_template.load_schema", return_value=schema):
        handle_template(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "missing" in data
    assert "event_type" in data["missing"]


def test_handle_template_apply_returns_zero(capsys):
    schema = _schema("event_id")
    args = _args(check=False)
    with patch("streamdiff.cli_template.load_schema", return_value=schema):
        code = handle_template(args)
    assert code == 0
    out = capsys.readouterr().out
    assert "Applied" in out


def test_handle_template_apply_json(capsys):
    schema = _schema("event_id")
    args = _args(check=False, as_json=True)
    with patch("streamdiff.cli_template.load_schema", return_value=schema):
        handle_template(args)
    data = json.loads(capsys.readouterr().out)
    assert "fields" in data
    names = [f["name"] for f in data["fields"]]
    assert "event_id" in names
    assert "event_type" in names
