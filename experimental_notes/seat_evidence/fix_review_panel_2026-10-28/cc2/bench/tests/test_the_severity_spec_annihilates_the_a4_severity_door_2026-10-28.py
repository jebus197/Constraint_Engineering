# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fix_review_panel_2026-10-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 5fbf2b115b72923221a071b5827de7b7948a2d1c17e0c6939bcacc080211cb33
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""FALSIFIER for CHANGE 5: with section 7.7 promoted, the A4 fail-safe's
severity condition is a TAUTOLOGY, and the obvious repair is UNREACHABLE.

Both halves are asserted here because the second is what stopped me shipping a
patch, and a panel that reports only the half that suits its proposal is not
reporting.

── THE DEFECT, DERIVED ──────────────────────────────────────────────────────
`effective_severity` is read at exactly ONE decision site,
`FindingRegistry.blocking_entry_ids`, whose release rule is

    if effective_severity(e) < CRITICAL_SEVERITY_THRESHOLD and severity_is_proven(e):
        continue                       # released; stops blocking convergence

With the specification deciding it returns `asserted * V`. Every entry whose
blocking decision is still IN PLAY there carries V <= 0.5: V = 1.0 requires
`falsifier_verdict == "CONFIRMED"`, and `_FALSIFIER_RESOLVED_VERDICTS ==
{"CONFIRMED"}`, so such an entry is released by the falsifier test 4 lines
later whatever the severity door decides. Severity is a [0, 1] score, so

    asserted * V  <=  0.5  <  0.7  =  CRITICAL_SEVERITY_THRESHOLD

UNCONDITIONALLY. The severity half of the conjunction is constant-true and the
door collapses to `severity_is_proven(e)` alone. A PROVEN, asserted-1.0,
unresolved critical is released from the A4 fail-safe.

── WHY NO PATCH IS DELIVERED, measured rather than argued ───────────────────
The obvious repair -- leave the `V(None) = 0.5` stand-in at identity and keep
only the measured factors V = 0 and V = 1 -- was written, executed, and
WITHDRAWN. Over 75 archived `runner_state.json` files and 3,617 registry
entries, the population it would still release is 1 entry UNCONFIRMED+REFUTED,
of which 0 are also proven. It is an addition nothing reaches, which the
project's additive standard forbids as squarely as it forbids a vacuous gate.
The committed form releases 30 of 3,617 -- every proven UNCONFIRMED entry,
at any asserted severity.

So the two available forms are "release everything proven" and "release
nothing", and neither is section 7.7. With V the only collected factor the
specification has NO discriminating power at a cut of 0.7, because its range on
the in-play domain is [0, 0.5]. Promotion needs the cut re-derived on the
specification's own scale -- which is precisely the full-range adjudication
CHANGE 8 costs. Changes 5 and 8 are one problem.

Run: python3 -m pytest bench/tests/test_the_severity_spec_annihilates_the_a4_severity_door_2026-10-28.py -q -s
"""
from __future__ import annotations

import glob
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import reference_runner_v3 as rr  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]
IN_PLAY_VERDICTS = ("", "REFUTED", "PENDING", "UNRESOLVED", None)


def _entry(severity: float, verdict="", proven: bool = True) -> dict:
    return {"status": "UNCONFIRMED", "severity": severity,
            "falsifier_code": "", "falsifier_verdict": verdict,
            "severity_proof": ({"status": "PASS"} if proven else None),
            "open_since_round": 1}


def _registry(entries: dict):
    reg = object.__new__(rr.FindingRegistry)
    reg.entries = entries
    return reg


def _spec(flag: bool):
    rr.wire_module_mirrors(rr.RunnerConfig(severity_spec_enabled=flag))


def test_a_proven_asserted_one_point_zero_critical_is_released():
    """The defect, on the real reader."""
    reg = _registry({"C1": _entry(1.0)})
    try:
        _spec(False)
        off = reg.blocking_entry_ids()
        _spec(True)
        on = reg.blocking_entry_ids()
    finally:
        _spec(False)
    print(f"asserted 1.0, PROVEN, unresolved falsifier: "
          f"spec OFF blocks={off}  spec ON blocks={on}")
    assert off == ["C1"], "the asserted path must block a 1.0 critical"
    assert on == [], (
        "FALSIFIER REFUTED: the flag did not release it after all")


def test_the_severity_condition_is_constant_true_over_the_in_play_domain():
    _spec(True)
    try:
        worst = max(rr.effective_severity(_entry(s, v))
                    for s in (0.0, 0.5, 0.7, 0.9, 1.0)
                    for v in IN_PLAY_VERDICTS)
    finally:
        _spec(False)
    print(f"max effective_severity over the in-play domain = {worst}; "
          f"CRITICAL_SEVERITY_THRESHOLD = {rr.CRITICAL_SEVERITY_THRESHOLD}")
    assert worst < rr.CRITICAL_SEVERITY_THRESHOLD, (
        "not a tautology -- some in-play entry can still reach the cut")


def test_z3_agrees_no_in_play_entry_can_reach_the_cut():
    """Second tool, on the real constants."""
    try:
        import z3
    except ImportError:                                      # pragma: no cover
        print("z3 unavailable -- cross-check skipped")
        return
    sev, V = z3.Real("asserted"), z3.Real("V")
    s = z3.Solver()
    s.add(sev >= 0, sev <= 1)
    s.add(z3.Or(V == z3.RealVal("1/2"), V == 0))        # the in-play factors
    s.add(sev * V >= z3.RealVal("7/10"))
    res = s.check()
    print(f"z3: exists an in-play entry with asserted*V >= 0.7 ?  {res}")
    assert res == z3.unsat


def test_the_withdrawn_repair_would_have_been_unreachable():
    """The measurement that stopped a patch being shipped."""
    files = glob.glob(str(REPO / "bench" / "**" / "runner_state.json"),
                      recursive=True)
    if not files:
        import pytest
        pytest.skip("no archived runner_state.json in this checkout")
    total = unconf = proven = refuted = refuted_proven = 0
    for f in files:
        try:
            d = json.load(open(f))
        except Exception:                                    # noqa: BLE001
            continue
        for e in ((d.get("registry") or {}).get("entries") or {}).values():
            total += 1
            if e.get("status") != "UNCONFIRMED":
                continue
            unconf += 1
            pr = rr.severity_is_proven(e)
            proven += pr
            if str(e.get("falsifier_verdict") or "").upper() == "REFUTED":
                refuted += 1
                refuted_proven += pr
    print(f"archive: {len(files)} states, {total} entries, {unconf} UNCONFIRMED; "
          f"proven {proven}; UNCONFIRMED+REFUTED {refuted}, also proven "
          f"{refuted_proven}")
    assert refuted_proven == 0, (
        "the V=0-only repair IS reachable after all -- reconsider shipping it")
    assert proven > 0, (
        "the committed form reaches nothing either, which would make the whole "
        "promotion an addition nothing reaches")


def test_the_convergence_critical_series_is_untouched_by_the_flag():
    """The suspected change-5 / change-1-2 interaction does NOT run via crit_s."""
    reg = _registry({
        "C1": {"status": "OPEN", "severity": 0.9, "open_since_round": 1,
               "falsifier_verdict": "REFUTED"},
        "C2": {"status": "OPEN", "severity": 0.8, "open_since_round": 2,
               "falsifier_verdict": ""}})
    try:
        _spec(False)
        _, crit_off = rr._settled_novelty_series(reg, 3)
        _spec(True)
        _, crit_on = rr._settled_novelty_series(reg, 3)
    finally:
        _spec(False)
    print(f"crit_s spec OFF = {crit_off}   spec ON = {crit_on}")
    assert crit_off == crit_on, (
        "the gate's critical series DID move -- the brief's suspected "
        "interaction is real and this claim is refuted")
    assert sum(crit_on) == 2
