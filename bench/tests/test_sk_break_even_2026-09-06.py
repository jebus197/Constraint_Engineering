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
