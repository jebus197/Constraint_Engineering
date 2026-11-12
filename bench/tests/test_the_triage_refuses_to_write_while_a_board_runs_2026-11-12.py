#!/usr/bin/env python3
"""B155: the triage script must not write to the tree while a commit board runs.

★ THIS IS A LIVE DEFECT THAT FIRED 5 TIMES IN ONE NIGHT. `hooks/work_not_narrate.py`
refuses a stop and names its own remedy: "If something genuinely prevents
progress, classify it first: python3 scripts/blocker_triage.py --title ...".
On 2026-11-12 the obstacle BEING reported was that a commit board was mid-pytest
and no file in the tree could be edited. Running the named remedy APPENDED a
section to experimental_notes/PARKED_FOR_THE_FOUNDER.md -- a file in the tree --
27 minutes into that board.

★ WHY IT IS NOT COSMETIC. 3 of that board's 259 test files read that path, and
`test_the_parked_file_regenerates_without_losing_him_2026-10-17.py` reads the
live file at one instant, copies it at a later one, and asserts the count of
`## ` headings is equal across the 2. The append took that count from 72 to 73,
failing the assertion on a tree that is otherwise correct: a TIMING ARTEFACT
INDISTINGUISHABLE FROM A DEFECT.

★ WHY THE WRITER AND NOT THE GATE. 2 repairs were available: the gate checks for
a live board before naming a writer, or the writer refuses while one runs. The
2nd is simpler and closer to the fault -- the writer KNOWS it is writing, the
gate does not. Composing both is NOT recommended without a measurement showing
the pair dominates either alone, which is this project's own standard for
composability. With the writer fixed, following the gate's advice during a board
becomes merely useless rather than damaging, so the single fix removes the harm
at the point of harm.

★ EVERY CASE DRIVES A TEMPORARY TARGET. If a predicate here regressed and the
test wrote to the real queue, the test itself would reproduce the defect it
exists to prevent.

Costs nothing: writes only into pytest's own temporary directory, dispatches to
no model, runs no pytest of its own.
"""
from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "blocker_triage.py"
REAL_QUEUE = REPO / "experimental_notes" / "PARKED_FOR_THE_FOUNDER.md"
SEAM = "CDSFL_BT_BOARD"
DETAIL = "detail long enough to satisfy the detail check and say what this is"


@pytest.fixture
def bt(tmp_path, monkeypatch):
    """A fresh module whose write target is a temp file, never the real queue."""
    assert SCRIPT.is_file(), f"the triage script is missing: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("bt_guard", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["bt_guard"] = m
    spec.loader.exec_module(m)
    monkeypatch.setattr(m, "PARKED", tmp_path / "PARKED.md")
    return m


class TestItRefusesWhileABoardRuns:
    def test_park_raises_instead_of_writing(self, bt, monkeypatch):
        monkeypatch.setenv(SEAM, "1")
        with pytest.raises(bt.BoardIsRunning):
            bt.park("a probe", DETAIL)
        assert not bt.PARKED.exists(), (
            "park() created its target before refusing, so the refusal is after "
            "the write and the defect is not closed")

    def test_an_existing_queue_is_not_appended_to(self, bt, monkeypatch):
        """The real defect was an APPEND to a file that already existed."""
        bt.PARKED.write_text("# queue\n\n## an existing heading\n", encoding="utf-8")
        before = hashlib.sha256(bt.PARKED.read_bytes()).hexdigest()
        monkeypatch.setenv(SEAM, "1")
        with pytest.raises(bt.BoardIsRunning):
            bt.park("a probe", DETAIL)
        assert hashlib.sha256(bt.PARKED.read_bytes()).hexdigest() == before


class TestItDoesNotOverRefuse:
    def test_it_writes_normally_when_no_board_runs(self, bt, monkeypatch):
        """★ THE FALSIFIER. A predicate that always reported a board would pass
        every test above while breaking the script entirely."""
        monkeypatch.setenv(SEAM, "0")
        out = bt.park("a probe", DETAIL)
        assert out is not None and bt.PARKED.exists(), (
            "the triage can no longer park anything, which is worse than the "
            "defect it was written to close")

    def test_the_predicate_is_empty_when_the_seam_forces_no_board(self, bt, monkeypatch):
        monkeypatch.setenv(SEAM, "0")
        assert bt.a_commit_board_is_running() == ""


class TestTheDetectorItself:
    def test_it_excludes_shells(self):
        """★ REUSED, NOT REWRITTEN. `pgrep -f` matches the WHOLE command line, so
        a shell whose ARGUMENTS merely name the runner reads as a live board.
        Measured against a real board on 2026-11-12: a raw pgrep returned 4 pids
        of which 3 were shells. `hooks/cy_monitor_gate.py` already carries this
        exclusion, corrected on his 2026-11-08 ruling, and a 2nd matcher would
        be the producer-consumer divergence this project keeps meeting."""
        src = SCRIPT.read_text(encoding="utf-8")
        assert "cy_monitor_gate" in src, (
            "the board detector does not reuse the corrected shell exclusion")
        assert "_is_shell" in src

    def test_it_fails_safe_toward_writing(self, bt, monkeypatch):
        """A broken detector must cost the PROTECTION, never the triage: refusing
        to classify because the detector died is worse than the defect."""
        monkeypatch.delenv(SEAM, raising=False)
        monkeypatch.setattr(bt, "REPO", pathlib.Path("/nonexistent-for-this-test"))
        assert bt.a_commit_board_is_running() == ""


class TestTheRealQueueIsNeverTouchedByThisFile:
    def test_the_live_queue_is_unchanged(self, bt, monkeypatch):
        before = hashlib.sha256(REAL_QUEUE.read_bytes()).hexdigest() \
            if REAL_QUEUE.is_file() else None
        monkeypatch.setenv(SEAM, "0")
        bt.park("a probe", DETAIL)
        after = hashlib.sha256(REAL_QUEUE.read_bytes()).hexdigest() \
            if REAL_QUEUE.is_file() else None
        assert before == after, "this guard wrote to the real queue"
