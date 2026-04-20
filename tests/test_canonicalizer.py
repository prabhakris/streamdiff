"""Tests for streamdiff.canonicalizer."""
import pytest

from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.canonicalizer import (
    CanonicalField,
    CanonicalSchema,
    canonicalize,
    diff_canonical,
)


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, type=ftype, required=required)


def _schema(*fields: SchemaField, name: str = "test") -> StreamSchema:
    return StreamSchema(name=name, fields=list(fields))


# --- CanonicalField ---

def test_canonical_field_to_dict():
    cf = CanonicalField(name="id", type="string", required=True)
    assert cf.to_dict() == {"name": "id", "type": "string", "required": True}


def test_canonical_field_str_required():
    cf = CanonicalField(name="id", type="string", required=True)
    assert "required" in str(cf)


def test_canonical_field_str_optional():
    cf = CanonicalField(name="tag", type="string", required=False)
    assert "optional" in str(cf)


# --- CanonicalSchema ---

def test_canonical_schema_bool_empty():
    cs = CanonicalSchema(name="s")
    assert not bool(cs)


def test_canonical_schema_bool_with_fields():
    cs = CanonicalSchema(name="s", fields=[CanonicalField("x", "int", True)])
    assert bool(cs)


def test_canonical_schema_to_dict_structure():
    cs = CanonicalSchema(
        name="events",
        fields=[CanonicalField("a", "string", True)],
    )
    d = cs.to_dict()
    assert d["name"] == "events"
    assert len(d["fields"]) == 1
    assert d["fields"][0]["name"] == "a"


def test_canonical_schema_str_includes_name():
    cs = CanonicalSchema(name="orders", fields=[CanonicalField("id", "string", True)])
    assert "orders" in str(cs)


# --- canonicalize ---

def test_canonicalize_empty_schema():
    s = _schema(name="empty")
    cs = canonicalize(s)
    assert cs.name == "empty"
    assert cs.fields == []


def test_canonicalize_sorts_fields_by_default():
    s = _schema(_field("z"), _field("a"), _field("m"))
    cs = canonicalize(s)
    assert [f.name for f in cs.fields] == ["a", "m", "z"]


def test_canonicalize_preserves_order_when_sort_false():
    s = _schema(_field("z"), _field("a"), _field("m"))
    cs = canonicalize(s, sort=False)
    assert [f.name for f in cs.fields] == ["z", "a", "m"]


def test_canonicalize_normalizes_type_to_lowercase():
    s = _schema(_field("count", FieldType.INTEGER))
    cs = canonicalize(s)
    assert cs.fields[0].type == "integer"


def test_canonicalize_preserves_required_flag():
    s = _schema(_field("opt", required=False))
    cs = canonicalize(s)
    assert cs.fields[0].required is False


# --- diff_canonical ---

def test_diff_canonical_no_changes():
    s = _schema(_field("id"), _field("name"))
    old = canonicalize(s)
    new = canonicalize(s)
    result = diff_canonical(old, new)
    assert result == {"added": [], "removed": [], "changed": []}


def test_diff_canonical_detects_added_field():
    old = canonicalize(_schema(_field("id")))
    new = canonicalize(_schema(_field("id"), _field("email")))
    result = diff_canonical(old, new)
    assert "email" in result["added"]
    assert result["removed"] == []


def test_diff_canonical_detects_removed_field():
    old = canonicalize(_schema(_field("id"), _field("email")))
    new = canonicalize(_schema(_field("id")))
    result = diff_canonical(old, new)
    assert "email" in result["removed"]
    assert result["added"] == []


def test_diff_canonical_detects_type_change():
    old = canonicalize(_schema(_field("count", FieldType.INTEGER)))
    new = canonicalize(_schema(_field("count", FieldType.STRING)))
    result = diff_canonical(old, new)
    assert "count" in result["changed"]
