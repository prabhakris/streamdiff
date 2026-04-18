import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.tracer import trace_field, trace_all, FieldTrace, TraceEntry


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields):
    return StreamSchema(name="s", fields=list(fields))


def test_trace_field_present_in_all():
    v1 = ("v1", _schema(_field("id")))
    v2 = ("v2", _schema(_field("id")))
    t = trace_field("id", [v1, v2])
    assert t.field_name == "id"
    assert all(e.present for e in t.entries)
    assert t.added_in() == "v1"
    assert t.removed_in() is None


def test_trace_field_added_midway():
    v1 = ("v1", _schema(_field("x")))
    v2 = ("v2", _schema(_field("x"), _field("y")))
    t = trace_field("y", [v1, v2])
    assert t.entries[0].present is False
    assert t.entries[1].present is True
    assert t.added_in() == "v2"


def test_trace_field_removed():
    v1 = ("v1", _schema(_field("a"), _field("b")))
    v2 = ("v2", _schema(_field("a")))
    t = trace_field("b", [v1, v2])
    assert t.removed_in() == "v2"


def test_trace_field_never_present():
    v1 = ("v1", _schema(_field("a")))
    t = trace_field("z", [v1])
    assert t.added_in() is None
    assert t.removed_in() is None


def test_trace_all_collects_all_names():
    v1 = ("v1", _schema(_field("a")))
    v2 = ("v2", _schema(_field("a"), _field("b")))
    result = trace_all([v1, v2])
    assert "a" in result
    assert "b" in result


def test_to_dict_structure():
    v1 = ("v1", _schema(_field("id")))
    t = trace_field("id", [v1])
    d = t.to_dict()
    assert d["field"] == "id"
    assert d["added_in"] == "v1"
    assert isinstance(d["history"], list)
    assert d["history"][0]["field_type"] == "string"


def test_type_recorded_in_entry():
    v1 = ("v1", _schema(_field("n", FieldType.INTEGER)))
    t = trace_field("n", [v1])
    assert t.entries[0].field_type == "integer"
    assert t.entries[0].required is True
