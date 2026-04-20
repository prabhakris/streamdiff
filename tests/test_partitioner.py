import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.partitioner import (
    partition,
    partition_by_required,
    partition_by_type,
    partition_by_prefix,
    PartitionResult,
)


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_partition_by_required_splits_correctly():
    schema = _schema(_field("a"), _field("b", required=False))
    result = partition_by_required(schema)
    assert result.strategy == "required"
    assert len(result.partitions["required"]) == 1
    assert len(result.partitions["optional"]) == 1
    assert result.partitions["required"][0].name == "a"
    assert result.partitions["optional"][0].name == "b"


def test_partition_by_required_all_required():
    schema = _schema(_field("x"), _field("y"))
    result = partition_by_required(schema)
    assert len(result.partitions["required"]) == 2
    assert result.partitions["optional"] == []


def test_partition_by_type_groups_same_type():
    schema = _schema(_field("a", FieldType.STRING), _field("b", FieldType.INT), _field("c", FieldType.STRING))
    result = partition_by_type(schema)
    assert result.strategy == "type"
    assert len(result.partitions["string"]) == 2
    assert len(result.partitions["int"]) == 1


def test_partition_by_type_single_field():
    schema = _schema(_field("only", FieldType.BOOLEAN))
    result = partition_by_type(schema)
    assert "boolean" in result.partitions
    assert result.partitions["boolean"][0].name == "only"


def test_partition_by_prefix_groups_by_prefix():
    schema = _schema(_field("user_id"), _field("user_name"), _field("order_id"))
    result = partition_by_prefix(schema)
    assert result.strategy == "prefix"
    assert len(result.partitions["user"]) == 2
    assert len(result.partitions["order"]) == 1
    assert result.unpartitioned == []


def test_partition_by_prefix_unmatched_goes_to_unpartitioned():
    schema = _schema(_field("id"), _field("user_name"))
    result = partition_by_prefix(schema)
    assert len(result.unpartitioned) == 1
    assert result.unpartitioned[0].name == "id"


def test_partition_unknown_strategy_returns_none():
    schema = _schema(_field("a"))
    result = partition(schema, strategy="nonexistent")
    assert result is None


def test_partition_bool_false_when_empty_partitions():
    result = PartitionResult(strategy="test")
    assert not bool(result)


def test_partition_to_dict_structure():
    schema = _schema(_field("a"), _field("b", required=False))
    result = partition_by_required(schema)
    d = result.to_dict()
    assert "strategy" in d
    assert "partitions" in d
    assert "unpartitioned" in d
    assert d["strategy"] == "required"


def test_partition_str_includes_strategy():
    schema = _schema(_field("a"))
    result = partition_by_required(schema)
    text = str(result)
    assert "required" in text
    assert "a" in text
