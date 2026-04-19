import argparse
import json
import pytest
from unittest.mock import patch, MagicMock
from streamdiff.cli_readiness import add_readiness_subparser, handle_readiness
from streamdiff.scorer3 import ReadinessReport, FieldReadiness
from streamdiff.schema import SchemaField, FieldType, StreamSchema


def _parse(*args):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_readiness_subparser(sub)
    return parser.parse_args(["readiness", *args])


def _schema(*fields):
    return StreamSchema(name="t", fields=list(fields))


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


def test_add_readiness_subparser_registers():
    args = _parse("schema.json")
    assert args.schema == "schema.json"
    assert args.as_json is False
    assert args.min_score == 0.0


def test_add_readiness_subparser_json_flag():
    args = _parse("schema.json", "--json")
    assert args.as_json is True


def test_add_readiness_subparser_min_score():
    args = _parse("schema.json", "--min-score", "7.5")
    assert args.min_score == 7.5


def test_handle_readiness_bad_file_returns_two():
    args = _parse("nonexistent.json")
    with patch("streamdiff.cli_readiness.load_schema", side_effect=FileNotFoundError("no file")):
        assert handle_readiness(args) == 2


def test_handle_readiness_returns_zero_above_threshold(capsys):
    args = _parse("schema.json", "--min-score", "5.0")
    schema = _schema(_field("email"), _field("name"))
    with patch("streamdiff.cli_readiness.load_schema", return_value=schema):
        code = handle_readiness(args)
    assert code == 0


def test_handle_readiness_returns_one_below_threshold(capsys):
    args = _parse("schema.json", "--min-score", "9.9")
    from streamdiff.schema import FieldType
    schema = _schema(_field("x", FieldType.NULL))
    with patch("streamdiff.cli_readiness.load_schema", return_value=schema):
        code = handle_readiness(args)
    assert code == 1


def test_handle_readiness_json_output(capsys):
    args = _parse("schema.json", "--json")
    schema = _schema(_field("status"))
    with patch("streamdiff.cli_readiness.load_schema", return_value=schema):
        handle_readiness(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "overall" in data
    assert "fields" in data
