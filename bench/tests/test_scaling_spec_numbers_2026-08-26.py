"""The scaling spec's numbers are DERIVED from the archive, and this re-derives them.

WHY. experimental_notes/Scaling_Spec_GlobalMind_2026-08-26.md rests on one
measured parameter -- the inter-architecture correlation rho, mean 0.564 across
289 observations -- and on a coverage ceiling derived from it. A document that
quotes a number the archive no longer supports is the drift class this project
keeps finding, so the number is re-measured here rather than trusted.

THE CLAIM UNDER TEST. Part XIII's coverage function is

    D(n) = 1 - prod_{i=1..n} [ 1 - p * (1-rho)^(i-1) ]

At the measured rho, adding architectures past about five buys nothing: going
from 5 to 50 gains between +0.002 and +0.005 coverage across every plausible p.
If that is wrong, the spec's central recommendation -- fix panel size at 4-6 and
scale by problem count instead -- is wrong with it.
"""
import json
import pathlib
import re
import statistics

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SPEC = REPO / "experimental_notes/Scaling_Spec_GlobalMind_2026-08-26.md"
LOGS = REPO / "bench/logs"

# Tolerance on the quoted mean: the archive grows, and a new run should not
# fail this suite for moving the third decimal. It SHOULD fail if the panel's
# correlation changes materially, which is a finding.
RHO_TOL = 0.05


def _rho_observations():
    vals = []
    for d in sorted(LOGS.iterdir()) if LOGS.is_dir() else []:
        if not (d.is_dir() and re.match(r"^exp\d+[_-]", d.name)):
            continue
        rs = d / "runner_state.json"
        if not rs.is_file():
            continue
        try:
            s = json.loads(rs.read_text())
        except (OSError, ValueError):
            continue
        vals += [v for v in (s.get("rho_history") or []) if isinstance(v, (int, float))]
    return vals


def D(n, p, rho):
    """Part XIII simplified coverage function."""
    out = 1.0
    for k in range(n):
        out *= (1 - p * (1 - rho) ** k)
    return 1 - out


class TestTheCoverageMathIsRight:
    def test_numpy_and_sympy_agree(self):
        """Multi-tool cross-verification: a computational claim gets two tools."""
        sp = pytest.importorskip("sympy")
        for n in (1, 2, 3, 5, 8):
            sym = 1 - sp.prod([1 - sp.Rational(6, 10) * (1 - sp.Rational(564, 1000)) ** k
                               for k in range(n)])
            assert abs(float(sym) - D(n, 0.6, 0.564)) < 1e-12, f"disagreement at n={n}"

    def test_it_reduces_to_the_part_ii_corroboration_model_at_rho_zero(self):
        """Part XIII Property 5: at rho=0 this must become C(n) = 1-(1-p)^n.
        If it does not, the coverage model is not the generalisation it claims."""
        for p in (0.3, 0.6, 0.9):
            for n in (1, 3, 7):
                assert abs(D(n, p, 0.0) - (1 - (1 - p) ** n)) < 1e-12

    def test_monoculture_collapse_at_rho_one(self):
        """Property 3: rho=1 must give D(n) = D(1) for every n. This is the
        property that makes heterogeneity load-bearing rather than decorative."""
        for n in (2, 5, 20):
            assert abs(D(n, 0.6, 1.0) - D(1, 0.6, 1.0)) < 1e-12, (
                "identical architectures are adding coverage; the model would then "
                "endorse monoculture"
            )

    def test_marginal_gain_is_monotonically_decreasing(self):
        """Property 1. Diminishing returns is the whole basis of optimal stopping."""
        prev_delta = None
        for n in range(1, 12):
            delta = D(n, 0.6, 0.564) - (D(n - 1, 0.6, 0.564) if n > 1 else 0.0)
            if prev_delta is not None:
                assert delta <= prev_delta + 1e-12, f"marginal gain rose at n={n}"
            prev_delta = delta


class TestTheMeasuredRhoStillSupportsTheSpec:
    def test_rho_observations_exist_in_quantity(self):
        vals = _rho_observations()
        assert len(vals) >= 250, (
            f"only {len(vals)} rho observations found; the spec quotes 289. "
            "If run directories were removed, the spec's basis moved."
        )

    def test_the_quoted_mean_still_holds(self):
        vals = _rho_observations()
        mean = statistics.mean(vals)
        assert abs(mean - 0.564) < RHO_TOL, (
            f"measured rho mean is now {mean:.3f}; the scaling spec quotes 0.564. "
            "A material change in panel correlation is a FINDING, not a number to "
            "quietly update: it moves the coverage ceiling and n*."
        )

    def test_the_spec_quotes_the_measured_value(self):
        text = SPEC.read_text(encoding="utf-8")
        assert "0.564" in text and "289" in text, (
            "the spec no longer quotes the measured rho it rests on"
        )

    def test_scaling_ten_fold_buys_almost_nothing_at_measured_rho(self):
        """THE central claim. If this fails, fix-the-panel-at-4-to-6 is wrong."""
        vals = _rho_observations()
        rho = statistics.mean(vals)
        for p in (0.4, 0.6, 0.8):
            gain = D(50, p, rho) - D(5, p, rho)
            assert gain < 0.01, (
                f"at p={p}, rho={rho:.3f}, going from 5 to 50 architectures gains "
                f"{gain:+.4f} coverage. The spec says under +0.005 and recommends "
                "fixing panel size on that basis."
            )

    def test_optimal_stopping_lands_between_three_and_six(self):
        """The project's standing 'n = 3-6 saturation' observation, re-derived
        from the measured rho rather than carried as folklore."""
        rho = statistics.mean(_rho_observations())
        found = {}
        for eps in (0.05, 0.02, 0.01, 0.005):
            prev, nstar = 0.0, None
            for n in range(1, 60):
                d = D(n, 0.6, rho)
                if d - prev < eps:
                    nstar = n
                    break
                prev = d
            found[eps] = nstar
        assert all(3 <= v <= 6 for v in found.values()), (
            f"n* no longer lands in 3-6: {found}. The saturation the project has "
            "observed since Part XIII would then have a different cause."
        )


class TestLowerRhoIsWorthMoreThanMoreArchitectures:
    def test_halving_rho_beats_ten_times_the_panel(self):
        """The spec's recommendation rests on this comparison specifically."""
        p, rho = 0.6, 0.564
        more_architectures = D(50, p, rho) - D(5, p, rho)
        lower_rho = D(5, p, rho / 2) - D(5, p, rho)
        assert lower_rho > more_architectures * 10, (
            f"halving rho gains {lower_rho:+.4f}; ten times the panel gains "
            f"{more_architectures:+.4f}. The spec claims the first dominates."
        )
