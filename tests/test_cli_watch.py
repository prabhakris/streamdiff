import argparse
import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from streamdiff.cli_watch import add_watch_subparser, handle_watch


def _parse(args):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_watch_subparser(sub)
    return parser.parse_args(args)


def _write(path, fields):
    path.write_text(json.dumps({"name": "s", "fields": fields}))


def test_add_watch_subparser_defaults():
    ns = _parse(["watch", "schema.json"])
    assert ns.interval == 5.0
    assert ns.watch_format == "text"
    assert ns.break_on_breaking is False


def test_add_watch_subparser_custom():
    ns = _parse(["watch", "schema.json", "--interval", "2", "--format", "json"])
    assert ns.interval == 2.0
    assert ns.watch_format == "json"


def test_handle_watch_returns_zero(tmp_path, monkeypatch):
    p = tmp_path / "s.json"
    _write(p, [{"name": "id", "type": "string", "required": True}])

    monkeypatch.setattr(time, "sleep", lambda _: None)

    ns = _parse(["watch", str(p), "--interval", "0"])
    # Limit iterations via max_iterations by patching WatchConfig
    from streamdiff import cli_watch
    original_watch = cli_watch.watch

    def limited_watch(cfg):
        cfg.max_iterations = 0
        original_watch(cfg)

    monkeypatch.setattr(cli_watch, "watch", limited_watch)
    code = handle_watch(ns)
    assert code == 0


def test_handle_watch_keyboard_interrupt(tmp_path, monkeypatch):
    p = tmp_path / "s.json"
    _write(p, [])

    from streamdiff import cli_watch

    monkeypatch.setattr(cli_watch, "watch", lambda cfg: (_ for _ in ()).throw(KeyboardInterrupt()))
    ns = _parse(["watch", str(p)])
    code = handle_watch(ns)
    assert code == 0
