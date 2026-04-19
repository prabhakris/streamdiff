import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.pruner import prune_by_names, prune_optional, apply_prune, PruneResult


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_prune_by_names_removes_matching():
    s = _schema(_field("a"), _field("b"), _field("c"))
    result = prune_by_names(s, {"b"})
    assert len(result.pruned) == 1
    assert result.pruned[0].name == "b"
    assert len(result.kept) == 2


def test_prune_by_names_no_match_keeps_all():
    s = _schema(_field("a"), _field("b"))
    result = prune_by_names(s, {"z"})
    assert len(result.pruned) == 0
    assert len(result.kept) == 2


def test_prune_by_names_empty_set_keeps_all():
    s = _schema(_field("a"), _field("b"))
    result = prune_by_names(s, set())
    assert not result


def test_prune_optional_removes_non_required():
    s = _schema(_field("a", required=True), _field("b", required=False), _field("c", required=False))
    result = prune_optional(s)
    assert len(result.pruned) == 2
    assert all(not f.required for f in result.pruned)
    assert len(result.kept) == 1


def test_prune_optional_all_required_keeps_all():
    s = _schema(_field("a"), _field("b"))
    result = prune_optional(s)
    assert not result
    assert len(result.kept) == 2


def test_apply_prune_returns_new_schema():
    s = _schema(_field("a"), _field("b"), _field("c"))
    result = prune_by_names(s, {"b"})
    pruned_schema = apply_prune(s, result)
    assert pruned_schema.name == s.name
    assert len(pruned_schema.fields) == 2
    assert all(f.name != "b" for f in pruned_schema.fields)


def test_prune_result_to_dict():
    s = _schema(_field("x"), _field("y", required=False))
    result = prune_optional(s)
    d = result.to_dict()
    assert d["pruned_count"] == 1
    assert d["kept_count"] == 1
    assert "y" in d["pruned"]


def test_prune_result_str_no_pruned():
    result = PruneResult(pruned=[], kept=[])
    assert "No fields pruned" in str(result)


def test_prune_result_str_with_pruned():
    result = PruneResult(pruned=[_field("a"), _field("b")], kept=[])
    assert "2" in str(result)
    assert "a" in str(result)
