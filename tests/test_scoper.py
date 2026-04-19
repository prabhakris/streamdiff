import pytest
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.scoper import ScopeConfig, ScopeResult, apply_scope, scope_field_names


def _field(name: str) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=False)


def _change(name: str, ct: ChangeType = ChangeType.ADDED) -> SchemaChange:
    return SchemaChange(field_name=name, change_type=ct, old_field=None, new_field=_field(name))


def _result(*names: str) -> DiffResult:
    return DiffResult(changes=[_change(n) for n in names])


def test_no_config_returns_all():
    r = _result("a", "b", "c")
    cfg = ScopeConfig()
    out = apply_scope(r, cfg)
    assert out.total_after == 3
    assert out.dropped == 0


def test_include_pattern_filters():
    r = _result("user.name", "user.email", "order.id")
    cfg = ScopeConfig(includes=["user.*"])
    out = apply_scope(r, cfg)
    assert out.total_after == 2
    assert all(c.field_name.startswith("user.") for c in out.changes)


def test_exclude_pattern_filters():
    r = _result("user.name", "user.email", "order.id")
    cfg = ScopeConfig(excludes=["order.*"])
    out = apply_scope(r, cfg)
    assert out.total_after == 2
    assert all(not c.field_name.startswith("order.") for c in out.changes)


def test_include_and_exclude_combined():
    r = _result("user.name", "user.password", "order.id")
    cfg = ScopeConfig(includes=["user.*"], excludes=["*.password"])
    out = apply_scope(r, cfg)
    assert out.total_after == 1
    assert out.changes[0].field_name == "user.name"


def test_dropped_count_correct():
    r = _result("a", "b", "c", "d")
    cfg = ScopeConfig(includes=["a", "b"])
    out = apply_scope(r, cfg)
    assert out.dropped == 2


def test_to_dict_keys():
    r = _result("x")
    cfg = ScopeConfig()
    d = apply_scope(r, cfg).to_dict()
    assert "changes" in d
    assert "total_before" in d
    assert "total_after" in d
    assert "dropped" in d


def test_scope_field_names_include():
    names = ["foo.bar", "foo.baz", "qux"]
    cfg = ScopeConfig(includes=["foo.*"])
    assert scope_field_names(names, cfg) == ["foo.bar", "foo.baz"]


def test_scope_field_names_exclude():
    names = ["foo.bar", "foo.baz", "qux"]
    cfg = ScopeConfig(excludes=["qux"])
    assert scope_field_names(names, cfg) == ["foo.bar", "foo.baz"]


def test_bool_empty_config_is_falsy():
    assert not ScopeConfig()


def test_bool_non_empty_config_is_truthy():
    assert ScopeConfig(includes=["*"])
