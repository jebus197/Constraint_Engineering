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


class TestSpendResetsWhenItsKeyChanges:
    """`spend()`'s reset mechanism, which is NOT a test of B209's candidates.

    ★ THESE WERE WRITTEN AS A CONDITION-2 DISCRIMINATOR AND THEY ARE NOT ONE.
    THE CORRECTION IS RECORDED HERE RATHER THAN QUIETLY MADE. The claim was
    that they go RED under candidate (a), keying the refusal counter on the
    session id alone. **Driven against a real mutant of `hooks/cy_monitor_gate.py`
    whose `main()` builds a constant key, this class PASSES: the first period
    exhausts at 61 and the next opens at 1.** The earlier "verification" drove
    `spend("sess")` with a constant key BY HAND, which is a different test from
    the one written here.

    ★ WHY IT CANNOT DISCRIMINATE, AND THE REASON GENERALISES TO ALL 3
    CONDITIONS. `spend(key)` is KEY-AGNOSTIC: it resets whenever the key it is
    GIVEN differs from the stored one. Every candidate repair changes the KEY
    CONSTRUCTION, which lives inline in `main()` at
    `hooks/cy_monitor_gate.py:415`. A test that chooses its own keys can never
    see what `main()` would have chosen. **So conditions 1, 2 and 3 are all
    properties of the key, and NONE of them can judge a candidate until
    `refusal_key()` is extracted from `main()` -- which is therefore part of
    the repair and not a tidy-up.**

    ★ WHAT THESE 2 TESTS ARE STILL WORTH, which is why they are kept rather
    than deleted: they pin `spend()`'s reset as the mechanism that makes
    condition 2 satisfiable at all. If a future repair removes the reset -- as
    candidate (a) does, by handing `spend()` a key that never changes -- these
    stay green while the SYSTEM breaks, and that is exactly the gap
    `TestCondition3` is reserved for. They are a regression guard on
    `spend()`, not a judge of the repair.
    """

    def test_a_different_key_opens_a_fresh_count(self, gate):
        """Driven: K1 to exhaustion, then a different key starts at 1."""
        for _ in range(gate.MAX_REFUSALS + 1):
            spent = gate.spend("sess|['bench/logs/run_one']")
        assert spent > gate.MAX_REFUSALS, (
            f"the first period did not reach the budget ({spent} against "
            f"{gate.MAX_REFUSALS}), so this test cannot show anything about "
            f"what happens AFTER exhaustion -- fix the arm, not the assertion")
        later = gate.spend("sess|['bench/logs/run_two']")
        assert later == 1, (
            f"a different key opened at {later} rather than 1, so `spend()`'s "
            f"reset -- `if st.get('key') != key` -- no longer fires. That reset "
            f"is the ONLY mechanism by which an exhausted budget ever recovers, "
            f"so losing it silences the gate permanently for a session. Read "
            f"spend() before weakening this.")

    def test_the_reset_is_a_reset_and_not_a_clamp(self, gate):
        """ANTI-VACUITY: discriminate a RESET from a CLAMP at the budget."""
        for _ in range(gate.MAX_REFUSALS + 1):
            gate.spend("sess|['a']")
        first = gate.spend("sess|['b']")
        for _ in range(gate.MAX_REFUSALS + 1):
            gate.spend("sess|['b']")
        second = gate.spend("sess|['c']")
        assert first == second == 1, (
            f"period 2 opened at {first} and period 3 at {second}; a reset "
            f"gives 1 both times, a clamp gives the budget both times, and "
            f"anything else means the state carries something across periods "
            f"that neither model explains")


@pytest.mark.skip(reason="B209 condition 3: requires `refusal_key()` to be "
                         "extracted from main(), which is PART of the repair. "
                         "The key is built inline at cy_monitor_gate.py:415, "
                         "so there is nothing to call. UNSKIP with the repair; "
                         "do not delete -- a dropped test is a lost condition.")
class TestCondition3TheKeyMustBeComputableWithNoWatchedRun:
    """The unwatched case is the ONLY one needing the protection at all.

    So a candidate key that secretly requires reading the run defeats the
    purpose. This cannot be asserted until the key construction is callable.
    """

    def test_a_key_exists_when_the_watched_set_is_empty(self, gate):
        key = gate.refusal_key({"session_id": "s"}, [], [], ["111", "222"])
        assert key, "no key derivable with an empty watched set"

    def test_the_key_does_not_vary_with_child_process_churn(self, gate):
        a = gate.refusal_key({"session_id": "s"}, [], [], ["111"])
        b = gate.refusal_key({"session_id": "s"}, [], [], ["111", "222"])
        assert a == b, (
            f"the key moved from {a!r} to {b!r} when only a CHILD process "
            f"appeared. That is B209 itself, and any repair must hold this.")
