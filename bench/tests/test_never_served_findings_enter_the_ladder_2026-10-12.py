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


def test_never_served_subcritical_is_served_exactly_once_and_still_blocks():
    reg = rr.FindingRegistry()
    reg.entries["C9001"] = _never_served_entry(0.45)
    served = []

    def fake_route(finding, *a, **k):
        served.append(finding["id"])
        return _Unresolved()

    with mock.patch.object(routing, "route", fake_route):
        rr._apply_routing(reg, 6, EXP, cfg=_cfg())
        rr._apply_routing(reg, 7, EXP, cfg=_cfg())

    assert served == ["C9001"], (
        "the never-served entry must be dispatched exactly once; the "
        "routing_history record is the one-attempt guard")
    assert len(reg.entries["C9001"].get("routing_history", [])) == 1
    # SERVICE, NOT RELEASE: unresolved and unproven, it still blocks A4.
    assert reg.unverified_critical_count() == 1


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


def test_an_already_served_entry_is_not_re_entered():
    reg = rr.FindingRegistry()
    e = _never_served_entry(0.45)
    e["routing_history"] = [{"round": 3, "verdict": "UNRESOLVED"}]
    reg.entries["C9001"] = e
    served = []

    def fake_route(finding, *a, **k):
        served.append(finding["id"])
        return _Unresolved()

    with mock.patch.object(routing, "route", fake_route):
        rr._apply_routing(reg, 6, EXP, cfg=_cfg())

    assert served == [], (
        "an entry the ladder already served must not re-enter through the "
        "never-served door")
