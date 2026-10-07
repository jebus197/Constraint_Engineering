"""The intra-round correlation is now measured, so the hazard figure is pinned.

The panel brief for `dynamic_roster_and_derived_ladder_2026-10-07` states that
the intra-round correlation has never been measured in this project and asks the
seats how it could be. It can be, and this guard holds the answer so the figure
cannot drift back to the independence assumption.

MEASURED over 64 archived reports carrying both a rounds list and a registry,
395 rounds with 2 or more responding seats, 1968 seat-rounds:

    q   (per-seat-per-round new-critical rate) = 0.233740, Wilson [0.215572, 0.252945]
    rho pairwise intraclass                    = 0.405989, bootstrap [0.332313, 0.476821]
    rho overdispersion method of moments       = 0.360248
    rho Pearson over within-round seat pairs   = 0.393096, p = 4.203e-297

3 independent estimators within 0.046 of each other. Critical is severity at or
above 0.7, the threshold the live runner uses at 4 sites.

WHAT THIS DOES TO THE EARLIER FIGURE. The 8.49986 factor in the brief assumed
BOTH independence and q = 0.3. At the measured rho and q the 6-seat-to-4-seat
spurious-convergence factor is 1.4291, against 4.9402 under independence at the
same q. The hazard is real -- above 1, so a shrinking roster does go quiet
sooner -- and roughly 5.9 times smaller than stated.

WHAT IT DOES NOT CHANGE. The reason to record the live roster beside the
quiet-round count never depended on the magnitude: z3 shows 0 new criticals from
a healthy panel and 0 from a depleted one are the same integer at any rho.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def M():
    return _load("icc_meas",
                 "bench/the_intra_round_correlation_measured_2026-10-07.py")


@pytest.fixture(scope="module")
def rounds(M):
    rs, _ = M.collect_rounds(REPO)
    return rs


class TestThePopulationIsRealAndLargeEnough:
    def test_enough_rounds_to_estimate_a_correlation(self, rounds):
        assert len(rounds) >= 100, (
            f"only {len(rounds)} usable rounds; the estimate would be noise")

    def test_every_round_has_at_least_two_responding_seats(self, rounds):
        assert all(n >= 2 for n, _ in rounds), (
            "a within-round pairwise correlation is undefined on 1 seat")

    def test_raising_counts_never_exceed_the_responding_roster(self, rounds):
        bad = [(n, x) for n, x in rounds if x > n]
        assert not bad, (
            f"{len(bad)} round(s) credit more seats with a finding than "
            f"responded, so the seat matching is wrong: {bad[:3]}")


class TestTheCorrelationIsPositiveAndAgreedByTwoRoutes:
    def test_the_correlation_is_clearly_positive(self, M, rounds):
        rho, q, pairs = M.rho_pairwise(rounds)
        assert rho == rho, "pairwise estimator returned NaN"
        assert rho > 0.15, (
            f"rho = {rho:.6f}; at this level the independence assumption would "
            "be close enough and the brief's figure would stand")
        assert pairs > 1000

    def test_the_two_estimators_agree(self, M, rounds):
        rho_p, _q, _n = M.rho_pairwise(rounds)
        rho_o = M.rho_overdispersion(rounds)
        assert rho_o == rho_o, "overdispersion estimator returned NaN"
        assert abs(rho_p - rho_o) < 0.12, (
            f"pairwise {rho_p:.6f} and overdispersion {rho_o:.6f} disagree; "
            "one of the 2 routes is wrong and the figure is not established")

    def test_q_is_not_the_assumed_value(self, M, rounds):
        """The brief also assumed q = 0.3. It is not."""
        _rho, q, _n = M.rho_pairwise(rounds)
        assert 0.15 < q < 0.32, f"q = {q:.6f} is outside any plausible range"
        assert abs(q - 0.3) > 0.03, (
            "q is close enough to the assumed 0.3 that only rho mattered; "
            "this assertion records which assumptions were actually wrong")


class TestTheHazardShrinksButSurvives:
    def test_at_the_measured_values_the_factor_is_well_below_the_claim(
            self, M, rounds):
        C = _load("corr_chk",
                  "bench/the_spurious_convergence_ratio_depends_on_correlation"
                  "_2026-10-07.py")
        rho, q, _n = M.rho_pairwise(rounds)
        measured = C.ratio_exact_beta_binomial(rho, q=q)
        independent = C.ratio_independent(q=q)
        assert measured > 1.0, (
            "if the factor fell to 1 the roster hazard would be retired, and "
            "the design argument would need a different justification")
        assert measured < independent / 2.0, (
            f"measured {measured:.4f} against independent {independent:.4f}; "
            "the correction is the whole point of this guard")

    def test_the_necessity_argument_is_independent_of_the_magnitude(self):
        S = _load("shrink_chk",
                  "bench/a_shrinking_roster_converges_sooner_2026-10-07.py")
        d = S.claim_the_gate_cannot_distinguish_the_two_causes()
        assert d["distinguishable_from_the_count_alone"] is False, (
            "if the count alone could separate the 2 causes, recording the live "
            "roster would be optional and this whole line of work unnecessary")


class TestThePooledFigureIsConfounded:
    """P-PASS of the measurement itself, 2026-10-07.

    The pooled rho of 0.405989 measures 2 things at once: that some ROUNDS go
    quiet, and that some EXPERIMENTS are quieter than others. The second is an
    ecological confound. It also mixes simulated runs with real ones, and the
    simulation shim is far more correlated than live seats.

        pooled, all runs          rho = 0.405989
        within-experiment         rho = 0.236014   (inflation 1.7202)
        simulated runs only       rho = 0.681094
        real runs only            rho = 0.275298

    So the earlier correction OVER-corrected: at the de-confounded values the
    6-seat-to-4-seat factor is 1.7766 to 1.9258 for a real run, not the 1.4291
    the pooled figure gave and not the 8.49986 first briefed.
    """

    def test_the_within_experiment_estimator_exists_and_is_lower(self, M):
        """If pooling did not inflate, the confound would not matter."""
        import json
        import glob
        per = []
        for f in sorted(glob.glob("bench/logs/**/*report*.json", recursive=True)):
            try:
                d = json.load(open(f))
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            rounds, reg = d.get("rounds"), d.get("registry")
            if not isinstance(rounds, list) or not isinstance(reg, dict):
                continue
            entries = (reg.get("entries")
                       if isinstance(reg.get("entries"), dict) else reg)
            if not isinstance(entries, dict):
                continue
            raised = {}
            for e in entries.values():
                if not isinstance(e, dict):
                    continue
                try:
                    sev = float(e.get("severity") or 0.0)
                except (TypeError, ValueError):
                    continue
                if sev < M.CRITICAL:
                    continue
                r, m = e.get("open_since_round"), M._norm(e.get("source_model"))
                if r is None or not m:
                    continue
                try:
                    raised.setdefault(int(r), set()).add(m)
                except (TypeError, ValueError):
                    continue
            rs = []
            for rec in rounds:
                if not isinstance(rec, dict):
                    continue
                resp = rec.get("models_responded")
                if not isinstance(resp, list) or len(resp) < 2:
                    continue
                try:
                    rn = int(rec.get("round"))
                except (TypeError, ValueError):
                    continue
                rset = {M._norm(x) for x in resp}
                rs.append((len(rset), len(rset & raised.get(rn, set()))))
            if rs:
                per.append(rs)

        assert hasattr(M, "rho_within_experiment"), (
            "the de-confounded estimator is missing, so the honest figure has "
            "no producer")
        within, kept = M.rho_within_experiment(per)
        pooled, _q, _p = M.rho_pairwise([r for rs in per for r in rs])
        assert kept >= 20, f"only {kept} reports carried enough rounds"
        assert within < pooled, (
            f"within-experiment {within:.6f} is not below pooled {pooled:.6f}; "
            "if pooling did not inflate rho this whole correction is spurious")
        assert pooled / within > 1.3, (
            f"inflation only {pooled / within:.4f}; at that level the pooled "
            "figure would have been close enough to report")

    def test_the_deconfounded_factor_is_larger_than_the_pooled_one(self, M):
        """The correction moves the hazard back UP, which is the honest direction."""
        C = _load("corr_dec",
                  "bench/the_spurious_convergence_ratio_depends_on_correlation"
                  "_2026-10-07.py")
        pooled_factor = C.ratio_exact_beta_binomial(0.4060, q=0.2337)
        real_factor = C.ratio_exact_beta_binomial(0.2753, q=0.2462)
        assert real_factor > pooled_factor, (
            f"real-run factor {real_factor:.4f} should exceed the pooled "
            f"{pooled_factor:.4f}; a lower rho means a larger factor")
        assert 1.0 < real_factor < 3.0, real_factor

    def test_simulated_runs_are_more_correlated_than_real_ones(self):
        """Recorded as a FACT about the shim, with consequences for simulation.

        A simulated arm whose seats are 0.6811 correlated cannot rehearse the
        roster hazard a real run faces at 0.2753: the simulation is ALREADY in
        the regime where the hazard nearly vanishes, factor 1.1280 against
        1.7766. Simulation will therefore under-report this class of defect.
        """
        C = _load("corr_sim",
                  "bench/the_spurious_convergence_ratio_depends_on_correlation"
                  "_2026-10-07.py")
        sim = C.ratio_exact_beta_binomial(0.6811, q=0.2086)
        real = C.ratio_exact_beta_binomial(0.2753, q=0.2462)
        assert sim < real, (sim, real)
        assert real / sim > 1.3, (
            "if simulation and reality gave the same factor, a simulated arm "
            "would rehearse this hazard faithfully; it does not")
