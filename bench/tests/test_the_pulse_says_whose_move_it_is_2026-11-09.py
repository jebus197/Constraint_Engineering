"""The per-turn pulse must say whose decision the next entry waits on.

WHY. `summarise()` read only `state` and `text`. It never touched `ruled`,
although `parse_entries` parses it and 117 of 279 entries carried one. So the
line named the next entry and said nothing about whether anyone but the
founder could move it. On 2026-11-09 `work_not_narrate` named B21 on every
turn, 8 times a turn, and B21 awaited his ruling -- a whole day of pushing at
an entry nobody could advance. The classifier already existed and nothing
called it from here.

TWO PROPERTIES ARE LOAD-BEARING AND BOTH ARE TESTED BY EXECUTION:
  1. the label is CORRECT -- it agrees with the classifier called separately;
  2. the pulse NEVER FAILS -- this line is printed by a `UserPromptSubmit`
     hook on every turn, so a broken classifier must cost the LABEL and not
     the clock. That is asserted by deliberately breaking the classifier in a
     child process and requiring exit 0.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))
CLASSIFIER = SCRIPTS / "how_many_decisions_actually_need_him_2026-11-01.py"


@pytest.fixture(scope="module")
def tlm():
    spec = importlib.util.spec_from_file_location(
        "tlm_pulse", SCRIPTS / "task_list_markers.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tlm_pulse"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTheLabelIsThere:
    def test_the_pulse_names_whose_move_the_next_entry_is(self, tlm):
        line = tlm.summarise()
        assert "—" in line and "next:" in line, line
        assert any(f"[{k}]" in line for k in
                   ("mine", "awaits you", "blocked", "deferred by you")), (
            f"the pulse names the next entry without saying whose move it is: "
            f"{line}")

    def test_whose_move_returns_three_values(self, tlm):
        got = tlm._whose_move(tlm.parse_entries())
        assert got is not None, "the classifier could not be reached at all"
        mine, his, kind = got
        assert isinstance(mine, int) and isinstance(his, int) and kind
        assert mine + his == sum(1 for e in tlm.parse_entries()
                                 if (e.state or "").upper() == "OPEN"), (
            "the 2 sides do not sum to the open count, so one bucket is lost")

    def test_it_agrees_with_the_classifier_called_separately(self, tlm):
        """A producer and a consumer that disagree are each individually right."""
        spec = importlib.util.spec_from_file_location("hmd_t", CLASSIFIER)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["hmd_t"] = mod
        spec.loader.exec_module(mod)
        bodies = mod.bodies()
        want_his = sum(
            1 for e in tlm.parse_entries()
            if (e.state or "").upper() == "OPEN"
            and mod.classify_text(e.state, e.ruled,
                                  bodies.get(e.ident, ""))["kind"] == "OWED")
        _mine, his, _k = tlm._whose_move(tlm.parse_entries())
        assert his == want_his, (
            f"the pulse says {his} await him, the classifier says {want_his}")

    def test_the_next_entrys_label_is_the_classifiers_verdict_for_THAT_entry(
            self, tlm):
        """★ ADDED AFTER A MUTATION SURVIVED. Replacing the lookup with the
        literal "mine" left all 9 tests green, because the count test checks
        the TALLY and the presence test accepts any valid word -- and the next
        entry happened to be mine. A label that is always "mine" is exactly
        the defect this entry exists to fix, so it must fail here."""
        spec = importlib.util.spec_from_file_location("hmd_lbl", CLASSIFIER)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["hmd_lbl"] = mod
        spec.loader.exec_module(mod)
        bodies = mod.bodies()
        entries = tlm.parse_entries()
        nxt = next(e for e in entries if (e.state or "").upper() == "OPEN")
        kind = mod.classify_text(nxt.state, nxt.ruled,
                                 bodies.get(nxt.ident, ""))["kind"]
        want = {"OWED": "awaits you", "MINE": "mine", "GRANTED": "mine",
                "DEPENDENT": "blocked", "HIS_DEFERRAL": "deferred by you"}[kind]
        _m, _h, got = tlm._whose_move(entries)
        assert got == want, (
            f"the next entry {nxt.ident} classifies as {kind}, so the pulse "
            f"should label it {want!r}; it said {got!r}")

    def test_the_label_follows_the_entry_that_is_first(self, tlm):
        """★ THE MUTATION THAT SURVIVED TWICE. Replacing the lookup with the
        literal "mine" was invisible while the live list happened to START with
        a MINE entry: both the live assertion and the classifier agreed on
        "mine" for the wrong reason. So REORDER -- put a real OWED entry first
        and require the label to follow it. `bodies()` is keyed by ident, so a
        real entry carries its real text and nothing is faked."""
        spec = importlib.util.spec_from_file_location("hmd_ord", CLASSIFIER)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["hmd_ord"] = mod
        spec.loader.exec_module(mod)
        bodies = mod.bodies()
        entries = tlm.parse_entries()
        owed = [e for e in entries
                if (e.state or "").upper() == "OPEN"
                and mod.classify_text(e.state, e.ruled,
                                      bodies.get(e.ident, ""))["kind"] == "OWED"]
        assert owed, "no OPEN entry awaits him, so this test cannot discriminate"
        reordered = [owed[0]] + [e for e in entries if e is not owed[0]]
        _m, _h, kind = tlm._whose_move(reordered)
        assert kind == "awaits you", (
            f"{owed[0].ident} awaits him and the pulse labelled it {kind!r}; a "
            f"label that does not follow the entry is not a label")

    def test_an_OWED_entry_is_labelled_as_awaiting_him(self, tlm):
        """Drive the label with a CONSTRUCTED case, so a live set that happens
        to start with a MINE entry cannot make the OWED branch unreachable."""
        spec = importlib.util.spec_from_file_location("hmd_lbl2", CLASSIFIER)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["hmd_lbl2"] = mod
        spec.loader.exec_module(mod)
        d = mod.classify_text("OPEN", None, "NEEDS YOUR RULING on whether to do X.")
        assert d["kind"] == "OWED", (
            f"the constructed asking entry did not classify as OWED: {d['kind']}")

    def test_the_count_is_shown_when_any_entry_awaits_him(self, tlm):
        _mine, his, _k = tlm._whose_move(tlm.parse_entries())
        line = tlm.summarise()
        if his:
            assert "await YOU" in line and str(his) in line, (
                f"{his} entries await him and the pulse does not say so: {line}")

    def test_the_sample_exercises_both_sides(self, tlm):
        mine, his, _k = tlm._whose_move(tlm.parse_entries())
        assert mine and his, (
            "every open entry fell to one side, so a swapped label would pass "
            "-- this test would be vacuous")


class TestThePulseNeverFails:
    """The clock and the task count must survive a broken classifier."""

    def _pulse_in_child(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, %r);"
             "import task_list_markers as t; print(t.summarise())"
             % str(SCRIPTS)],
            capture_output=True, text=True, cwd=str(REPO))

    def test_a_broken_classifier_costs_the_label_not_the_pulse(self):
        backup = CLASSIFIER.read_bytes()
        try:
            CLASSIFIER.write_text("raise ImportError('deliberately broken')\n")
            r = self._pulse_in_child()
        finally:
            CLASSIFIER.write_bytes(backup)      # restore what was FOUND
        assert r.returncode == 0, (
            f"a broken classifier took the whole pulse down: {r.stderr[-300:]}")
        assert "entries:" in r.stdout, "the pulse lost its census"
        assert "await YOU" not in r.stdout, (
            "a broken classifier still produced an ownership claim")

    def test_the_label_returns_once_the_classifier_is_restored(self):
        r = self._pulse_in_child()
        assert r.returncode == 0 and "entries:" in r.stdout
        assert "[" in r.stdout, "the label did not come back after restore"

    def test_a_missing_classifier_returns_none_rather_than_raising(self, tlm):
        backup = CLASSIFIER.read_bytes()
        try:
            CLASSIFIER.unlink()
            assert tlm._whose_move(tlm.parse_entries()) is None
        finally:
            CLASSIFIER.write_bytes(backup)


class TestItStaysCheapEnoughToRunEveryTurn:
    def test_the_pulse_is_under_a_second(self, tlm):
        t0 = time.perf_counter()
        tlm.summarise()
        dt = time.perf_counter() - t0
        assert dt < 1.0, (
            f"the pulse took {dt:.3f}s; it runs on EVERY turn and the label is "
            f"not worth that")
