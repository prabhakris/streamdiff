import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.splitter import split_by_prefix, split_by_names, SplitResult


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*names: str) -> StreamSchema:
    return StreamSchema(name="test", fields=[_field(n) for n in names])


def test_split_by_prefix_groups_correctly():
    schema = _schema("user_id", "user_name", "order_id", "standalone")
    result = split_by_prefix(schema)
    assert "user" in result.groups
    assert "order" in result.groups
    assert len(result.groups["user"].fields) == 2
    assert len(result.groups["order"].fields) == 1


def test_split_by_prefix_unmatched_has_no_separator():
    schema = _schema("user_id", "standalone", "bare")
    result = split_by_prefix(schema)
    unmatched_names = [f.name for f in result.unmatched.fields]
    assert "standalone" in unmatched_names
    assert "bare" in unmatched_names
    assert "user_id" not in unmatched_names


def test_split_by_prefix_all_unmatched():
    schema = _schema("alpha", "beta")
    result = split_by_prefix(schema)
    assert result.groups == {}
    assert len(result.unmatched.fields) == 2
    assert not result


def test_split_by_prefix_custom_separator():
    schema = _schema("user.id", "user.name", "order.id")
    result = split_by_prefix(schema, separator=".")
    assert "user" in result.groups
    assert len(result.groups["user"].fields) == 2


def test_split_by_names_assigns_fields():
    schema = _schema("a", "b", "c", "d")
    result = split_by_names(schema, {"group1": ["a", "b"], "group2": ["c"]})
    assert len(result.groups["group1"].fields) == 2
    assert len(result.groups["group2"].fields) == 1
    unmatched = [f.name for f in result.unmatched.fields]
    assert "d" in unmatched


def test_split_by_names_empty_name_sets():
    schema = _schema("x", "y")
    result = split_by_names(schema, {})
    assert result.groups == {}
    assert len(result.unmatched.fields) == 2


def test_split_result_to_dict():
    schema = _schema("user_id", "user_name", "bare")
    result = split_by_prefix(schema)
    d = result.to_dict()
    assert "groups" in d
    assert "unmatched" in d
    assert "user_id" in d["groups"]["user"] or "user_name" in d["groups"]["user"]


def test_split_result_bool_true_when_groups_exist():
    schema = _schema("a_b", "a_c")
    result = split_by_prefix(schema)
    assert bool(result) is True
