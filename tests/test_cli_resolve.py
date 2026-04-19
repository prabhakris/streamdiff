import json
import pytest
from types import SimpleNamespace
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.resolver import resolve_schemas, ResolvedField
from streamdiff.cli_resolve import handle_resolve, _parse_named_schemas


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields):
    return StreamSchema(fields=list(fields))


def _args(**kwargs):
    defaults = {"schemas": [], "output_json": False, "strict": False}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_parse_named_schemas_invalid_spec():
    with pytest.raises(ValueError, match="NAME:FILE"):
        _parse_named_schemas(["nocolon"])


def test_parse_named_schemas_missing_file():
    with pytest.raises(FileNotFoundError):
        _parse_named_schemas(["main:/nonexistent/path.json"])


def test_handle_resolve_bad_spec_returns_two(capsys):
    args = _args(schemas=["badspec"])
    code = handle_resolve(args)
    assert code == 2


def test_handle_resolve_text_output(monkeypatch, capsys):
    s1 = _schema(_field("id"))
    s2 = _schema(_field("ts"))
    monkeypatch.setattr(
        "streamdiff.cli_resolve._parse_named_schemas",
        lambda _: {"a": s1, "b": s2},
    )
    args = _args(schemas=["a:x", "b:y"])
    code = handle_resolve(args)
    assert code == 0
    out = capsys.readouterr().out
    assert "2 field(s)" in out


def test_handle_resolve_json_output(monkeypatch, capsys):
    s = _schema(_field("id"))
    monkeypatch.setattr(
        "streamdiff.cli_resolve._parse_named_schemas",
        lambda _: {"main": s},
    )
    args = _args(schemas=["main:x"], output_json=True)
    code = handle_resolve(args)
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert "resolved" in data
    assert "conflicts" in data


def test_handle_resolve_conflict_strict_returns_one(monkeypatch, capsys):
    s1 = _schema(_field("x", FieldType.INT))
    s2 = _schema(_field("x", FieldType.STRING))
    monkeypatch.setattr(
        "streamdiff.cli_resolve._parse_named_schemas",
        lambda _: {"a": s1, "b": s2},
    )
    args = _args(schemas=["a:x", "b:y"], strict=True)
    code = handle_resolve(args)
    assert code == 1


def test_handle_resolve_conflict_non_strict_returns_zero(monkeypatch, capsys):
    s1 = _schema(_field("x", FieldType.INT))
    s2 = _schema(_field("x", FieldType.STRING))
    monkeypatch.setattr(
        "streamdiff.cli_resolve._parse_named_schemas",
        lambda _: {"a": s1, "b": s2},
    )
    args = _args(schemas=["a:x", "b:y"], strict=False)
    code = handle_resolve(args)
    assert code == 0
