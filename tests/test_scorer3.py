import pytest
from streamdiff.schema import SchemaField, FieldType, StreamSchema
from streamdiff.scorer3 import score_readiness, FieldReadiness, ReadinessReport


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields):
    return StreamSchema(name="test", fields=list(fields))


def test_empty_schema_returns_zero():
    result = score_readiness(_schema())
    assert result.overall == 0.0
    assert result.fields == []


def test_single_required_string_field_full_score():
    result = score_readiness(_schema(_field("username")))
    assert len(result.fields) == 1
    assert result.fields[0].score == 10
    assert result.overall == 10.0


def test_optional_field_loses_one_point():
    result = score_readiness(_schema(_field("nickname", required=False)))
    assert result.fields[0].score == 9
    assert "optional field reduces confidence" in result.fields[0].notes


def test_short_name_loses_two_points():
    result = score_readiness(_schema(_field("id")))
    assert result.fields[0].score == 8
    assert "very short name" in result.fields[0].notes


def test_null_type_has_low_score():
    result = score_readiness(_schema(_field("nothing", ftype=FieldType.NULL)))
    assert result.fields[0].score == 2


def test_overall_is_average_normalised():
    s = _schema(
        _field("alpha", FieldType.STRING),   # 10
        _field("beta", FieldType.NULL),       # 2
    )
    result = score_readiness(s)
    assert result.overall == pytest.approx(6.0)


def test_bool_report_true_when_overall_gte_7():
    result = score_readiness(_schema(_field("active", FieldType.BOOLEAN)))
    assert bool(result) is True


def test_bool_report_false_when_overall_lt_7():
    result = score_readiness(_schema(_field("x", FieldType.NULL)))
    assert bool(result) is False


def test_to_dict_structure():
    result = score_readiness(_schema(_field("email")))
    d = result.to_dict()
    assert "overall" in d
    assert "fields" in d
    assert d["fields"][0]["name"] == "email"


def test_field_readiness_str():
    fr = FieldReadiness(name="foo", score=8, max_score=10)
    assert str(fr) == "foo: 8/10"
