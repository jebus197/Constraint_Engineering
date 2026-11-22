#!/usr/bin/env python3
"""The cy gate's anti-trap budget must bind for EVERY run, watched or not.

DRAFTED 2026-11-22; destination `bench/tests/`. **SAFE for the `GUARDS` list
BECAUSE the 2 known-failing cases are `xfail(strict=True)`, not bare failures --
the first draft said "onto the GUARDS list" while 2 tests were RED, which would
have refused EVERY commit until the repair landed.** Held in the scratchpad
until the batch-2 board finishes, because the board reads the tree.

GUARDS: `hooks/cy_monitor_gate.py` -- `spend()` and the key `main()` builds.
PRODUCER: `scripts/the_cy_refusal_budget_never_binds_2026-11-22.py`.

★ ENTRY B209. `MAX_REFUSALS = 60` is an ANTI-TRAP SAFEGUARD: on exhaustion the
gate prints *"Allowing the stop so a session cannot be trapped."* The key is
`session_id + "|" + str(sorted(run dirs) or pids)`, and `spend()` zeroes the
count whenever the key changes. With no WATCHED run the key falls back to the
live pid list, a commit board replaces its pytest child per guard file, so the
key moves and the counter resets. **So the safeguard is inert for precisely the
runs the gate cannot read, which is the only case where a trap is possible.**

★ THE 2 UNWATCHED CASES ARE `xfail(strict=True)`, AND THE STRICTNESS IS THE
WHOLE DEVICE. They record the defect as it stands, so the suite is honest rather
than green-by-omission; and because `strict=True` turns an unexpected PASS into a
FAILURE, the day the key is repaired this file goes red and forces the markers
off. A plain `xfail` would have let the repair land with the markers still on,
leaving 2 tests permanently excused -- which is how a known-failing case becomes
a silently disabled one.

They are committed BEFORE the repair deliberately: a guard written after its fix
can only confirm what its author already believed. Neither candidate repair is
chosen here, because these assert the PROPERTY (the budget binds) and not the
MECHANISM (which key) -- so whichever of B209's 2 options is taken, this file
judges it.

**IF A FUTURE READER FINDS THESE XPASSING: the defect is fixed. Remove the
markers; do not weaken the assertions.**

★ IT TOUCHES NOTHING LIVE. Every case overrides `CDSFL_CY_STATE` to a `tmp_path`
and asserts the override is in force before spending, because a probe that
spent the real session's budget while measuring it would corrupt the thing it
measures -- and the gate is a LIVE Stop hook sharing an inode with its
repository copy.
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import sys

import pytest


#: ★ THE FALLBACK IS NOT DECORATION. Drafted without it and copied to a scratch
#: path to be exercised before promotion, `_find_repo` raised `SystemExit` AT
#: IMPORT, which pytest escalates to INTERNALERROR -- "no tests ran" rather than
#: a legible failure. A guard that cannot be run anywhere but its destination
#: cannot be tested BEFORE it reaches its destination, which is the whole point
#: of drafting it outside the tree. The sibling producer already carried this
#: fallback and this file did not, which is the inconsistency that surfaced it.
def _find_repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for cand in [here.parent, *here.parents]:
        if (cand / "hooks").is_dir() and (cand / "bench" / "tests").is_dir():
            return cand
    fb = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
    if (fb / "hooks").is_dir() and (fb / "bench" / "tests").is_dir():
        return fb
    raise SystemExit(
        "cannot locate the repository from " + str(here))


REPO = _find_repo()
#: ★ A SEAM, matching the sibling producer's. It exists so the STRICTNESS of the
#: xfail markers below can be PROVED against a repaired gate without editing the
#: live one -- `strict=True` is only worth having if an unexpected pass really
#: does fail, and that is a claim about pytest's behaviour in THIS file, not a
#: fact to assume. Default is the real hook, so a normal run guards the real
#: thing.
GATE = pathlib.Path(os.environ.get("CDSFL_CY_GATE_PATH")
                    or REPO / "hooks" / "cy_monitor_gate.py")

#: The shape a board produces, taken from the live board of 2026-11-22 rather
#: than invented: 1 long-lived process, and a child replaced per guard file.
CHURNING = [["70507"], ["70507", "76042"], ["70507", "77353"],
            ["70507", "78785"], ["70507", "79475"]]


@pytest.fixture
def gate(tmp_path, monkeypatch):
    """The real hook, with its state file pointed at a throwaway path."""
    monkeypatch.setenv("CDSFL_CY_STATE", str(tmp_path / "state.json"))
    spec = importlib.util.spec_from_file_location("cy_gate_under_test", GATE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["cy_gate_under_test"] = m
    spec.loader.exec_module(m)
    assert str(m.state_path()).startswith(str(tmp_path)), (
        f"the CDSFL_CY_STATE override is not in force ({m.state_path()}); this "
        f"test would otherwise spend the live session's refusal budget")
    return m


class TestTheWatchedBudgetBinds:
    """The case that already works. Here so the RED below is not vacuous."""

    def test_a_stable_key_climbs(self, gate):
        key = "sess|['bench/logs/run1']"
        assert [gate.spend(key) for _ in range(5)] == [1, 2, 3, 4, 5]

    def test_it_reaches_the_declared_budget(self, gate):
        key = "sess|['bench/logs/run1']"
        n = 0
        for _ in range(gate.MAX_REFUSALS + 1):
            n = gate.spend(key)
        assert n > gate.MAX_REFUSALS, (
            f"a stable key stalled at {n} against a declared budget of "
            f"{gate.MAX_REFUSALS}, so the budget does not bind even when the key "
            f"holds still -- a wider break than B209 describes")


class TestTheUnwatchedBudgetBinds:
    """★ KNOWN-FAILING TODAY, strictly. The regression guard for B209's repair."""

    @pytest.mark.xfail(strict=True, reason="B209: the refusal budget's key falls "
                       "back to a churning pid list for unwatched runs, so the "
                       "counter resets and the 60-refusal anti-trap budget is "
                       "unreachable. STRICT: an XPASS means the key was repaired "
                       "and this marker must come off.")
    def test_a_churning_pid_key_still_climbs(self, gate):
        got = [gate.spend("sess|" + str(p)) for p in CHURNING]
        assert got != [1] * len(CHURNING), (
            "the refusal counter RESET on every poll because the key is derived "
            "from a churning pid list, so the 60-refusal anti-trap budget can "
            "never be reached for an unwatched run. This is B209 and it is the "
            "recorded state: repair the key in hooks/cy_monitor_gate.py, do not "
            "weaken this assertion.")
        assert got == list(range(1, len(CHURNING) + 1)), got

    @pytest.mark.xfail(strict=True, reason="B209: same cause. STRICT, so the "
                       "repair cannot land with this case still excused.")
    def test_an_idle_session_cannot_be_refused_for_ever(self, gate):
        """The property the budget exists for, stated as the property."""
        spent = 0
        for i in range(gate.MAX_REFUSALS * 2):
            pids = ["70507", str(80000 + i)]      # a fresh child every poll
            spent = gate.spend("sess|" + str(pids))
        assert spent > gate.MAX_REFUSALS, (
            f"after {gate.MAX_REFUSALS * 2} refusals of an unwatched run the "
            f"counter stands at {spent}, so the gate would go on refusing for "
            f"ever and an IDLE session is trapped. That is the condition B209 "
            f"names as the real severity.")


class TestTheKeyIsWhereTheDefectLives:
    def test_the_fallback_to_pids_is_what_moves(self, gate):
        """ANTI-VACUITY: pin WHY it resets, so a repair elsewhere cannot pass.

        Driving `spend` alone cannot show that the pid fallback is the cause.
        This asserts the 2 key shapes behave differently under the SAME number
        of polls, which is the discriminating observation.
        """
        stable = [gate.spend("sess|['bench/logs/run1']") for _ in range(5)]
        churn = [gate.spend("sess|" + str(p)) for p in CHURNING]
        assert stable[-1] > churn[-1], (
            f"stable key reached {stable[-1]} and the churning key reached "
            f"{churn[-1]}; if these ever match, either the defect is fixed or "
            f"both arms are broken -- read spend() before believing either")
