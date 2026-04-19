"""Tests for streamdiff.auditor."""
import pytest
from streamdiff.auditor import AuditEntry, record_entry, load_entries, clear_audit


@pytest.fixture()
def audit_dir(tmp_path):
    return str(tmp_path / "audit")


def test_record_creates_entry(audit_dir):
    entry = record_entry("old.json", "new.json", False, 2, audit_dir=audit_dir, user="ci")
    assert isinstance(entry, AuditEntry)
    assert entry.user == "ci"
    assert entry.breaking is False
    assert entry.change_count == 2


def test_record_persists(audit_dir):
    record_entry("a.json", "b.json", True, 3, audit_dir=audit_dir, user="alice")
    entries = load_entries(audit_dir=audit_dir)
    assert len(entries) == 1
    assert entries[0].breaking is True
    assert entries[0].user == "alice"


def test_multiple_entries(audit_dir):
    record_entry("a.json", "b.json", False, 1, audit_dir=audit_dir)
    record_entry("b.json", "c.json", True, 4, audit_dir=audit_dir)
    entries = load_entries(audit_dir=audit_dir)
    assert len(entries) == 2


def test_load_empty_returns_empty(audit_dir):
    entries = load_entries(audit_dir=audit_dir)
    assert entries == []


def test_clear_removes_entries(audit_dir):
    record_entry("a.json", "b.json", False, 0, audit_dir=audit_dir)
    clear_audit(audit_dir=audit_dir)
    assert load_entries(audit_dir=audit_dir) == []


def test_tags_stored(audit_dir):
    record_entry("a.json", "b.json", False, 1, audit_dir=audit_dir, tags=["release", "v2"])
    entries = load_entries(audit_dir=audit_dir)
    assert entries[0].tags == ["release", "v2"]


def test_str_breaking(audit_dir):
    entry = record_entry("a.json", "b.json", True, 5, audit_dir=audit_dir, user="bob")
    assert "[BREAKING]" in str(entry)


def test_str_not_breaking(audit_dir):
    entry = record_entry("a.json", "b.json", False, 1, audit_dir=audit_dir, user="bob")
    assert "[BREAKING]" not in str(entry)


def test_to_dict_keys(audit_dir):
    entry = record_entry("a.json", "b.json", False, 0, audit_dir=audit_dir)
    d = entry.to_dict()
    for key in ("timestamp", "user", "old_schema", "new_schema", "breaking", "change_count", "tags"):
        assert key in d
