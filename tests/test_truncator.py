"""Tests for streamdiff.truncator."""
import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.truncator import TruncateResult, truncate_schema


def _field(name: str, required: bool = True, ftype: FieldType = FieldType.STRING) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(fields=list(fields))


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_truncate_empty_schema_returns_empty():
    result = truncate_schema(_schema(), limit=5)
    assert result.original_count == 0
    assert result.kept == []
    assert result.dropped == []
    assert not result


def test_truncate_limit_larger_than_schema_keeps_all():
    s = _schema(_field("a"), _field("b"))
    result = truncate_schema(s, limit=10)
    assert len(result.kept) == 2
    assert result.dropped == []
    assert not result


def test_truncate_limit_zero_drops_all():
    s = _schema(_field("a"), _field("b"), _field("c"))
    result = truncate_schema(s, limit=0)
    assert result.kept == []
    assert len(result.dropped) == 3
    assert bool(result)


def test_truncate_exact_limit():
    s = _schema(_field("a"), _field("b"), _field("c"))
    result = truncate_schema(s, limit=2)
    assert len(result.kept) == 2
    assert len(result.dropped) == 1


# ---------------------------------------------------------------------------
# required_first ordering
# ---------------------------------------------------------------------------

def test_required_first_keeps_required_over_optional():
    opt = _field("opt", required=False)
    req = _field("req", required=True)
    s = _schema(opt, req)  # optional listed first in schema
    result = truncate_schema(s, limit=1, required_first=True)
    assert result.kept[0].name == "req"
    assert result.dropped[0].name == "opt"


def test_required_first_false_preserves_schema_order():
    opt = _field("opt", required=False)
    req = _field("req", required=True)
    s = _schema(opt, req)
    result = truncate_schema(s, limit=1, required_first=False)
    assert result.kept[0].name == "opt"


# ---------------------------------------------------------------------------
# to_dict / __str__ / to_schema
# ---------------------------------------------------------------------------

def test_to_dict_structure():
    s = _schema(_field("x"), _field("y"), _field("z"))
    result = truncate_schema(s, limit=2)
    d = result.to_dict()
    assert d["original_count"] == 3
    assert d["kept_count"] == 2
    assert d["dropped_count"] == 1
    assert d["limit"] == 2
    assert isinstance(d["kept"], list)
    assert isinstance(d["dropped"], list)


def test_str_no_drops():
    s = _schema(_field("a"))
    result = truncate_schema(s, limit=5)
    assert "no fields dropped" in str(result)


def test_str_with_drops():
    s = _schema(_field("a"), _field("b"), _field("c"))
    result = truncate_schema(s, limit=1)
    assert "kept" in str(result)
    assert "dropped" in str(result)


def test_to_schema_returns_stream_schema():
    s = _schema(_field("a"), _field("b"), _field("c"))
    result = truncate_schema(s, limit=2)
    out = result.to_schema()
    assert len(out.fields) == 2


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_negative_limit_raises():
    s = _schema(_field("a"))
    with pytest.raises(ValueError, match="limit must be >= 0"):
        truncate_schema(s, limit=-1)
