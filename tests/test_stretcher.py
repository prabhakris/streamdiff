import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.stretcher import stretch_by_suffix, stretch_by_types, StretchResult


def _field(name: str, ft: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ft, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_stretch_by_suffix_adds_variants():
    s = _schema(_field("user_id"), _field("email"))
    result = stretch_by_suffix(s, ["raw", "clean"])
    names = {f.name for f in result.schema.fields}
    assert "user_id_raw" in names
    assert "user_id_clean" in names
    assert "email_raw" in names
    assert "email_clean" in names


def test_stretch_by_suffix_original_count():
    s = _schema(_field("x"), _field("y"))
    result = stretch_by_suffix(s, ["v2"])
    assert result.original_count == 2
    assert result.expanded_count == 4


def test_stretch_by_suffix_no_duplicates():
    s = _schema(_field("score"), _field("score_raw"))
    result = stretch_by_suffix(s, ["raw"])
    names = [f.name for f in result.schema.fields]
    assert names.count("score_raw") == 1


def test_stretch_by_suffix_bool_true_when_expanded():
    s = _schema(_field("a"))
    result = stretch_by_suffix(s, ["x"])
    assert bool(result) is True


def test_stretch_by_suffix_bool_false_when_no_change():
    s = _schema(_field("a_x"))
    result = stretch_by_suffix(s, ["x"])
    # "a_x_x" would be added since base is "a_x"
    # let's use empty suffix list
    result2 = stretch_by_suffix(s, [])
    assert bool(result2) is False


def test_stretch_by_suffix_added_fields_required_false():
    s = _schema(_field("name"))
    result = stretch_by_suffix(s, ["alt"], required=False)
    for f in result.added_fields:
        assert f.required is False


def test_stretch_by_types_adds_missing_types():
    s = _schema(_field("x", FieldType.STRING))
    result = stretch_by_types(s, [FieldType.INTEGER, FieldType.BOOLEAN])
    types = {f.field_type for f in result.schema.fields}
    assert FieldType.INTEGER in types
    assert FieldType.BOOLEAN in types


def test_stretch_by_types_skips_existing():
    s = _schema(_field("x", FieldType.STRING))
    result = stretch_by_types(s, [FieldType.STRING])
    assert result.original_count == result.expanded_count
    assert bool(result) is False


def test_stretch_by_types_to_dict():
    s = _schema(_field("a"))
    result = stretch_by_types(s, [FieldType.INTEGER])
    d = result.to_dict()
    assert "original_count" in d
    assert "expanded_count" in d
    assert "added_fields" in d


def test_stretch_result_str():
    s = _schema(_field("a"))
    result = stretch_by_suffix(s, ["v2"])
    assert "->" in str(result)
