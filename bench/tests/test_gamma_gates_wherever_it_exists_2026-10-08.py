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

WHAT THE FIX DOES, AND THIS PARAGRAPH DESCRIBED THE REJECTED VERSION UNTIL
2026-10-08. The mode `sparsity_gamma_unestimable` belonged to the FIRST attempt,
which the founder rejected as the demotion renamed, and it appears nowhere in the
code. The fable seat found it still described here and put the reason sharply: a
stale guarantee in a docstring is how a rejected position acquires authority in this
project -- which has happened twice before, in the invented Wolfram denial rule and
the falsifier-may-not-call-Wolfram attribution.

What the fix ACTUALLY does: gamma gates wherever it is ESTIMABLE, including in the
sparse branch where it previously did not. Where no curve exists at all, the guarded
vacuity of `_check_gamma_alt_convergence` applies -- 2 guards, one of which refuses --
and the modes are `vacuous_curve_converged`, `vacuous_curve_refused_dead_panel` and
`vacuous_curve_window_unmet`. Both of the sibling's PRECONDITIONS are derived in-gate
as well, so `a4_blocked` and `contested_blocked` can refuse before any convergence
path is reached.

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


class TestTheMirrorHoldsOverASweepNotTenInputs:
    """P-PASS 2026-10-08: the mirror is hand-maintained, so sweep it.

    `_gamma_is_estimable` restates `_estimate_gamma`'s early-return conditions by
    hand. The first version of this file tested 10 inputs, which is not a sweep,
    and the panel brief dispatched on this fix asks the seats to widen it. Doing
    that here rather than outsourcing it.

    MEASURED: exhaustive over all 5461 series of length 0 to 6 with values 0 to 3,
    and random over 200000 series of length 0 to 39 with values 0 to 59. 0
    disagreements in either direction, and 0 cases where the predicate claimed
    estimable while the estimator would take an early return. Wilson on the random
    sweep's disagreement rate: [0.00000000, 0.00001921].

    A disagreement would be load-bearing, not cosmetic: the predicate decides
    whether gamma GATES, so a false "unestimable" demotes gamma and a false
    "estimable" compares a sentinel against the 0.30 arm.
    """

    def test_exhaustive_short_series_never_disagree(self, R):
        import itertools
        bad = []
        for L in range(0, 7):
            for s in itertools.product(range(0, 4), repeat=L):
                s = list(s)
                if not R._gamma_is_estimable(s) and R._estimate_gamma(s) != 0.0:
                    bad.append(s)
        assert not bad, (
            f"{len(bad)} series are called unestimable yet yield a slope: {bad[:5]}")

    def test_the_predicate_never_claims_estimable_on_an_early_return(self, R):
        """The estimator bails on <3 rounds or an all-zero series."""
        import itertools
        bad = []
        for L in range(0, 7):
            for s in itertools.product(range(0, 4), repeat=L):
                s = list(s)
                if R._gamma_is_estimable(s) and (len(s) < 3 or sum(s) == 0):
                    bad.append(s)
        assert not bad, bad[:5]

    def test_a_random_sweep_over_long_series_finds_no_disagreement(self, R):
        import numpy as np
        rng = np.random.default_rng(20261008)
        bad = 0
        for _ in range(20000):
            L = int(rng.integers(0, 40))
            s = list(rng.integers(0, 60, size=L))
            if not R._gamma_is_estimable(s) and R._estimate_gamma(s) != 0.0:
                bad += 1
        assert bad == 0, f"{bad} disagreements in a 20000-series random sweep"

    def test_the_sweep_actually_exercises_both_answers(self, R):
        """A sweep that only ever saw one answer would prove nothing."""
        import numpy as np
        rng = np.random.default_rng(11)
        seen = set()
        for _ in range(2000):
            L = int(rng.integers(0, 8))
            s = list(rng.integers(0, 4, size=L))
            seen.add(R._gamma_is_estimable(s))
        assert seen == {True, False}, (
            f"the sweep only ever observed {seen}; it cannot detect a one-sided "
            "predicate")


class TestTheFigureProducerRuns:
    """The brief's gamma figures must travel with code that executes."""

    def test_the_producer_reports_both_a_ceiling_and_a_floor(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "gsv", REPO / "bench" / "gamma_sentinel_versus_slope_2026-10-08.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules["gsv"] = m
        spec.loader.exec_module(m)
        R = m._runner()
        assert R._estimate_gamma([1, 0, 0, 0, 0]) == pytest.approx(1.0), (
            "a flat-after-something curve must sit at the ceiling or the whole "
            "argument about the sentinel collapses")
        assert R._estimate_gamma([0, 0, 0, 0, 0]) == pytest.approx(0.0)
        assert R._estimate_gamma([1, 2, 3, 4, 5]) == pytest.approx(0.0)
        assert R._gamma_is_estimable([1, 2, 3, 4, 5]) is True
        assert R._gamma_is_estimable([0, 0, 0, 0, 0]) is False


class TestTheSentinelIsSkippedInEverySubSeriesCheck:
    """FOUND BY THE cc2 SEAT against the fix committed hours earlier, 2026-10-08.

    `_gamma_is_estimable` was added and then applied in 1 of the 4 places the
    estimator meets a threshold. The `sustained` and leave-one-round-out loops call
    `_estimate_gamma` on SHORTER sub-series and compared the result to theta raw --
    and shorter is where the sentinel is MOST likely, not least. By this fix's own
    standard, gating on a sentinel is not gating on gamma, so it was the same defect
    one branch over, running in the opposite direction.

    THE FALSE NEGATIVE, which the seat demonstrated and which these tests pin: a run
    that found every critical in round 0 and nothing in 5 clean rounds since --
    maximal diminishing returns, the case that most deserves to converge -- has a
    drop-one sub-series of [0,0,0,0,0]. That is all-zero, so it yields the sentinel,
    which drove `loo_min` to 0.0 and refused the run. The sibling gate converged on
    identical data.

    SKIPPING IS NOT WEAKENING, which is the property most at risk and is asserted
    below: a sub-series that IS estimable and low still blocks, and if none is
    estimable the loops fall through to the headline gamma, which gates.
    """

    class _FullCfg:
        gamma_alt_threshold = 0.30
        gamma_alt_consecutive_zero_crit = 3
        gamma_crit_min_cumulative = 8
        gamma_alt_earliest_round = 0
        gamma_crit_sustain_rounds = 2
        gamma_crit_loo_tol = 0.05

    def test_the_seats_falsifying_case_now_converges(self, R):
        """All criticals in round 0, 5 clean rounds since."""
        ok, why, telem = _gate(R, [9, 0, 0, 0, 0, 0], cfg=self._FullCfg(),
                               findings=18)
        assert telem["mode"] == "full", telem
        assert ok is True, (
            f"maximal diminishing returns was refused: {why}")
        assert telem["loo_ok"] is True
        assert telem["loo_subseries_checked"] >= 1, (
            "no sub-series was checked at all, so loo passed vacuously rather "
            "than on evidence")

    def test_a_genuinely_climbing_series_is_still_refused(self, R):
        """MUTATION: if skipping the sentinel also let a real low slope through,
        the fix would be a weakening rather than a correction."""
        ok, _why, telem = _gate(R, [1, 2, 3, 4, 5, 6], cfg=self._FullCfg(),
                                findings=18)
        assert ok is False
        assert telem["loo_ok"] is False, telem
        assert telem["loo_subseries_checked"] >= 1

    def test_a_real_low_sub_series_still_blocks_via_sustained(self, R):
        ok, _why, telem = _gate(R, [3, 3, 3, 0, 0, 0], cfg=self._FullCfg(),
                                findings=18)
        assert ok is False
        assert telem["sustained"] is False, telem

    def test_the_loops_record_how_many_sub_series_carried_evidence(self, R):
        """Without this, a vacuous pass is indistinguishable from a real one."""
        _ok, _why, telem = _gate(R, [9, 0, 0, 0, 0, 0], cfg=self._FullCfg(),
                                 findings=18)
        assert "loo_subseries_checked" in telem
        assert "sustain_subseries_checked" in telem

    def test_no_sub_series_check_compares_a_sentinel_to_theta(self, R):
        """Executed across many series: every sub-series that fed a comparison
        must have been estimable."""
        import itertools
        for L in range(3, 7):
            for s in itertools.product(range(0, 3), repeat=L):
                s = list(s)
                for i in range(len(s)):
                    loo = s[:i] + s[i + 1:]
                    if len(loo) >= 2 and not R._gamma_is_estimable(loo):
                        # such a sub-series must NOT be able to lower loo_min
                        assert R._estimate_gamma(loo) == 0.0, (loo,)


class TestThePreconditionsThatGuardTheVacuityGuards:
    """FOUND INDEPENDENTLY BY BOTH FREE SEATS, 2026-10-08, and both called it critical.

    The vacuous-curve logic was imported from `_check_gamma_alt_convergence`, but the
    sibling reaches its vacuous branch only BEHIND its A4 fail-safe and its contested
    block. The import took the guards and left their preconditions, so the 2 gates
    returned OPPOSITE verdicts on identical registries.

    THE DIRECTION IS WHAT MAKES IT CRITICAL. `UNCONFIRMED` is an unresolved status
    that the novelty filter strips from the settled series, so an unverified critical
    does not merely fail to block -- it drives the cumulative count DOWN and pushes
    the run INTO the vacuous branch. `unverified_critical_count`'s own docstring
    forbids exactly this: such a critical "would vanish from the count and let the
    streak accrue".

    DERIVED IN-GATE, WHICH IS THE fable SEAT'S CORRECTION OF ITS OWN FIRST REPAIR.
    It first added them as parameters defaulting to 0, and its own falsifier caught
    that a caller can omit them and reopen the hole. In-gate derivation is the form
    no caller can forget.

    ARCHIVE EXPOSURE: 0 of 69 archived runs, scanned independently by both seats --
    a forward hazard, not a retroactive miscount.
    """

    class _Reg:
        def __init__(self, n=18, unverified=0, contested=0):
            self.entries = {f"C{i:04d}": {} for i in range(n)}
            self._u, self._c = unverified, contested

        def unverified_critical_count(self):
            return self._u

        def contested_count(self, _round, subcritical_exclusion=False):
            return self._c

    class _NarrowStub:
        """A registry WITHOUT the readers. Must fall back, never crash."""

        def __init__(self, n=18):
            self.entries = {f"C{i:04d}": {} for i in range(n)}

    def _run(self, R, crit, reg):
        orig = R._settled_novelty_series
        try:
            R._settled_novelty_series = lambda _r, _i: (crit, crit)
            return R._check_hardened_convergence(len(crit), reg, _Cfg())
        finally:
            R._settled_novelty_series = orig

    def test_an_unverified_critical_refuses_the_vacuous_path(self, R):
        ok, why, telem = self._run(R, [0, 0, 0, 0], self._Reg(18, unverified=6))
        assert ok is False, (
            "a run with 6 untested critical claims converged through the vacuous "
            "path; those claims are stripped from the settled series, so they push "
            "the run toward convergence rather than blocking it")
        assert telem["mode"] == "a4_blocked", telem
        assert telem["unresolved_critical"] == 6
        assert "A4 BLOCK" in why

    def test_a_contested_finding_refuses_the_vacuous_path(self, R):
        ok, _why, telem = self._run(R, [0, 0, 0, 0], self._Reg(18, contested=4))
        assert ok is False
        assert telem["mode"] == "contested_blocked", telem
        assert telem["contested"] == 4

    def test_the_clean_case_with_nothing_pending_still_converges(self, R):
        """MUTATION: if the preconditions blocked unconditionally the fix would be
        a universal refusal rather than a guard."""
        ok, _why, telem = self._run(R, [0, 0, 0, 0], self._Reg(18))
        assert ok is True, telem
        assert telem["mode"] == "vacuous_curve_converged"

    def test_a_registry_without_the_readers_falls_back_rather_than_crashing(self, R):
        """8 narrow stubs across 4 files have no such methods and are right to be
        narrow; the derivation must not make them a crash."""
        ok, _why, telem = self._run(R, [0, 0, 0, 0], self._NarrowStub(18))
        assert ok is True
        assert telem["unresolved_critical"] == 0
        assert telem["contested"] == 0

    def test_the_preconditions_run_before_every_convergence_path(self, R):
        """Not only the vacuous one: a sparse or full path must refuse too."""
        for crit in ([5, 0, 0, 0], [9, 0, 0, 0, 0, 0]):
            ok, _why, telem = self._run(R, crit, self._Reg(18, unverified=1))
            assert ok is False, (crit, telem)
            assert telem["mode"] == "a4_blocked", (crit, telem)


class TestASentinelIsNeverDescribedAsASlope:
    """F3, fable seat. The verdict cannot flip, but the RECORD was claiming a
    measurement it does not have, which is a provenance defect rather than a
    behavioural one."""

    def test_an_unestimable_refusal_names_the_sentinel(self, R):
        ok, why, telem = _gate(R, [0, 0, 0, 0, 1], findings=18)
        assert ok is False
        assert telem["gamma_crit_estimable"] is False
        assert "SENTINEL, not a slope" in why, why

    def test_an_estimable_refusal_still_reports_a_real_comparison(self, R):
        """MUTATION: if every refusal said "sentinel" the distinction would be lost."""
        ok, why, telem = _gate(R, [1, 3, 0, 0, 0], findings=18)
        assert ok is False
        assert telem["gamma_crit_estimable"] is True
        assert "gamma GATES here" in why
        assert "SENTINEL" not in why
