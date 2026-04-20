import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.scorer4 import score_coverage, CoverageReport


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_empty_schema_returns_zero():
    report = score_coverage(_schema())
    assert report.total_score == 0.0
    assert report.max_score == 0.0
    assert report.percent == 0.0


def test_single_required_string_full_score():
    report = score_coverage(_schema(_field("id")))
    assert report.total_score == 1.0
    assert report.max_score == 1.0
    assert report.percent == 100.0


def test_optional_field_loses_points():
    report = score_coverage(_schema(_field("x", required=False)))
    assert report.total_score < 1.0
    assert report.percent < 100.0


def test_complex_type_loses_points():
    report = score_coverage(_schema(_field("tags", FieldType.ARRAY, required=True)))
    assert report.total_score < 1.0


def test_optional_complex_type_loses_both():
    report = score_coverage(_schema(_field("meta", FieldType.MAP, required=False)))
    assert report.fields[0].score == pytest.approx(0.7, abs=0.01)


def test_multiple_fields_percent():
    schema = _schema(
        _field("a"),
        _field("b", required=False),
    )
    report = score_coverage(schema)
    assert report.max_score == 2.0
    assert 0 < report.percent < 100.0


def test_to_dict_has_expected_keys():
    report = score_coverage(_schema(_field("id")))
    d = report.to_dict()
    assert "fields" in d
    assert "total_score" in d
    assert "max_score" in d
    assert "percent" in d


def test_str_contains_percent():
    report = score_coverage(_schema(_field("id")))
    assert "Coverage" in str(report)
    assert "%" in str(report)


def test_field_to_dict():
    report = score_coverage(_schema(_field("id")))
    fd = report.fields[0].to_dict()
    assert fd["name"] == "id"
    assert fd["required"] is True
    assert "score" in fd


def test_field_score_reflects_field_type():
    """Verify that more complex field types receive progressively lower scores."""
    required_string = score_coverage(_schema(_field("a", FieldType.STRING, required=True)))
    required_array = score_coverage(_schema(_field("b", FieldType.ARRAY, required=True)))
    required_map = score_coverage(_schema(_field("c", FieldType.MAP, required=True)))

    assert required_string.total_score >= required_array.total_score
    assert required_array.total_score >= required_map.total_score
