import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.merger import merge_schemas, MergeResult


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields):
    return StreamSchema(name="test", fields=list(fields))


def test_merge_no_overlap():
    base = _schema(_field("a"))
    other = _schema(_field("b"))
    result = merge_schemas(base, other)
    assert result.ok
    names = {f.name for f in result.schema.fields}
    assert names == {"a", "b"}


def test_merge_identical_fields():
    f = _field("a")
    result = merge_schemas(_schema(f), _schema(f))
    assert result.ok
    assert len(result.schema.fields) == 1


def test_merge_required_union():
    base = _schema(_field("a", required=False))
    other = _schema(_field("a", required=True))
    result = merge_schemas(base, other)
    assert result.ok
    assert result.schema.field_map()["a"].required is True


def test_merge_type_conflict_prefer_base():
    base = _schema(_field("x", FieldType.STRING))
    other = _schema(_field("x", FieldType.INT))
    result = merge_schemas(base, other, prefer="base")
    assert not result.ok
    assert len(result.conflicts) == 1
    assert str(result.conflicts[0]).startswith("Conflict on 'x'")
    assert result.schema.field_map()["x"].field_type == FieldType.STRING


def test_merge_type_conflict_prefer_other():
    base = _schema(_field("x", FieldType.STRING))
    other = _schema(_field("x", FieldType.INT))
    result = merge_schemas(base, other, prefer="other")
    assert result.schema.field_map()["x"].field_type == FieldType.INT


def test_merge_adds_new_fields_from_other():
    base = _schema(_field("a"))
    other = _schema(_field("a"), _field("b"), _field("c"))
    result = merge_schemas(base, other)
    assert result.ok
    assert len(result.schema.fields) == 3


def test_merge_invalid_prefer_raises():
    base = _schema(_field("a"))
    with pytest.raises(ValueError, match="prefer must be"):
        merge_schemas(base, base, prefer="newest")


def test_merge_result_ok_no_conflicts():
    base = _schema(_field("a"))
    result = merge_schemas(base, base)
    assert result.ok is True
    assert result.conflicts == []
