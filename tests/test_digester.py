"""Tests for streamdiff.digester."""
import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.digester import (
    compute_digest,
    compare_digests,
    DigestComparison,
)


def _field(name: str, required: bool = True, ftype: FieldType = FieldType.STRING) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField, name: str = "events") -> StreamSchema:
    return StreamSchema(name=name, fields=list(fields))


def test_compute_digest_returns_string():
    s = _schema(_field("id"))
    d = compute_digest(s)
    assert isinstance(d, str) and len(d) == 64


def test_same_schema_same_digest():
    s1 = _schema(_field("id"), _field("name"))
    s2 = _schema(_field("id"), _field("name"))
    assert compute_digest(s1) == compute_digest(s2)


def test_field_order_does_not_affect_digest():
    s1 = _schema(_field("a"), _field("b"))
    s2 = _schema(_field("b"), _field("a"))
    assert compute_digest(s1) == compute_digest(s2)


def test_added_field_changes_digest():
    s1 = _schema(_field("id"))
    s2 = _schema(_field("id"), _field("ts"))
    assert compute_digest(s1) != compute_digest(s2)


def test_type_change_changes_digest():
    s1 = _schema(_field("id", ftype=FieldType.STRING))
    s2 = _schema(_field("id", ftype=FieldType.INT))
    assert compute_digest(s1) != compute_digest(s2)


def test_md5_algorithm():
    s = _schema(_field("id"))
    d = compute_digest(s, algorithm="md5")
    assert len(d) == 32


def test_compare_digests_unchanged():
    s = _schema(_field("id"))
    result = compare_digests(s, s)
    assert isinstance(result, DigestComparison)
    assert not result.changed
    assert result.old_digest == result.new_digest


def test_compare_digests_changed():
    s1 = _schema(_field("id"))
    s2 = _schema(_field("id"), _field("extra"))
    result = compare_digests(s1, s2)
    assert result.changed


def test_str_unchanged():
    s = _schema(_field("id"))
    result = compare_digests(s, s)
    assert "UNCHANGED" in str(result)


def test_str_changed():
    s1 = _schema(_field("id"))
    s2 = _schema(_field("id"), _field("x"))
    result = compare_digests(s1, s2)
    assert "CHANGED" in str(result)


def test_to_dict_keys():
    s1 = _schema(_field("id"))
    s2 = _schema(_field("id"), _field("x"))
    d = compare_digests(s1, s2).to_dict()
    assert {"old_digest", "new_digest", "changed"} == set(d.keys())
    assert d["changed"] is True
