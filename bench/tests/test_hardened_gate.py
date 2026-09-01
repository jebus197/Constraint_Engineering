"""Regression tests for the Exp 40 hardened convergence gate
(F4 settled-registry + F6 critical-severity constant + conjunction +
dual-series + sparsity fallback; founder-directed 2026-05-18).

Contract:
  - _settled_novelty_series reads the SETTLED registry by the runner's
    own post-reconciliation rule (open_since_round==r AND status not in
    the non-novel terminal set), split all vs critical (sev >=
    CRITICAL_SEVERITY_THRESHOLD).
  - _check_hardened_convergence is the CONJUNCTION: converged iff
    (γ_crit ≥ θ, sustained, leave-one-round-out robust) AND (W
    consecutive settled zero-novel-critical rounds). Sparsity fallback:
    if cumulative critical < min, gate on the count criterion alone,
    γ reported-not-gated. γ_all is diagnostic only and never gates.
  - Default-off: existing experiments keep the legacy γ-alt OR gate
    unchanged (covered by the existing γ-alt tests, re-run in the
    sweep).
"""
from __future__ import annotations

import types

import pytest

import bench.reference_runner_v3 as rr


def _cfg(**over):
    base = dict(
        gamma_alt_threshold=0.30,
        gamma_alt_consecutive_zero_crit=3,
        gamma_alt_earliest_round=3,
        gamma_crit_sustain_rounds=2,
        gamma_crit_min_cumulative=8,
        gamma_crit_loo_tol=0.05,
    )
    base.update(over)
    return types.SimpleNamespace(**base)


class _Reg:
    """Minimal registry: .entries dict of canonical_id -> entry dict."""

    def __init__(self, crit_per_round, noncrit_per_round=None,
                 status="CONFIRMED"):
        self.entries = {}
        n = 0
        for r, c in enumerate(crit_per_round):
            for _ in range(c):
                self.entries[f"C{n:04d}"] = {
                    "open_since_round": r, "status": status,
                    "severity": 0.85}
                n += 1
        if noncrit_per_round:
            for r, c in enumerate(noncrit_per_round):
                for _ in range(c):
                    self.entries[f"C{n:04d}"] = {
                        "open_since_round": r, "status": status,
                        "severity": 0.4}
                    n += 1


def test_settled_series_excludes_non_novel_and_splits_severity():
    reg = _Reg([2, 0, 1], noncrit_per_round=[1, 1, 0])
    # add a MERGED + an UNCONFIRMED at round 0 — must be excluded
    reg.entries["X1"] = {"open_since_round": 0, "status": "MERGED",
                         "severity": 0.9}
    reg.entries["X2"] = {"open_since_round": 1, "status": "UNCONFIRMED",
                         "severity": 0.9}
    all_s, crit_s = rr._settled_novelty_series(reg, 2)
    assert crit_s == [2, 0, 1]
    assert all_s == [3, 1, 1]  # crit + noncrit, terminal-status excluded


def test_too_early_returns_not_converged():
    reg = _Reg([1, 1, 1])
    ok, reason, _ = rr._check_hardened_convergence(2, reg, _cfg())
    assert ok is False and "too early" in reason


def test_full_mode_conjunction_converges():
    crit = [5, 3, 1, 0, 0, 0]            # strong decay, zero tail
    g = rr._estimate_gamma(crit)
    assert g >= 0.30 and sum(crit) >= 8   # precondition: full mode
    ok, reason, telem = rr._check_hardened_convergence(
        5, _Reg(crit), _cfg())
    assert ok is True
    assert "HARDENED_CONVERGED" in reason
    assert telem["mode"] == "full" and telem["zero_crit_ok"] is True


def test_conjunction_blocks_when_late_critical_appears():
    crit = [5, 3, 1, 0, 0, 2]            # γ may be high, but R5 has a crit
    ok, reason, telem = rr._check_hardened_convergence(
        5, _Reg(crit), _cfg())
    assert ok is False
    assert telem["zero_crit_ok"] is False


def test_sparsity_fallback_converges_on_count_only():
    crit = [2, 1, 0, 0, 0]              # cum=3 < 8 -> sparsity fallback
    ok, reason, telem = rr._check_hardened_convergence(
        4, _Reg(crit), _cfg())
    assert ok is True
    assert telem["mode"] == "sparsity_fallback"
    assert "reported-not-gated" in reason


def test_sparsity_fallback_blocks_when_zero_crit_not_met():
    crit = [2, 1, 0, 1, 0]             # cum=4 < 8; last 3 = [0,1,0]
    ok, reason, telem = rr._check_hardened_convergence(
        4, _Reg(crit), _cfg())
    assert ok is False and telem["mode"] == "sparsity_fallback"


def test_gamma_all_is_diagnostic_only_never_gates():
    # crit decays strongly to a zero tail (would converge); all-novelty
    # is large & flat (γ_all low) — must NOT block convergence.
    crit = [5, 3, 1, 0, 0, 0]
    noncrit = [9, 9, 9, 9, 9, 9]
    ok, reason, telem = rr._check_hardened_convergence(
        5, _Reg(crit, noncrit_per_round=noncrit), _cfg())
    assert ok is True
    assert "gamma_all_settled" in telem            # logged
    assert telem["gamma_all_settled"] < telem["gamma_crit_settled"]


def test_knife_edge_single_round_crossing_rejected():
    # Construct a critical series whose γ clears θ only at the final
    # point (prefix γ < θ): the sustained check must reject it.
    found = None
    for rise in range(3, 9):
        for lvl in (1, 2, 3):
            for tail in range(0, 14):
                s = [lvl] * rise + [0] * tail
                if (sum(s) >= 8
                        and rr._estimate_gamma(s) >= 0.30
                        and rr._estimate_gamma(s[:-1]) < 0.30):
                    found = s
                    break
            if found:
                break
        if found:
            break
    assert found is not None, (
        "expected a knife-edge integer series (full γ≥0.30 but "
        "prefix γ<0.30) to exist in the search space")
    ok, reason, telem = rr._check_hardened_convergence(
        len(found) - 1, _Reg(found), _cfg())
    assert ok is False
    assert telem.get("sustained") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
