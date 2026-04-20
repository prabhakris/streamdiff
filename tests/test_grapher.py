import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.grapher import build_graph, isolated_fields, FieldGraph, GraphNode


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, type=FieldType.STRING, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_empty_schema_returns_empty_graph():
    g = build_graph(_schema())
    assert g.nodes == {}


def test_single_field_no_neighbors():
    g = build_graph(_schema(_field("user_id")))
    node = g.get("user_id")
    assert node is not None
    assert node.neighbors == []


def test_shared_prefix_creates_edge():
    g = build_graph(_schema(_field("user_id"), _field("user_name")))
    assert "user_name" in g.get("user_id").neighbors
    assert "user_id" in g.get("user_name").neighbors


def test_different_prefix_no_edge():
    g = build_graph(_schema(_field("user_id"), _field("order_id")))
    assert g.get("user_id").neighbors == []
    assert g.get("order_id").neighbors == []


def test_three_fields_same_prefix_all_connected():
    g = build_graph(_schema(_field("evt_type"), _field("evt_ts"), _field("evt_src")))
    assert len(g.get("evt_type").neighbors) == 2
    assert "evt_ts" in g.get("evt_type").neighbors
    assert "evt_src" in g.get("evt_type").neighbors


def test_isolated_fields_returns_no_prefix_match():
    g = build_graph(_schema(_field("user_id"), _field("order_id"), _field("status")))
    iso = isolated_fields(g)
    assert "status" in iso
    assert "user_id" in iso
    assert "order_id" in iso


def test_isolated_fields_excludes_connected():
    g = build_graph(_schema(_field("user_id"), _field("user_name"), _field("ts")))
    iso = isolated_fields(g)
    assert "user_id" not in iso
    assert "user_name" not in iso
    assert "ts" in iso


def test_to_dict_structure():
    g = build_graph(_schema(_field("user_id"), _field("user_name")))
    d = g.to_dict()
    assert "user_id" in d
    assert d["user_id"]["neighbors"] == ["user_name"]


def test_graph_node_str():
    node = GraphNode(field=_field("user_id"), neighbors=["user_name"])
    assert "user_id" in str(node)
    assert "user_name" in str(node)
