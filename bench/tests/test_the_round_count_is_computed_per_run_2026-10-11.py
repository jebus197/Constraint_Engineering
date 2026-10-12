"""Item 9: the round recommendation is COMPUTED per run, and it gates nothing.

HIS ORDER, 2026-10-11: *"9: Then yes, do this also."* With the constraint that
shapes every assertion here: *"there is a case to be considered at where that
average number might sit in experiments ran by other researchers."* A shipped
constant of 10 would violate it; a number fitted to each run's own novelty series
satisfies it.

WHAT THIS PINS
  1. The formula is the project's own and reproduces the March 2026 figures.
  2. It uses the INTENSITY fit, not `_estimate_gamma`'s cumulative slope -- and
     the test records the 2.3882x error that the obvious wiring would have caused.
  3. `_estimate_gamma` and the convergence gate are UNTOUCHED. Gamma is not demoted.
  4. It is WIRED: the telemetry carries it on a real call of the hardened gate.
  5. It is ADVISORY: the gate's verdict is byte-identical with it and without it.
  6. It REFUSES rather than guessing -- churn, too few rounds, a <= theta.
"""
from __future__ import annotations

import math
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from round_budget import DEFAULT_THETA, project_optimal_rounds  # noqa: E402

#: The project's own early data (Codex, 23 March 2026), and the figures derived
#: from it then: a = 4.89, gamma = 0.709, n* = 9.37 at theta = 1.
EARLY = [5, 3, 2, 2]


class TestItReproducesTheProjectsOwnFigures:
    def test_a_and_gamma_match_march_2026(self):
        b = project_optimal_rounds(EARLY, theta=1.0)
        assert b.status == "OK"
        assert abs(b.a - 4.89) < 0.005, f"a={b.a}"
        assert abs(b.gamma - 0.709) < 0.0005, f"gamma={b.gamma}"

    def test_n_star_matches_the_recorded_9_37(self):
        b = project_optimal_rounds(EARLY, theta=1.0)
        assert abs(b.n_star - 9.37) < 0.005, f"n*={b.n_star}"

    def test_it_agrees_with_mpmath_to_machine_precision(self):
        import mpmath as mp
        mp.mp.dps = 40
        b = project_optimal_rounds(EARLY, theta=1.0)
        exact = mp.power(mp.mpf(b.a) / mp.mpf(1.0), mp.mpf(1) / mp.mpf(b.gamma))
        assert abs(b.n_star - float(exact)) < 1e-12


class TestTheFormulaIsTheOneDerived:
    def test_sympy_solves_the_stopping_rule_to_this_root(self):
        import sympy as sp
        n, a, g, th = sp.symbols("n a gamma theta", positive=True)
        roots = sp.solve(sp.Eq(a * n ** (-g), th), n)
        assert roots == [(a / th) ** (1 / g)]

    def test_more_rounds_are_justified_by_a_slower_decay(self):
        """d n*/d gamma < 0 for a > theta: a faster-depleting space earns FEWER
        rounds. If this inverted, the recommendation would be backwards."""
        slow = project_optimal_rounds([5, 4, 4, 3], theta=1.0)
        fast = project_optimal_rounds([5, 2, 1, 1], theta=1.0)
        assert slow.gamma < fast.gamma
        assert slow.n_star > fast.n_star

    def test_a_higher_threshold_asks_for_fewer_rounds(self):
        """theta is the researcher's cost/value call, so raising it must stop sooner."""
        cheap = project_optimal_rounds(EARLY, theta=0.5)
        dear = project_optimal_rounds(EARLY, theta=2.0)
        assert cheap.n_star > dear.n_star


class TestItDoesNotUseTheGatesGamma:
    def test_the_two_estimators_genuinely_disagree_on_this_data(self):
        """THE DEFECT THE DESIGN AVOIDS. The 2026-09-20 proposal said to feed
        `_estimate_gamma` into the formula, and did NOT say where `a` comes from --
        `_estimate_gamma` returns only gamma and discards its intercept. So three
        wirings were available and ALL THREE overestimate; the SMALLEST error is
        2.3882x. Measured on the project's own early data against the correct 9.3695."""
        import math

        import reference_runner_v3 as R
        g_cum = R._estimate_gamma(EARLY)
        b = project_optimal_rounds(EARLY, theta=1.0)
        assert abs(g_cum - 0.3717) < 0.001, f"cumulative gamma={g_cum}"
        assert abs(b.gamma - 0.7094) < 0.001, f"intensity gamma={b.gamma}"

        # the coherent cumulative fit, recovering the intercept the gate throws away
        cum, t = [], 0
        for c in EARLY:
            t += c
            cum.append(t)
        lx = [math.log(i + 1) for i in range(len(cum))]
        ly = [math.log(c) for c in cum]
        n = len(lx)
        sx, sy = sum(lx), sum(ly)
        sxy = sum(x * y for x, y in zip(lx, ly))
        sx2 = sum(x * x for x in lx)
        beta = (n * sxy - sx * sy) / (n * sx2 - sx * sx)
        a_cum = math.exp((sy - beta * sx) / n) * beta

        for label, a_wrong, expected in (
                ("cumulative a and gamma", a_cum, 2.3882),
                ("intensity a, cumulative gamma", b.a, 7.6358),
                ("round-1 count as a", 5.0, 8.1068)):
            ratio = ((a_wrong ** (1.0 / g_cum)) / b.n_star)
            assert abs(ratio - expected) < 0.01, (
                f"{label}: overestimate is {ratio:.4f}x, not the measured {expected}x")

    def test_the_cumulative_fit_is_biased_low_at_the_round_counts_we_run(self):
        """On EXACT counts from a known power law the intensity fit recovers the
        true gamma at every n; the cumulative fit does not until n is far beyond
        any round count this project runs."""
        import reference_runner_v3 as R
        true_g = 0.709
        for n_rounds in (4, 10, 21):
            counts = [5.0 * (k ** -true_g) for k in range(1, n_rounds + 1)]
            assert abs(project_optimal_rounds(counts).gamma - true_g) < 1e-9
            assert R._estimate_gamma([round(c) for c in counts]) < true_g - 0.15


class TestItRefusesRatherThanGuessing:
    def test_churn_has_no_optimal_round_count(self):
        b = project_optimal_rounds([2, 2, 2, 2, 2])
        assert b.status == "NO_DECAY"
        assert b.n_star is None

    def test_too_few_rounds_is_reported_not_extrapolated(self):
        for series in ([5], [5, 3], [0, 0, 0]):
            assert project_optimal_rounds(series).status == "TOO_EARLY"

    def test_a_rate_already_below_the_threshold_asks_for_no_more_rounds(self):
        b = project_optimal_rounds([2, 1, 1, 1], theta=5.0)
        assert b.status == "ALREADY_BELOW_THRESHOLD"
        assert b.rounds_remaining == 0

    def test_a_non_positive_threshold_is_refused(self):
        for bad in (0.0, -1.0):
            assert project_optimal_rounds(EARLY, theta=bad).status == "INVALID_THETA"

    def test_every_refusal_says_what_it_observed(self):
        for series, theta in (([2, 2, 2, 2], 1.0), ([5], 1.0), ([2, 1, 1, 1], 5.0),
                              (EARLY, 0.0)):
            b = project_optimal_rounds(series, theta=theta)
            assert b.detail.strip(), f"{b.status} gave no detail"


class TestItIsWiredAndAdvisory:
    def _telem_for(self, crit_series, **cfg_kw):
        import reference_runner_v3 as R
        cfg = R.RunnerConfig(**cfg_kw)
        real = R._settled_novelty_series
        try:
            R._settled_novelty_series = (
                lambda registry, rnd, **kw: (list(crit_series), list(crit_series)))
            return R._check_hardened_convergence(round_idx=20, registry={}, cfg=cfg)
        finally:
            R._settled_novelty_series = real

    def test_the_telemetry_carries_the_projection(self):
        """WIRED. An addition nothing reaches is not additive."""
        _, _, telem = self._telem_for(EARLY)
        assert telem["round_budget_status"] == "OK"
        assert abs(telem["round_budget_n_star"] - 9.37) < 0.005
        assert telem["round_budget_rounds_remaining"] == 6
        assert telem["round_budget_is_advisory"] is True

    def test_it_reports_its_own_gamma_separately_from_the_gates(self):
        """Both gammas in one record, labelled — so they can never be read as one."""
        _, _, telem = self._telem_for(EARLY)
        assert abs(telem["gamma_crit_settled"] - 0.3717) < 0.001
        assert abs(telem["round_budget_gamma_intensity"] - 0.7094) < 0.001

    def test_the_gate_verdict_does_not_depend_on_it(self):
        """ADVISORY. Changing theta moves n* and must move no verdict."""
        verdicts = []
        for th in (0.1, 1.0, 100.0):
            ok, why, telem = self._telem_for(EARLY, round_budget_theta=th)
            verdicts.append((ok, why))
            assert telem["round_budget_theta"] == th
        assert len(set(verdicts)) == 1, (
            f"the gate's verdict moved with the advisory threshold: {verdicts}")

    def test_a_broken_projection_cannot_fell_a_run(self):
        """A diagnostic must not fell a run — the contract the threshold profile
        states in its own except clause."""
        import reference_runner_v3 as R
        import round_budget as RB
        real = RB.project_optimal_rounds
        try:
            RB.project_optimal_rounds = lambda *a, **k: (_ for _ in ()).throw(
                ValueError("deliberate"))
            ok, why, telem = self._telem_for(EARLY)
            assert str(telem["round_budget_status"]).startswith("ERROR: ValueError")
            assert isinstance(ok, bool)
        finally:
            RB.project_optimal_rounds = real

    def test_the_two_thetas_are_distinct_config_fields(self):
        """`theta` was already bound to the gate's cutoff in that module. One name
        for two quantities is how the two gammas got conflated."""
        import reference_runner_v3 as R
        cfg = R.RunnerConfig()
        assert cfg.round_budget_theta == DEFAULT_THETA == 1.0
        assert cfg.gamma_alt_threshold == 0.30
        assert cfg.round_budget_theta != cfg.gamma_alt_threshold


class TestGammaIsNotDemoted:
    def test_estimate_gamma_is_unchanged_by_this_work(self):
        """The gate's estimator keeps its own scale and its own thresholds."""
        import reference_runner_v3 as R
        assert abs(R._estimate_gamma([5, 3, 2, 2]) - 0.3717) < 0.001
        assert R._estimate_gamma([2, 2, 2]) == 0.0      # the sentinel still means
        assert R._estimate_gamma([5]) == 0.0            # "not estimable"

    def test_moving_the_gates_thresholds_does_not_move_the_projection(self):
        """CONVERTED FROM A SOURCE-TEXT ASSERTION, 2026-10-12. The first form
        grepped `round_budget.py` for the gate's threshold names. That asserts the
        module describes itself consistently and cannot detect a producer and a
        consumer that disagree -- `execute-do-not-grep`, and the same class of
        blindness repaired in 3 guards the same night. This EXECUTES: it moves
        every gate threshold to an absurd value and requires the projection to be
        byte-identical, which is the property the grep was standing in for."""
        import reference_runner_v3 as R
        real = R._settled_novelty_series
        try:
            R._settled_novelty_series = (
                lambda registry, rnd, **kw: (list(EARLY), list(EARLY)))
            base = R._check_hardened_convergence(
                round_idx=20, registry={}, cfg=R.RunnerConfig())[2]
            moved = R._check_hardened_convergence(
                round_idx=20, registry={},
                cfg=R.RunnerConfig(gamma_alt_threshold=0.99,
                                   gamma_hard_threshold=0.98,
                                   gamma_soft_threshold=0.97))[2]
        finally:
            R._settled_novelty_series = real
        keys = [k for k in base if k.startswith("round_budget")]
        assert keys, "the projection did not reach the telemetry at all"
        for k in keys:
            assert base[k] == moved[k], (
                f"{k} moved when a GATE threshold moved, so the projection is "
                f"consulting the gate's cutoffs")

    def test_it_never_calls_the_gates_estimator(self):
        """The one genuinely structural half of the old grep, kept and narrowed:
        `_estimate_gamma` is the gate's estimator on the gate's scale, and calling
        it here is the 2.3882x-to-8.1068x error this module exists to avoid."""
        import ast
        src = (pathlib.Path(__file__).resolve().parents[1] / "round_budget.py"
               ).read_text(encoding="utf-8")
        called = {n.func.id for n in ast.walk(ast.parse(src))
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        assert "_estimate_gamma" not in called
