import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.resolver import resolve_schemas, find_field, ResolvedField


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields):
    return StreamSchema(fields=list(fields))


def test_resolve_single_schema_no_conflicts():
    s = _schema(_field("id"), _field("name"))
    result = resolve_schemas({"main": s})
    assert result.ok
    assert len(result.resolved) == 2
    assert all(r.source == "main" for r in result.resolved)


def test_resolve_disjoint_schemas():
    s1 = _schema(_field("id"))
    s2 = _schema(_field("timestamp"))
    result = resolve_schemas({"a": s1, "b": s2})
    assert result.ok
    names = [r.name for r in result.resolved]
    assert "id" in names
    assert "timestamp" in names


def test_resolve_overlapping_same_type_no_conflict():
    s1 = _schema(_field("id", FieldType.STRING))
    s2 = _schema(_field("id", FieldType.STRING))
    result = resolve_schemas({"a": s1, "b": s2})
    assert result.ok
    assert len(result.resolved) == 1


def test_resolve_type_conflict_detected():
    s1 = _schema(_field("count", FieldType.INT))
    s2 = _schema(_field("count", FieldType.STRING))
    result = resolve_schemas({"a": s1, "b": s2})
    assert not result.ok
    assert len(result.conflicts) == 1
    assert "count" in result.conflicts[0]


def test_resolve_multiple_conflicts():
    s1 = _schema(_field("x", FieldType.INT), _field("y", FieldType.FLOAT))
    s2 = _schema(_field("x", FieldType.STRING), _field("y", FieldType.STRING))
    result = resolve_schemas({"a": s1, "b": s2})
    assert len(result.conflicts) == 2


def test_resolved_field_to_dict():
    f = _field("id", FieldType.STRING, required=True)
    rf = ResolvedField(name="id", source="main", schema_field=f)
    d = rf.to_dict()
    assert d["name"] == "id"
    assert d["source"] == "main"
    assert d["required"] is True


def test_resolved_field_str():
    f = _field("id", FieldType.STRING, required=False)
    rf = ResolvedField(name="id", source="shared", schema_field=f)
    assert "id" in str(rf)
    assert "shared" in str(rf)
    assert "optional" in str(rf)


def test_find_field_found():
    s = _schema(_field("user_id"))
    rf = find_field("user_id", {"main": s})
    assert rf is not None
    assert rf.name == "user_id"
    assert rf.source == "main"


def test_find_field_not_found():
    s = _schema(_field("id"))
    rf = find_field("missing", {"main": s})
    assert rf is None


def test_find_field_returns_first_match():
    s1 = _schema(_field("id"))
    s2 = _schema(_field("id"))
    rf = find_field("id", {"first": s1, "second": s2})
    assert rf.source == "first"
