import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.slotter import slot_by_type, slot_by_pattern, SlotResult


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_slot_by_type_empty_schema():
    result = slot_by_type(_schema())
    assert result.buckets == {}
    assert result.unslotted == []


def test_slot_by_type_groups_same_type():
    s = _schema(_field("a", FieldType.STRING), _field("b", FieldType.STRING))
    result = slot_by_type(s)
    assert "string" in result.buckets
    assert len(result.buckets["string"]) == 2


def test_slot_by_type_multiple_types():
    s = _schema(_field("a", FieldType.STRING), _field("b", FieldType.INT))
    result = slot_by_type(s)
    assert len(result.buckets) == 2
    assert len(result.buckets["string"]) == 1
    assert len(result.buckets["int"]) == 1


def test_slot_by_type_no_unslotted():
    s = _schema(_field("x", FieldType.BOOLEAN))
    result = slot_by_type(s)
    assert result.unslotted == []


def test_slot_by_pattern_matches_bucket():
    s = _schema(_field("user_id"), _field("user_name"), _field("amount"))
    result = slot_by_pattern(s, {"user": "user", "finance": "amount"})
    assert len(result.buckets["user"]) == 2
    assert len(result.buckets["finance"]) == 1
    assert result.unslotted == []


def test_slot_by_pattern_unslotted_when_no_match():
    s = _schema(_field("timestamp"), _field("user_id"))
    result = slot_by_pattern(s, {"finance": "amount"})
    assert result.unslotted == [_field("timestamp"), _field("user_id")]
    assert result.buckets == {}


def test_slot_by_pattern_case_insensitive():
    s = _schema(_field("UserID"))
    result = slot_by_pattern(s, {"user": "user"})
    assert len(result.buckets["user"]) == 1


def test_slot_result_bool_true():
    r = SlotResult(buckets={"a": [_field("x")]}, unslotted=[])
    assert bool(r) is True


def test_slot_result_bool_false():
    r = SlotResult(buckets={}, unslotted=[])
    assert bool(r) is False


def test_slot_result_to_dict():
    f = _field("x", FieldType.INT)
    r = SlotResult(buckets={"nums": [f]}, unslotted=[])
    d = r.to_dict()
    assert d["buckets"]["nums"][0]["name"] == "x"
    assert d["buckets"]["nums"][0]["type"] == "int"


def test_slot_result_str_no_fields():
    r = SlotResult()
    assert str(r) == "No fields slotted."


def test_slot_result_str_with_buckets():
    f = _field("email", FieldType.STRING)
    r = SlotResult(buckets={"contact": [f]}, unslotted=[])
    out = str(r)
    assert "[contact]" in out
    assert "email" in out
