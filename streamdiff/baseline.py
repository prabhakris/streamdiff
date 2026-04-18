"""Baseline comparison: compare current schema against a saved snapshot baseline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from streamdiff.diff import DiffResult, compute_diff
from streamdiff.snapshot import load_snapshot, list_snapshots, snapshot_path
from streamdiff.schema import StreamSchema


@dataclass
class BaselineResult:
    baseline_name: str
    baseline_path: Path
    diff: DiffResult
    found: bool

    def __bool__(self) -> bool:
        return self.found


def latest_snapshot(stream: str, snapshot_dir: str = ".streamdiff") -> Optional[str]:
    """Return the name of the most recently saved snapshot for a stream."""
    snapshots = list_snapshots(snapshot_dir)
    matches = [s for s in snapshots if s.startswith(stream + "_") or s == stream]
    if not matches:
        return None
    return sorted(matches)[-1]


def compare_to_baseline(
    current: StreamSchema,
    name: str,
    snapshot_dir: str = ".streamdiff",
) -> BaselineResult:
    """Load the named snapshot and diff it against *current*."""
    path = snapshot_path(name, snapshot_dir)
    if not path.exists():
        empty = StreamSchema(name=name, fields=[])
        return BaselineResult(
            baseline_name=name,
            baseline_path=path,
            diff=compute_diff(empty, current),
            found=False,
        )
    baseline: StreamSchema = load_snapshot(name, snapshot_dir)
    return BaselineResult(
        baseline_name=name,
        baseline_path=path,
        diff=compute_diff(baseline, current),
        found=True,
    )
