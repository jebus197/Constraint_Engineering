# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'integrity_advisory_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 035fdf4011f235e7333eab397a0d406ba1654d51e3ae45103cb064f25d5f8f66
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Panel round 2 (2026-10-02), seat fable: the surviving D2/D3 variant.

The ruling: a key-access integrity refusal must not BLOCK convergence, and must
be REPORTED at the end of the run. The surviving variant is the synthesis of
both round-1 implementations:

  * release is decided by ONE shared predicate (`_integrity_released`) consumed
    by `_irreducible_queue_split`, `unverified_critical_count` AND the halt
    alarm's evidence collector (cc2's shared-predicate property);
  * the observer-did-not-install class (`integrity_unobserved`) is carved out
    and KEEPS BLOCKING (fable's carve-out) -- a machine-wide sitecustomize
    failure must not drain every critical out of A4;
  * the release is paired with a MANDATORY record
    (`integrity_refused_criticals`), a per-round KEY-ACCESS ADVISORY log line,
    and a `key_access_advisory` field in completion_signal.json (cc2's record,
    extended to the signal per D-4);
  * a refusal landing on a ROUTING RUNG (run 1b's C0029: entry label stays
    UNTOOLABLE/ERROR) is stamped at the rung site, so the shared predicate
    covers the ladder-side path too (D-6).
"""
from __future__ import annotations

import inspect
import json
import types
from pathlib import Path

import pytest

from bench import falsifier_verify as fv
from bench.reference_runner_v3 import (
    EQUIPMENT_FAILURE_VERDICTS,
    INTEGRITY_REFUSED_VERDICT,
    ROUTABLE_INSTRUMENT_FAULTS,
    FindingRegistry,
    RunnerConfig,
    _check_gamma_alt_convergence,
    _classify_integrity_refusal,
    _integrity_released,
    _irreducible_queue_split,
    _stamp_integrity_refusal,
)

REPO = Path(__file__).resolve().parents[2]
RUN1B = REPO / "bench/logs/prose_convergence_run1b_2026-10-02_20261002T044234Z"


def _reg(**entry) -> FindingRegistry:
    r = FindingRegistry()
    base = {"status": "UNCONFIRMED", "severity": 0.8, "description": "x"}
    base.update(entry)
    r.entries["C9001"] = base
    return r


# ── the verdict constant ─────────────────────────────────────────────────────

def test_verdict_constant_pinned_to_the_gate_and_in_neither_fault_set():
    assert INTEGRITY_REFUSED_VERDICT == fv.INTEGRITY_VIOLATION
    assert INTEGRITY_REFUSED_VERDICT not in EQUIPMENT_FAILURE_VERDICTS
    assert INTEGRITY_REFUSED_VERDICT not in ROUTABLE_INSTRUMENT_FAULTS


# ── release + report ─────────────────────────────────────────────────────────

def test_key_access_refusal_is_released_from_both_counters_and_reported():
    r = _reg(integrity_refused=True,
             irreducible_escalation=True, routing_deferred=True,
             integrity_refusal_events=[{"round": 0, "site": "entry",
                                        "kind": "key_access", "reason": "r"}])
    assert r.unverified_critical_count() == 0          # A4 released
    assert r.irreducible_queue_count() == 0            # queue/halt released
    rec = r.integrity_refused_criticals()              # ...and REPORTED
    assert [x["canonical_id"] for x in rec] == ["C9001"]
    assert rec[0]["events"][0]["site"] == "entry"


def test_without_the_flag_it_still_blocks_so_the_release_is_not_vacuous():
    r = _reg()
    assert r.unverified_critical_count() == 1
    r2 = _reg(routing_deferred=True)
    assert r2.irreducible_queue_count() == 1
    assert r2.integrity_refused_criticals() == []


def test_unobserved_refusal_keeps_blocking_and_is_not_reported_as_released():
    # fable's carve-out: observer-did-not-install is EQUIPMENT, not key access.
    r = _reg(integrity_refused=True, integrity_unobserved=True,
             routing_deferred=True)
    assert not _integrity_released(r.entries["C9001"])
    assert r.unverified_critical_count() == 1
    assert r.irreducible_queue_count() == 1
    assert r.integrity_refused_criticals() == []


def test_shared_predicate_means_all_or_none():
    # cc2's property: an entry is excluded from BOTH counters or NEITHER.
    # routing_deferred is the state BOTH counters observe pre-release (an
    # irreducible_escalation entry is already excluded from A4 by the
    # pre-existing HIL-handoff rule, so it cannot witness this property).
    for flags in ({}, {"integrity_refused": True},
                  {"integrity_refused": True, "integrity_unobserved": True}):
        r = _reg(routing_deferred=True, **flags)
        released = _integrity_released(r.entries["C9001"])
        assert (r.unverified_critical_count() == 0) == released
        assert (r.irreducible_queue_count() == 0) == released


def test_report_is_not_severity_gated():
    # cc2's own named weakness: a model-assigned float (AUC 0.464) must not be
    # able to hide the record by drifting below 0.7.
    r = _reg(integrity_refused=True, severity=0.2)
    assert [x["canonical_id"] for x in r.integrity_refused_criticals()] == ["C9001"]


def test_terminal_entries_leave_the_report():
    r = _reg(integrity_refused=True, status="CLOSED")
    assert r.integrity_refused_criticals() == []


# ── the classifier at the stamp site ─────────────────────────────────────────

def _with_rejection(violations):
    fv.INTEGRITY_REJECTIONS.append(
        {"where": "t", "violations": violations, "code_head": ""})


def test_classifier_key_access_vs_unobserved(monkeypatch):
    monkeypatch.setattr(fv, "INTEGRITY_REJECTIONS", [])
    _with_rejection([{"reason": "an answer-key file path",
                      "matched": "exam_answer_key.json"}])
    assert _classify_integrity_refusal()[0] == "key_access"
    _with_rejection([{"reason": "the runtime observer did not install, so this "
                                "falsifier ran with no boundary",
                      "matched": "observer trace absent"}])
    assert _classify_integrity_refusal()[0] == "unobserved"


def test_classifier_fail_safe_default_is_block(monkeypatch):
    monkeypatch.setattr(fv, "INTEGRITY_REJECTIONS", [])
    kind, reason = _classify_integrity_refusal()
    assert kind == "unobserved"        # no evidence -> keeps blocking
    _with_rejection([])
    assert _classify_integrity_refusal()[0] == "unobserved"


def test_stamp_routes_by_kind(monkeypatch):
    monkeypatch.setattr(fv, "INTEGRITY_REJECTIONS", [])
    _with_rejection([{"reason": "a claims->truth lookup (the answer-key schema)",
                      "matched": 'key["claims"]["CH-13"]["truth"]'}])
    e: dict = {}
    assert _stamp_integrity_refusal(e, 3, "routing_rung") == "key_access"
    assert e.get("integrity_refused") and not e.get("integrity_unobserved")
    assert e["integrity_refusal_events"][0]["site"] == "routing_rung"
    _with_rejection([{"reason": "x", "matched": "observer trace absent"}])
    e2: dict = {}
    assert _stamp_integrity_refusal(e2, 3, "entry") == "unobserved"
    assert e2.get("integrity_unobserved") and not e2.get("integrity_refused")


# ── D-6: the ladder-side path, replayed from run 1b's own record ─────────────

def test_d6_rung_refusal_shape_from_run1b_is_released_once_stamped(monkeypatch):
    """Run 1b's C0029: entry verdict UNTOOLABLE/ERROR, rung verdict
    INTEGRITY_VIOLATION. An entry-verdict predicate alone never sees it; the
    rung-site stamp is what brings it under the shared predicate."""
    st = json.loads((RUN1B / "runner_state.json").read_text())
    c29 = st["registry"]["entries"]["C0029"]
    assert [h["verdict"] for h in c29["routing_history"]] == ["INTEGRITY_VIOLATION"]
    # The halt-round shape: live, deferred, entry label is an equipment verdict.
    live = {"status": "UNCONFIRMED", "severity": c29["severity"],
            "falsifier_verdict": "UNTOOLABLE", "routing_deferred": True}
    r = FindingRegistry(); r.entries["C0029"] = live
    assert r.irreducible_queue_count() == 1            # pre-stamp: in the queue
    monkeypatch.setattr(fv, "INTEGRITY_REJECTIONS", [])
    _with_rejection([{"reason": "an answer-key file path", "matched": "k.json"}])
    _stamp_integrity_refusal(live, 2, "routing_rung")
    assert r.irreducible_queue_count() == 0            # post-stamp: released
    assert r.unverified_critical_count() == 0
    assert [x["canonical_id"] for x in r.integrity_refused_criticals()] == ["C0029"]


# ── REQUIRED SECTION 2: gate input invariance + S_k untouched ────────────────

def test_gate_input_invariance_queue_reaches_only_the_halt():
    cfg = RunnerConfig()
    kw = dict(round_idx=max(6, getattr(cfg, "gamma_alt_earliest_round", 6)),
              gamma=0.432,
              novel_critical_history=[3, 1, 0, 0, 0, 0, 0, 0],
              cfg=cfg, unresolved_critical=0, contested=0, rho_churn=False,
              gamma_critical=0.336, total_findings=40)
    a = _check_gamma_alt_convergence(irreducible_queue=0, **kw)
    b = _check_gamma_alt_convergence(irreducible_queue=3, **kw)
    assert a[0] == b[0], (a, b)        # the queue reaches only the halt
    assert a[0] is True, a             # and both gate conditions pass here


def test_a4_still_blocks_the_gate_so_the_invariance_test_is_not_vacuous():
    cfg = RunnerConfig()
    kw = dict(round_idx=max(6, getattr(cfg, "gamma_alt_earliest_round", 6)),
              gamma=0.432,
              novel_critical_history=[3, 1, 0, 0, 0, 0, 0, 0],
              cfg=cfg, contested=0, rho_churn=False,
              gamma_critical=0.336, total_findings=40, irreducible_queue=0)
    blocked = _check_gamma_alt_convergence(unresolved_critical=1, **kw)
    assert blocked[0] is False and "A4 BLOCK" in blocked[1]


def test_new_paths_read_no_sk_state():
    from bench import reference_runner_v3 as rr
    for fn in (rr._classify_integrity_refusal, rr._stamp_integrity_refusal,
               rr._integrity_released,
               rr.FindingRegistry.integrity_refused_criticals):
        src = inspect.getsource(fn)
        assert "sk_" not in src, fn.__name__


def test_sk_tristates_of_run1b_are_what_the_archive_says():
    st = json.loads((RUN1B / "runner_state.json").read_text())
    from collections import Counter
    c = Counter((e.get("sk_result") or {}).get("tristate", "(none)")
                for e in st["registry"]["entries"].values())
    assert c == Counter({"NO_SCORE": 30, "REJECTED": 6, "(none)": 4})


# ── D-4: the advisory lands where the status lands ───────────────────────────

def test_completion_signal_carries_advisory_and_repo_root(tmp_path):
    from bench.insect_brain import InsectBrain
    fake = types.SimpleNamespace()
    fake.state = types.SimpleNamespace(
        converged=True, failed=False, convergence_reason="CRITICAL_QUIESCENCE",
        stop_reason="", failure_reason="", all_findings=[], round_records=[],
        active_models=["m"])
    fake.logs_dir = tmp_path
    written = {}
    fake._atomic_write_json = lambda fp, obj: written.update(obj)
    sig = InsectBrain.signal_complete(
        fake, extras={"repo_root": "/run/repo",
                      "key_access_advisory": [{"canonical_id": "C0035"}],
                      "status": "FORGED"})
    assert written["repo_root"] == "/run/repo"
    assert written["key_access_advisory"][0]["canonical_id"] == "C0035"
    assert written["status"] == "CONVERGED"   # extras cannot overwrite status


def test_signal_without_extras_is_unchanged(tmp_path):
    from bench.insect_brain import InsectBrain
    fake = types.SimpleNamespace()
    fake.state = types.SimpleNamespace(
        converged=False, failed=False, convergence_reason="",
        stop_reason="BUDGET_EXHAUSTED x", failure_reason="",
        all_findings=[], round_records=[], active_models=[])
    fake.logs_dir = tmp_path
    written = {}
    fake._atomic_write_json = lambda fp, obj: written.update(obj)
    InsectBrain.signal_complete(fake)
    assert "key_access_advisory" not in written and "repo_root" not in written
