"""Tests for streamdiff.cli_audit."""
import argparse
import pytest
from streamdiff.cli_audit import add_audit_subparser, handle_audit
from streamdiff.auditor import record_entry


def _parse(args, audit_dir):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    add_audit_subparser(sub)
    ns = parser.parse_args(["audit"] + args)
    ns.audit_dir = audit_dir
    return ns


@pytest.fixture()
def audit_dir(tmp_path):
    return str(tmp_path / "audit")


def test_add_audit_subparser_registers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    add_audit_subparser(sub)
    ns = parser.parse_args(["audit"])
    assert ns.cmd == "audit"


def test_handle_audit_empty(audit_dir, capsys):
    ns = _parse([], audit_dir)
    rc = handle_audit(ns)
    assert rc == 0
    assert "No audit entries" in capsys.readouterr().out


def test_handle_audit_shows_entry(audit_dir, capsys):
    record_entry("a.json", "b.json", False, 1, audit_dir=audit_dir, user="ci")
    ns = _parse([], audit_dir)
    handle_audit(ns)
    out = capsys.readouterr().out
    assert "a.json" in out


def test_handle_audit_json(audit_dir, capsys):
    record_entry("a.json", "b.json", True, 3, audit_dir=audit_dir)
    ns = _parse(["--json"], audit_dir)
    handle_audit(ns)
    import json
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert data[0]["breaking"] is True


def test_handle_audit_only_breaking(audit_dir, capsys):
    record_entry("a.json", "b.json", False, 1, audit_dir=audit_dir)
    record_entry("b.json", "c.json", True, 2, audit_dir=audit_dir)
    ns = _parse(["--only-breaking"], audit_dir)
    handle_audit(ns)
    out = capsys.readouterr().out
    assert "[BREAKING]" in out
    assert out.count("->")==1


def test_handle_audit_clear(audit_dir, capsys):
    record_entry("a.json", "b.json", False, 0, audit_dir=audit_dir)
    ns = _parse(["--clear"], audit_dir)
    rc = handle_audit(ns)
    assert rc == 0
    from streamdiff.auditor import load_entries
    assert load_entries(audit_dir=audit_dir) == []


def test_handle_audit_limit(audit_dir, capsys):
    for i in range(5):
        record_entry(f"{i}.json", f"{i+1}.json", False, i, audit_dir=audit_dir)
    ns = _parse(["--limit", "2"], audit_dir)
    handle_audit(ns)
    out = capsys.readouterr().out
    assert out.count("->") == 2
