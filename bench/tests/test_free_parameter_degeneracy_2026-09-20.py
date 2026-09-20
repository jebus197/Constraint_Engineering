#!/usr/bin/env python3
"""The free-parameter degeneracy, EXECUTED against the revised model's own arithmetic.

FOUNDER, 2026-09-19: is `free_parameters_can_fit_any_desired_risk: true` good or bad?

THE ANSWER IS A MEASUREMENT, NOT AN OPINION, which is why it has a producer:
`scripts/free_parameter_degeneracy_2026-09-20.py`. The package's own checker
exhibits 1 point per target -- removal effectiveness s = 1 - desired and
introduction rate b = desired. The producer establishes something strictly
stronger by solving the same equation for b given ANY s, which yields a whole
1-parameter family. That difference matters: an isolated point can be dismissed
as unphysical, a line crossing the physical region cannot.

WHAT THESE TESTS HOLD. That the producer's 3 claims are true by execution, that
its contrast with the existing model is real, and that it would NOTICE if the
revised model's action step ever stopped having this property -- because a
finding that cannot go away is not a finding about the model, it is a property
of the test.
"""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "free_parameter_degeneracy_2026-09-20.py"
PACKAGE = ROOT / "docs" / "maths_revision_review_2026-09-10"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("fpd", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestThePackagesOwnCheckReproduces:
    """The flag is read from the committed output, not restated from memory."""

    def test_the_committed_flag_is_true(self, mod):
        reported = mod.the_package_reports_it()
        if reported is None:
            pytest.skip("the review package is not in this tree")
        assert reported is True, (
            "the package no longer reports the degeneracy; if the model changed, "
            "the founder's answer changes with it and this must be re-derived")

    def test_the_exhibited_point_holds_in_exact_rationals(self, mod):
        holds, cases = mod.exhibited_point_holds()
        assert holds is True
        assert cases == 81, f"expected a 9x9 grid, got {cases} cases"


class TestTheDegeneracyIsALineNotAPoint:
    """The claim that goes beyond the package, so it carries the heavier burden."""

    def test_solving_for_b_given_any_s_succeeds(self, mod):
        line = mod.degeneracy_is_a_line()
        assert line["identically_the_target"] is True
        assert line["free_directions"] == 1, (
            "the solver found no free direction, so the 'line not a point' claim "
            "in the producer and in the founder's answer is not established")
        assert line["b_as_a_function_of_any_s"], "no expression for b was returned"

    def test_the_line_crosses_the_PHYSICAL_region(self, mod):
        """The whole force of 'a line, not a point' is that it cannot be waved
        away as unphysical. So at least 1 solution with s and b both inside
        [0, 1], at an s DIFFERENT from the exhibited 1 - d, must exist."""
        import sympy as sp
        z, s, b, d = sp.symbols("z s b d", real=True)
        after = sp.sympify(mod.ACTION, locals={"z": z, "s": s, "b": b})
        expr = sp.solve(sp.Eq(after, d), b)[0]
        found = []
        for zv in (F(1, 4), F(1, 2), F(3, 4)):
            for dv in (F(1, 4), F(1, 2)):
                for sv in (F(1, 10), F(3, 10), F(7, 10), F(9, 10)):
                    if sv == 1 - dv:
                        continue          # that is the point the package exhibits
                    bv = expr.subs({z: zv, d: dv, s: sv})
                    if 0 <= bv <= 1:
                        # and it really does land on the target
                        got = (1 - sv) * zv + bv * (1 - zv)
                        assert sp.nsimplify(got - dv) == 0
                        found.append((zv, dv, sv, bv))
        assert found, ("every solution off the exhibited point fell outside "
                       "[0, 1], so the degeneracy IS confined to that point and "
                       "the stronger claim must be withdrawn")

    def test_mpmath_agrees_independently(self, mod):
        """Second tool on the same claim, per the cross-verification rule."""
        assert mod.numerically_independent() == pytest.approx(0.0, abs=1e-30)


class TestTheContrastWithTheExistingModelIsReal:
    """What is being given up. GAMMA IS LOAD-BEARING and so is this: the existing
    form forbids outcomes, which is the property a 2-parameter form loses until
    its parameters are pinned."""

    def test_the_existing_form_is_strictly_monotone_in_p(self, mod):
        c = mod.the_contrast()
        assert c["strictly_negative_at_every_sample"] is True, (
            f"the collapse form is not strictly decreasing in p: {c['samples']}")
        assert c["free_parameters"] == 1

    def test_more_review_sensitivity_can_never_RAISE_residual_risk(self):
        """Stated as the thing a user of the model cannot do, because that is
        what 'it forbids outcomes' means."""
        import sympy as sp
        R, p1, p2 = sp.Rational(1, 2), sp.Rational(1, 4), sp.Rational(3, 4)
        f = lambda r, p: r * (1 - p) / (1 - p * r)      # noqa: E731
        assert f(R, p2) < f(R, p1), (
            "raising sensitivity did not lower residual risk, which would break "
            "the contrast the founder's answer rests on")


class TestTheFindingCanGoAway:
    """ANTI-VACUITY. A test that would pass whatever the model did measures
    nothing. Driving a NON-degenerate action step must break the claim."""

    def test_a_single_parameter_action_step_has_NO_free_direction(self):
        import sympy as sp
        z, s, d = sp.symbols("z s d", real=True)
        # Removal only, no re-introduction: risk_after = (1-s)z. This CANNOT hit
        # an arbitrary target from an arbitrary z with s confined to [0, 1].
        after = (1 - s) * z
        sol = sp.solve(sp.Eq(after, d), s)
        assert len(sol) == 1
        # At z = 1/4 and a target of 1/2 the required s is negative: impossible.
        need = sol[0].subs({z: sp.Rational(1, 4), d: sp.Rational(1, 2)})
        assert need < 0, (
            f"a removal-only step reached a target above its starting risk with "
            f"s = {need}; then the degeneracy would not distinguish the 2 forms")
