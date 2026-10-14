"""A convergence blocker that cannot reach a halt path is a silent max_rounds exit.

FREE PANEL, 2026-10-13, ITEMS 2 and 3. This file pins the measurement that
refutes the brief's ITEM 3 premise, and the conservation property the repair
should establish. It asserts the CURRENT state explicitly so that a later repair
FAILS here and has to be re-derived in place rather than silently absorbed.

THE PREMISE THAT FAILED. The 2026-10-13 brief, and the paragraph that stood at
bench/reference_runner_v3.py:3427-3434 until it was corrected the same day, both
said: "Measured on study_run1b_2026-10-03, the 2 never-read survivors put the
queue at exactly 2." Executed, the queue is ZERO. The alarm is therefore silent
at a bound of 2, at 1, and at 0 alike, so the per-class bound the brief proposed
for ITEM 3 fires on none of those entries.

WHY. `_irreducible_queue_split`'s never-read arm opens with
`bool(e.get("routing_history"))`, and the 3 non-terminal entries carry None.
They were never ROUTED, so `routing_deferred` was never set either, and their
severities (0.45, 0.45, 0.50) fail the severity skip as well -- 3 independent
exclusions. Meanwhile `unverified_critical_count()` returns 2 on the same
registry, so they DO refuse convergence. The run exited at max_rounds with
stop_reason UNRECORDED_STOP.

Producer: scripts/the_queue_is_zero_not_two_2026-10-13.py
"""
import json
import pathlib
import types

import pytest

import bench.reference_runner_v3 as rr

REPO = pathlib.Path(__file__).resolve().parents[2]
RUN = REPO / "bench" / "logs" / "study_run1b_2026-10-03_20261003T100439Z"
STATE = RUN / "runner_state.json"
TERMINAL = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}


def _registry():
    if not STATE.exists():
        pytest.skip("study_run1b registry absent in this clone")
    reg = rr.FindingRegistry()
    reg.entries = json.loads(STATE.read_text())["registry"]["entries"]
    return reg


class TestTheQueueIsZeroNotTwo:
    """The ITEM 3 premise, measured rather than cited."""

    def test_the_split_returns_zero_on_study_run1b(self):
        reg = _registry()
        locked, deferred = rr._irreducible_queue_split(reg.entries)
        assert (locked, deferred) == (0, 0), (
            f"the split returned ({locked}, {deferred}); the 2026-10-13 "
            f"measurement of (0, 0) no longer holds. If the never-read arm was "
            f"widened, re-derive this file and the corrected comment at "
            f"bench/reference_runner_v3.py:3427 -- do NOT relax the assertion.")

    def test_no_bound_makes_the_alarm_fire_on_this_registry(self):
        """The decisive refutation of a per-class bound of 1."""
        reg = _registry()
        count = reg.irreducible_queue_count()
        for bound in (0, 1, 2, 3):
            cfg = types.SimpleNamespace(max_irreducible_queue=bound)
            assert rr.build_irreducible_queue_alarm(cfg=cfg, registry=reg,
                                                    round_idx=8) is None, (
                f"the alarm fired at bound={bound}; with a count of {count} that "
                f"should be impossible, so either the count changed or the "
                f"comparison changed. Re-derive, do not relax.")

    def test_the_blockers_carry_no_routing_history(self):
        """The root cause: never ROUTED, not merely never read."""
        reg = _registry()
        nonterm = [(c, e) for c, e in reg.entries.items()
                   if e.get("status") not in TERMINAL]
        assert nonterm, "fixture has no non-terminal entries"
        for cid, e in nonterm:
            assert not e.get("routing_history"), (
                f"{cid} now carries routing_history; the never-read arm may "
                f"admit it and this file needs re-deriving")
            assert not e.get("routing_deferred"), f"{cid} now carries routing_deferred"


class TestTheAsymmetryIsTheDefect:
    """A blocker invisible to every halt path can only end in max_rounds."""

    def test_blockers_exceed_the_queue(self):
        reg = _registry()
        blockers = reg.unverified_critical_count()
        queue = reg.irreducible_queue_count()
        assert blockers > queue, (
            f"blockers={blockers} queue={queue}; the asymmetry this file exists "
            f"to record is gone. If the 2 predicates now agree on their "
            f"population the conservation property below holds and THIS "
            f"assertion should be REPLACED by it, not deleted.")

    def test_the_conservation_property_is_currently_violated(self):
        """blockers > 0 must imply a reachable NAMED terminal state.

        Asserted in the negative because it is currently FALSE and the
        counterexample is archived. A repair makes this test fail, which is the
        intended signal: swap the body for the positive form and say so here.
        """
        reg = _registry()
        blockers = reg.unverified_critical_count()
        cfg = types.SimpleNamespace(max_irreducible_queue=2)
        alarm = rr.build_irreducible_queue_alarm(cfg=cfg, registry=reg, round_idx=8)
        assert blockers > 0 and alarm is None, (
            "the conservation property now HOLDS on this registry: every "
            "convergence blocker can reach a named terminal state. Replace this "
            "assertion with the positive form -- `blockers == 0 or alarm is not "
            "None` -- and record the repair that achieved it.")


class TestTheCorrectedCommentIsInPlace:
    """The wrong figure must not come back."""

    def test_the_runner_no_longer_claims_the_queue_is_two(self):
        """The queue IS zero, established by CALLING the predicate.

        ★ CONVERTED FROM A SOURCE-TEXT ASSERTION, 2026-10-14. It read
        `bench/reference_runner_v3.py` and asserted on the wording of a COMMENT:
        that a wrong figure's phrase was absent, or a correction phrase present,
        and that the comment cited its producer. That verified the runner
        describes itself consistently and nothing about the queue.

        `execute-do-not-grep`: "Where both forms exist as live code, the test
        must CALL them and compare outputs." The underlying claim is executable,
        because the figure has a committed producer, so the fact is checked here
        instead of the sentence recording it. It also removes this test from
        `scripts/source_text_assertions_2026-09-11.py`'s census, which the
        guard's own message asks for in preference to raising its ceiling: 4
        guards of this class broke on CORRECT changes in a single day.
        """
        state = (REPO / "bench" / "logs"
                 / "study_run1b_2026-10-03_20261003T100439Z" / "runner_state.json")
        if not state.is_file():
            pytest.skip("study_run1b is not archived in this clone")
        entries = json.loads(state.read_text(encoding="utf-8"))["registry"]["entries"]
        locked, deferred = rr._irreducible_queue_split(entries)
        reg = rr.FindingRegistry()
        reg.entries = entries
        # BOTH live forms, compared against each other and against the figure.
        assert locked + deferred == 0, (
            f"_irreducible_queue_split put study_run1b's queue at "
            f"(locked={locked}, deferred={deferred}); the brief's figure of 2 was "
            f"measured wrong on 2026-10-13 and the producer is "
            f"scripts/the_queue_is_zero_not_two_2026-10-13.py")
        assert reg.irreducible_queue_count() == 0, (
            f"irreducible_queue_count() returned "
            f"{reg.irreducible_queue_count()}, disagreeing with the split")
        assert (REPO / "scripts" / "the_queue_is_zero_not_two_2026-10-13.py").is_file(), (
            "the producer for this figure must stay committed; a measured rate "
            "travels with the script that produced it")
