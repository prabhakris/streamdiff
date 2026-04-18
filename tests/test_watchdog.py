import json
import time
from pathlib import Path

import pytest

from streamdiff.watchdog import WatchConfig, WatchEvent, watch


def _write_schema(path: Path, fields):
    schema = {"name": "test", "fields": fields}
    path.write_text(json.dumps(schema))


@pytest.fixture
def schema_file(tmp_path):
    p = tmp_path / "schema.json"
    _write_schema(p, [{"name": "id", "type": "string", "required": True}])
    return p


def test_no_change_no_callback(schema_file, monkeypatch):
    calls = []
    monkeypatch.setattr(time, "sleep", lambda _: None)

    cfg = WatchConfig(
        schema_path=str(schema_file),
        interval=0,
        max_iterations=2,
        on_change=lambda e: calls.append(e),
    )
    watch(cfg)
    assert calls == []


def test_change_triggers_on_change(schema_file, monkeypatch):
    calls = []
    iteration = [0]

    def fake_sleep(_):
        iteration[0] += 1
        if iteration[0] == 1:
            _write_schema(
                schema_file,
                [
                    {"name": "id", "type": "string", "required": True},
                    {"name": "name", "type": "string", "required": False},
                ],
            )

    monkeypatch.setattr(time, "sleep", fake_sleep)
    cfg = WatchConfig(
        schema_path=str(schema_file),
        interval=0,
        max_iterations=2,
        on_change=lambda e: calls.append(e),
    )
    watch(cfg)
    assert len(calls) == 1
    assert calls[0].iteration == 1


def test_breaking_change_triggers_on_breaking(schema_file, monkeypatch):
    breaking = []
    iteration = [0]

    def fake_sleep(_):
        iteration[0] += 1
        if iteration[0] == 1:
            _write_schema(schema_file, [])

    monkeypatch.setattr(time, "sleep", fake_sleep)
    cfg = WatchConfig(
        schema_path=str(schema_file),
        interval=0,
        max_iterations=2,
        on_breaking=lambda e: breaking.append(e),
    )
    watch(cfg)
    assert len(breaking) == 1


def test_load_error_is_skipped(schema_file, monkeypatch):
    calls = []
    iteration = [0]

    def fake_sleep(_):
        iteration[0] += 1
        if iteration[0] == 1:
            schema_file.write_text("not json")

    monkeypatch.setattr(time, "sleep", fake_sleep)
    cfg = WatchConfig(
        schema_path=str(schema_file),
        interval=0,
        max_iterations=2,
        on_change=lambda e: calls.append(e),
    )
    watch(cfg)
    assert calls == []
