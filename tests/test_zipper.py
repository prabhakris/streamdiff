"""Tests for streamdiff.zipper."""
import pytest
from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.zipper import ZipPair, ZipResult, zip_schemas


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_zip_identical_schemas_all_aligned():
    s = _schema(_field("a"), _field("b"))
    result = zip_schemas(s, s)
    assert len(result.pairs) == 2
    assert all(p.aligned() for p in result.pairs)
    assert bool(result) is True


def test_zip_disjoint_schemas_all_unaligned():
    left = _schema(_field("a"))
    right = _schema(_field("b"))
    result = zip_schemas(left, right)
    assert len(result.pairs) == 2
    assert len(result.aligned()) == 0
    assert len(result.unaligned()) == 2
    assert bool(result) is False


def test_zip_partial_overlap():
    left = _schema(_field("a"), _field("b"))
    right = _schema(_field("b"), _field("c"))
    result = zip_schemas(left, right)
    assert len(result.pairs) == 3
    names = [p.name for p in result.pairs]
    assert names == ["a", "b", "c"]
    aligned = result.aligned()
    assert len(aligned) == 1
    assert aligned[0].name == "b"


def test_zip_pair_only_left():
    left = _schema(_field("x"))
    right = _schema()
    result = zip_schemas(left, right)
    pair = result.pairs[0]
    assert pair.only_left() is True
    assert pair.only_right() is False


def test_zip_pair_only_right():
    left = _schema()
    right = _schema(_field("y"))
    result = zip_schemas(left, right)
    pair = result.pairs[0]
    assert pair.only_right() is True
    assert pair.only_left() is False


def test_zip_result_to_dict_keys():
    left = _schema(_field("a"))
    right = _schema(_field("a"), _field("b"))
    result = zip_schemas(left, right)
    d = result.to_dict()
    assert "total" in d
    assert "aligned" in d
    assert "unaligned" in d
    assert "pairs" in d
    assert d["total"] == 2
    assert d["aligned"] == 1
    assert d["unaligned"] == 1


def test_zip_pair_to_dict_aligned():
    f = _field("id", FieldType.STRING)
    pair = ZipPair(name="id", left=f, right=f)
    d = pair.to_dict()
    assert d["name"] == "id"
    assert d["aligned"] is True
    assert d["left_type"] == FieldType.STRING.value
    assert d["right_type"] == FieldType.STRING.value


def test_zip_pair_str_aligned():
    f = _field("score", FieldType.FLOAT)
    pair = ZipPair(name="score", left=f, right=f)
    assert "score" in str(pair)


def test_zip_pair_str_missing_right():
    f = _field("gone")
    pair = ZipPair(name="gone", left=f, right=None)
    assert "missing" in str(pair)


def test_zip_result_str_empty():
    result = ZipResult(pairs=[])
    assert str(result) == "(no fields)"


def test_zip_result_str_non_empty():
    left = _schema(_field("a"))
    right = _schema(_field("a"))
    result = zip_schemas(left, right)
    assert "a" in str(result)
