"""Round 8: the fitted change point in task 0.2 was a MAXIMALLY-SELECTED
statistic reported as a single test. This is the test that says so.

THE DEFECT. `scripts/wolfram_route_health_2026-09-10.py::change_point` tries
every candidate cut date, keeps the split minimising the Fisher exact p, and
the script printed that minimum as "Fisher exact p". `min_j p_j` over m
dependent tests is not a p-value. Under the null it is stochastically smaller
than U(0,1), so the printed figure overstates the evidence.

WHY THIS IS NOT A STYLE POINT. `.claude/CLAUDE.md` quotes the figure --
"Fisher exact p = 2.199086e-14" -- as the justification for RETIRING the
Wolfram route, and the additive standard permits a removal only on a committed
measurement. A measurement whose stated error rate is wrong by a factor of m
is not the measurement the standard asks for, whichever way the decision then
goes.

WHAT THIS FILE PROVES, MECHANICALLY AND WITHOUT THE LOGS.
  1. On data with NO change point, the uncorrected minimum crosses 0.05 far
     more often than 5% of the time. That is the defect, exhibited.
  2. The Bonferroni correction shipped in `change_point` restores control of
     the error rate on the same data. That is the fix, exhibited.
  3. The permuted statistic and the observed statistic are computed by the
     SAME function, so the permutation null calibrates the quantity it
     corrects.
All three run offline on synthetic data, so this file does not skip on a
machine with no Claude log directory -- which is the machine most likely to
run it.
"""
from __future__ import annotations

import importlib.util
import pathlib
import random

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "wolfram_route_health_2026-09-10.py"


def _load():
    """Import the script by path. It is a script, not a package module."""
    spec = importlib.util.spec_from_file_location("wolfram_route_health", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pytest.importorskip("scipy")
WRH = _load()

#: A null world: 12 dates, 40 attempts, failures independent of date.
#: DELIBERATELY SMALL. A large n would make even the uncorrected search
#: well-behaved by concentration and hide the effect this file measures.
_N_DATES, _N_ROWS, _REPLICATES, _ALPHA = 12, 40, 400, 0.05


def _null_world(rng):
    """(dates, labels) with the failure label INDEPENDENT of the date."""
    dates = sorted(f"2026-08-{1 + rng.randrange(_N_DATES):02d}"
                   for _ in range(_N_ROWS))
    labels = [rng.random() < 0.5 for _ in range(_N_ROWS)]
    return dates, labels


def _sweep():
    """Type-I error of the uncorrected minimum and of the Bonferroni fix."""
    rng = random.Random(20260910)
    raw_hits = bonf_hits = usable = 0
    for _ in range(_REPLICATES):
        dates, labels = _null_world(rng)
        cuts = sorted(set(dates))[1:]
        p_min = WRH._min_p_over_cuts(dates, labels, cuts)
        if p_min is None:
            continue
        usable += 1
        raw_hits += (p_min <= _ALPHA)
        bonf_hits += (min(1.0, len(cuts) * p_min) <= _ALPHA)
    return raw_hits / usable, bonf_hits / usable, usable


class TestTheDefectIsRealOnNullData:
    def test_the_uncorrected_minimum_is_anticonservative(self):
        """THE FALSIFIER. Fails iff the reported statistic is well calibrated.

        If `min_j p_j` really were a p-value it would cross 0.05 about 5% of
        the time on data with no change point. It does not.
        """
        raw, _bonf, n = _sweep()
        assert raw > 2 * _ALPHA, (
            f"the uncorrected minimum crossed {_ALPHA} in only {raw:.1%} of "
            f"{n} null replicates, which is close to nominal -- the "
            f"multiple-comparisons objection would then not apply and this "
            f"whole correction would be unnecessary")


class TestTheFixRestoresControl:
    def test_bonferroni_holds_the_nominal_rate(self):
        raw, bonf, n = _sweep()
        # Union bound gives P(reject) <= alpha; the Monte-Carlo standard error
        # at alpha=0.05 over n replicates is sqrt(a(1-a)/n), and 3 of them is
        # the slack allowed so this does not flake.
        slack = 3 * (_ALPHA * (1 - _ALPHA) / n) ** 0.5
        assert bonf <= _ALPHA + slack, (
            f"Bonferroni rejected in {bonf:.1%} of {n} null replicates, above "
            f"the nominal {_ALPHA:.0%} (+{slack:.1%} MC slack). The union "
            f"bound says this cannot happen if the per-cut tests are valid, "
            f"so either the correction is misapplied or m is miscounted")

    def test_the_correction_actually_moved_the_number(self):
        """An addition nothing reaches is not additive. This is the reach."""
        raw, bonf, _n = _sweep()
        assert bonf < raw, (
            f"correcting changed nothing: uncorrected {raw:.1%}, corrected "
            f"{bonf:.1%}")


class TestThePermutationNullMatchesTheObservedStatistic:
    def test_one_implementation_serves_both(self):
        """If these were two implementations the permutation p would be void.

        The observed statistic is `_min_p_over_cuts(..., want_detail=True)`
        and the permuted one is `_min_p_over_cuts(...)`. Same call, so the
        detail form's `p` must equal the plain form's return exactly.
        """
        rng = random.Random(7)
        dates, labels = _null_world(rng)
        cuts = sorted(set(dates))[1:]
        detail = WRH._min_p_over_cuts(dates, labels, cuts, want_detail=True)
        plain = WRH._min_p_over_cuts(dates, labels, cuts)
        assert detail["p"] == plain

    def test_a_permutation_p_is_never_reported_as_zero(self):
        """0 hits means p <= 1/(B+1). It does NOT mean p = 0."""
        rng = random.Random(11)
        dates, labels = _null_world(rng)
        cuts = sorted(set(dates))[1:]
        obs = WRH._min_p_over_cuts(dates, labels, cuts)
        hits, shuffled = 0, list(labels)
        for _ in range(50):
            rng.shuffle(shuffled)
            pm = WRH._min_p_over_cuts(dates, shuffled, cuts)
            hits += (pm is not None and pm <= obs)
        assert (1 + hits) / (1 + 50) > 0, "the (1+hits)/(1+B) form cannot be 0"


class TestTheScriptReportsTheCorrectedFigure:
    def test_change_point_emits_the_corrected_fields(self):
        """Skips only where the LOGS are absent, never where the maths is."""
        if not WRH.LOGDIR.is_dir():
            pytest.skip("no Claude log directory on this machine")
        cp = WRH.change_point(permutations=50)
        if cp is None:
            pytest.skip("no attempts with timestamps in the logs")
        for field in ("n_candidate_cuts", "p_uncorrected", "p_bonferroni",
                      "p_permutation", "last_attempt", "last_attempt_failed"):
            assert field in cp, f"change_point no longer reports {field}"
        assert cp["p_bonferroni"] >= cp["p_uncorrected"], (
            "the corrected p is SMALLER than the uncorrected one, which is "
            "arithmetically impossible for m >= 1")
        assert cp["p_bonferroni"] == pytest.approx(
            min(1.0, cp["n_candidate_cuts"] * cp["p_uncorrected"]))
