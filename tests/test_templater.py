import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.templater import (
    list_templates,
    get_template,
    match_template,
    apply_template,
    SchemaTemplate,
    TemplateField,
)


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, type=ftype, required=required)


def _schema(*fields):
    return StreamSchema(fields=list(fields))


def test_list_templates_includes_builtins():
    names = list_templates()
    assert "event" in names
    assert "audit" in names


def test_get_template_returns_template():
    t = get_template("event")
    assert t is not None
    assert t.name == "event"
    assert any(f.name == "event_id" for f in t.fields)


def test_get_template_unknown_returns_none():
    assert get_template("nonexistent") is None


def test_match_template_no_missing():
    t = get_template("event")
    schema = _schema(
        _field("event_id"),
        _field("event_type"),
        _field("timestamp", FieldType.LONG),
    )
    missing = match_template(schema, t)
    assert missing == []


def test_match_template_missing_required():
    t = get_template("event")
    schema = _schema(_field("event_id"))
    missing = match_template(schema, t)
    assert "event_type" in missing
    assert "timestamp" in missing


def test_match_template_optional_not_reported():
    t = get_template("event")
    schema = _schema(
        _field("event_id"),
        _field("event_type"),
        _field("timestamp", FieldType.LONG),
    )
    missing = match_template(schema, t)
    assert "source" not in missing


def test_apply_template_adds_missing_fields():
    t = get_template("event")
    schema = _schema(_field("event_id"))
    result = apply_template(schema, t)
    names = {f.name for f in result.fields}
    assert "event_type" in names
    assert "timestamp" in names
    assert "event_id" in names


def test_apply_template_does_not_duplicate():
    t = get_template("event")
    schema = _schema(_field("event_id"), _field("event_type"), _field("timestamp", FieldType.LONG))
    result = apply_template(schema, t)
    names = [f.name for f in result.fields]
    assert names.count("event_id") == 1


def test_template_to_dict():
    t = get_template("audit")
    d = t.to_dict()
    assert d["name"] == "audit"
    assert isinstance(d["fields"], list)
    assert d["fields"][0]["name"] == "actor_id"
