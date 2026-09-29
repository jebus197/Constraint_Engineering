"""The adaptive-spec estimator audit, executed, with its own headline figure bounded.

WHY THIS FILE EXISTS. The founder is deciding where the adaptive distributed-compute
spec sits on the runway and whether it earns a paid arm. That decision will quote
numbers, so under `measured-rate-travels-with-its-script` the numbers must come from
committed code rather than from prose in a chat log.

IT ALSO GUARDS AGAINST CC1'S OWN OVERSTATEMENT. The inversion rate was first reported
as a single figure, 7.9630%, measured under uniform sampling. That is a property of an
arbitrary prior, not of this project's runs. `test_the_rate_is_prior_dependent` fails
if the script is ever reduced to one number, and `test_the_high_risk_regime_is_worse`
pins the direction that actually bears on the decision.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import sympy as sp

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "adaptive_spec_estimator_audit_2026-09-29.py"


@pytest.fixture(scope="module")
def mod():
    assert SCRIPT.is_file(), f"missing producer: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("adaptive_audit", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["adaptive_audit"] = m
    spec.loader.exec_module(m)
    return m


class TestDefectOneTheEstimatorIsConditional:
    def test_the_spec_estimator_is_not_the_expected_improvement(self, mod):
        assert sp.simplify(mod.G_SPEC - mod.G_EXP) != 0

    def test_the_spec_estimator_is_never_above_the_expectation(self, mod):
        """Wolfram returned True for the ForAll; checked numerically here too."""
        gs = sp.lambdify((mod.R, mod.Q, mod.S, mod.V), mod.G_SPEC, "math")
        ge = sp.lambdify((mod.R, mod.Q, mod.S, mod.V), mod.G_EXP, "math")
        import random
        rng = random.Random(3)
        for _ in range(4000):
            a = (rng.uniform(.02, .99), rng.uniform(.02, .98),
                 rng.uniform(.02, 1.0), rng.uniform(0, .45))
            assert gs(*a) <= ge(*a) + 1e-12, a

    def test_the_gap_has_the_closed_form_the_docstring_states(self, mod):
        R, q, s, v = mod.R, mod.Q, mod.S, mod.V
        want = -R**2 * q * s * (1 - v) * (1 - q) / (1 - q * R)
        assert sp.simplify(sp.simplify(mod.G_SPEC - mod.G_EXP) - want) == 0


class TestDefectTwoTheStateUpdateMismatch:
    def test_the_spec_form_and_the_live_form_agree_only_at_perfect_repair(self, mod):
        sols = mod.algebra()["agree_only_when"]
        assert 1 in sols, sols

    def test_the_spec_understates_residual_risk_below_perfect_repair(self, mod):
        """Direction matters: an optimistic scheduler under-books verification."""
        R, q, s = mod.R, mod.Q, mod.S
        nb, nf = sp.symbols("nu_b nu_f", nonnegative=True)
        base = s * mod.R_DET + (1 - s) * R
        nu_eff = 1 - (1 - nb) * (1 - (1 - s) * nf)
        live = base * (1 - nu_eff) + nu_eff
        spec = base * (1 - nb) + nb
        sub = {R: sp.Rational(9, 10), q: sp.Rational(4, 10),
               s: sp.Rational(8, 10), nb: sp.Rational(1, 10), nf: sp.Rational(2, 10)}
        assert float(spec.subs(sub)) < float(live.subs(sub))

    def test_it_matches_the_live_runner_exactly(self, mod):
        """EXECUTE the shipped function rather than trusting the transcription."""
        sys.path.insert(0, str(REPO))
        from bench.reference_runner_v3 import compute_rk
        R, q, s = mod.R, mod.Q, mod.S
        nb, nf = sp.symbols("nu_b nu_f", nonnegative=True)
        base = s * mod.R_DET + (1 - s) * R
        nu_eff = 1 - (1 - nb) * (1 - (1 - s) * nf)
        live = base * (1 - nu_eff) + nu_eff
        for Rv, qv, sv, nbv, nfv in [(.5, .3, 1.0, .0, .2), (.9, .4, .8, .1, .2),
                                     (.99, .3, .5, .05, .2)]:
            got = float(live.subs({R: Rv, q: qv, s: sv, nb: nbv, nf: nfv}))
            assert abs(got - compute_rk(Rv, qv, sv, nbv, nfv)) < 1e-12, (Rv, qv, sv)


class TestTheHeadlineFigureIsBounded:
    @pytest.fixture(scope="class")
    def rows(self, mod):
        return mod.inversion_rates(trials=6000)

    def test_the_rate_is_prior_dependent(self, rows):
        """A single number here would be the overstatement this file exists to stop."""
        rates = [r["rate"] for r in rows]
        assert max(rates) - min(rates) > 0.05, (
            f"the spread across priors collapsed to {max(rates)-min(rates):.4%}; "
            "if the script now reports effectively one rate, the prior-dependence "
            "caveat in its docstring has become false")

    def test_the_high_risk_regime_is_worse_than_the_uniform_headline(self, rows):
        by = {r["prior"]: r["rate"] for r in rows}
        uni = by["uniform (first reported)"]
        hi = by["high-risk regime R>0.8"]
        assert hi > uni * 1.5, (
            f"high-risk {hi:.4%} vs uniform {uni:.4%}; the decision-relevant claim is "
            "that the defect is worse where a scheduler matters most")

    def test_every_rate_carries_an_interval_containing_it(self, rows):
        for r in rows:
            lo, hi = r["wilson"]
            assert lo <= r["rate"] <= hi, r

    def test_the_two_interval_tools_agree(self, mod):
        from statsmodels.stats.proportion import proportion_confint
        worst = 0.0
        for k, n in [(0, 6000), (632, 8000), (1314, 8000), (8000, 8000)]:
            a, b = mod.wilson(k, n)
            c, d = proportion_confint(k, n, method="wilson")
            worst = max(worst, abs(a - c), abs(b - d))
        assert worst < 1e-12, worst


class TestItIsCheapAndHonest:
    def test_help_does_not_run_the_measurement(self, mod):
        with pytest.raises(SystemExit) as e:
            mod.main(["--help"])
        assert e.value.code == 0

    def test_it_names_the_measurement_it_cannot_make(self, mod, capsys):
        assert mod.main(["--trials", "400"]) == 0
        out = capsys.readouterr().out
        assert "NOT MEASURED HERE" in out, (
            "the script must state that the operational rate is unavailable rather "
            "than let a reader take a prior-conditioned figure as the real one")
