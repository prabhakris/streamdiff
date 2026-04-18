"""Tests for streamdiff.baseline."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.baseline import compare_to_baseline, latest_snapshot
from streamdiff.snapshot import save_snapshot


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*field_names: str) -> StreamSchema:
    return StreamSchema(name="orders", fields=[_field(n) for n in field_names])


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def test_compare_no_snapshot_returns_not_found(tmp_dir):
    current = _schema("id", "amount")
    result = compare_to_baseline(current, "orders_v1", tmp_dir)
    assert not result.found
    assert result.baseline_name == "orders_v1"


def test_compare_no_snapshot_diff_shows_all_added(tmp_dir):
    current = _schema("id", "amount")
    result = compare_to_baseline(current, "orders_v1", tmp_dir)
    added = [c for c in result.diff.changes if c.change_type.name == "ADDED"]
    assert len(added) == 2


def test_compare_with_matching_snapshot_no_changes(tmp_dir):
    schema = _schema("id", "amount")
    save_snapshot(schema, "orders_v1", tmp_dir)
    result = compare_to_baseline(schema, "orders_v1", tmp_dir)
    assert result.found
    assert result.diff.changes == []


def test_compare_detects_added_field(tmp_dir):
    old = _schema("id")
    new = _schema("id", "amount")
    save_snapshot(old, "orders_v1", tmp_dir)
    result = compare_to_baseline(new, "orders_v1", tmp_dir)
    assert result.found
    assert len(result.diff.changes) == 1
    assert result.diff.changes[0].field_name == "amount"


def test_latest_snapshot_none_when_empty(tmp_dir):
    assert latest_snapshot("orders", tmp_dir) is None


def test_latest_snapshot_returns_most_recent(tmp_dir):
    schema = _schema("id")
    save_snapshot(schema, "orders_v1", tmp_dir)
    save_snapshot(schema, "orders_v2", tmp_dir)
    name = latest_snapshot("orders", tmp_dir)
    assert name == "orders_v2"
