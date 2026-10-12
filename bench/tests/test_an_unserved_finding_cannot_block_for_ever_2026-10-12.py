"""A finding the routing ladder NEVER SERVED must not block convergence for the
life of the run -- and must be NAMED when it is excused.

MEASURED, NOT ARGUED. On the live registry
bench/logs/study_run1b_2026-10-03_20261003T100439Z/runner_state.json (75
entries) `unverified_critical_count()` returned 2 before this fix. Both
survivors -- C0066 at severity 0.45 and C0073 at 0.50 -- carried 0 verdicts, 0
routing_history entries, 0 characters of falsifier_code, an empty
falsifier_verdict and `severity_proof_status == SKIP`. Nothing had ever been
dispatched to them, and NEITHER release door could reach them. That is the
whole of what stopped that run converging.

These tests pin the two doors shut, so that a later edit to either one cannot
silently reopen the hole, and pin the narrowness of the new door, so that it
cannot drift wide enough to release an entry an instrument actually ruled on.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import reference_runner_v3 as R  # noqa: E402

_LIVE = os.path.join(
    os.path.dirname(__file__), "..", "logs",
    "study_run1b_2026-10-03_20261003T100439Z", "runner_state.json")


def _unserved_entry(**over):
    """An UNCONFIRMED entry carrying no trace of any instrument."""
    e = {"status": "UNCONFIRMED", "severity": 0.45, "verdicts": [],
         "routing_history": [], "falsifier_code": "", "falsifier_verdict": "",
         "last_status_change_round": 0}
    e.update(over)
    return e


def _reg(entries):
    r = R.FindingRegistry()
    r.entries = entries
    return r


# ── THE DOOR ────────────────────────────────────────────────────────────────

def test_an_unserved_finding_KEEPS_BLOCKING_and_is_named_and_queued():
    """REPLACED ON HIS RULING, 2026-10-12. Verbatim: "No. If a record exists
    that says a problem was never read by a model, this should simply be fed
    back into the mechanics of the harness for resolution, this can include
    routing, the sweep mechanics and the other machinery we have for dealing
    with problems of this nature."

    This test asserted that such a finding was RELEASED from the blocker
    count. An exclusion is not a resolution, so the release is withdrawn and
    the contract is stronger: the finding KEEPS BLOCKING, is NAMED so nothing
    is silent, and REACHES the halt machinery so the founder is handed a
    bundle rather than a run burning quietly to its round cap.
    """
    r = _reg({"C0001": _unserved_entry()})
    assert r.unverified_critical_count(current_round=1) == 1, (
        "a finding nothing ever read was excused from the blocker count")
    assert r.ladder_unserved_findings(current_round=1) == ["C0001"], (
        "blocking but not named")
    # AND IT MUST NOT YET REACH THE HALT QUEUE. This assertion was the
    # OPPOSITE when first written, and the full board refuted it: counting a
    # finding that has not yet had a ladder turn would put 3 fresh criticals
    # over the bound and HALT a run that had barely started
    # (test_static_queue_closure.py caught it). The queue is for a finding the
    # ladder PASSED OVER, which the record distinguishes by a non-empty
    # routing_history of no-reading entries.
    locked, deferred = R._irreducible_queue_split(r.entries)
    assert locked + deferred == 0, (
        "a finding awaiting its first verification was queued for the halt "
        "alarm; that halts healthy runs")


def test_a_brand_new_unserved_finding_STILL_blocks():
    """The age lock. A finding that has only just arrived has not been passed
    over by the routing ladder -- it has not been reached yet. Releasing it
    would be a false convergence, and the unlocked first draft of this door
    broke test_severity_calibration.py's anti-vote test by doing exactly that."""
    r = _reg({"C0001": _unserved_entry(last_status_change_round=4)})
    assert r.unverified_critical_count(current_round=4) == 1
    assert r.ladder_unserved_findings(current_round=4) == []


def test_without_a_round_the_door_is_disabled_so_old_callers_are_unchanged():
    """`current_round=None` is the default and must preserve prior behaviour
    exactly, so adding the parameter cannot change any existing call site."""
    r = _reg({"C0001": _unserved_entry()})
    assert r.unverified_critical_count() == 1


def test_blocking_implies_reported():
    """REPLACED ON HIS RULING, 2026-10-12, and the property is now STRONGER.

    It asserted that whatever the door DROPPED, the reader named -- a
    no-silent-exclusion rule over an exclusion that no longer happens. With
    the release withdrawn the obligation widens: whatever BLOCKS must be
    named, because a founder cannot act on a blocker the round log does not
    report. Nothing is dropped, so nothing can be dropped silently.
    """
    r = _reg({"C0001": _unserved_entry(), "C0002": _unserved_entry(severity=0.5)})
    assert r.unverified_critical_count(current_round=1) == 2, (
        "both never-read findings must still block")
    assert r.ladder_unserved_findings(current_round=1) == ["C0001", "C0002"], (
        "a blocking finding that the reader does not name is unactionable")


def test_the_reader_is_silent_when_there_is_nothing_to_say():
    r = _reg({"C0001": _unserved_entry(verdicts=[{"seat": "cc2"}])})
    assert r.ladder_unserved_findings(current_round=1) == []


# ── THE DOOR IS NARROW: a ruling by ANY instrument still blocks ─────────────

@pytest.mark.parametrize("field,value", [
    ("verdicts", [{"seat": "cc2"}]),
    ("routing_history", [{"verdict": "UNTOOLABLE"}]),
    ("falsifier_code", "assert False"),
    ("falsifier_verdict", "UNTOOLABLE"),
    ("falsifier_verdict", "ERROR"),
    ("routing_verdict_unreconciled", "UNTOOLABLE"),
    ("routing_deferred", True),
    ("hil_escalated", True),
])
def test_any_trace_of_an_instrument_keeps_it_blocking(field, value):
    """UNTOOLABLE is a RULING, not an absence. An instrument ran and reported
    that no runnable tool can be written. It must still block."""
    e = _unserved_entry(**{field: value})
    assert R._routing_ladder_never_served(e) is False
    assert _reg({"C0001": e}).unverified_critical_count(current_round=1) == 1
    assert _reg({"C0001": e}).ladder_unserved_findings(current_round=1) == []


# ── THE TWO DOORS THAT CANNOT RELEASE THESE, PINNED SHUT ───────────────────

def test_the_severity_proof_door_cannot_release_an_unserved_finding():
    """With no corroboration block there is nothing to recompute, so
    severity_proof_status is SKIP and severity_is_proven is False. A sub-critical
    severity alone must NOT buy a release -- that is the no-votes rule."""
    e = _unserved_entry()
    # The STATUS STRING is not the invariant and this test first asserted the
    # wrong one: a hand-built entry returns ABSENT while the live C0066/C0073
    # return SKIP. Both are outside _RK_PROOF_ACCEPTED, which is the property
    # the door actually depends on, so that is what is asserted.
    assert R.severity_proof_status(e) not in R._RK_PROOF_ACCEPTED
    assert R.severity_is_proven(e) is False


def test_widening_the_exhausted_valve_severity_term_releases_nothing_here():
    """The `exhausted` valve requires severity >= 0.7 AND len(verdicts) > 0.
    An unserved entry fails BOTH conjuncts, so the obvious fix -- widening the
    severity term -- is INSUFFICIENT. Asserted so nobody re-proposes it."""
    e = _unserved_entry(severity=0.95)          # severity term now satisfied
    assert len(e["verdicts"]) == 0              # but this one is not
    r = _reg({"C0001": e})
    R._update_finding_statuses(r, round_idx=99,
                               cfg=R.RunnerConfig(max_rounds=100))
    assert e.get("exhausted") is False, (
        "the valve fired without any review, which it must never do")


# ── THE LIVE REGISTRY, END TO END ──────────────────────────────────────────

@pytest.mark.skipif(not os.path.exists(_LIVE), reason="archived run not present")
def test_the_live_run_does_NOT_clear_at_any_round():
    """REPLACED ON HIS RULING, 2026-10-12, AND IT REVERSES THIS TEST'S ADVICE.

    Two earlier drafts of this test both said study_run1b could be cleared.
    The first had no age lock and reported A4 = 0 at the run's own round 7 --
    over-wide, and withdrawn. The second added the lock and said the remedy
    was ONE MORE ROUND, because at round 8 both survivors aged past the lock
    and the door released them.

    BOTH DRAFTS RESTED ON THE RELEASE, AND HE HAS WITHDRAWN IT: "If a record
    exists that says a problem was never read by a model, this should simply
    be fed back into the mechanics of the harness for resolution." An extra
    round does not make an unread finding read. So the honest answer is that
    NO number of rounds clears this run by ageing, at round 7 or 8 or 20 --
    what clears it is a tool reading C0066 and C0073, which is what the
    routing fix of the same day makes possible.
    """
    with open(_LIVE) as fh:
        reg = R.FindingRegistry.from_dict(json.load(fh)["registry"])
    for rd in (7, 8, 9, 20):
        assert reg.unverified_critical_count(current_round=rd) == 2, (
            f"at round {rd} the count fell below 2, so ageing alone excused a "
            f"finding nothing ever read")
    assert reg.ladder_unserved_findings(current_round=8) == ["C0066", "C0073"], (
        "both blockers must be named at every round, so the founder can see "
        "what is holding the run")


@pytest.mark.skipif(not os.path.exists(_LIVE), reason="archived run not present")
def test_the_live_run_does_not_reach_the_halt_queue_and_WHY():
    """CORRECTED THE SAME NIGHT IT WAS WRITTEN, by the full board.

    The first version asserted that study_run1b's 2 survivors reached the halt
    queue. They do not, and they should not: the queue is for a finding the
    ladder PASSED OVER, and this registry predates the routing fix of the same
    day, so C0066 and C0073 carry NO routing_history at all -- the ladder never
    had a turn at them, which is the whole defect that fix addresses.

    SO THE ARCHIVE CANNOT DEMONSTRATE THE HALT PATH, and saying so is the
    honest position. In a live run with routing enabled, the serve admits these
    entries, a transport-dead or empty-ladder outcome writes a no-reading
    record, and THEN they queue. That is what the next simulated run measures.
    """
    with open(_LIVE) as fh:
        reg = R.FindingRegistry.from_dict(json.load(fh)["registry"])
    locked, deferred = R._irreducible_queue_split(reg.entries)
    assert (locked, deferred) == (0, 0), (
        f"expected the archived survivors NOT to queue, since the ladder never "
        f"had a turn at them; got locked={locked} deferred={deferred}")
    # They still BLOCK, and are still NAMED. That is the part the archive does
    # demonstrate, and it is what his ruling requires.
    assert reg.unverified_critical_count(current_round=9) == 2
    assert reg.ladder_unserved_findings(current_round=9) == ["C0066", "C0073"]


@pytest.mark.skipif(not os.path.exists(_LIVE), reason="archived run not present")
def test_excluded_implies_reported_on_the_live_registry_at_every_round():
    with open(_LIVE) as fh:
        reg = R.FindingRegistry.from_dict(json.load(fh)["registry"])
    for rd in range(0, 10):
        named = reg.ladder_unserved_findings(rd)
        dropped = sorted(
            cid for cid, e in reg.entries.items()
            if e.get("status") == "UNCONFIRMED"
            and R._routing_ladder_never_served(e)
            and rd - int(e.get("last_status_change_round") or 0)
            >= R.LADDER_UNSERVED_MIN_AGE_ROUNDS)
        assert dropped == named, f"silent exclusion at round {rd}"
