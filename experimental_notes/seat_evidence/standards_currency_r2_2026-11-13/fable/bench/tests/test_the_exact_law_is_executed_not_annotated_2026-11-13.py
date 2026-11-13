# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'standards_currency_r2_2026-11-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 202ea7bfdda82429a139758785ffbfdb2544281285c56a275eaef80a83dfb095
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The joint-round fixes of 2026-11-13 hold: the exact exposure law is EXECUTED
by the producer, not merely annotated, and the ratchet instrument demonstrates
what it claims.

WHY THIS GUARD EXISTS. The blind-round concession said the producer's Monte
Carlo tolerance "is now derived from the simulation's own sampling error" --
but the shipped producer still asserted the FIRST-ORDER form against 1 seed
under a typed 0.12 tolerance, and `exposure_ceiling_cadence` had no caller at
all: a correction recorded in a docstring while the executed path was
unchanged, plus an addition nothing reached, inside the very producer written
to correct for both shapes. These tests go RED if either regression returns.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
PRODUCER = REPO / "scripts" / "standards_currency_and_model_staleness_2026-11-13.py"
RATCHET = REPO / "scripts" / "a_bound_from_honoured_sizes_ratchets_2026-11-13.py"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def prod():
    return _load(PRODUCER, "cdsfl_standards_currency_joint")


@pytest.fixture(scope="module")
def producer_stdout():
    r = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, f"producer exited {r.returncode}:\n{r.stderr[-1500:]}"
    return r.stdout


def test_the_ceiling_root_agrees_across_two_independent_routes(prod):
    """scipy brentq inside the producer vs mpmath findroot computed HERE."""
    import mpmath as mp
    for lam in (0.5, 2.0 / 9.0, 1.0 / 7.0, 1.0 / 9.0):
        got = prod.exposure_ceiling_cadence(lam)
        L = mp.mpf(lam) / mp.mpf("365.25")
        f = lambda T: 1 - (1 - mp.e ** (-L * T)) / (L * T) - mp.mpf("0.01")
        ref = float(mp.findroot(f, 15))
        assert abs(got - ref) < 1e-6, (
            f"brentq {got} and mpmath {ref} disagree at lambda={lam}")


def test_the_exact_value_agrees_with_an_independent_quadrature(prod):
    """exposure_exact_value vs mpmath.quad of 1-exp(-lam*t) over the interval."""
    import mpmath as mp
    for lam, td in ((0.5, 30), (0.5, 180), (1.0 / 9.0, 30)):
        got = prod.exposure_exact_value(lam, td)
        L = mp.mpf(lam) / mp.mpf("365.25")
        ref = float(mp.quad(lambda t: 1 - mp.e ** (-L * t), [0, td]) / td)
        assert abs(got - ref) < 1e-12, f"{got} vs quadrature {ref} at ({lam},{td})"


def test_the_cross_check_is_anchored_to_the_exact_law(producer_stdout):
    """The EXECUTED cross-check must print z against the exact law and must not
    have reverted to the single-seed typed-tolerance form."""
    assert "z exact" in producer_stdout and "z 1st" in producer_stdout, (
        "the cross-check no longer reports its deviation from the exact law in "
        "units of the simulation's own standard error; the typed-tolerance "
        "single-seed form is the defect this replaced")
    assert "agree on 4 of 4, worst relative error" not in producer_stdout, (
        "the vacuous agreement line is back")


def test_the_ceiling_function_is_reached_by_the_producer(producer_stdout):
    """exposure_ceiling_cadence had NO caller; the producer must now execute it."""
    assert "T_max_worst_days_exact" in producer_stdout, (
        "the exact ceiling is no longer printed, so exposure_ceiling_cadence "
        "has lost its caller and is an addition nothing reaches again")
    # And the declared first-order figure the brief cites must still print.
    assert "T_max_worst_days = 14.61" in producer_stdout


def test_a_bound_of_honoured_sizes_ratchets_and_a_jump_binds():
    """D1, executed: growth up to HEADROOM per step is never stopped; above it,
    the bound binds immediately. Derived from the subject, not typed output."""
    m = _load(RATCHET, "cdsfl_ratchet_instrument")
    grow = [20 * m.HEADROOM ** k for k in range(20)]
    h, binds = m.drive(grow)
    assert len(h) == 20 and binds == 0, (
        f"growth at exactly HEADROOM per step should never bind: {binds} binds")
    jump = [20 * (m.HEADROOM * 1.05) ** k for k in range(20)]
    h2, binds2 = m.drive(jump)
    assert binds2 > 0, "a jump above HEADROOM per step must bind"
    # Exogenous record (the commit-timeout analogue): stationary values never
    # push the bound upward without limit. The value sits below FLOOR because
    # writing this test found a cold-start property: on an EMPTY record the
    # bound is FLOOR alone, so a stationary value above FLOOR is rejected
    # forever -- the first draft used 60.0 and honoured nothing.
    stat = [40.0] * 50
    h3, binds3 = m.drive(stat)
    assert len(h3) == 50 and max(h3) == 40.0 and binds3 == 0, (
        "a stationary record below FLOOR must be honoured in full, unchanged")
    h4, binds4 = m.drive([60.0] * 5)
    assert not h4 and binds4 == 5, (
        "cold start: an empty record bounds at FLOOR, so a stationary value "
        "above FLOOR is never honoured -- if this changes, drive() changed")


def test_the_ratchet_instrument_runs_clean():
    r = subprocess.run([sys.executable, str(RATCHET)], cwd=REPO,
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    assert "binds 0" in r.stdout and "binds 29" in r.stdout
