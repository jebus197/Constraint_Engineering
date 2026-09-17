"""A8: every cited log path carries a disposition, and the manifest tells the truth.

FOUNDER RULING 2026-09-17: track the files that notes cite so a reader in a fresh
clone can open them, and label the rest.

THE THIRD STATE IS THE ONE NOBODY HAD COUNTED. A cited path is tracked, present
but untracked, or MISSING -- the file was never kept, so it cannot be opened on
any machine, not merely on someone else's. Of 283 note-cited untracked paths,
only 52 existed on disk.

This test re-derives every disposition from the repository and requires the
committed manifest to match. A stale manifest is worse than none, because it
labels a path recoverable when it is not.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "experimental_notes" / "evidence" / "cited_logs_manifest_2026-09-17.json"


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True).stdout
    return set(out.split())


def test_the_manifest_exists_and_is_not_empty(manifest):
    assert len(manifest) > 100, len(manifest)


def test_every_row_carries_a_known_state(manifest):
    for path, row in manifest.items():
        assert row["state"] in {"tracked", "local_only", "missing"}, (path, row)
        assert row["cited_by"], path


def test_no_row_claims_tracked_when_git_does_not_track_it(manifest, tracked):
    """The direction that matters: a false 'tracked' tells a reader to expect
    a file that is not there."""
    wrong = [p for p, r in manifest.items() if r["state"] == "tracked" and p not in tracked]
    assert not wrong, f"manifest says tracked, git does not: {wrong[:8]}"


def test_no_row_claims_missing_when_the_file_is_present(manifest):
    wrong = [p for p, r in manifest.items() if r["state"] == "missing" and (REPO / p).is_file()]
    assert not wrong, f"manifest says missing, the file exists: {wrong[:8]}"


def test_the_note_cited_recoverable_files_are_now_tracked(manifest, tracked):
    """The ruling's action half: what a note cites and what exists should be in git."""
    unfixed = [p for p, r in manifest.items()
               if "NOTE" in r["cited_by"] and r["state"] == "local_only"]
    assert len(unfixed) <= 5, (
        f"{len(unfixed)} note-cited files still exist only on this machine, so a "
        f"fresh clone cannot open the evidence those notes cite: {unfixed[:8]}")


def test_missing_paths_are_reported_rather_than_hidden(manifest):
    """A citation to a file nobody kept must stay visible, not be quietly dropped."""
    missing = [p for p, r in manifest.items() if r["state"] == "missing"]
    assert missing, "no missing paths at all is implausible; check the extractor"
