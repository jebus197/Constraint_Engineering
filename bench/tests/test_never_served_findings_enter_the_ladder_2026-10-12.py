"""A finding nothing ever served enters the routing ladder once (2026-10-12).

THE DEFECT (STUDY_IN_FLIGHT.json, open_defects[2]; free panel 2026-10-12,
fable seat). C0066 (severity 0.45) and C0073 (0.50) in
study_run1b_2026-10-03_20261003T100439Z reached UNCONFIRMED with zero
verdicts, no falsifier_code, no falsifier_verdict and no routing_history.
`_apply_routing` gated on `escalated`, which they never were, so the one
mechanism that could have produced the missing falsifier never saw them,
while `unverified_critical_count` blocked convergence on them for the life
of the run: their severity_proof is SKIP, so the proven-sub-critical
release (restored 2026-10-06) cannot fire, and the `exhausted` valve
requires severity >= 0.7 AND verdicts > 0, neither of which they satisfy.

Executed before the fix against the real module: a C0066-shaped entry is
routed never (served == []) and A4 == 1 with no exit.

THE FIX is a SERVICE, not a release: the entry is dispatched up the
existing ladder exactly once (the appended routing_history is the
one-attempt guard). If a tool resolves it, A4 clears through a tool
verdict; if nothing resolves it, it keeps blocking, which is the honest
state under TOOLS DECIDE, NOT VOTES.
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import bench.reference_runner_v3 as rr  # noqa: E402
import bench.routing as routing  # noqa: E402

EXP = {"models": [{"label": "X-SIM"}, {"label": "Y-SIM"}]}


def _cfg():
    return rr.RunnerConfig(routing_enabled=True)


def _never_served_entry(sev, cid="C9001"):
    return {
        "canonical_id": cid, "status": "UNCONFIRMED", "severity": sev,
        "description": "never served", "source_model": "X-SIM",
        "falsifier_code": "", "falsifier_verdict": "", "verdicts": [],
        "escalated": False, "verified": False,
        "open_since_round": 5, "last_status_change_round": 5,
    }


class _Unresolved:
    verdict = "UNRESOLVED"
    resolved = False
    model_used = "Y-SIM"
    duplicate_of = None
    falsifier_code = ""
    rungs_tried = 1
    ladder_was_empty = False


def test_a_no_reading_serve_is_retried_and_a_ruled_serve_is_not():
    """REPLACED 2026-10-12 (joint round J1), and the old pin was measured
    wrong at system level. This test pinned "served exactly once" for an
    UNRESOLVED outcome. The only live serve that produces an UNRESOLVED
    record is one NO model answered (transport-dead: measured by
    scripts/transport_dead_serve_blocks_for_ever_2026-10-12.py, the ladder's
    reachable verdicts never include the no-reading sentinels), and burning
    the one admission on it contradicts the transport-dead guard's own
    promise ("must not burn the attempt") -- composed with the never-served
    door it blocked a C0066-shaped entry FOR EVER. The sharper pin
    distinguishes by outcome: a serve that read nothing is retried; a serve
    an instrument RULED on is served exactly once."""
    reg = rr.FindingRegistry()
    reg.entries["C9001"] = _never_served_entry(0.45)
    served = []

    def fake_route(finding, *a, **k):
        served.append(finding["id"])
        return _Unresolved()

    with mock.patch.object(routing, "route", fake_route):
        rr._apply_routing(reg, 6, EXP, cfg=_cfg())
        rr._apply_routing(reg, 7, EXP, cfg=_cfg())

    assert served == ["C9001", "C9001"], (
        "a serve that produced NO reading must not consume the admission; "
        "a healed transport can never decide a finding it is refused")
    assert len(reg.entries["C9001"].get("routing_history", [])) == 2
    # LEGACY CALLERS UNCHANGED: with no round passed, the door is disabled
    # and the unresolved, unproven entry still blocks A4.
    assert reg.unverified_critical_count() == 1

    # THE RULED HALF, same machinery: UNTOOLABLE is a ruling and is final.
    reg2 = rr.FindingRegistry()
    reg2.entries["C9001"] = _never_served_entry(0.45)
    served2 = []

    class _Ruled(_Unresolved):
        verdict = "UNTOOLABLE"

    def fake_route2(finding, *a, **k):
        served2.append(finding["id"])
        return _Ruled()

    with mock.patch.object(routing, "route", fake_route2):
        rr._apply_routing(reg2, 6, EXP, cfg=_cfg())
        rr._apply_routing(reg2, 7, EXP, cfg=_cfg())

    assert served2 == ["C9001"], (
        "an entry an instrument ruled on must be served exactly once")
    assert reg2.unverified_critical_count() == 1


def test_a_tool_resolution_clears_a4():
    reg = rr.FindingRegistry()
    reg.entries["C9001"] = _never_served_entry(0.45)

    class _Resolved(_Unresolved):
        verdict = "CONFIRMED"
        resolved = True
        falsifier_code = "assert False, 'FALSIFIED'"

    def fake_route(finding, *a, **k):
        reg.entries["C9001"].update(
            falsifier_code="assert False, 'FALSIFIED'",
            falsifier_verdict="CONFIRMED")
        return _Resolved()

    with mock.patch.object(routing, "route", fake_route):
        rr._apply_routing(reg, 6, EXP, cfg=_cfg())

    assert reg.unverified_critical_count() == 0, (
        "a finding the routed tool resolved must stop blocking A4")


def test_error_class_subcritical_routing_is_unchanged():
    reg = rr.FindingRegistry()
    reg.entries["C9002"] = {
        **_never_served_entry(0.5, "C9002"),
        "escalated": True, "falsifier_verdict": "ERROR",
        "falsifier_code": "x",
    }
    served = []

    def fake_route(finding, *a, **k):
        served.append(finding["id"])
        return _Unresolved()

    with mock.patch.object(routing, "route", fake_route):
        rr._apply_routing(reg, 6, EXP, cfg=_cfg())

    assert served == ["C9002"], "pre-existing ERROR-class routing regressed"


def test_an_already_RULED_entry_is_not_re_entered():
    """REPLACED 2026-10-12 (joint round J1), sharper, and the old fixture was
    the measured-wrong shape: it keyed "already served" on a routing_history
    record whose verdict was UNRESOLVED -- a record that says NOTHING READ
    THE FINDING. Refusing re-entry on that record is what blocked a
    C0066-shaped entry for ever when composed with the never-served door.
    The sharper pins: a RULED record refuses re-entry; so does error_routed
    (stamped only when a rung genuinely reached a model) even when the
    telemetry record was lost."""
    reg = rr.FindingRegistry()
    e = _never_served_entry(0.45)
    e["routing_history"] = [{"round": 3, "verdict": "UNTOOLABLE",
                             "resolved": False}]
    reg.entries["C9001"] = e
    served = []

    def fake_route(finding, *a, **k):
        served.append(finding["id"])
        return _Unresolved()

    with mock.patch.object(routing, "route", fake_route):
        rr._apply_routing(reg, 6, EXP, cfg=_cfg())

    assert served == [], (
        "an entry the ladder already ruled on must not re-enter through the "
        "never-served admission")

    # A LOST TELEMETRY RECORD IS NOT A LOST SERVICE: error_routed alone
    # (the pre-2026-09-02 archive shape, 68 entries) also refuses re-entry.
    reg2 = rr.FindingRegistry()
    e2 = _never_served_entry(0.45)
    e2["error_routed"] = True
    reg2.entries["C9001"] = e2
    served2 = []

    def fake_route2(finding, *a, **k):
        served2.append(finding["id"])
        return _Unresolved()

    with mock.patch.object(routing, "route", fake_route2):
        rr._apply_routing(reg2, 6, EXP, cfg=_cfg())

    assert served2 == [], (
        "error_routed records a model was reached; the admission must refuse "
        "it even when the routing_history write failed")
