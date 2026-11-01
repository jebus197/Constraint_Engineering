"""The R_k carry must not be able to drive residual risk to exactly 1.0.

WHY THIS IS A STANDING CHECK AND NOT A ONE-OFF PROOF. The carry tier shipped on
2026-10-31. `_sk_admits` treats R == 1 as a CORRUPTION SIGNAL and returns
(False, 1.0) there, refusing every fix, and it justified that with "model_params
has 0 writers, so R_old is 0.5 on every real run and R == 1 is not otherwise
reachable". The carry falsifies that PREMISE: R_old is now whatever the run
reached. The conclusion survives, but only because of 2 facts about the DEFAULT
re-injection parameters, and both are values a future change could move:

  * nu_b = 0.05 and nu_f = 0.20 are the `model_params` fallbacks. R_k == 1 is
    reachable with finite inputs when nu_b == 1, or when sk == 0 and nu_f == 1.
  * with sk = 0 the update is R <- R*(1-nu_eff) + nu_eff, whose EXACT fixed
    point is 1. In float64 it stalls 2 ulp short and never arrives.

So the safety of the carry rests on arithmetic, not on intent, and this file
executes that arithmetic against the live constants. Producer:
`scripts/can_the_carry_latch_the_gate_at_one_2026-10-31.py`.
"""
import math

import pytest

from bench.reference_runner_v3 import RunnerConfig, compute_rk

NU_B, NU_F = 0.05, 0.20   # the model_params fallbacks the runner actually uses


class TestOneIsUnreachableFromBelow:
    def test_the_sk_zero_iteration_never_reaches_one(self):
        r, seen = 0.5, set()
        for _ in range(5000):
            nxt = compute_rk(r, 0.5, 0.0, NU_B, NU_F)
            if nxt == r or nxt in seen:
                r = nxt
                break
            seen.add(nxt)
            r = nxt
        assert r < 1.0, (
            f"the carry drove R to {r!r}; at R == 1 `_sk_admits` refuses every "
            f"fix as corrupt, so a legitimately accumulated risk would be read "
            f"as a corrupt input")
        assert (1.0 - r) / 2 ** -53 == pytest.approx(2.0, abs=1.0), (
            f"the float stall point moved to {r!r}; it was 2 ulp below 1.0 when "
            f"the carry was cleared for release")

    def test_the_stall_point_is_a_fixed_point_of_the_rounded_map(self):
        # Not merely "the loop stopped": applying the map again must return the
        # same bits, or the loop stopped for some other reason.
        r = 0.5
        for _ in range(5000):
            nxt = compute_rk(r, 0.5, 0.0, NU_B, NU_F)
            if nxt == r:
                break
            r = nxt
        assert compute_rk(r, 0.5, 0.0, NU_B, NU_F) == r

    def test_one_is_absorbing_so_the_concern_is_real_not_hypothetical(self):
        # Discriminating control. If R == 1 were not absorbing there would be
        # nothing to protect against, and the test above would prove nothing.
        assert compute_rk(1.0, 0.5, 0.0, NU_B, NU_F) == 1.0

    def test_the_named_routes_to_one_still_reach_one(self):
        # The parameter routes to R_k == 1. These MUST still hit 1, or the guard
        # above passes because the routes closed rather than because the live
        # defaults are safe.
        #
        # CORRECTED BY EXECUTION. The first version asserted nu_b = 1 with the
        # default nu_f, and nu_f = 1 with the default nu_b. Both returned
        # 0.9305555555555556 and 0.9773242630385488, because `compute_rk`
        # enforces a HARD CONSTRAINT nu_b + nu_f <= 1 by RESCALING both, which
        # the producer's symbolic model had omitted. Post-rescale the only
        # parameter routes are the 2 CORNERS of that constraint.
        assert compute_rk(0.5, 0.5, 0.0, 1.0, 0.0) == 1.0, "nu_b = 1, nu_f = 0"
        assert compute_rk(0.5, 0.5, 0.0, 0.0, 1.0) == 1.0, "sk = 0, nu_f = 1, nu_b = 0"

    def test_the_rescaling_is_what_closes_the_other_routes(self):
        # Pins the MECHANISM, not just the outcome: nu_b = 1 beside a non-zero
        # nu_f is rescaled away from the corner and no longer reaches 1.
        assert compute_rk(0.5, 0.5, 0.0, 1.0, NU_F) < 1.0
        assert compute_rk(0.5, 0.5, 0.0, NU_B, 1.0) < 1.0
        assert compute_rk(0.5, 0.5, 0.0, 0.5, 0.5) < 1.0

    def test_the_defaults_are_strictly_inside_those_routes(self):
        # The whole safety argument is that the live fallbacks are not 1.
        assert NU_B < 1.0 and NU_F < 1.0


class TestTheRoundBudgetIsCountedInRounds:
    def test_the_budget_excludes_a_seconds_field(self):
        # The producer's first version compared a round count against
        # wall_clock_cap_s = 28800, which is an 8-hour wall clock. A round
        # budget may only be built from fields counted in rounds.
        cfg = RunnerConfig()
        budget = int(cfg.max_rounds) + int(cfg.extension_cap)
        assert budget < 1000, (
            f"round budget {budget} is implausibly large; a seconds field has "
            f"probably been added to it")
        assert cfg.wall_clock_cap_s > budget, (
            "sanity: the wall clock is in seconds and dwarfs the round count")

    def test_a_bool_is_not_counted_as_a_round(self):
        # isinstance(True, int) is True in Python, which is how the boolean
        # sk_carry_rk_across_rounds was swept into an int filter.
        cfg = RunnerConfig()
        assert isinstance(cfg.sk_carry_rk_across_rounds, bool)
        for name in ("max_rounds", "extension_cap"):
            v = getattr(cfg, name)
            assert isinstance(v, int) and not isinstance(v, bool), name

    def test_stationarity_needs_more_rounds_than_a_run_has(self):
        cfg = RunnerConfig()
        budget = int(cfg.max_rounds) + int(cfg.extension_cap)
        r, n = 0.5, 0
        while n < 5000:
            nxt = compute_rk(r, 0.5, 0.0, NU_B, NU_F)
            n += 1
            if nxt == r:
                break
            r = nxt
        assert n > budget, (
            f"the iteration goes stationary in {n} rounds against a budget of "
            f"{budget}; the margin that made this a bound has gone")
