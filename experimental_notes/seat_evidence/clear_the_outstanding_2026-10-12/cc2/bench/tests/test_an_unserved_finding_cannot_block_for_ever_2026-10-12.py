# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'clear_the_outstanding_2026-10-12', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2ad9300687dc7d2c06673f999611c141c4d346a95aa7e788f1290a5cde1309cf
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
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

def test_an_unserved_finding_does_not_block_a4_once_a_round_has_passed():
    r = _reg({"C0001": _unserved_entry()})
    assert r.unverified_critical_count(current_round=1) == 0


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


def test_excluded_implies_reported():
    """Whatever the door drops, the paired reader must name. No silent exclusion."""
    r = _reg({"C0001": _unserved_entry(), "C0002": _unserved_entry(severity=0.5)})
    assert r.unverified_critical_count(current_round=1) == 0
    assert r.ladder_unserved_findings(current_round=1) == ["C0001", "C0002"]


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
def test_the_live_run_at_its_own_final_round_does_NOT_fully_clear():
    """THE HONEST NUMBER, AND IT IS NOT ZERO. An earlier draft of this fix had
    no age lock and reported A4 = 0 on this registry. That was over-wide and is
    WITHDRAWN. Measured with the lock, at the run's own final round 7:

        C0066 arrived round 5, age 2 -> released and named
        C0073 arrived round 7, age 0 -> STILL BLOCKS

    A4 goes 2 -> 1. study_run1b still does not converge, and it should not:
    C0073 was emitted in the final round and nothing ever examined it. A gate
    that converged over it would report a clean run over an unread finding.
    The remedy is one more round, not a wider gate -- which test below."""
    with open(_LIVE) as fh:
        reg = R.FindingRegistry.from_dict(json.load(fh)["registry"])
    assert reg.unverified_critical_count(current_round=7) == 1
    assert reg.ladder_unserved_findings(current_round=7) == ["C0066"]


@pytest.mark.skipif(not os.path.exists(_LIVE), reason="archived run not present")
def test_one_further_round_is_what_clears_the_live_run():
    """The advice this fix yields, stated as an executable assertion: the run
    needed round 8. Neither a paid run nor a simulated severity test is
    required to clear this blocker."""
    with open(_LIVE) as fh:
        reg = R.FindingRegistry.from_dict(json.load(fh)["registry"])
    assert reg.unverified_critical_count(current_round=8) == 0
    assert reg.ladder_unserved_findings(current_round=8) == ["C0066", "C0073"]


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
