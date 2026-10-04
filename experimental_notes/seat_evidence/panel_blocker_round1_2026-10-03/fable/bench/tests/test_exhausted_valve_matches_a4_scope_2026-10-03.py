# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'panel_blocker_round1_2026-10-03', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ed87a42f5d48d72417a9848239e4d7a97e7b7e9b8b9f9e9c3a49801ad0dcf001
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The exhausted valve releases what the A4 counter blocks (panel 2026-10-03).

Run study_run1b_2026-10-03 ended BUDGET-EXHAUSTED with exactly 2 registry
entries holding the A4 fail-safe: C0066 (severity 0.45) and C0073 (0.50),
both UNCONFIRMED with verdicts == [] and no falsifier. Since founder ruling
23 (2026-09-06) unverified_critical_count is severity-free, but every exit
was not:

  * pre-pass 1's valve required severity >= 0.7  (Position A's site), AND
  * its has_reviews read ONLY `verdicts`, while the panel's five reasoned
    withdrawals per entry sat in `computed_evidence`, written by the
    WITHDRAW door that may not retire an unproven severity
    (Position B's discriminator).

Executed arm isolation over the archived registry, rounds 8..40
(scripts/a4_blocker_arm_isolation_2026-10-03.py): shipped code A4=2 forever;
either arm alone A4=2 forever; both arms A4 -> 1 at round 13, 0 at round 15,
statuses still UNCONFIRMED. The composition beats each arm alone because
each arm alone equals doing nothing on this registry.

Mutation map, EXECUTED 2026-10-03 (pre-pass-1 fix reverted by exact hunk
swap, then restored byte-identical): 4 fail, 5 pass.
  FAIL test_run1b_blockers_release_at_threshold_age   (A4 stays 2 at r13/15)
  FAIL test_subcritical_unconfirmed_with_recorded_withdrawal_exhausts
  FAIL test_severity_arm_alone_is_insufficient   (shipped code never enters
       the valve for a sub-critical UNCONFIRMED entry, so `exhausted` is
       POPPED, not False -- the assertion fails on key absence)
  FAIL test_age_guard_kept                       (same key-absence shape)
  PASS test_run1b_before_state_is_the_briefed_one (a fact, fix-independent)
  PASS test_evidence_arm_alone_is_insufficient_without_scope_match
  PASS test_no_recorded_activity_never_exhausts
  PASS test_critical_open_path_is_byte_identical
  PASS test_gate_before_and_after
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench import reference_runner_v3 as rv  # noqa: E402

RUN_DIR = ROOT / "bench/logs/study_run1b_2026-10-03_20261003T100439Z"
STATE = json.loads((RUN_DIR / "runner_state.json").read_text())

CFG = SimpleNamespace(exhausted_round_threshold=8, max_contested_rounds=3,
                      merge_arbitration_enabled=False, models=[],
                      test_article="", test_cmd="", fix_efficacy_mode="off")


def _rehydrate():
    return rv.FindingRegistry.from_dict(copy.deepcopy(STATE["registry"]))


def _entry(status="UNCONFIRMED", severity=0.45, verdicts=(), evidence=(),
           changed=0):
    return {"status": status, "severity": severity,
            "verdicts": list(verdicts),
            "computed_evidence": list(evidence),
            "last_status_change_round": changed,
            "source_model": "SRC-SIM", "open_since_round": changed,
            "escalated": False}


def _ev():
    return {"kind": "reasoned_withdrawal", "by": "CC2-SIM", "detail": "x"}


def _reg(*entries):
    r = rv.FindingRegistry()
    for i, e in enumerate(entries):
        r.entries[f"C{i:04d}"] = e
    return r


# ── The archived run, through the real registry and the real pre-pass ──

def test_run1b_before_state_is_the_briefed_one():
    reg = _rehydrate()
    assert reg.unverified_critical_count() == 2
    for cid, sev in (("C0066", 0.45), ("C0073", 0.5)):
        e = reg.entries[cid]
        assert e["status"] == "UNCONFIRMED"
        assert e["severity"] == sev
        assert e["verdicts"] == []
        assert not (e.get("falsifier_code") or "").strip()
        assert len(e.get("computed_evidence") or []) >= 1  # withdrawals ON FILE


def test_run1b_blockers_release_at_threshold_age():
    reg = _rehydrate()
    seen = {}
    for r in range(8, 16):
        rv._update_finding_statuses(reg, r, CFG)
        seen[r] = reg.unverified_critical_count()
    # exhausted_round_threshold=8: C0066 (UNCONFIRMED since r5) ages out at 13,
    # C0073 (since r7) at 15. Severity floats played no part.
    assert seen[12] == 2
    assert seen[13] == 1
    assert seen[15] == 0
    # ADDITIVE both ways: released from the COUNT, not retired. The entries
    # stay UNCONFIRMED -- the designed HIL hand-off state -- and nothing
    # upstream was closed, merged or deleted by the release.
    for cid in ("C0066", "C0073"):
        assert reg.entries[cid]["status"] == "UNCONFIRMED"
        assert reg.entries[cid]["exhausted"] is True
    assert reg.entries["C0069"]["status"] == "CLOSED"  # untouched neighbours
    assert reg.entries["C0042"]["status"] == "CLOSED"


# ── Arm isolation on a minimal synthetic entry (pins BOTH arms) ──

def test_subcritical_unconfirmed_with_recorded_withdrawal_exhausts():
    reg = _reg(_entry(severity=0.45, evidence=[_ev()], changed=0))
    rv._update_finding_statuses(reg, 8, CFG)
    assert reg.entries["C0000"]["exhausted"] is True
    assert reg.unverified_critical_count() == 0


def test_severity_arm_alone_is_insufficient():
    # verdicts == [] and computed_evidence == []: even with the severity
    # clause widened, "requires review activity" refuses -- Position A's
    # repair alone is a no-op on the run-1b shape.
    reg = _reg(_entry(severity=0.45, changed=0))
    rv._update_finding_statuses(reg, 40, CFG)
    assert reg.entries["C0000"]["exhausted"] is False
    assert reg.unverified_critical_count() == 1


def test_evidence_arm_alone_is_insufficient_without_scope_match():
    # The same withdrawal evidence on a non-UNCONFIRMED sub-critical does
    # NOT buy an exhausted flag: the valve only widened where its reader
    # (unverified_critical_count) is severity-free.
    reg = _reg(_entry(status="OPEN", severity=0.45, evidence=[_ev()],
                      changed=0))
    rv._update_finding_statuses(reg, 40, CFG)
    assert "exhausted" not in reg.entries["C0000"]


def test_no_recorded_activity_never_exhausts():
    reg = _reg(_entry(severity=0.9, changed=0))
    rv._update_finding_statuses(reg, 40, CFG)
    assert reg.entries["C0000"]["exhausted"] is False
    assert reg.unverified_critical_count() == 1


def test_age_guard_kept():
    reg = _reg(_entry(severity=0.45, evidence=[_ev()], changed=0))
    rv._update_finding_statuses(reg, 7, CFG)  # age 7 < threshold 8
    assert reg.entries["C0000"]["exhausted"] is False
    assert reg.unverified_critical_count() == 1


def test_critical_open_path_is_byte_identical():
    # The pre-fix clientele of the valve: OPEN critical with verdict rows.
    reg = _reg(_entry(status="OPEN", severity=0.8,
                      verdicts=[{"model": "m", "verdict": "CHALLENGE",
                                 "round": 1}], changed=0))
    rv._update_finding_statuses(reg, 8, CFG)
    assert reg.entries["C0000"]["exhausted"] is True
    reg2 = _reg(_entry(status="OPEN", severity=0.8, changed=0))
    rv._update_finding_statuses(reg2, 8, CFG)
    assert reg2.entries["C0000"]["exhausted"] is False


# ── The gate, called, not inferred ──

def test_gate_before_and_after():
    gcfg = SimpleNamespace(gamma_alt_earliest_round=3,
                           gamma_alt_consecutive_zero_crit=3,
                           gamma_alt_threshold=0.3,
                           max_irreducible_queue=2, rho_threshold=0.25)
    nch = STATE["novel_critical_history"]
    # As run: A4=2 blocks.
    ok, reason = rv._check_gamma_alt_convergence(
        7, 0.4274, nch, gcfg, unresolved_critical=2, gamma_critical=0.7323)
    assert not ok and reason.startswith("A4 BLOCK")
    # HONESTY PIN: the repair does NOT rescue run 1b at its cap. With A4=0
    # at round 7 the tail is [1, 0, 0] (a novel critical landed at round 5),
    # so the two-sided gate still refuses -- non-convergence at round 7 was
    # overdetermined. A test asserting True here would be the closing-sweep
    # rescue the design forbids.
    ok, reason = rv._check_gamma_alt_convergence(
        7, 0.4274, nch, gcfg, unresolved_critical=0, gamma_critical=0.7323)
    assert not ok and "novel_crit_recent=[1, 0, 0]" in reason
    # Continuation shape: zero tail + released A4 converges.
    ok, _ = rv._check_gamma_alt_convergence(
        9, 0.4274, nch + [0, 0], gcfg, unresolved_critical=0,
        gamma_critical=0.7323)
    assert ok
