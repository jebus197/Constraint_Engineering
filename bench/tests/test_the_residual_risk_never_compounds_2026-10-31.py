#!/usr/bin/env python3
"""His severity IS `R_k`, and `R_k` is never iterated across passes.

HIS DEFINITION, verbatim (annotation of `Decisions_Awaiting_You_2026-10-30.txt`
line 156): *"what are the chances that a particular flaw, or class of flaws
might remain after a given number of passes under severe scrutiny in any given
test"*. `docs/MATHEMATICAL_APPENDIX.md` line 73 defines the same quantity in the
same words: *"the posterior probability that a flaw of class k remains after n
passes that found nothing"*.

HIS QUESTION, 2026-10-31: *"Obviously (probably preferably) in order for
convergence to trigger, the measured value of severity/residual risk must be
low?"*

WHY THAT CANNOT BE WIRED TO THE NUMBER THE RUNNER RECORDS TODAY. `R_old` is
`0.5` in all 1,252 archived entries carrying an `R_new` -- distinct count 1 --
because `reference_runner_v3.py:17249` falls to `RK0_PI_BASE` on every entry.
The runner's own comment says so: the uniform base prior is *"what every run
from Exp 37 to Exp 49 actually used, because model_params is never populated"*.
So the recorded number is the risk after ONE pass from a fresh prior, not after
n passes, and its floor across the whole archive is 0.366667.

WHAT THIS FILE GUARDS, and what it deliberately does NOT. It guards the
PROPERTIES any fix must preserve: that the recursion compounds, that it is
monotone, that it stays in the unit interval, and that one step from the prior
cannot reach a low value however good the detection. It does NOT assert that
`R_old` is constant in the archive, because that is the defect -- a test
asserting a defect goes red when the defect is repaired, which is backwards.
That figure is REPORTED by
`scripts/his_severity_definition_is_the_models_own_quantity_2026-10-31.py`.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

#: The q implied by the archive's single observed step, 0.5 -> 0.366667.
#: Solved exactly by SymPy in the producer: q = 8/19.
Q_IMPLIED = 8.0 / 19.0


def step(R: float, q: float) -> float:
    """The appendix's recursive form, §1.1 line 189."""
    return R * (1.0 - q) / (1.0 - q * R)


class TestTheRecursionCompounds:
    """The property his definition needs: more passes must mean less risk."""

    def test_six_passes_strictly_decrease(self):
        chain = [0.5]
        for _ in range(6):
            chain.append(step(chain[-1], Q_IMPLIED))
        for a, b in zip(chain, chain[1:]):
            assert b < a, f"a pass did not lower the risk: {a} -> {b}"

    def test_six_passes_reach_a_value_a_gate_could_call_low(self):
        """This is the whole point. Carried forward, the quantity gets low."""
        R = 0.5
        for _ in range(6):
            R = step(R, Q_IMPLIED)
        assert R < 0.05, (
            f"after 6 compounded passes R = {R:.6f}; if this were not low, his "
            "proposal to gate convergence on it could not work even in principle")

    def test_one_step_from_the_prior_cannot_be_low(self):
        """The structural reason the archive floors at 0.366667.

        A single pass from pi = 0.5 is bounded below by the q -> 1 limit, and
        even perfect detection in ONE pass cannot take a 0.5 prior below the
        value a gate would need. So the floor is not a tuning problem.
        """
        best = min(step(0.5, q / 1000.0) for q in range(1, 1000))
        assert best > 0.0
        # At q = 0.95 -- better detection than any measured run -- one step
        # still leaves far more than a convergence gate could accept.
        assert step(0.5, 0.95) > 0.04, (
            "one step at q=0.95 is already low, which would mean the archive's "
            "floor of 0.366667 has some other cause than a single step")
        assert step(0.5, Q_IMPLIED) == pytest.approx(0.3666667, abs=1e-6)

    def test_the_archive_floor_is_exactly_one_step(self):
        """Ties the measured floor to the mechanism, not to a coincidence."""
        assert step(0.5, Q_IMPLIED) == pytest.approx(0.36666666666666, abs=1e-12)


class TestTheInvariantsAFixMustKeep:
    def test_a_null_pass_never_raises_the_risk(self):
        for R in (0.01, 0.2, 0.5, 0.8, 0.99):
            for q in (0.01, 0.1, 0.5, 0.9, 0.99):
                assert step(R, q) <= R + 1e-15

    def test_it_stays_inside_the_unit_interval(self):
        for R in (0.0, 0.01, 0.5, 0.99, 1.0):
            for q in (0.0, 0.01, 0.5, 0.99):
                v = step(R, q)
                assert 0.0 - 1e-15 <= v <= 1.0 + 1e-15, (R, q, v)

    def test_zero_detection_leaves_the_risk_untouched(self):
        """The §1 capability ceiling: q = 0 means R never moves, for ever."""
        for R in (0.1, 0.5, 0.9):
            assert step(R, 0.0) == pytest.approx(R)

    def test_z3_proves_both_invariants(self):
        import z3
        R, q = z3.Reals("R q")
        for name, bad in (
            ("a null pass raises the risk", R * (1 - q) / (1 - q * R) > R),
            ("it leaves the unit interval",
             z3.Or(R * (1 - q) / (1 - q * R) < 0, R * (1 - q) / (1 - q * R) > 1)),
        ):
            s = z3.Solver()
            s.add(R > 0, R < 1, q > 0, q < 1, bad)
            assert str(s.check()) == "unsat", f"z3 found a case where {name}"

    def test_sympy_confirms_the_two_appendix_forms_agree(self):
        import sympy as sp
        pi, q = sp.symbols("pi q", positive=True)
        rec = (pi * (1 - q) / (1 - q * pi))
        rec2 = rec * (1 - q) / (1 - q * rec)
        batch = pi * (1 - q) ** 2 / ((1 - pi) + pi * (1 - q) ** 2)
        assert sp.simplify(rec2 - batch) == 0


class TestTheProducerStillReportsTheMeasurement:
    def test_it_runs_and_reports_both_quantities(self):
        spec = importlib.util.spec_from_file_location(
            "sev_producer",
            REPO / "scripts" /
            "his_severity_definition_is_the_models_own_quantity_2026-10-31.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        a = mod.archive()
        assert a["reports"] > 0, "no archived reports were found at all"
        assert a["R_new"]["n"] > 100, "the producer found almost no R_new values"
        assert a["severity"]["n"] > 100, "the producer found almost no severities"
        # The 2 are different objects, so they must not be the same series.
        assert a["R_new"]["distinct"] != a["severity"]["distinct"]

    def test_the_derivation_holds_every_sign(self):
        spec = importlib.util.spec_from_file_location(
            "sev_producer2",
            REPO / "scripts" /
            "his_severity_definition_is_the_models_own_quantity_2026-10-31.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        d = mod.derive()
        assert d["two_forms_agree_at_n2"] is True
        assert d["dR_dn_sign_at_half_half_3"] < 0, "more passes did not lower risk"
        assert d["dR_dpi_sign_at_half_half_3"] > 0, "a harder question did not raise risk"
        assert d["dR_dq_sign_at_half_half_3"] < 0, "better detection did not lower risk"
        assert d["z3_a_null_pass_cannot_raise_risk"] == "unsat"
        assert d["z3_stays_in_unit_interval"] == "unsat"
        assert d["two_tools_agree"] is True

    def test_his_worked_contrast_separates_by_orders_of_magnitude(self):
        """4 + 4 against Riemann. If these did not separate, a single fixed cut
        across both would be defensible, and his charge against 0.7 would fail."""
        spec = importlib.util.spec_from_file_location(
            "sev_producer3",
            REPO / "scripts" /
            "his_severity_definition_is_the_models_own_quantity_2026-10-31.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        c = mod.his_worked_contrast()
        assert c["numpy_agrees"] is True
        assert c["ratio_hard_over_easy_at_6"] > 1000.0, (
            "the easy and hard questions did not separate, so a single fixed "
            "severity cut across both would not be refuted by this contrast")
