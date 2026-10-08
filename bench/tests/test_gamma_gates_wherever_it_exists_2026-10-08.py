"""Gamma gates in every case where gamma exists, and the sentinel is named.

FOUNDER'S RULING, 2026-10-08: *"Gamma should remain active in all cases. Fix it."*
Issued after the fable seat found `reference_runner_v3.py` making gamma
"reported-not-gated" whenever the cumulative critical pool falls below
`gamma_crit_min_cumulative`, so the gate advertised as two-sided went ONE-SIDED in
precisely the endgame regime -- and the surviving half, the zero-novel-critical
window, is the half a shrinking roster attacks.

WHY THE BRANCH COULD NOT SIMPLY BE DELETED, which bounds the ruling by arithmetic
rather than by preference. `_estimate_gamma` returns 0.0 as a SENTINEL for 4
distinct reasons, only 1 of which is a slope of 0.0: fewer than `min_rounds`
points, an all-zero series, fewer than 2 usable log points, and a degenerate
denominator. A CLEAN run has an all-zero critical series by construction, so
gating unconditionally on that 0.0 would make a clean target unable to converge --
and 3 consecutive clean convergences on the prose target is the programme of
study's own success criterion. Gating on a sentinel is not gating on gamma.

WHAT THE FIX DOES. Gamma gates wherever it is ESTIMABLE, including in the sparse
branch where it previously did not. Where it is not estimable the fact is recorded
as `sparsity_gamma_unestimable` and the window decides alone -- the same outcome as
before, but no longer silent.

MEASURED REACHABILITY, because a change that bites nowhere is an unwired addition.
A flat tail pushes gamma up, so "window met AND gamma low" is a narrow band. An
exhaustive sweep over short series found it: `[1, 3, 0, 0, 0]` gives gamma 0.1783
and `[1, 4, 0, 0, 0]` gives 0.0461 -- both estimable, both sparse, both with the
window met. Both converged under the old code and are refused under the new.

THE SECOND HALF OF THE FIX. The gate's telemetry reached the log file and nothing
else: a scan of every *report*.json under bench/logs for a record carrying `mode`
returned 0, so no archived run says which mode closed it and the ruling would have
been unauditable even once implemented. It now lands on the round record.

Every test here CALLS the gate and the estimator. The mirror between
`_gamma_is_estimable` and `_estimate_gamma` is executed against shared inputs, so
the 2 cannot drift -- `execute-do-not-grep`.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def R():
    spec = importlib.util.spec_from_file_location(
        "rr_gamma", REPO / "bench" / "reference_runner_v3.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["rr_gamma"] = m
    spec.loader.exec_module(m)
    return m


class _Cfg:
    gamma_alt_threshold = 0.30
    gamma_alt_consecutive_zero_crit = 3
    gamma_crit_min_cumulative = 8
    gamma_alt_earliest_round = 0
    gamma_crit_sustain_rounds = 1
    gamma_crit_loo_tol = 1.0


class _Reg:
    """A registry stub carrying a findings count, which is the second guard."""

    def __init__(self, n_findings: int = 18):
        self.entries = {f"C{i:04d}": {} for i in range(n_findings)}


def _gate(R, crit, cfg=None, findings: int = 18):
    """Drive the real gate with a chosen settled critical series."""
    orig = R._settled_novelty_series
    try:
        R._settled_novelty_series = lambda _reg, _r: (crit, crit)
        return R._check_hardened_convergence(
            len(crit), _Reg(findings), cfg or _Cfg())
    finally:
        R._settled_novelty_series = orig


class TestTheMirrorCannotDrift:
    """Both functions are CALLED on the same inputs, never compared by reading."""

    @pytest.mark.parametrize("series", [
        [], [0], [0, 0], [0, 0, 0], [1, 0, 0], [0, 1, 2],
        [1, 2, 3, 4], [5, 0, 0, 0], [1, 3, 0, 0, 0], [2, 2, 2],
    ])
    def test_unestimable_implies_the_sentinel(self, R, series):
        if not R._gamma_is_estimable(series):
            assert R._estimate_gamma(series) == 0.0, (
                f"{series} is called unestimable yet the estimator returned a "
                "non-zero slope, so the predicate is wrong")

    def test_at_least_one_series_is_estimable_and_one_is_not(self, R):
        """A predicate that answered the same way always would prove nothing."""
        assert R._gamma_is_estimable([1, 3, 0, 0, 0]) is True
        assert R._gamma_is_estimable([0, 0, 0]) is False


class TestVacuityIsGuardedNotGranted:
    """THE FOUNDER'S SECOND CHALLENGE, 2026-10-08: *"if gamma remains unestimable,
    how can gamma ever hit the 0.30 mark ...? Isn't this gamma demotion by another
    name?"*

    He was right about the first version, which renamed the demotion as
    "unestimable" and left the behaviour unguarded. The answer already existed in
    the sibling gate as VACUOUS CURVE, with 2 guards, and is imported rather than
    re-invented: cumulative critical over the WHOLE history must be zero, and the
    panel must have produced findings of SOME severity. The second guard can
    REFUSE, which is what makes the narrowing a domain restriction rather than a
    demotion.
    """

    @pytest.mark.parametrize("series", [[0, 0, 0], [0, 0, 0, 0, 0], [0] * 8])
    def test_a_clean_target_converges_when_the_panel_demonstrably_worked(
            self, R, series):
        ok, why, telem = _gate(R, series, findings=18)
        assert ok is True, (why, telem)
        assert telem["mode"] == "vacuous_curve_converged", telem
        assert telem["gamma_crit_gated"] is False
        assert "UNDEFINED rather than low" in why
        assert "REVIEW THIS RUN" in why, (
            "the residual ambiguity between a clean target and a broken severity "
            "classifier must be stated in the reason, not hidden")

    @pytest.mark.parametrize("series", [[0, 0, 0], [0, 0, 0, 0, 0]])
    def test_a_dead_panel_is_REFUSED(self, R, series):
        """The guard the first version lacked. This is the load-bearing test."""
        ok, why, telem = _gate(R, series, findings=0)
        assert ok is False, (
            "a run whose panel produced NO findings of any severity converged; "
            "that is a dead panel rendered as an exhausted error space")
        assert telem["mode"] == "vacuous_curve_refused_dead_panel", telem
        assert "dead panel" in why

    def test_the_window_still_binds_under_vacuity(self, R):
        ok, why, telem = _gate(R, [0, 0], findings=18)
        assert ok is False
        assert telem["mode"] == "vacuous_curve_window_unmet", telem

    def test_a_constant_rate_series_never_reaches_the_vacuous_path(self, R):
        """The opposite situation that drives the estimator to the same ~0.0.

        A constant arrival rate is the WORST case and must never be confused with
        the best one. Its cumulative count is positive, so it is excluded by the
        first guard.
        """
        series = [2, 2, 2, 2, 2, 2]
        ok, _why, telem = _gate(R, series, findings=30)
        assert ok is False
        assert not str(telem.get("mode", "")).startswith("vacuous"), telem


class TestGammaNowGatesWhereItDidNot:
    """The behavioural change, and it must be REACHABLE or it is unwired."""

    @pytest.mark.parametrize("series", [[1, 3, 0, 0, 0], [1, 4, 0, 0, 0]])
    def test_a_low_but_estimable_gamma_now_refuses(self, R, series):
        g = R._estimate_gamma(series)
        assert R._gamma_is_estimable(series) is True
        assert g < _Cfg.gamma_alt_threshold, (series, g)
        ok, why, telem = _gate(R, series)
        assert ok is False, (
            f"{series} has gamma {g:.4f} below the arm with the window met and "
            "still converged, so gamma is not gating here")
        assert telem["mode"] == "sparsity_gamma_gated", telem
        assert telem["gamma_crit_gated"] is True
        assert "gamma GATES here" in why

    def test_a_high_estimable_gamma_still_converges(self, R):
        series = [5, 0, 0, 0]
        assert R._estimate_gamma(series) >= _Cfg.gamma_alt_threshold
        ok, _why, telem = _gate(R, series)
        assert ok is True
        assert telem["mode"] == "sparsity_gamma_gated"
        assert telem["gamma_crit_gated"] is True

    def test_the_window_still_binds_independently(self, R):
        """Gamma gating must not replace the window; both are required."""
        series = [5, 0, 1]          # high-ish gamma, window NOT met
        ok, why, _telem = _gate(R, series)
        assert ok is False
        assert "window not satisfied" in why


class TestTheDemotionLanguageIsGone:
    def test_no_path_describes_gamma_as_reported_not_gated_in_the_sparse_branch(self, R):
        """The phrase named the defect; it must not survive in a converging path."""
        for series in ([0, 0, 0], [5, 0, 0, 0], [1, 3, 0, 0, 0]):
            _ok, why, _t = _gate(R, series)
            assert "reported-not-gated" not in why, (series, why)

    def test_every_sparse_outcome_names_its_mode(self, R):
        for series in ([0, 0, 0], [5, 0, 0, 0], [1, 3, 0, 0, 0]):
            _ok, _why, telem = _gate(R, series)
            mode = telem.get("mode", "")
            assert mode.startswith(("sparsity_gamma_", "vacuous_curve_")), telem
            assert "gamma_crit_estimable" in telem
            assert "total_findings" in telem, (
                "the second guard's input must be on the record, or a reader "
                "cannot tell a clean target from a dead panel")


class TestTheTelemetryIsPersistedNotOnlyLogged:
    def test_the_round_record_carries_the_gate_telemetry(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text()
        assert '"hardened_gate_telemetry"' in src, (
            "the gate telemetry no longer reaches the round record, so which mode "
            "closed a run is unauditable again")
        assert "_hardened_gate_telem_for_record" in src
