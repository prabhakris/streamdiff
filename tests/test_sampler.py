"""Tests for streamdiff.sampler."""
import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.sampler import sample_by_count, sample_by_fraction, SampleResult


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*names: str) -> StreamSchema:
    return StreamSchema(fields=[_field(n) for n in names])


def test_sample_by_count_returns_correct_count():
    s = _schema("a", "b", "c", "d", "e")
    result = sample_by_count(s, 3, seed=42)
    assert len(result.sampled) == 3
    assert result.original_count == 5


def test_sample_by_count_zero_returns_empty():
    s = _schema("a", "b", "c")
    result = sample_by_count(s, 0, seed=0)
    assert len(result.sampled) == 0
    assert not result


def test_sample_by_count_exceeds_clamps_to_total():
    s = _schema("a", "b")
    result = sample_by_count(s, 100, seed=1)
    assert len(result.sampled) == 2


def test_sample_by_count_seed_reproducible():
    s = _schema("a", "b", "c", "d", "e")
    r1 = sample_by_count(s, 3, seed=7)
    r2 = sample_by_count(s, 3, seed=7)
    assert [f.name for f in r1.sampled] == [f.name for f in r2.sampled]


def test_sample_by_fraction_half():
    s = _schema("a", "b", "c", "d")
    result = sample_by_fraction(s, 0.5, seed=0)
    assert len(result.sampled) == 2


def test_sample_by_fraction_zero_returns_empty():
    s = _schema("a", "b", "c")
    result = sample_by_fraction(s, 0.0, seed=0)
    assert len(result.sampled) == 0


def test_sample_by_fraction_one_returns_all():
    s = _schema("a", "b", "c")
    result = sample_by_fraction(s, 1.0, seed=0)
    assert len(result.sampled) == 3


def test_sample_by_fraction_invalid_raises():
    s = _schema("a", "b")
    with pytest.raises(ValueError):
        sample_by_fraction(s, 1.5)


def test_to_dict_contains_expected_keys():
    s = _schema("x", "y", "z")
    result = sample_by_count(s, 2, seed=3)
    d = result.to_dict()
    assert "original_count" in d
    assert "sampled_count" in d
    assert "fields" in d
    assert d["sampled_count"] == 2


def test_to_schema_returns_stream_schema():
    s = _schema("a", "b", "c")
    result = sample_by_count(s, 2, seed=5)
    schema = result.to_schema()
    assert isinstance(schema, StreamSchema)
    assert len(schema.fields) == 2


def test_str_representation():
    s = _schema("a", "b", "c")
    result = sample_by_count(s, 2, seed=1)
    assert "SampleResult" in str(result)
