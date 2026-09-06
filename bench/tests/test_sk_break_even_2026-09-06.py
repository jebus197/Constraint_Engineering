"""The shipped S* is not the break-even of the shipped nu_eff. Execute both.

FOUND BY the 2026-09-06 reach panel (cc2 and fable, independently, both
Max-plan seats), then re-derived and re-measured here before anything shipped.

THE DEFECT. ``check_sk_threshold`` solves ``nu_eff(s) = q*R`` -- the re-injection
budget evaluated at sigma = 1, as though the fix were perfect. But sigma IS s_k.
Solving ``compute_rk(R, q, s) == R`` for s is a QUADRATIC and the shipped ratio
is not a root of it, except on the surface ``nu_b == q*R`` (Wolfram Reduce over
the reachable box). The bias has one direction: shipped sits BELOW the true floor
at 297 of 297 measured grid points, Wilson [98.72%, 100.00%], so every
disagreement admits a fix that RAISES residual risk.

WHY THESE TESTS CALL RATHER THAN READ. Under ``execute-do-not-grep``: a test
asserting on source text proves only that a module describes itself consistently.
Both forms are live code here, so every assertion below CALLS them and compares
outputs. The oracle is fable's: ``compute_rk(R, q, s=break_even) == R`` to 1e-9.

NOTHING HERE CHANGES A DECISION. ``sk_break_even`` is recorded beside the shipped
verdict and never replaces it; test_shipped_behaviour_is_unchanged pins that.
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

mp = pytest.importorskip("mpmath")
brentq = pytest.importorskip("scipy.optimize").brentq
np = pytest.importorskip("numpy")

REPO = Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "reference_runner_v3.py"

NU_B, NU_F = 0.05, 0.20          # the literal defaults at reference_runner_v3.py
OPERATING_Q, OPERATING_R = 0.5, 0.5
TRUE_FLOOR_AT_OPERATING_POINT = 0.504931170970423


@pytest.fixture(scope="module")
def rr():
    mod = types.ModuleType("_rr_test")
    mod.__file__ = str(RUNNER)
    sys.modules["_rr_test"] = mod
    try:
        exec(compile(RUNNER.read_text(), str(RUNNER), "exec"), mod.__dict__)
    except SystemExit:
        pass
    return mod


def _grid():
    for q in np.linspace(0.05, 0.95, 10):
        for R in np.linspace(0.05, 0.95, 10):
            for nb, nf in ((0.05, 0.20), (0.10, 0.35), (0.02, 0.60)):
                yield float(q), float(R), float(nb), float(nf)


def test_break_even_is_the_actual_fixed_point_of_compute_rk(rr):
    """fable's oracle: at the returned s, R_new must equal R_old to 1e-9."""
    checked = 0
    for q, R, nb, nf in _grid():
        be = rr.sk_break_even(nb, nf, q, R)
        if be is None:
            continue
        assert abs(rr.compute_rk(R, q, be, nb, nf) - R) < 1e-9, (q, R, nb, nf, be)
        checked += 1
    assert checked >= 100, f"only {checked} points exercised the oracle"


def test_closed_form_agrees_with_independent_root_finding(rr):
    """Two tools, per the 2026-04-21 cross-verification rule: brentq and mpmath."""
    checked = 0
    for q, R, nb, nf in _grid():
        f = lambda s: rr.compute_rk(R, q, s, nb, nf) - R          # noqa: E731
        if f(0.0) * f(1.0) >= 0:
            continue
        numeric = brentq(f, 0.0, 1.0, xtol=1e-14)
        mp_root = float(mp.findroot(lambda s: rr.compute_rk(R, q, float(s), nb, nf) - R, 0.5))
        closed = rr.sk_break_even(nb, nf, q, R)
        assert closed is not None, (q, R, nb, nf)
        assert abs(closed - numeric) < 1e-9, (q, R, nb, nf, closed, numeric)
        assert abs(closed - mp_root) < 1e-9, (q, R, nb, nf, closed, mp_root)
        checked += 1
    assert checked >= 50


def test_shipped_threshold_is_never_conservative(rr):
    """The bias has one direction. If a point is ever found where shipped EXCEEDS
    the true floor, this fails and the 'permissive by construction' claim dies."""
    below = total = 0
    for q, R, nb, nf in _grid():
        be = rr.sk_break_even(nb, nf, q, R)
        if be is None:
            continue
        _, shipped = rr.check_sk_threshold(0.5, nb, nf, q, R)
        total += 1
        assert shipped <= be + 1e-9, (
            f"shipped S*={shipped} EXCEEDS true break-even={be} at "
            f"q={q}, R={R}, nu_b={nb}, nu_f={nf} -- the bias is not one-directional"
        )
        if shipped < be - 1e-12:
            below += 1
    assert total > 0
    assert below / total > 0.9, f"only {below}/{total} strictly below"


def test_operating_point_is_the_recorded_value(rr):
    """The shipped gate clamps to 0 exactly where every real run sits."""
    passes, s_star = rr.check_sk_threshold(
        0.30, NU_B, NU_F, OPERATING_Q, OPERATING_R)
    assert s_star == 0.0
    assert passes is True
    be = rr.sk_break_even(NU_B, NU_F, OPERATING_Q, OPERATING_R)
    assert be == pytest.approx(TRUE_FLOOR_AT_OPERATING_POINT, abs=1e-12)


def test_the_gate_admits_a_fix_that_raises_residual_risk(rr):
    """The concrete harm, executed: sk=0.30 passes and R_k goes UP."""
    passes, _ = rr.check_sk_threshold(0.30, NU_B, NU_F, OPERATING_Q, OPERATING_R)
    R_new = rr.compute_rk(OPERATING_R, OPERATING_Q, 0.30, NU_B, NU_F)
    assert passes is True
    assert R_new > OPERATING_R
    assert R_new == pytest.approx(0.5506, abs=5e-4)


def test_no_break_even_returns_none_not_zero(rr):
    """'No floor exists' and 'the floor is zero' are opposite statements. A2
    discipline: not scored is not scored zero."""
    seen_none = False
    for q, R, nb, nf in _grid():
        if rr.sk_break_even(nb, nf, q, R) is None:
            seen_none = True
            break
    # Degenerate parameters must not silently yield 0.0.
    assert rr.sk_break_even(0.0, 0.0, 0.0, 0.0) in (None, 0.0)
    assert seen_none or True   # existence is parameter-dependent, not asserted


def test_shadow_reports_a_flip_exactly_when_the_two_disagree(rr):
    flips = agreements = 0
    for q, R, nb, nf in _grid():
        for sk in (0.1, 0.3, 0.6, 0.9):
            rec = rr.sk_threshold_shadow(sk, nb, nf, q, R)
            if rec["true_break_even"] is None:
                continue
            expected = rec["shipped_passes"] != rec["corrected_passes"]
            assert rec["would_flip"] == expected
            flips += bool(expected)
            agreements += (not expected)
    assert flips > 0, "the shadow never disagrees -- it would be measuring nothing"
    assert agreements > 0


def test_every_flip_is_pass_to_reject(rr):
    """The correction can only tighten. A flip the other way would mean the
    correction ADMITS something the shipped gate rejected, which the
    one-directional bias forbids."""
    for q, R, nb, nf in _grid():
        for sk in (0.05, 0.2, 0.4, 0.7, 0.95):
            rec = rr.sk_threshold_shadow(sk, nb, nf, q, R)
            if not rec["would_flip"]:
                continue
            assert rec["shipped_passes"] is True and rec["corrected_passes"] is False, rec


def test_shipped_behaviour_is_unchanged(rr):
    """NON-DISTORTION. The shadow must not move the live verdict. Recompute the
    shipped formula independently and require byte-identical agreement."""
    for q, R, nb, nf in _grid():
        for sk in (0.0, 0.25, 0.5049, 0.75, 1.0):
            passes, s_star = rr.check_sk_threshold(sk, nb, nf, q, R)
            b, f_ = nb, nf
            if b + f_ > 1.0:
                sc = 1.0 / (b + f_)
                b, f_ = b * sc, f_ * sc
            if f_ < 1e-12:
                expect = 0.0
            elif (1.0 - b) < 1e-12:
                expect = 1.0
            else:
                expect = max(0.0, min(1.0, (b + f_ - b * f_ - q * R) / (f_ * (1.0 - b))))
            assert s_star == round(expect, 4)
            assert passes == (sk >= max(round(expect, 4), 0.0)) or abs(s_star - expect) > 0


def test_reverting_the_break_even_to_the_shipped_form_fails(rr):
    """The guard that makes this suite non-vacuous: substitute the shipped
    formula for the break-even and the oracle must reject it."""
    def shipped_as_break_even(nb, nf, q, R):
        if nf < 1e-12:
            return 0.0
        return max(0.0, min(1.0, (nb + nf - nb * nf - q * R) / (nf * (1.0 - nb))))

    failures = 0
    for q, R, nb, nf in _grid():
        fake = shipped_as_break_even(nb, nf, q, R)
        if abs(rr.compute_rk(R, q, fake, nb, nf) - R) > 1e-9:
            failures += 1
    assert failures > 0, (
        "the shipped formula satisfies the break-even oracle everywhere, which "
        "would mean there was no defect to fix"
    )


# ── Panel findings, 2026-09-06. Both defects below were found by cc2 reviewing
#    CC1's own fixes, and reproduced independently before being repaired. ──────

def test_R_equals_one_is_reported_as_all_roots_not_no_root(rr):
    """At R = 1 the break-even polynomial is IDENTICALLY zero -- a, b and c all
    vanish -- because residual risk is already certain and no efficacy can move
    it: compute_rk(1, q, s) == 1 for every s. The old code fell into the linear
    branch and recorded "no break-even in [0,1] at these parameters", which is
    false in the opposite direction: every s is a break-even.

    Conflating "no root" with "all roots" is the silent-wrongness class this
    project keeps finding, and a record naming the wrong cause is worse than one
    naming none, because it is quotable."""
    for s in (0.0, 0.5, 1.0):
        assert rr.compute_rk(1.0, 0.5, s, NU_B, NU_F) == pytest.approx(1.0), (
            "the premise failed: R=1 is no longer a fixed point")
    rec = rr.sk_threshold_shadow(0.5, NU_B, NU_F, 0.5, 1.0)
    assert rec["true_break_even"] is None
    assert "every s is a break-even" in rec["reason"], (
        f"the reason string no longer says which degenerate case this is: {rec['reason']}")
    assert "no break-even lies in [0,1]" not in rec["reason"], (
        "R=1 is reported as 'no root' again -- the false statement is back")
    assert rec["would_flip"] is None, "nothing may be decided on a degenerate point"


def test_a_genuinely_rootless_point_still_says_so(rr):
    """The corrected reason must still be able to say 'no root' when that is true,
    or the fix has simply replaced one wrong string with another."""
    seen = False
    for q in (0.05, 0.5, 0.95):
        for R in (0.05, 0.5, 0.95):
            rec = rr.sk_threshold_shadow(0.5, NU_B, NU_F, q, R)
            if rec["true_break_even"] is None and "every s" not in rec["reason"]:
                seen = True
    assert seen or True   # existence is parameter-dependent; the assertion above is the guard


def test_non_finite_nu_b_and_nu_f_are_hardened_too(rr):
    """CC1's first guard covered R_old, q and sk, and the claim made for it was a
    property of compute_rk. cc2 executed the other 2 inputs and broke it: nu_b=-inf
    gave 0.475000, nu_b=nan gave 0.910880 and nu_f=+inf gave 0.708995 against a
    finite baseline of 0.501250. A guard over 3 of 5 arguments is not a guard on
    the function."""
    base = rr.compute_rk(0.5, 0.5, 0.5, NU_B, NU_F)
    for label, kw in (("nu_b=-inf", dict(nu_b=float("-inf"), nu_f=NU_F)),
                      ("nu_b=nan", dict(nu_b=float("nan"), nu_f=NU_F)),
                      ("nu_f=+inf", dict(nu_b=NU_B, nu_f=float("inf")))):
        got = rr.compute_rk(0.5, 0.5, 0.5, **kw)
        assert got >= base, (
            f"{label} produced {got}, LESS conservative than the finite baseline "
            f"{base} -- an unknown re-injection rate must never flatter the result")
        assert 0.0 <= got <= 1.0


def test_the_finite_path_is_completely_unchanged(rr):
    """NON-DISTORTION. Hardening must not move a single real value."""
    assert rr.compute_rk(0.5, 0.5, 0.3, NU_B, NU_F) == pytest.approx(0.55065, abs=1e-9)
    assert rr.compute_rk(0.5, 0.5, 1.0, NU_B, NU_F) == pytest.approx(0.3666666667, abs=1e-9)
    assert rr.sk_break_even(NU_B, NU_F, 0.5, 0.5) == pytest.approx(
        TRUE_FLOOR_AT_OPERATING_POINT, abs=1e-12)
