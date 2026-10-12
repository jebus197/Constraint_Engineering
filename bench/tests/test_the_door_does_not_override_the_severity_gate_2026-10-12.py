"""The never-served door must not release what the severity gate refuses.

WHAT IS UNDER TEST. `reference_runner_v3.unverified_critical_count` evaluates
two independent release doors in sequence:

  1. the never-served door  -- `_routing_ladder_never_served(e)` + an age lock
  2. the severity test      -- `severity < 0.7 AND severity_is_proven(e)`

Door 1 is evaluated FIRST and reads no severity field at all. Door 2 was
restored on 2026-10-06 on the founder's repeatedly-stated ruling, and it is
gated on `severity_is_proven` -- a TOOL RECOMPUTATION of the model's stated
R_k -- precisely so that an unrecomputable number cannot buy a closure.

THE DEFECT THESE TESTS PIN. `severity_proof_status` returns FAIL when the
checker ran and the model's stated R_k did NOT reproduce. That is the one state
in which door 2 is GUARANTEED to refuse a release. Yet the R_k proof checker
writes only `severity_proof`; it touches none of the ladder, falsifier or HIL
fields door 1's predicate reads. So before the `severity_proof` conjunct was
added, an entry whose proof FAILED looked untouched to door 1 and was released
there -- making door 1 strictly WIDER than door 2 and nullifying it for this
entry class. Measured over every archived runner_state.json in bench/logs: the
pre-fix door released 431 non-terminal entries, of which 25 carried a non-SKIP
proof (5.80%, Wilson 95% [3.96%, 8.42%]) and 11 carried FAIL (2.55%, Wilson 95%
[1.43%, 4.51%]). Producer:
scripts/never_served_door_vs_instrument_contact_2026-10-12.py.

ANTI-VACUITY IS ASSERTED, NOT ASSUMED. The SKIP and ABSENT cases below are the
two entries study_run1b's blocker is actually made of, and they assert the door
STILL OPENS. Without them a conjunct that closed the door on everything would
pass this file while silently reverting the 2026-10-12 fix to a no-op.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import reference_runner_v3 as R  # noqa: E402


def _entry(**over):
    """A minimally-shaped entry carrying NO ladder, falsifier or HIL trace."""
    e = {
        "canonical_id": "C9001",
        "description": "a finding nothing ever dispatched",
        "status": "UNCONFIRMED",
        "severity": 0.45,
        "verdicts": [],
        "routing_history": [],
        "falsifier_code": "",
        "falsifier_verdict": "",
        "open_since_round": 0,
        "last_status_change_round": 0,
    }
    e.update(over)
    return e


# ── the sentinel set itself ───────────────────────────────────────────────────

def test_the_no_reading_set_is_disjoint_from_every_reading_status():
    """ABSENT/SKIP mean no reading; PASS/WARN/FAIL are readings."""
    assert R.NO_READING_SEVERITY_PROOF_STATUSES == frozenset({"ABSENT", "SKIP"})
    readings = {"PASS", "WARN", "FAIL"}
    assert not (R.NO_READING_SEVERITY_PROOF_STATUSES & readings)
    # Every status the accepting set honours is a READING, so the two sets
    # cannot drift into agreeing that a proven severity was never read.
    assert R._RK_PROOF_ACCEPTED <= readings


def test_an_unrecognised_proof_status_fails_closed():
    """A status nobody declared is treated as a ruling, never as silence."""
    e = _entry(severity_proof={"status": "SOME_FUTURE_STATUS"})
    assert R._routing_ladder_never_served(e) is False


# ── the predicate, all five proof states ─────────────────────────────────────

@pytest.mark.parametrize("status", sorted({"PASS", "WARN", "FAIL"}))
def test_a_proof_reading_closes_the_door(status):
    """The checker ran and reported. That is instrument contact."""
    e = _entry(severity_proof={"status": status, "model_rk": 0.12,
                               "recomputed_rk": 0.56, "round": 3})
    assert R.severity_proof_status(e) == status
    assert R._routing_ladder_never_served(e) is False, (
        f"severity_proof status {status} is a reading by the R_k checker; the "
        "door must not call this entry untouched"
    )


@pytest.mark.parametrize("proof", [None, {"status": "SKIP"}, {"status": ""}])
def test_no_proof_reading_leaves_the_door_open(proof):
    """ANTI-VACUITY. SKIP and ABSENT are the states the fix exists for."""
    e = _entry()
    if proof is not None:
        e["severity_proof"] = proof
    assert R.severity_proof_status(e) in R.NO_READING_SEVERITY_PROOF_STATUSES
    assert R._routing_ladder_never_served(e) is True, (
        "the door must still open on an entry no instrument read, or the "
        "2026-10-12 never-served fix is reverted to a no-op"
    )


# ── the two doors, measured against each other end to end ────────────────────

def _count(entry, current_round):
    reg = R.FindingRegistry()
    reg.entries[entry["canonical_id"]] = entry
    return reg.unverified_critical_count(current_round=current_round)


def test_the_door_no_longer_releases_what_the_severity_gate_refuses():
    """THE DEFECT ITSELF, through the live counter rather than the predicate.

    A sub-critical entry whose R_k proof FAILED: door 2 refuses it because
    `severity_is_proven` is False. Door 1 must not release it either.
    """
    e = _entry(severity=0.45,
               severity_proof={"status": "FAIL", "model_rk": 0.12,
                               "recomputed_rk": 0.56, "delta": 0.44,
                               "round": 0})
    assert R.severity_is_proven(e) is False, "door 2 must refuse this entry"
    assert _count(e, current_round=5) == 1, (
        "door 1 released an entry whose severity the R_k checker affirmatively "
        "failed to reproduce, so door 1 is wider than the gate restored on "
        "2026-10-06"
    )


def test_a_proven_subcritical_is_still_released_by_the_severity_gate():
    """The composed form must not have made door 2 unreachable."""
    e = _entry(severity=0.45,
               severity_proof={"status": "PASS", "model_rk": 0.44,
                               "recomputed_rk": 0.441, "delta": 0.001,
                               "round": 0})
    assert R.severity_is_proven(e) is True
    assert _count(e, current_round=5) == 0


def test_an_untouched_entry_is_still_released_by_the_never_served_door():
    """ANTI-VACUITY for the counter, not just the predicate."""
    e = _entry(severity=0.45)
    assert _count(e, current_round=5) == 0
    # and the age lock still holds it in its arrival round
    assert _count(_entry(severity=0.45), current_round=0) == 1


def test_the_paired_reader_still_names_what_the_door_drops():
    """Excluded-implies-reported, held across the new conjunct."""
    reg = R.FindingRegistry()
    reg.entries["C9001"] = _entry()
    reg.entries["C9002"] = _entry(canonical_id="C9002",
                                  severity_proof={"status": "FAIL"})
    assert reg.ladder_unserved_findings(current_round=5) == ["C9001"], (
        "the reader must name exactly what the counter dropped -- C9002 is "
        "now blocked, so naming it would read as excused when it is not"
    )
    assert reg.unverified_critical_count(current_round=5) == 1


# ── the age bound, answered from the ladder's own record ─────────────────────

def test_the_age_bound_matches_the_ladders_measured_first_serve_latency():
    """LADDER_UNSERVED_MIN_AGE_ROUNDS = 1 is measured, not chosen.

    Over every archived runner_state.json in bench/logs, 230 of 230
    ladder-served entries were first served in their ARRIVAL round
    (first_routing_round - open_since_round == 0; Wilson 95% [98.36%, 100%]).
    The ladder serves an entry in its arrival round or never, so one completed
    round is a full round of margin over a bound the data puts at 0 and a
    longer wait buys no service. Producer:
    scripts/never_served_door_vs_instrument_contact_2026-10-12.py.
    """
    assert R.LADDER_UNSERVED_MIN_AGE_ROUNDS == 1
    e = _entry(severity=0.45, last_status_change_round=7)
    # emitted this round: not yet passed over, still blocks
    assert _count(dict(e), current_round=7) == 1
    # one completed round later: the ladder had its turn and did not take it
    assert _count(dict(e), current_round=8) == 0
