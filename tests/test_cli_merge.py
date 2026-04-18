import json
import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.merger import MergeResult, MergeConflict
import streamdiff.cli_merge as cli_merge


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields):
    return StreamSchema(name="s", fields=list(fields))


def _args(**kwargs):
    defaults = dict(base="a.json", other="b.json", prefer="base", as_json=False, strict=False)
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_handle_merge_no_conflicts_returns_zero(capsys):
    schema = _schema(_field("x"))
    result = MergeResult(schema=schema, conflicts=[])
    with patch("streamdiff.cli_merge.load_schema", return_value=schema), \
         patch("streamdiff.cli_merge.merge_schemas", return_value=result):
        code = cli_merge.handle_merge(_args())
    assert code == 0
    out = capsys.readouterr().out
    assert "No conflicts" in out


def test_handle_merge_conflicts_strict_returns_one(capsys):
    schema = _schema(_field("x"))
    conflict = MergeConflict("x", _field("x", FieldType.STRING), _field("x", FieldType.INT))
    result = MergeResult(schema=schema, conflicts=[conflict])
    with patch("streamdiff.cli_merge.load_schema", return_value=schema), \
         patch("streamdiff.cli_merge.merge_schemas", return_value=result):
        code = cli_merge.handle_merge(_args(strict=True))
    assert code == 1


def test_handle_merge_conflicts_not_strict_returns_zero(capsys):
    schema = _schema(_field("x"))
    conflict = MergeConflict("x", _field("x", FieldType.STRING), _field("x", FieldType.INT))
    result = MergeResult(schema=schema, conflicts=[conflict])
    with patch("streamdiff.cli_merge.load_schema", return_value=schema), \
         patch("streamdiff.cli_merge.merge_schemas", return_value=result):
        code = cli_merge.handle_merge(_args(strict=False))
    assert code == 0


def test_handle_merge_json_output(capsys):
    schema = _schema(_field("a"))
    result = MergeResult(schema=schema, conflicts=[])
    with patch("streamdiff.cli_merge.load_schema", return_value=schema), \
         patch("streamdiff.cli_merge.merge_schemas", return_value=result):
        cli_merge.handle_merge(_args(as_json=True))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "fields" in data
    assert data["fields"][0]["name"] == "a"


def test_add_merge_subparser_registers_command():
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    cli_merge.add_merge_subparser(sub)
    args = parser.parse_args(["merge", "base.json", "other.json"])
    assert args.cmd == "merge"
    assert args.prefer == "base"
    assert args.strict is False
