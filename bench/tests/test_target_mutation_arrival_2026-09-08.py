"""Guards for scripts/target_mutation_arrival_2026-09-08.py.

Written 2026-09-08 18:15 BST, AFTER the P-pass on that script found 3 defects
its first version shipped with. Every test here CALLS the function and checks a
value; none inspects source text, per `execute-do-not-grep`. Each was
mutation-verified by reverting the corresponding fix and confirming it goes red.

The defect that matters is the first one: the published p-value flattered its
own conclusion by 3.9x because it treated the window endpoints as free draws
when the window is defined BY those endpoints.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest
from scipy import stats as sps

_SPEC = importlib.util.spec_from_file_location(
    "target_mutation_arrival",
    Path(__file__).resolve().parents[2] / "scripts" / "target_mutation_arrival_2026-09-08.py",
)
tma = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(tma)

REAL_LOG = Path(__file__).resolve().parents[1] / "logs" / "target_mutation_watch_2026-09-08" / "target_state_transitions.log"


def _line(state: int, hhmmss: str, blob: str = "deadbeef", size: int = 21000) -> str:
    return f"NEW target state {state} at {hhmmss}: blob {blob}, {size} bytes (+0 vs HEAD)"


# --- Defect 1: the burst probability must condition on the endpoints. ---------

def test_burst_probability_uses_interior_points_only():
    """The first arrival defines the window's start, so it is in the slice by
    construction and cannot be evidence of clustering. Only interior points are
    free draws. Counting all 12 gives 6.541e-06; the correct 6-of-10 is 2.538e-05."""
    t, _, _ = tma.parse_log(REAL_LOG.read_text())
    s = tma.arrival_stats(t)
    assert s["n"] == 12
    assert s["k_in_window"] == 7, "7 of 12 states land in the first 600 s"
    assert s["k_interior_in_window"] == 6, "but only 6 of them are interior points"
    assert s["n_interior"] == 10
    q = s["burst_window_s"] / s["span_s"]
    unconditional = float(sps.binom.sf(7 - 1, 12, q))
    assert s["burst_p_scipy"] == pytest.approx(2.538e-05, rel=1e-3)
    assert s["burst_p_scipy"] > unconditional, (
        "the conditioned p-value must be LARGER (less impressive) than the "
        "unconditional one; if it is not, the endpoint conditioning was dropped"
    )
    assert s["burst_p_scipy"] / unconditional == pytest.approx(3.88, rel=0.02)


def test_burst_probability_agrees_across_two_tools():
    t, _, _ = tma.parse_log(REAL_LOG.read_text())
    s = tma.arrival_stats(t)
    assert s["burst_p_scipy"] == pytest.approx(s["burst_p_mpmath"], rel=1e-9)


# --- Defect 2: midnight rollover. --------------------------------------------

def test_midnight_rollover_does_not_produce_negative_gaps():
    """The log stores a time of day with no date. Unwrapped, 23:58:00 -> 00:03:00
    is +300 s; raw, it is -86,100 s and every statistic downstream is garbage."""
    text = "\n".join([_line(1, "23:58:00"), _line(2, "00:03:00"), _line(3, "00:09:00")])
    t, _, _ = tma.parse_log(text)
    gaps = np.diff(t)
    assert (gaps > 0).all(), f"negative gap across midnight: {gaps}"
    assert gaps.tolist() == [300.0, 360.0]


def test_rollover_survives_multiple_days():
    text = "\n".join([_line(1, "23:59:00"), _line(2, "00:01:00"),
                      _line(3, "23:59:30"), _line(4, "00:02:00")])
    t, _, _ = tma.parse_log(text)
    assert (np.diff(t) > 0).all()
    # 23:59:00 on day 1 to 00:02:00 on day 3 is 1 day plus 3 minutes.
    assert t[-1] - t[0] == pytest.approx(86400 + 3 * 60, abs=1)


def test_ordinary_log_is_untouched_by_the_rollover_logic():
    """A log that does not cross midnight must parse exactly as before."""
    t, _, _ = tma.parse_log(REAL_LOG.read_text())
    assert t[0] == 7 * 3600 + 15 * 60 + 3
    assert t[-1] == 9 * 3600 + 31 * 60 + 15
    assert t[-1] - t[0] == 8172


# --- Defect 3: degenerate inputs report, not crash. ---------------------------

@pytest.mark.parametrize("text,label", [
    ("", "empty log"),
    (_line(1, "07:00:00"), "single entry"),
    ("\n".join([_line(1, "07:00:00"), _line(2, "07:00:15")]), "two entries, no interior point"),
])
def test_degenerate_logs_raise_insufficient_data(text, label):
    t, _, _ = tma.parse_log(text)
    with pytest.raises(tma.InsufficientData):
        tma.arrival_stats(t)


def test_all_arrivals_at_one_instant_is_insufficient_not_a_zero_division():
    text = "\n".join(_line(i, "07:00:00", blob=f"b{i}") for i in range(1, 5))
    t, _, _ = tma.parse_log(text)
    with pytest.raises(tma.InsufficientData):
        tma.arrival_stats(t)


# --- The conclusion itself, so a future edit cannot quietly reverse it. -------

def test_the_clustering_conclusion_holds_on_two_independent_statistics():
    t, _, _ = tma.parse_log(REAL_LOG.read_text())
    s = tma.arrival_stats(t)
    assert s["ks_p"] < 0.01, "KS against uniform arrivals must still reject"
    assert s["cv_p"] < 0.01, "gap dispersion must still reject"
    assert s["cv"] > s["cv_null_mean"], "gaps must be MORE dispersed than uniform, not less"


def test_a_genuinely_even_spread_is_not_called_a_burst():
    """Mutation guard on the conclusion: evenly spaced arrivals must NOT reject."""
    text = "\n".join(_line(i, f"07:{i*5:02d}:00", blob=f"b{i}") for i in range(0, 12))
    t, _, _ = tma.parse_log(text)
    s = tma.arrival_stats(t)
    assert s["cv"] < 0.2, "perfectly even arrivals have near-zero gap dispersion"
    assert s["cv_p"] > 0.5, "an even spread must not be reported as clustered"
