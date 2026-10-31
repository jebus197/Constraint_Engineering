#!/usr/bin/env python3
"""R_k now accumulates across passes, which is his definition of severity.

HIS INSTRUCTION, 2026-10-31, verbatim: *"carry R forward across passes"*.

WHAT IT REPAIRS, MEASURED BEFORE IT WAS BUILT. Appendix section 1.1 sets
`R_k(0) = pi_k` as an INITIAL condition and gives the recursion
`R_k(i) = R_k(i-1)(1-q)/(1-q R_k(i-1))` for every pass after it. The runner
applied the recursion but re-seeded `R_k(0)` for every finding on every round,
so it ran once and never accumulated. Across the archive, `R_old` is 0.500000
in all 1,252 entries carrying an `R_new` -- distinct count 1 -- and `R_new`
floors at 0.366667 with 743 of 1,252 sitting exactly there, 0.593450, Wilson
[0.565997, 0.620332]. The recorded number was therefore the risk after ONE pass
from a fresh prior, not the risk "after a given number of passes" which is what
he asked for and what the appendix defines. Producer:
`scripts/his_severity_definition_is_the_models_own_quantity_2026-10-31.py`.

WHY A NEW PRECEDENCE TIER RATHER THAN A REWRITE. The existing order is
model-supplied R, then the section 1.5 blended memory prior, then the uniform
base prior. A carried value is neither a prior nor a model estimate: it is the
run's own accumulated state, so it sits BELOW a fresher model estimate and
ABOVE both priors, which are initial conditions and must not overwrite an
updated state. On the first round nothing is carried, so round 1 is identical
to the old behaviour and only rounds 2 and later differ.

THESE TESTS DRIVE THE PRODUCTION FUNCTION with a real registry, a real target
and a real SEARCH/REPLACE fix, following `test_immune_memory_consumption.py`,
whose fixture is lifted verbatim so the 2 suites cannot drift apart while
claiming to exercise the same pipeline. Nothing here asserts on the precedence
block's source text: per `execute-do-not-grep`, a test that reads the block
only proves the block describes itself. The 1 structural assertion is about
WHERE the carry dict is created, which no unit test can reach.
"""
from __future__ import annotations

import ast
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    Finding, FindingRegistry, RunnerConfig, _capture_baseline,
    _evaluate_sk_for_findings)

TARGET_SRC = (
    '"""Toy target module for the S_k pipeline."""\n'
    "\n"
    "\n"
    "def widen(value):\n"
    "    return value * 2\n"
    "\n"
    "\n"
    "def narrow(value):\n"
    "    return value / 2\n"
)

GOOD_FIX = (
    "<<<< SEARCH toy_target.py\n"
    "def widen(value):\n"
    "    return value * 2\n"
    "====\n"
    "def widen(value):\n"
    "    if value is None:\n"
    '        raise ValueError("value must not be None")\n'
    "    return value * 2\n"
    ">>>> REPLACE\n"
)

#: The REAL baseline capture, as `test_immune_memory_consumption.py` does
#: it. A hand-written dict leaves the effect gates reporting "ruff baseline
#: unavailable" and the pipeline ESCALATES before it reaches the S* decision,
#: so no R_k update happens at all -- which is how the first version of this
#: file produced 6 failures that were about the fixture and not the carry.
_BASELINE = _capture_baseline(TARGET_SRC, source_path="toy_target.py")


def _linters_present() -> bool:
    for mod in ("ruff", "bandit"):
        try:
            r = subprocess.run([sys.executable, "-m", mod, "--version"],
                               capture_output=True, timeout=60)
        except Exception:                                      # noqa: BLE001
            return False
        if r.returncode != 0:
            return False
    return True


_needs_pipeline = pytest.mark.skipif(
    not _linters_present(),
    reason="ruff and/or bandit are not installed, so the S_k effect gates "
           "cannot run. This guard checks the TOOLING, never the component.")


def _mk_registry(flaw_classes):
    reg = FindingRegistry()
    for i, fc in enumerate(flaw_classes):
        cid = reg.register(
            Finding(finding_id="F%03d" % i, model_id="CC2", round_idx=0,
                    flaw_class=fc, severity=0.8, abstraction_index=0.3,
                    description="finding of flaw class %d" % fc,
                    verified=False, origin_type="model",
                    proposed_fix=GOOD_FIX),
            "CC2")
        reg.entries[cid]["proposed_fix"] = GOOD_FIX
    return reg


def _round(flaw_classes, rk_carry, round_idx=0, carry=True,
           source_path="toy_target.py"):
    reg = _mk_registry(flaw_classes)
    _evaluate_sk_for_findings(
        reg, TARGET_SRC, source_path,
        baseline=_BASELINE, round_idx=round_idx, test_cmd=None, s_floor=0.0,
        rk_carry=rk_carry, carry_rk=carry)
    rows = [e["sk_result"] for e in reg.entries.values() if "sk_result" in e]
    return reg, [r for r in rows if "R_new" in r]


@_needs_pipeline
class TestItActuallyCompounds:
    def test_the_second_round_starts_where_the_first_ended(self):
        carry = {}
        _, r1 = _round([1], carry, round_idx=0)
        assert r1, "the first round produced no R_new at all"
        first_new = r1[0]["R_new"]
        assert r1[0]["R_old"] == pytest.approx(0.5), (
            "round 1 must still start from the prior; the carry is only for "
            "later rounds and round 1 has to stay byte-identical")
        _, r2 = _round([1], carry, round_idx=1)
        assert r2, "the second round produced no R_new"
        assert r2[0]["R_old"] == pytest.approx(first_new), (
            "round 2 started at %s instead of round 1's %s; R is not carried"
            % (r2[0]["R_old"], first_new))
        assert r2[0]["R_new"] < first_new, (
            "a second pass did not lower the accumulated risk")

    def test_ten_rounds_fall_well_below_the_archive_floor(self):
        carry = {}
        last = 1.0
        for i in range(10):
            _, rows = _round([1], carry, round_idx=i)
            assert rows, "round %d produced no R_new" % i
            cur = rows[0]["R_new"]
            assert cur < last, "round %d did not lower R: %s -> %s" % (i, last, cur)
            last = cur
        assert last < 0.366666, (
            "after 10 carried passes R = %.6f, still at or above the archive's "
            "one-pass floor of 0.366667 -- the carry is not compounding" % last)

    def test_each_flaw_class_carries_its_own_state(self):
        """★ A MUTATION SURVIVED THE FIRST VERSION OF THIS TEST. Replacing the
        per-class lookup with `list(rk_carry.values())[0]` -- one shared state
        for every class -- left it GREEN, because both classes sat at the SAME
        value after round 1, so reading the wrong one was indistinguishable
        from reading the right one. The classes are now driven APART first, so
        a shared state reads a demonstrably wrong number."""
        carry = {}
        _round([1, 2], carry, round_idx=0)
        assert set(carry) == {1, 2}, carry
        # Drive class 1 three rounds further so the 2 classes are far apart.
        for i in (1, 2, 3):
            _round([1], carry, round_idx=i)
        assert carry[1] < carry[2] - 0.05, (
            "the 2 classes did not separate, so this test cannot tell a "
            "per-class state from a shared one: %r" % (carry,))
        before2 = carry[2]
        # Now advance class 2 by 1 round. If the state were shared it would
        # read class 1's much lower value and fall far too fast.
        _, rows = _round([2], carry, round_idx=4)
        assert rows[0]["R_old"] == pytest.approx(before2), (
            "class 2 started from %s, not its own carried %s -- the carry is "
            "not keyed per flaw class" % (rows[0]["R_old"], before2))
        assert carry[1] < carry[2], "class 1's state was overwritten"

    def test_the_source_of_each_value_is_recorded(self):
        """Provenance, under the convention this report already uses: the key
        is emitted ONLY when the source is not the default uniform prior.

        The first version of this test asserted `rk0_source == "uniform"` on
        round 1, which forced an unconditional write and broke
        `test_immune_memory_consumption.py::test_off_path_is_the_uniform_prior`
        -- whose property is that turning a path off emits no new report keys.
        That guard was right and this test was wrong: a report shape that
        changes with a switch cannot be compared across runs.
        """
        carry = {}
        _, r1 = _round([1], carry, round_idx=0)
        assert "rk0_source" not in r1[0], (
            "round 1 used the default prior, so no provenance key belongs in "
            "the report: %r" % (r1[0].get("rk0_source"),))
        _, r2 = _round([1], carry, round_idx=1)
        assert r2[0].get("rk0_source") == "carried", (
            "a carried value must say so, or the number cannot be audited: %r"
            % (r2[0].get("rk0_source"),))


@_needs_pipeline
class TestTheOldBehaviourIsStillReachable:
    def test_carry_off_reproduces_the_one_pass_floor(self):
        """★ A MUTATION SURVIVED THE FIRST VERSION. Deleting `carry_rk` from
        the READ condition left this green, because the WRITE is gated on the
        same flag: with the flag off nothing was ever written, so the read had
        nothing to find and the mutation was masked. The dict is now
        PRE-POPULATED, so the read path is exercised on its own and must still
        refuse the carried value when the flag is off."""
        carry = {1: 0.05}          # a value the read would obviously use
        seen = []
        for i in range(4):
            _, rows = _round([1], carry, round_idx=i, carry=False)
            seen.append(rows[0]["R_old"])
        assert all(v == pytest.approx(0.5) for v in seen), (
            "with the carry off, R_old moved: %s; either the flag is ignored "
            "on the read path or the old behaviour is no longer reproducible"
            % seen)
        assert carry == {1: 0.05}, (
            "with the carry off, the dict was written to: %r" % (carry,))

    def test_the_flag_is_honoured_on_the_read_path_specifically(self):
        """The same property stated directly, so it cannot be masked again.

        The carried value is 0.3 rather than something very small ON PURPOSE.
        At R_old = 0.05 this fixture's fix is REJECTED by the Valley of Bad
        Fixes rule, the R_k update is skipped entirely, and no `R_old` reaches
        `sk_result` -- so a tiny value would make this test unable to see the
        read tier at all. That interaction is real and is recorded in
        `TestWhatTheCarryDoesNotDoYet` below.
        """
        carry = {1: 0.3}
        _, off = _round([1], carry, round_idx=2, carry=False)
        assert off[0]["R_old"] == pytest.approx(0.5), (
            "with the carry off a pre-populated value was still read")
        _, on = _round([1], dict(carry), round_idx=2, carry=True)
        assert on[0]["R_old"] == pytest.approx(0.3), (
            "with the carry ON a pre-populated value was ignored, so the read "
            "tier is not working: %s" % on[0]["R_old"])


@_needs_pipeline
class TestWhatTheCarryDoesNotDoYet:
    """A BOUNDARY THIS CHANGE INHERITS AND DOES NOT CROSS, recorded so it is
    not mistaken for part of the repair.

    The R_k update sits behind `if passes:`, so it runs only for a fix that
    clears the S* threshold. A REJECTED fix therefore leaves the accumulated
    risk FROZEN rather than moving it a little. Under the appendix that is
    arguably wrong: `R_base = sk*R_det + (1-sk)*R_old` already handles a poor
    fix by barely moving, so a rejected pass should apply the recursion with a
    low sigma rather than be skipped. Changing it would alter admissibility
    accounting across every archived comparison, so it is RAISED rather than
    done, and these tests pin the behaviour as it actually is so the question
    cannot be lost.
    """

    def test_a_rejected_pass_leaves_the_carry_untouched(self):
        carry = {1: 0.05}          # low enough to trip the Valley rule
        before = dict(carry)
        _round([1], carry, round_idx=1)
        assert carry == before, (
            "a rejected pass changed the carried risk; if that is now wanted, "
            "this test records the OLD behaviour and should be updated "
            "deliberately rather than deleted: %r" % (carry,))

    def test_a_frozen_carry_is_visible_rather_than_silent(self):
        """Whatever is decided, the state must be inspectable: the entry still
        records its sk_result so a reader can see the pass happened."""
        reg, rows = _round([1], {1: 0.05}, round_idx=1)
        results = [e.get("sk_result") for e in reg.entries.values()]
        assert results and results[0], "the pass left no sk_result at all"
        assert "tristate" in results[0]

    def test_a_none_carry_is_tolerated(self):
        _, rows = _round([1], None, round_idx=3)
        assert rows and rows[0]["R_old"] == pytest.approx(0.5)


@_needs_pipeline
class TestANoScorePassDoesNotResetTheState:
    """★ THE THIRD MUTATION THAT SURVIVED. Deleting the write-back on the
    NO_SCORE path left the guard green, because the toy fix always scores, so
    that branch was never entered by any test here. A pass that formed no
    opinion must carry the accumulated risk FORWARD UNCHANGED -- resetting it
    to the prior would let a single unscoreable finding throw away every
    earlier pass."""

    def test_no_score_is_actually_reached_by_this_fixture(self):
        """If this stops producing NO_SCORE the tests below go vacuous."""
        reg, rows = _round([1], {}, round_idx=0, source_path="notes.md")
        assert rows, "no sk_result carried an R_new at all"
        assert rows[0].get("tristate") == "NO_SCORE" or \
            "NO_SCORE" in str(rows[0].get("rk_note", "")), (
                "the non-Python target did not produce NO_SCORE, so the "
                "NO_SCORE branch is still untested: %r" % (rows[0],))

    def test_a_no_score_pass_SEEDS_an_empty_carry(self):
        """★ THE DISCRIMINATING CASE, and the first version of this class did
        not have it. Removing the NO_SCORE write-back survived every test here
        because each one PRE-POPULATED the dict with the same value the
        write-back would store, so deleting the write was invisible. Starting
        from an EMPTY dict is the only shape that can tell them apart: with the
        write-back present the class appears at the prior, without it the dict
        stays empty and the next pass re-seeds from the prior for ever."""
        carry = {}
        _, rows = _round([1], carry, round_idx=0, source_path="notes.md")
        assert rows, "no sk_result carried an R_new"
        assert rows[0]["R_new"] == pytest.approx(0.5), (
            "NO_SCORE must pin R_new to R_old, which is the uniform prior here")
        assert 1 in carry, (
            "an unscoreable first pass left the carry EMPTY, so every later "
            "pass will restart from the prior: %r" % (carry,))
        assert carry[1] == pytest.approx(0.5)

    def test_a_no_score_pass_carries_the_state_forward(self):
        carry = {1: 0.2}
        _, rows = _round([1], carry, round_idx=1, source_path="notes.md")
        assert rows[0]["R_old"] == pytest.approx(0.2)
        assert rows[0]["R_new"] == pytest.approx(0.2), (
            "NO_SCORE must pin R_new to R_old")
        assert carry[1] == pytest.approx(0.2), (
            "the NO_SCORE pass did not write the state back, so the next pass "
            "will reset to the prior and discard every earlier pass: %r"
            % (carry,))

    def test_a_no_score_pass_does_not_lose_an_accumulated_value(self):
        """End to end: 3 scoring passes, then an unscoreable one, then another
        scoring pass must continue from where it was."""
        carry = {}
        for i in (0, 1, 2):
            _round([1], carry, round_idx=i)
        before = carry[1]
        assert before < 0.4, before
        _round([1], carry, round_idx=3, source_path="notes.md")
        assert carry[1] == pytest.approx(before), (
            "an unscoreable pass changed the accumulated risk from %s to %s"
            % (before, carry[1]))
        _, rows = _round([1], carry, round_idx=4)
        assert rows[0]["R_old"] == pytest.approx(before), (
            "after an unscoreable pass the next pass restarted from %s instead "
            "of %s" % (rows[0]["R_old"], before))


class TestTheFlagAndThePlumbing:
    def test_the_config_defaults_to_carrying(self):
        assert RunnerConfig().sk_carry_rk_across_rounds is True, (
            "his instruction was to carry R forward; a default of False would "
            "leave it an addition nothing reaches")

    def test_the_runner_owns_one_carry_per_run(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text()
        tree = ast.parse(src)
        loop_line = None
        for n in ast.walk(tree):
            if isinstance(n, ast.For) and isinstance(n.target, ast.Name) \
                    and n.target.id == "round_idx":
                loop_line = n.lineno
                break
        assert loop_line, "the round loop was not found"
        carry_line = None
        for n in ast.walk(tree):
            if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) \
                    and n.target.id == "_rk_carry":
                carry_line = n.lineno
                break
        assert carry_line, "_rk_carry is not assigned anywhere"
        assert carry_line < loop_line, (
            "_rk_carry is created at line %d, INSIDE or after the round loop "
            "at %d; it would reset every round" % (carry_line, loop_line))
