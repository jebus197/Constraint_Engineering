"""The ratchet needs BOTH a non-decreasing statistic AND a growing series.

ENTRY B164. The 2 free panel seats of 2026-11-13 diagnosed the same phenomenon
oppositely: cc2 said the fault is the statistic's DIRECTION, fable said it is the
RECORD'S PROVENANCE. Neither ran the test that separates them -- the same bound
driven over an EXOGENOUS record -- and the answer is that both are partly right.

These contracts pin that result so a later reader cannot take either half alone
and build a bound that ratchets.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
MOD = REPO / "scripts" / "does_the_ratchet_need_an_endogenous_record_2026-11-13.py"


@pytest.fixture(scope="module")
def r():
    assert MOD.is_file(), f"the instrument is missing: {MOD}"
    spec = importlib.util.spec_from_file_location("cdsfl_ratchet", MOD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_ratchet"] = m
    spec.loader.exec_module(m)
    return m


def test_c1_a_growing_series_defeats_the_bound_whatever_the_record(r):
    """cc2's half: provenance does not save a non-decreasing statistic."""
    drift = [100.0 * (1.10 ** k) for k in range(60)]
    endo = r.drive(drift, endogenous=True)
    exo = r.drive(drift, endogenous=False)
    assert endo["binds"] == 0 and exo["binds"] == 0, (
        f"the drifting series now binds ({endo['binds']}/{exo['binds']}); the "
        f"ratchet no longer reproduces and cc2's half is unsupported")
    span = max(drift) / min(drift)
    assert span > 100, "the fixture no longer spans enough to demonstrate anything"
    assert exo["final_bound"] > 100 * r.FLOOR, (
        "the exogenous bound did not run away on a growing series, which would "
        "mean provenance alone is sufficient and cc2 is wrong")


def test_c2_a_stationary_exogenous_record_does_not_ratchet(r):
    """fable's half: an exogenous record that does not grow gives a stable bound."""
    import numpy as np
    rng = np.random.default_rng(20261113)
    st = list(rng.uniform(150, 320, 60))
    exo = r.drive(st, endogenous=False)
    assert exo["binds"] == 0, "the stationary series should not bind"
    ceiling = r.HEADROOM * max(st)
    assert exo["final_bound"] <= ceiling * 1.001, (
        f"the bound {exo['final_bound']:.4g} escaped HEADROOM x the series "
        f"maximum {ceiling:.4g}, so it is not tracking the series")


def test_c3_the_bound_still_refuses_a_genuine_excursion(r):
    """A bound that never refuses anything is not a bound."""
    import numpy as np
    rng = np.random.default_rng(7)
    series = list(rng.uniform(150, 320, 30)) + [50_000.0] + list(rng.uniform(150, 320, 30))
    out = r.drive(series, endogenous=False)
    assert out["binds"] >= 1, (
        "a 50,000 excursion against a stationary record was admitted; the bound "
        "refuses nothing and is decorative")


def test_c4_the_endogenous_record_only_ever_holds_admitted_values(r):
    """The mechanism behind fable's half, checked rather than asserted."""
    series = [100.0] * 5 + [10_000_000.0] + [100.0] * 5
    endo = r.drive(series, endogenous=True)
    exo = r.drive(series, endogenous=False)
    assert endo["max_in_record"] < exo["max_in_record"], (
        f"the endogenous record held {endo['max_in_record']:.4g} and the "
        f"exogenous {exo['max_in_record']:.4g}; if they are equal the record "
        f"discipline is not actually filtering and C1/C2 compare nothing")
    assert endo["binds"] >= 1, "the excursion should have been refused"


def test_c5_neither_half_alone_is_recorded_as_sufficient(r):
    """The conclusion must not be summarised into 1 of its 2 halves."""
    src = MOD.read_text()
    for phrase in ("NON-INCREASING", "does not gate", "Neither constraint is redundant"):
        assert phrase in src, (
            f"the instrument no longer records {phrase!r}. The result is that "
            f"BOTH constraints are needed; dropping either half from the record "
            f"lets a reader build a bound that ratchets.")


def test_c6_a_windowed_statistic_is_not_non_increasing(r):
    """★ cc2's remedy, as stated, does not work -- and the condition is exact.

    Its joint-round position was that a bound on human load must use "an order
    statistic that is monotone NON-INCREASING in the record, or typed".
    Implemented as `min` over the same trailing window that `max` used, it still
    admits everything on a drifting series, because the oldest value in the
    window is only `growth ** window` behind the newest. Where that factor is
    below HEADROOM, nothing can bind.

    Neither seat tested this. It matters for B164 because "non-increasing in the
    record" is the whole of the remedy, and a windowed reading of it is no
    remedy at all.
    """
    drift = [100.0 * (1.10 ** k) for k in range(60)]

    def binds(stat, window):
        rec, n = [], 0
        for v in drift:
            if v > r.bound_with(rec, stat, window):
                n += 1
            rec.append(v)
        return n

    windowed_min = binds(min, r.WINDOW)
    whole_min = binds(min, None)
    assert windowed_min == 0, (
        f"a windowed min now binds {windowed_min} time(s); the fixture no "
        f"longer demonstrates that windowing defeats the remedy")
    assert whole_min > 0, (
        "an UNWINDOWED min binds nothing, so there is no working remedy here "
        "and the contract compares 2 failures")
    assert whole_min > windowed_min, (
        f"the unwindowed statistic ({whole_min}) must bind more than the "
        f"windowed one ({windowed_min}), or the distinction is not real")

    # ...and the condition is DERIVABLE rather than observed.
    g = drift[1] / drift[0]
    assert r.window_is_defeated(g, r.WINDOW) is True, (
        f"growth {g} ** {r.WINDOW} = {g ** r.WINDOW:.4f} against HEADROOM "
        f"{r.HEADROOM}: the predicate disagrees with the measurement")
    assert r.window_is_defeated(2.0, r.WINDOW) is False, (
        "a series doubling every step must NOT be defeated by the window; the "
        "predicate is accepting everything")
