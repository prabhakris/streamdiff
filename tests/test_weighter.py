"""Tests for streamdiff.weighter."""
import pytest
from streamdiff.schema import SchemaField, StreamSchema, FieldType
from streamdiff.weighter import weight_field, weight_schema, FieldWeight, WeightReport


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_required_field_has_higher_base_weight_than_optional():
    req = _field("x", required=True)
    opt = _field("x", required=False)
    assert weight_field(req).weight > weight_field(opt).weight


def test_high_importance_type_gets_bonus():
    f = _field("value", ftype=FieldType.INT, required=False)
    w = weight_field(f)
    assert w.weight > 1.0
    assert any("int" in r for r in w.reasons)


def test_name_pattern_id_gets_bonus():
    f = _field("user_id", ftype=FieldType.BOOLEAN, required=False)
    w = weight_field(f)
    assert any("id" in r for r in w.reasons)
    assert w.weight > 1.0


def test_name_pattern_timestamp_gets_bonus():
    f = _field("created_timestamp", required=False)
    w = weight_field(f)
    assert any("timestamp" in r for r in w.reasons)


def test_plain_optional_field_weight_is_one():
    f = _field("description", ftype=FieldType.BOOLEAN, required=False)
    w = weight_field(f)
    assert w.weight == 1.0


def test_weight_schema_returns_report():
    s = _schema(_field("id"), _field("name", required=False))
    report = weight_schema(s)
    assert isinstance(report, WeightReport)
    assert len(report.weights) == 2


def test_weight_schema_sorted_descending():
    s = _schema(
        _field("description", ftype=FieldType.BOOLEAN, required=False),
        _field("record_id", ftype=FieldType.INT, required=True),
    )
    report = weight_schema(s)
    weights = [w.weight for w in report.weights]
    assert weights == sorted(weights, reverse=True)


def test_weight_schema_min_weight_filters():
    s = _schema(
        _field("description", ftype=FieldType.BOOLEAN, required=False),
        _field("record_id", ftype=FieldType.INT, required=True),
    )
    report = weight_schema(s, min_weight=3.0)
    assert all(w.weight >= 3.0 for w in report.weights)


def test_weight_report_total():
    s = _schema(_field("a"), _field("b"))
    report = weight_schema(s)
    assert report.total() == sum(w.weight for w in report.weights)


def test_weight_report_by_field():
    s = _schema(_field("alpha"), _field("beta", required=False))
    report = weight_schema(s)
    mapping = report.by_field()
    assert "alpha" in mapping
    assert "beta" in mapping


def test_to_dict_structure():
    f = _field("event_type", ftype=FieldType.STRING, required=True)
    w = weight_field(f)
    d = w.to_dict()
    assert "field" in d
    assert "weight" in d
    assert "reasons" in d


def test_report_to_dict_has_total():
    s = _schema(_field("x"))
    report = weight_schema(s)
    d = report.to_dict()
    assert "total" in d
    assert "weights" in d
