"""The FOLLOW window is anchored PER CYCLE, not at the turn's first edit.

HIS RULING, 2026-11-01, verbatim: *"Anchor it per cycle as you suggest. stm"*
and, granting the file, *"Permission is granted. stm"*.

THE DEFECT. `followed` was computed from scans with `i < first`, where `first`
is the turn's FIRST mutation. On any turn running more than 1 FFAFP cycle, every
cycle after the first was UNSATISFIABLE BY CONSTRUCTION, because cycle 2's scan
necessarily sits after cycle 1's edit. It refused 4 times in a row on 2026-10-18
on turns that had each done the tracing it asked for, and twice more in the turn
that repaired it -- including once immediately after a tree scan and 154 passing
tests, both of which it could not see.

WHY THAT MATTERS RATHER THAN BEING MERELY ANNOYING. A gate that cannot be
satisfied stops carrying information: the only way past it is to ignore it, and
once it is ignored a REAL refusal is ignored with it.

WHAT IS NOT RELAXED, which is the half that keeps the gate worth having. A scan
must still PRECEDE the edit to the file it names. The only change is that an
earlier file's edit no longer closes the window on a later file's cycle.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
AUDIT = REPO / "hooks" / "ffafp_audit.py"


@pytest.fixture(scope="module")
def fa():
    spec = importlib.util.spec_from_file_location("_fa_percycle", AUDIT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _turn(fa, calls):
    t = fa.new_turn("u", "2026-11-01T22:00:00.000Z", "p")
    for name, inp in calls:
        fa.record_tool(t, name, inp)
    return t


GREP_A = ("Grep", {"pattern": "reference_runner_v3"})
EDIT_A = ("Edit", {"file_path": "bench/reference_runner_v3.py"})
GREP_B = ("Grep", {"pattern": "immune_agents"})
EDIT_B = ("Edit", {"file_path": "bench/immune_agents.py"})
TESTS = ("Bash", {"command": "python3 -m pytest bench/tests/ -q"})


class TestTheSecondCycleIsSatisfiable:

    #: THE ONLY CYCLE WITH A TRACE IS THE SECOND ONE. `followed` is an `any`
    #: over the changed paths, so a turn whose FIRST cycle is traced passes
    #: under either anchor and demonstrates nothing. My first version of this
    #: test did exactly that and passed while `mut_first` was EMPTY on every
    #: live turn, which is how a repair that reached nothing looked green.
    SECOND_CYCLE_ONLY = [EDIT_A, GREP_B, EDIT_B, TESTS]

    def test_a_second_cycle_scan_after_the_first_edit_now_counts(self, fa):
        """THE REGRESSION. A is edited with no trace; B is then scanned and edited.

        Under the turn-global anchor the window ends at A's edit, so B's scan is
        discarded and FOLLOW is reported missing on a turn that did trace B.
        """
        v = fa.audit(_turn(fa, self.SECOND_CYCLE_ONLY))
        assert v["followed"] is True, v
        assert "FOLLOW" not in (v.get("missing") or []), v

    def test_the_turn_global_anchor_would_have_FAILED_that(self, fa):
        """ANTI-VACUITY, recomputing the OLD rule on the SAME turn.

        If this ever passes a turn the new rule also passes, the pair above
        proves nothing about the repair.
        """
        t = _turn(fa, self.SECOND_CYCLE_ONLY)
        first = t["first_mut"]
        scans = t.get("scans") or []
        old_text = " ".join(s for i, s in scans if first is None or i < first)
        old_followed = any(b in old_text for b in ("immune_agents",
                                                   "reference_runner_v3"))
        assert old_followed is False, (
            f"the old turn-global window saw {old_text!r}, so this turn does "
            f"not discriminate the 2 anchors")

    def test_the_anchor_is_actually_populated_on_this_turn(self, fa):
        """The repair must REACH the audit, not sit behind an empty fallback."""
        t = _turn(fa, self.SECOND_CYCLE_ONLY)
        assert t["mut_first"], (
            "mut_first is empty, so every path falls back to the turn-global "
            "anchor and the per-cycle repair reaches nothing")
        assert t["mut_first"]["bench/immune_agents.py"] > t["first_mut"], t["mut_first"]


class TestNothingIsRelaxedWithinACycle:

    def test_a_scan_AFTER_its_own_edit_still_does_not_count(self, fa):
        """The direction that must stay refused: edit first, scan afterwards."""
        v = fa.audit(_turn(fa, [EDIT_B, GREP_B, TESTS]))
        assert v["followed"] is False, v
        assert "FOLLOW" in (v.get("missing") or []), v

    def test_a_turn_that_scans_for_nothing_still_fails(self, fa):
        v = fa.audit(_turn(fa, [("Read", {"file_path": "bench/immune_agents.py"}),
                                EDIT_B, TESTS]))
        assert v["followed"] is False, v
        assert "FOLLOW" in (v.get("missing") or []), v

    def test_a_scan_for_an_unrelated_name_does_not_count(self, fa):
        v = fa.audit(_turn(fa, [("Grep", {"pattern": "totally_unrelated_xyz"}),
                                EDIT_B, TESTS]))
        assert v["followed"] is False, v


class TestTheAnchorIsRecordedAndSurvivesLegacyState:

    def test_the_per_path_anchor_is_recorded(self, fa):
        t = _turn(fa, [GREP_A, EDIT_A, TESTS, GREP_B, EDIT_B])
        assert t["mut_first"]["bench/reference_runner_v3.py"] == 1, t["mut_first"]
        assert t["mut_first"]["bench/immune_agents.py"] == 4, t["mut_first"]
        assert t["first_mut"] == 1, t["first_mut"]

    def test_setdefault_keeps_the_FIRST_edit_of_a_path(self, fa):
        """A file edited twice anchors on its first edit, not its last."""
        t = _turn(fa, [GREP_B, EDIT_B, EDIT_B])
        assert t["mut_first"]["bench/immune_agents.py"] == 1, t["mut_first"]

    def test_a_legacy_turn_without_the_key_still_audits(self, fa):
        """A state file written before 2026-11-01 has no `mut_first`.

        It must fall back to the turn-global anchor rather than raise, or the
        gate traps every session until the state file rolls over.
        """
        t = _turn(fa, [GREP_B, EDIT_B, TESTS])
        legacy = {k: v for k, v in t.items() if k != "mut_first"}
        v = fa.audit(legacy)
        assert v["followed"] is True, v
