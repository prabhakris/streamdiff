"""Tests for streamdiff.transcriber."""
import pytest

from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.transcriber import (
    TranscribedField,
    TranscribeReport,
    transcribe_schema,
    _describe_field,
)


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField, name: str = "test_stream") -> StreamSchema:
    return StreamSchema(name=name, fields=list(fields))


def test_empty_schema_returns_empty_report():
    s = _schema(name="empty")
    report = transcribe_schema(s)
    assert report.schema_name == "empty"
    assert report.fields == []
    assert not report


def test_single_field_transcribed():
    s = _schema(_field("user_id", FieldType.STRING, required=True))
    report = transcribe_schema(s)
    assert len(report.fields) == 1
    tf = report.fields[0]
    assert tf.name == "user_id"
    assert tf.type_name == FieldType.STRING.value
    assert tf.required is True


def test_optional_field_marked_optional():
    s = _schema(_field("nickname", FieldType.STRING, required=False))
    report = transcribe_schema(s)
    assert report.fields[0].required is False
    assert "optional" in report.fields[0].description.lower()


def test_required_field_description_says_required():
    f = _field("event_time", FieldType.STRING, required=True)
    desc = _describe_field(f)
    assert "Required" in desc


def test_multiple_fields_all_transcribed():
    s = _schema(
        _field("id", FieldType.INT, required=True),
        _field("name", FieldType.STRING, required=False),
        _field("score", FieldType.FLOAT, required=False),
    )
    report = transcribe_schema(s)
    assert len(report.fields) == 3
    names = [tf.name for tf in report.fields]
    assert names == ["id", "name", "score"]


def test_to_dict_structure():
    s = _schema(_field("payload", FieldType.STRING, required=True), name="my_stream")
    report = transcribe_schema(s)
    d = report.to_dict()
    assert d["schema"] == "my_stream"
    assert len(d["fields"]) == 1
    assert d["fields"][0]["name"] == "payload"
    assert d["fields"][0]["required"] is True


def test_str_output_contains_schema_name():
    s = _schema(_field("x"), name="stream_x")
    report = transcribe_schema(s)
    text = str(report)
    assert "stream_x" in text
    assert "x" in text


def test_custom_name_overrides_schema_name():
    s = _schema(_field("a"), name="original")
    report = transcribe_schema(s, name="overridden")
    assert report.schema_name == "overridden"


def test_bool_true_when_fields_present():
    s = _schema(_field("z"))
    report = transcribe_schema(s)
    assert bool(report) is True
