"""The published answer to the founder's boundaries question must not drift.

WHAT THIS PINS AND WHY IT MATTERS. His second question, truncated in the record
at "what should realistic boundaries for these", is answered by the floor of the
shipped risk recursion, because the only boundary expressible today is a
multiple of that floor. The 2026-10-31 joint round produced the floor table, and
the 2 seats gave DIFFERENT floors:

  * nu_b = 0.05 is a VALID lower bound -- z3 is unsat for any output below it.
  * nu_eff = 1 - (1 - nu_b)(1 - (1 - S_k) nu_f) is the ATTAINED infimum, reached
    exactly at R_old = 0, and it tracks FIX EFFICACY rather than question
    difficulty.

They are not in conflict, because nu_eff >= nu_b always, and the distinction is
the whole practical point: nu_eff equals nu_b ONLY at a perfect fix. At a fix
efficacy of 0.5 the attained floor is 0.145, which is 2.9 times the nominal
bound, so a boundary pre-registered against nu_b would be UNREACHABLE at every
imperfect fix -- and the archive is all imperfect fixes. A gate holding such a
boundary would silently never fire.

So this file executes the published table against the shipped function. It is
not a restatement: every value comes back from `compute_rk` itself.

Producer: `scripts/is_the_floor_nu_b_or_nu_eff_2026-10-31.py`.
"""
import numpy as np
import pytest

from bench.reference_runner_v3 import compute_rk

NU_B, NU_F = 0.05, 0.20

#: Published in the joint round and transcribed here so it can FAIL.
PUBLISHED_FLOOR = {1.0: 0.0500, 0.95: 0.0595, 0.92: 0.0652,
                   0.80: 0.0880, 0.50: 0.1450, 0.0: 0.2400}


def nu_eff(sk, nu_b=NU_B, nu_f=NU_F):
    return 1 - (1 - nu_b) * (1 - (1 - sk) * nu_f)


class TestThePublishedFloorTable:
    @pytest.mark.parametrize("sk,published", sorted(PUBLISHED_FLOOR.items()))
    def test_each_published_value_comes_back_from_the_shipped_function(
            self, sk, published):
        # The minimum over the OTHER 2 free arguments, from the real function.
        grid = np.linspace(0.0, 1.0, 201)
        swept = min(compute_rk(float(r), float(q), float(sk), NU_B, NU_F)
                    for r in grid for q in grid)
        assert swept == pytest.approx(published, abs=5e-5), (
            f"the floor at S_k = {sk} is {swept!r}, not the published "
            f"{published}; the answer given to the founder has drifted")

    @pytest.mark.parametrize("sk", sorted(PUBLISHED_FLOOR))
    def test_the_closed_form_matches_the_function(self, sk):
        # The floor is ATTAINED at R_old = 0, which is what makes it an
        # infimum rather than a bound.
        assert compute_rk(0.0, 0.5, sk, NU_B, NU_F) == pytest.approx(
            nu_eff(sk), abs=1e-12)


class TestTheTwoFloorsAreOrderedNotEqual:
    def test_nu_b_is_a_valid_lower_bound(self):
        grid = np.linspace(0.0, 1.0, 51)
        worst = min(compute_rk(float(r), float(q), float(s), NU_B, NU_F)
                    for r in grid for q in grid for s in grid)
        assert worst >= NU_B - 1e-12, (
            f"an output of {worst!r} fell below nu_b, which z3 proved "
            f"unsatisfiable")

    def test_the_two_floors_coincide_only_at_a_perfect_fix(self):
        assert nu_eff(1.0) == pytest.approx(NU_B, abs=1e-12)
        # DISCRIMINATING: if these were equal everywhere the distinction this
        # file exists to pin would be vacuous.
        for sk in (0.0, 0.5, 0.8, 0.95):
            assert nu_eff(sk) > NU_B + 1e-9, sk

    def test_the_practical_gap_is_large_where_the_archive_sits(self):
        # 2.9x at a half-effective fix. Stated as a number so a change shows up
        # as a failing assertion rather than as a quieter answer.
        assert nu_eff(0.5) / NU_B == pytest.approx(2.9, abs=1e-6)
        assert nu_eff(0.0) / NU_B == pytest.approx(4.8, abs=1e-6)


class TestTheSaturationRegimeIsNeverConverge:
    def test_the_long_run_floor_exceeds_one_when_detection_is_weak(self):
        # fable's point: at q <= nu_b the long-run floor nu_b/q is at or above
        # 1, and a gate must read that as never-converge rather than as a high
        # threshold. Pinned because it decides a BRANCH, not just a number.
        for q in (0.05, 0.04, 0.01):
            assert NU_B / q >= 1.0, q
        assert NU_B / 0.10 < 1.0, "the regime boundary moved"

    def test_one_is_absorbing(self):
        for q in (0.0, 0.5, 1.0):
            for s in (0.0, 0.5, 1.0):
                assert compute_rk(1.0, q, s, NU_B, NU_F) == 1.0, (q, s)
