import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.amplifier import amplify_schema, AmplifyResult


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_empty_schema_returns_empty_result():
    result = amplify_schema(_schema())
    assert result.original_count == 0
    assert result.added_count == 0
    assert result.fields == []


def test_amplify_adds_suffixed_variants():
    schema = _schema(_field("user_id"), _field("email"))
    result = amplify_schema(schema, suffix="_raw")
    assert result.added_count == 2
    names = [f.name for f in result.fields]
    assert "user_id_raw" in names
    assert "email_raw" in names


def test_amplify_variants_are_optional():
    schema = _schema(_field("user_id", required=True))
    result = amplify_schema(schema, suffix="_copy")
    variant = next(f for f in result.fields if f.name == "user_id_copy")
    assert variant.required is False


def test_amplify_with_type_filter_only_matches():
    schema = _schema(
        _field("count", FieldType.INTEGER),
        _field("label", FieldType.STRING),
    )
    result = amplify_schema(schema, suffix="_str", type_filter=FieldType.INTEGER)
    added_names = [f.name for f in result.fields]
    assert "count_str" in added_names
    assert "label_str" not in added_names
    assert result.added_count == 1


def test_amplify_with_target_type_changes_variant_type():
    schema = _schema(_field("amount", FieldType.INTEGER))
    result = amplify_schema(
        schema,
        suffix="_as_str",
        type_filter=FieldType.INTEGER,
        target_type=FieldType.STRING,
    )
    variant = next(f for f in result.fields if f.name == "amount_as_str")
    assert variant.field_type == FieldType.STRING


def test_amplify_no_duplicate_if_name_exists():
    schema = _schema(_field("score"), _field("score_raw"))
    result = amplify_schema(schema, suffix="_raw")
    raw_fields = [f for f in result.fields if f.name == "score_raw"]
    assert len(raw_fields) == 1
    assert result.added_count == 0


def test_bool_false_when_nothing_added():
    schema = _schema(_field("x", FieldType.INTEGER))
    result = amplify_schema(schema, suffix="_raw", type_filter=FieldType.BOOLEAN)
    assert not result


def test_bool_true_when_fields_added():
    schema = _schema(_field("x"))
    result = amplify_schema(schema, suffix="_copy")
    assert result


def test_to_dict_structure():
    schema = _schema(_field("val", FieldType.INTEGER))
    result = amplify_schema(schema, suffix="_ext")
    d = result.to_dict()
    assert d["original_count"] == 1
    assert d["added_count"] == 1
    assert d["total_count"] == 2
    assert any(f["name"] == "val_ext" for f in d["fields"])


def test_to_schema_returns_stream_schema():
    schema = _schema(_field("a"), _field("b"))
    result = amplify_schema(schema, suffix="_dup")
    out = result.to_schema(name="amplified_test")
    assert out.name == "amplified_test"
    assert len(out.fields) == result.original_count + result.added_count


def test_str_representation():
    schema = _schema(_field("x"))
    result = amplify_schema(schema, suffix="_v2")
    s = str(result)
    assert "AmplifyResult" in s
    assert "original=1" in s
