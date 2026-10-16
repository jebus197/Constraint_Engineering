#!/usr/bin/env python3
"""A finding that blocks release and cannot be served must be reported, not hidden.

HIS LIST, 2026-10-16, item 3 of the 7 smaller defects: *"A counter whose release
condition disagrees with it about severity."* His ruling: *"Fix it all."*

THE DISAGREEMENT, MEASURED ACROSS EVERY ARCHIVED runner_state.json. Of 3,400
entries, 212 are counted as blockers by `unverified_critical_count`, and 94 of
those 212 -- 44.3396%, Wilson 95% [37.8121%, 51.0686%], Clopper-Pearson
[37.5377%, 51.3020%] -- are entries `_apply_routing` would decline to admit,
across 18 runs. On the most recent run, leg 3 of the shakedown, A4 stands at 9
and 5 of those 9 are in that state. Such a finding can neither be resolved nor
released: permanent limbo.

WHY THE REPAIR REPORTS RATHER THAN RELEASES. Releasing them would loosen the A4
gate on a model-assigned severity float, which is the change the founder has
rejected 4 times and struck permanently on 2026-10-16. Widening routing instead
costs a paid dispatch per entry per round and changes paid-run behaviour, so it
is his decision. What is additive without a ruling is to SAY SO -- his ruling of
2026-10-12 is that such a finding must be *"fed back into the mechanics of the
harness for resolution"*, and a run that cannot feed it back should report that
rather than burn silently to the round cap.

THE BOUNDARY, STATED. `_apply_routing` DISPATCHES TO MODELS, and no paid
dispatch happens without his express authorisation, so these tests do not call
it. Instead they pin the two things that make a drift between the predicate and
the router detectable: the predicate's behaviour on hand-built entries covering
every branch, and the fact that both readers resolve the SAME constant objects,
so changing a threshold or the fault set moves both at once.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "bench"))

import reference_runner_v3 as R  # noqa: E402

THR = R.CRITICAL_SEVERITY_THRESHOLD


#: A routing record that counts as a READING. `_routing_ladder_never_served`
#: treats a record whose verdict is '' or 'UNRESOLVED' as NO reading, so a
#: fixture using `{"rung": "x"}` leaves the entry still never-served -- which is
#: how the first version of this file asserted the wrong thing twice. The
#: sentinel set is read from the module so the fixture cannot drift from it.
SERVED_RECORD = [{"verdict": "CONFIRMED", "resolved": False}]


def entry(**kw):
    e = {"status": "UNCONFIRMED", "severity": 0.5}
    e.update(kw)
    return e


def test_the_served_fixture_really_counts_as_served():
    """The premise the refusal tests rest on, checked rather than assumed."""
    assert "" in R.NO_READING_ROUTING_VERDICTS
    assert SERVED_RECORD[0]["verdict"].upper() not in R.NO_READING_ROUTING_VERDICTS
    assert R._routing_ladder_never_served(
        entry(routing_history=SERVED_RECORD)) is False
    # And the shape that fooled the first draft, kept as the counterexample.
    assert R._routing_ladder_never_served(
        entry(routing_history=[{"rung": "x"}])) is True


# ───────────────────────── the predicate, branch by branch ───────────────────

def test_a_critical_escalated_entry_is_admitted():
    assert R._routing_would_admit(entry(severity=0.9, escalated=True)) is True


def test_an_unescalated_entry_that_was_never_served_is_admitted():
    """His 2026-10-12 ruling: a never-read finding is worked, not excused."""
    e = entry(escalated=False)
    assert R._routing_ladder_never_served(e) is True
    assert R._routing_would_admit(e) is True


def test_a_subcritical_with_history_and_no_routable_fault_is_REFUSED():
    """The limbo class. This is the 44.3396 per cent the archive carries."""
    e = entry(escalated=True, severity=0.5, routing_history=SERVED_RECORD,
              falsifier_verdict="")
    assert R._routing_ladder_never_served(e) is False
    assert R._routing_would_admit(e) is False


def test_a_subcritical_whose_one_attempt_is_spent_is_REFUSED():
    """The other limbo class: `error_routed` already consumed."""
    fault = sorted(R.ROUTABLE_INSTRUMENT_FAULTS)[0]
    e = entry(escalated=True, severity=0.5, falsifier_verdict=fault,
              error_routed=True)
    assert R._routing_would_admit(e) is False


def test_a_subcritical_with_a_routable_fault_and_an_unspent_attempt_is_admitted():
    fault = sorted(R.ROUTABLE_INSTRUMENT_FAULTS)[0]
    e = entry(escalated=True, severity=0.5, falsifier_verdict=fault,
              error_routed=False)
    assert R._routing_would_admit(e) is True


def test_an_unescalated_entry_that_was_served_is_refused():
    e = entry(escalated=False, routing_history=SERVED_RECORD,
              falsifier_verdict="CONFIRMED")
    assert R._routing_would_admit(e) is False


# ──────────────── the 2 readers share their constants, so they move together ──

def test_both_readers_resolve_the_same_threshold_and_fault_set():
    """`composability`: a change to either constant must move both readers.

    This is what makes the mirror safe without calling `_apply_routing`. The
    predicate reads the module-level `CRITICAL_SEVERITY_THRESHOLD` and
    `ROUTABLE_INSTRUMENT_FAULTS`, and so does the router, so there is exactly 1
    definition of each to change.
    """
    assert isinstance(R.CRITICAL_SEVERITY_THRESHOLD, float)
    assert R.ROUTABLE_INSTRUMENT_FAULTS, "the routable fault set is empty"

    saved = R.CRITICAL_SEVERITY_THRESHOLD
    try:
        # Raise the threshold so a 0.9 entry becomes sub-critical; the predicate
        # must follow the constant rather than a copy of its old value.
        R.CRITICAL_SEVERITY_THRESHOLD = 0.95
        e = entry(severity=0.9, escalated=True,
                  routing_history=SERVED_RECORD, falsifier_verdict="")
        assert R._routing_would_admit(e) is False, (
            "the predicate did not follow CRITICAL_SEVERITY_THRESHOLD, so it is "
            "reading a captured copy and will drift from the router"
        )
    finally:
        R.CRITICAL_SEVERITY_THRESHOLD = saved
    assert R.CRITICAL_SEVERITY_THRESHOLD == saved


# ─────────────────────── the reader, on the live registry ────────────────────

def test_the_reader_is_a_subset_of_the_blocker_count():
    """Limbo entries are blockers. A limbo count above A4 would be incoherent."""
    state = (REPO_ROOT / "bench" / "logs"
             / "leg3_final_shakedown_20261015T220118Z" / "runner_state.json")
    if not state.is_file():
        pytest.skip("leg 3 state absent")
    reg = R.FindingRegistry.from_dict(json.loads(state.read_text())["registry"])
    a4 = reg.unverified_critical_count()
    limbo = reg.blockers_routing_cannot_serve()
    assert len(limbo) <= a4, (len(limbo), a4)
    assert a4 == 9, f"leg 3's A4 moved from 9 to {a4}; re-derive this file"
    assert len(limbo) == 5, (
        f"leg 3's limbo count moved from 5 to {len(limbo)}. Re-measure with "
        f"the producer before trusting either figure."
    )


def test_the_reader_skips_the_same_entries_the_counter_skips():
    """The reader must not report an entry the COUNTER has already released.

    `unverified_critical_count` releases 3 classes before any severity question
    is asked: an irreducible escalation without an unobserved integrity
    refusal, an `exhausted` entry, and an integrity-violation exclusion. An
    entry in one of those classes is not blocking, so calling it limbo would
    report a problem that does not exist and send the founder after a
    non-finding.

    Built synthetically, because the archive happens to contain no entry that is
    BOTH exhausted and unservable -- a mutation removing the skip survived until
    this test existed.
    """
    reg = R.FindingRegistry()
    # Unservable by construction: sub-critical, served, no routable fault.
    base = dict(status="UNCONFIRMED", severity=0.5, escalated=True,
                routing_history=SERVED_RECORD, falsifier_verdict="")
    reg.entries = {
        "C0001": dict(base),                                  # plain limbo
        "C0002": dict(base, exhausted=True),                  # age valve
        "C0003": dict(base, irreducible_escalation=True),     # handed to HIL
        "C0004": dict(base, irreducible_escalation=True,
                      integrity_unobserved=True),             # still blocking
    }
    for cid, e in reg.entries.items():
        assert R._routing_would_admit(e) is False, cid

    limbo = reg.blockers_routing_cannot_serve()
    assert "C0001" in limbo, limbo
    assert "C0002" not in limbo, (
        "an `exhausted` entry is reported as limbo. The counter already "
        "released it through the age valve, so it is not blocking and naming "
        "it sends the founder after a non-finding."
    )
    assert "C0003" not in limbo, (
        "an irreducible escalation already handed to the human is reported as "
        "limbo"
    )
    assert "C0004" in limbo, (
        "an irreducible escalation with an UNOBSERVED integrity refusal still "
        "blocks the counter, so it must still be reported as limbo"
    )


def test_the_reader_mutates_nothing():
    """A pure reader. Calling it twice must give the same answer and leave the
    registry untouched, or a diagnostic would be changing the run."""
    state = (REPO_ROOT / "bench" / "logs"
             / "leg3_final_shakedown_20261015T220118Z" / "runner_state.json")
    if not state.is_file():
        pytest.skip("leg 3 state absent")
    raw = json.loads(state.read_text())["registry"]
    reg = R.FindingRegistry.from_dict(raw)
    before = json.dumps(reg.entries, sort_keys=True, default=str)
    first = reg.blockers_routing_cannot_serve()
    second = reg.blockers_routing_cannot_serve()
    after = json.dumps(reg.entries, sort_keys=True, default=str)
    assert first == second
    assert before == after, "the reader mutated the registry"


def test_the_archive_carries_the_disagreement_this_file_records():
    """The ratchet on the measured figure, so it cannot go stale unnoticed."""
    logs = REPO_ROOT / "bench" / "logs"
    if not logs.is_dir():
        pytest.skip("no archive")
    blocked = unservable = 0
    for path in sorted(logs.rglob("runner_state.json")):
        try:
            ents = (json.loads(path.read_text(errors="replace"))
                    .get("registry") or {}).get("entries") or {}
        except (OSError, ValueError):
            continue
        for e in ents.values():
            if not isinstance(e, dict) or e.get("status") != "UNCONFIRMED":
                continue
            if e.get("irreducible_escalation") and not e.get("integrity_unobserved"):
                continue
            if e.get("exhausted"):
                continue
            blocked += 1
            if not R._routing_would_admit(e):
                unservable += 1
    assert blocked > 100, blocked
    assert unservable > 0, (
        "no archived blocker is now unservable. If the router was widened or "
        "the counter narrowed, that is a behaviour change needing his ruling, "
        "not a green test."
    )
    share = unservable / blocked
    assert 0.30 < share < 0.60, (
        f"the unservable share moved to {100*share:.4f}% ({unservable} of "
        f"{blocked}), outside the band this file records around 44.3396%. "
        f"Re-measure before citing the figure."
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
