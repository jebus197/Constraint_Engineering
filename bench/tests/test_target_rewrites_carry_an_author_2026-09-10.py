"""Task 6.6: a target rewrite must record WHO, not only WHAT.

THE DEFECT. The 2026-09-08 watch recorded 12 rewrites of `bench/dm/_memory.py`
like this:

    NEW target state 4 at 07:15:49: blob 1ded5f0a, 21046 bytes (+441 vs HEAD)

Every one is unattributable. A blob hash says what changed and nothing about who
changed it, and `target_hash_event` returned exactly 2 hashes and no context.
Task R6 then had to report the blast radius with the actor column empty.

NAMING THE WRITING PROCESS NEEDS ROOT and is not attempted. On macOS that means
`fs_usage` or `dtrace`, which is the founder's to grant. What was free, and was
simply never collected, narrows "someone" to a short list:

  * the SEATS IN FLIGHT at the instant of detection, each with how long it had
    been running -- a seat that started after the write cannot have made it, and
    a stale registration is visible as stale rather than passing as current;
  * the file's own `stat`: the writing UID, the mode, and the MTIME, which dates
    the write independently of when the check noticed it;
  * the pid and thread doing the noticing, so a runner-side write is
    distinguishable from a seat-side one.

WIRED, NOT MERELY ADDED. `seat_in_flight` is called at the top of
`_dispatch_single_model`, and `target_attribution` at the integrity-warning site,
where the record is attached to the event. An addition nothing reaches is not
additive, and this file asserts both call sites by AST rather than by grep.

IT CHANGES NO PROMPT, NO VERDICT AND NO GATE. It records more at a moment where
the record was blank, so it does not invalidate replay of archived runs the way
the parked composer findings would.
"""
from __future__ import annotations

import ast
import os
import pathlib
import sys
import threading

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))
sys.path.insert(0, str(ROOT))

import reference_runner_v3 as rr  # noqa: E402

RUNNER = ROOT / "bench" / "reference_runner_v3.py"


@pytest.fixture(autouse=True)
def _clean_registry():
    rr.seat_done("")
    with rr._SEATS_LOCK:
        rr._SEATS_IN_FLIGHT.clear()
    yield
    with rr._SEATS_LOCK:
        rr._SEATS_IN_FLIGHT.clear()


class TestTheRecordNamesCandidates:
    def test_a_dispatching_seat_appears_in_flight(self):
        assert rr.seats_in_flight() == []
        rr.seat_in_flight("CC2")
        seats = rr.seats_in_flight()
        assert [s["label"] for s in seats] == ["CC2"]
        assert seats[0]["running_for_s"] >= 0.0
        rr.seat_done("CC2")
        assert rr.seats_in_flight() == []

    def test_several_threads_are_all_recorded(self):
        """The point of the record: a rewrite has a CANDIDATE SET, not a name."""
        done = threading.Event()
        started = []

        def worker(label):
            rr.seat_in_flight(label)
            started.append(label)
            done.wait(timeout=5)

        threads = [threading.Thread(target=worker, args=(l,))
                   for l in ("CC2", "Codex", "Gemini")]
        for t in threads:
            t.start()
        while len(started) < 3:
            pass
        labels = {s["label"] for s in rr.seats_in_flight()}
        done.set()
        for t in threads:
            t.join(timeout=5)
        assert labels == {"CC2", "Codex", "Gemini"}, labels

    def test_staleness_is_visible_rather_than_hidden(self):
        """A registration carries its age, so an old one cannot pass as current."""
        rr.seat_in_flight("CC2")
        s = rr.seats_in_flight()[0]
        assert "running_for_s" in s and isinstance(s["running_for_s"], float)


class TestTheFileEvidence:
    def test_it_records_uid_mode_and_mtime(self):
        rec = rr.target_attribution(ROOT / "bench" / "dm" / "_memory.py")
        assert rec["file"]["uid"] == os.getuid()
        assert rec["file"]["mode"].startswith("0o")
        assert "mtime" in rec["file"] and "mtime_epoch" in rec["file"]
        assert rec["file"]["size"] > 0

    def test_it_names_the_noticing_process_and_thread(self):
        rec = rr.target_attribution(ROOT / "bench" / "dm" / "_memory.py")
        assert rec["noticed_by_pid"] == os.getpid()
        assert rec["noticed_on_thread"] == threading.current_thread().name

    def test_it_says_what_it_cannot_know(self):
        """An instrument that is silent about its limit invites over-reading."""
        rec = rr.target_attribution(ROOT / "bench" / "dm" / "_memory.py")
        assert "root" in rec["root_needed_for_more"]

    def test_a_missing_file_is_reported_not_raised(self):
        """An attribution instrument that raises would be read as 'nothing to
        report' rather than 'the instrument broke'."""
        rec = rr.target_attribution(ROOT / "no" / "such" / "file.py")
        assert "file_error" in rec, rec
        assert "seats_in_flight" in rec, "the rest of the record was lost too"


class TestItIsActuallyWired:
    """AST, not grep. An addition nothing reaches is not additive."""

    def test_both_functions_have_call_sites_in_the_runner(self):
        tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
        called = {n.func.id for n in ast.walk(tree)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        assert "seat_in_flight" in called, (
            "no seat registers itself, so the candidate set is always empty")
        assert "target_attribution" in called, (
            "the attribution record is never taken, so the event stays blank")

    def test_the_record_is_attached_to_the_integrity_event(self):
        src = RUNNER.read_text(encoding="utf-8")
        assert '"attribution": _attrib' in src, (
            "the record is computed and discarded, which is worse than not "
            "computing it")
