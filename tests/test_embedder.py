import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.embedder import (
    embed_schema,
    cosine_similarity,
    EmbedVector,
    EmbedReport,
    TYPE_INDEX,
)


def _field(name: str, type_: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, type=type_, required=required)


def _schema(*fields: SchemaField, name: str = "test") -> StreamSchema:
    return StreamSchema(name=name, fields=list(fields))


def test_empty_schema_returns_empty_report():
    s = _schema()
    report = embed_schema(s)
    assert isinstance(report, EmbedReport)
    assert report.vectors == []


def test_single_field_vector_length():
    s = _schema(_field("age", FieldType.INT))
    report = embed_schema(s)
    assert len(report.vectors) == 1
    expected_len = len(TYPE_INDEX) + 1
    assert len(report.vectors[0].values) == expected_len


def test_required_field_first_component_is_one():
    s = _schema(_field("name", FieldType.STRING, required=True))
    report = embed_schema(s)
    assert report.vectors[0].values[0] == 1.0


def test_optional_field_first_component_is_zero():
    s = _schema(_field("nickname", FieldType.STRING, required=False))
    report = embed_schema(s)
    assert report.vectors[0].values[0] == 0.0


def test_type_component_is_set():
    s = _schema(_field("score", FieldType.FLOAT))
    report = embed_schema(s)
    idx = TYPE_INDEX[FieldType.FLOAT.value]
    assert report.vectors[0].values[1 + idx] == 1.0


def test_by_field_returns_correct_vector():
    s = _schema(_field("a"), _field("b", FieldType.INT))
    report = embed_schema(s)
    v = report.by_field("b")
    assert v is not None
    assert v.field_name == "b"


def test_by_field_missing_returns_none():
    s = _schema(_field("a"))
    report = embed_schema(s)
    assert report.by_field("z") is None


def test_cosine_similarity_identical():
    v = [1.0, 0.0, 1.0]
    assert cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal():
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert cosine_similarity(a, b) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector():
    a = [0.0, 0.0]
    b = [1.0, 0.0]
    assert cosine_similarity(a, b) == 0.0


def test_cosine_similarity_length_mismatch_raises():
    with pytest.raises(ValueError):
        cosine_similarity([1.0], [1.0, 2.0])


def test_to_dict_structure():
    s = _schema(_field("x", FieldType.BOOLEAN), name="mystream")
    report = embed_schema(s)
    d = report.to_dict()
    assert d["schema"] == "mystream"
    assert len(d["vectors"]) == 1
    assert "field" in d["vectors"][0]
    assert "vector" in d["vectors"][0]
