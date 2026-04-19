"""Tests for streamdiff.stamper."""
import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.stamper import (
    SchemaStamp,
    StampedSchema,
    compare_stamps,
    stamp_schema,
)


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, type=FieldType.STRING, required=required)


def _schema(*names: str) -> StreamSchema:
    return StreamSchema(fields=[_field(n) for n in names])


def test_stamp_schema_returns_stamped_schema():
    s = _schema("id", "name")
    result = stamp_schema(s, version="1.0.0", author="alice")
    assert isinstance(result, StampedSchema)
    assert result.stamp.version == "1.0.0"
    assert result.stamp.author == "alice"
    assert result.schema is s


def test_stamp_schema_default_tags_empty():
    s = _schema("id")
    result = stamp_schema(s, version="2.0", author="bob")
    assert result.stamp.tags == []


def test_stamp_schema_custom_tags():
    s = _schema("id")
    result = stamp_schema(s, version="2.0", author="bob", tags=["stable", "v2"])
    assert "stable" in result.stamp.tags
    assert "v2" in result.stamp.tags


def test_stamp_schema_custom_timestamp():
    s = _schema("id")
    result = stamp_schema(s, version="1", author="x", ts="2024-01-01T00:00:00+00:00")
    assert result.stamp.timestamp == "2024-01-01T00:00:00+00:00"


def test_stamp_schema_auto_timestamp():
    s = _schema("id")
    result = stamp_schema(s, version="1", author="x")
    assert result.stamp.timestamp  # non-empty


def test_stamped_schema_to_dict_contains_stamp():
    s = _schema("id")
    result = stamp_schema(s, version="3", author="carol", description="initial")
    d = result.to_dict()
    assert d["stamp"]["version"] == "3"
    assert d["stamp"]["author"] == "carol"
    assert d["stamp"]["description"] == "initial"
    assert isinstance(d["fields"], list)


def test_stamped_schema_to_dict_fields():
    s = _schema("a", "b")
    result = stamp_schema(s, version="1", author="x")
    names = [f["name"] for f in result.to_dict()["fields"]]
    assert names == ["a", "b"]


def test_stamp_str():
    stamp = SchemaStamp(version="1.0", author="dave", timestamp="T", tags=["prod"])
    text = str(stamp)
    assert "1.0" in text
    assert "dave" in text
    assert "prod" in text


def test_compare_stamps_no_diff():
    a = SchemaStamp(version="1", author="x", timestamp="T")
    b = SchemaStamp(version="1", author="x", timestamp="T2")
    assert compare_stamps(a, b) == {}


def test_compare_stamps_version_diff():
    a = SchemaStamp(version="1", author="x", timestamp="T")
    b = SchemaStamp(version="2", author="x", timestamp="T")
    diff = compare_stamps(a, b)
    assert diff["version"] == {"old": "1", "new": "2"}


def test_compare_stamps_tag_diff():
    a = SchemaStamp(version="1", author="x", timestamp="T", tags=["old"])
    b = SchemaStamp(version="1", author="x", timestamp="T", tags=["new"])
    diff = compare_stamps(a, b)
    assert "tags" in diff
    assert diff["tags"]["added"] == ["new"]
    assert diff["tags"]["removed"] == ["old"]
