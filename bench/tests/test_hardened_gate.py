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

SUPERSEDED CONTRACT REMOVED 2026-10-08. This docstring stated that gamma is
"reported-not-gated" in the sparse branch. That contract no longer exists: the
founder ruled on 2026-10-08 that gamma remains active in all cases, and the fable
seat found this text still asserting the removed behaviour. A stale guarantee in a
docstring is how a rejected position acquires authority here.

What now holds: gamma GATES wherever a curve is estimable. Where no curve exists,
guarded vacuity applies -- cumulative critical over the whole history must be zero
AND the panel must have produced findings of some severity, and the second guard
refuses. The sibling gate's A4 and contested preconditions are derived in-gate and
can refuse before any convergence path.
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


# ─────── UPDATED 2026-10-08 ON THE FOUNDER'S RULING, NOT DELETED ───────
# His words: *"Gamma should remain active in all cases. Fix it."* The 2 tests
# below used to assert the behaviour the ruling removes -- one of them was named
# `test_sparsity_fallback_converges_on_count_only` and required the phrase
# "reported-not-gated" to appear in the reason. They were guarding the defect.
#
# They are rewritten to the new truth rather than removed, so the behaviour they
# cover stays covered: a sparse pool now GATES on gamma wherever gamma is
# estimable, and only where the estimator returns its 0.0 sentinel -- too few
# rounds, an all-zero series, fewer than 2 usable log points, a degenerate fit --
# does the zero-critical window decide alone. The mode names which case.
#
# WHY THE SENTINEL CASE MUST SURVIVE: a CLEAN run has an all-zero critical series
# by construction, and 3 consecutive clean convergences on the prose target is the
# programme of study's success criterion. Gating on a sentinel is not gating on
# gamma; it would make a clean target unable to converge.

def test_sparse_pool_gates_on_gamma_when_it_is_estimable():
    crit = [2, 1, 0, 0, 0]              # cum=3 < 8, and gamma IS estimable here
    ok, reason, telem = rr._check_hardened_convergence(
        4, _Reg(crit), _cfg())
    assert rr._gamma_is_estimable(crit) is True
    assert telem["mode"] == "sparsity_gamma_gated"
    assert telem["gamma_crit_gated"] is True
    assert "reported-not-gated" not in reason, (
        "the phrase that named the demotion is back in a sparse-pool reason")
    # the outcome follows gamma, not the count alone
    g = rr._estimate_gamma(crit)
    assert ok is (g >= _cfg().gamma_alt_threshold), (g, ok, reason)


def test_a_clean_target_converges_under_guarded_vacuity():
    """No critical curve exists, AND the panel demonstrably produced findings.

    UPDATED 2026-10-08. The first version passed `_Reg([0,0,0,0])` with no
    non-critical findings, which builds an EMPTY registry -- so it was modelling a
    DEAD PANEL and calling it a clean target. The gate now refuses that case, and
    the test was wrong rather than the gate. A clean target means the panel worked
    and nothing it found was critical, which is what the non-critical series below
    supplies.
    """
    crit = [0, 0, 0, 0]
    ok, reason, telem = rr._check_hardened_convergence(
        3, _Reg(crit, noncrit_per_round=[5, 4, 5, 4]), _cfg())
    assert rr._gamma_is_estimable(crit) is False
    assert telem["mode"] == "vacuous_curve_converged", telem
    assert telem["gamma_crit_gated"] is False
    assert telem["total_findings"] == 18, telem
    assert ok is True, (
        "a clean all-zero critical series over a working panel must still "
        f"converge, or the programme of study cannot meet its own success "
        f"criterion: {reason}")
    assert "REVIEW THIS RUN" in reason


def test_a_dead_panel_is_refused_not_converged():
    """The guard that makes the narrowing a domain restriction, not a demotion.

    Zero criticals AND zero findings of any severity is a dead panel or a broken
    severity classifier, not an exhausted error space.
    """
    crit = [0, 0, 0, 0]
    ok, reason, telem = rr._check_hardened_convergence(
        3, _Reg(crit), _cfg())          # EMPTY registry: nothing came back
    assert ok is False, (
        "a run whose panel returned nothing at all converged; that is the "
        "failure-looks-like-success shape this project keeps paying for")
    assert telem["mode"] == "vacuous_curve_refused_dead_panel", telem
    assert telem["total_findings"] == 0
    assert "dead panel" in reason


def test_sparse_pool_blocks_when_zero_crit_not_met():
    crit = [2, 1, 0, 1, 0]             # cum=4 < 8; last 3 = [0,1,0]
    ok, reason, telem = rr._check_hardened_convergence(
        4, _Reg(crit), _cfg())
    assert ok is False
    assert telem["mode"].startswith("sparsity_gamma_")
    assert "window not satisfied" in reason


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
