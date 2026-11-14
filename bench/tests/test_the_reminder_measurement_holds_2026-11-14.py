"""The reminder measurement's CONTRACTS, not its figures.

★ WHAT IS GUARDED AND WHAT DELIBERATELY IS NOT. The figures in
`scripts/does_a_per_turn_reminder_change_compliance_2026-11-14.py` move every
day, because the after-period grows and the transcripts grow with it. Pinning
them would make this guard go red on a day when nothing broke -- the shape this
project records as a guard pinning the defect as current behaviour. So the
contracts are pinned instead: that a power is a probability, that the 2 power
routes agree, that the day-count requirement moves in the right direction, and
that the install moment matches the commit it claims.

★ THE POWER-OUT-OF-RANGE DEFECT IS PINNED EXPLICITLY, because it happened. The
first version of `power_analytic` computed `2 * (1 - Phi(z - d))` and returned
**1.9997** -- an impossible power. It was caught by the value lying outside
[0, 1], not by rereading the algebra, so the range check is the assertion that
would have caught it and it is here by name.

★ AND THE INSTALL MOMENT IS NOT A ROUND NUMBER. `REMINDER_INSTALLED` is the
author timestamp of commit `371f55cc`, which added `open_roster` and its
per-turn injection. If that constant is ever edited to a tidy midnight, the
before/after split silently moves and every figure shifts with it.

EXECUTES the producer's functions. It does not read its source text.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))


def _producer():
    spec = importlib.util.spec_from_file_location(
        "reminder_effect",
        REPO / "scripts" / "does_a_per_turn_reminder_change_compliance_2026-11-14.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["reminder_effect"] = m
    spec.loader.exec_module(m)
    return m


P = _producer()


@pytest.mark.parametrize("n_days", [4, 7, 14, 30, 45, 60, 90, 200])
@pytest.mark.parametrize("sd", [0.01, 0.0807, 0.3])
def test_a_power_is_always_a_probability(n_days, sd):
    """★ THE DEFECT THAT HAPPENED: the first formula returned 1.9997."""
    a = P.power_analytic(n_days, sd)
    assert 0.0 <= a <= 1.0, f"power {a} is not a probability at n={n_days}, sd={sd}"


def test_the_two_power_routes_agree():
    """1 route agreeing with itself is not a cross-check."""
    worst = 0.0
    for n in (14, 30, 45, 60):
        a = P.power_analytic(n, 0.0807)
        s = P.power_simulated(n, 0.0807, trials=4000)
        worst = max(worst, abs(a - s))
    assert worst < 0.06, f"analytic and simulated power disagree by {worst:.4f}"


def test_power_rises_with_days():
    sd = 0.0807
    vals = [P.power_analytic(n, sd) for n in (4, 14, 30, 45, 60, 90)]
    assert vals == sorted(vals), f"power is not monotone in days: {vals}"


def test_power_falls_as_the_noise_rises():
    vals = [P.power_analytic(30, s) for s in (0.01, 0.05, 0.0807, 0.2, 0.4)]
    assert vals == sorted(vals, reverse=True), f"power is not monotone in sd: {vals}"


def test_more_noise_needs_more_days():
    quiet = P.days_needed(0.02)
    noisy = P.days_needed(0.2)
    assert 0 < quiet < noisy, (quiet, noisy)


def test_the_detectable_effect_is_declared_as_a_figure():
    """A test with an undeclared effect size cannot be under-powered on purpose."""
    assert abs(P.DETECTABLE_DECAY_PER_DAY - 0.10 / 30) < 1e-15


def test_the_install_moment_matches_the_commit_it_names():
    """★ NOT A ROUND NUMBER. SKIPS where the commit is unreachable."""
    r = subprocess.run(["git", "log", "-1", "--format=%aI", P.REMINDER_COMMIT],
                       cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        pytest.skip(f"commit {P.REMINDER_COMMIT} is not reachable from this checkout")
    actual = dt.datetime.fromisoformat(r.stdout.strip().replace("Z", "+00:00"))
    assert P.REMINDER_INSTALLED == actual.astimezone(dt.timezone.utc), (
        f"the declared install moment {P.REMINDER_INSTALLED.isoformat()} is not "
        f"the author time of {P.REMINDER_COMMIT} ({actual.isoformat()}); the "
        f"before/after split has silently moved")
    assert (P.REMINDER_INSTALLED.minute, P.REMINDER_INSTALLED.second) != (0, 0), \
        "a tidy midnight is a sign the constant was typed rather than measured"


def test_the_scan_returns_timestamped_rows_in_both_arms():
    """NON-VACUITY: a comparison with an empty arm is not a comparison."""
    rows, no_stamp, n_files = P.scan(limit=3)
    assert n_files > 0, "no transcripts were read"
    assert rows, "0 known entry codes found, so the predicate accused nothing"
    assert all(isinstance(ts, dt.datetime) for ts, _b in rows)
    before = [b for ts, b in rows if ts < P.REMINDER_INSTALLED]
    after = [b for ts, b in rows if ts >= P.REMINDER_INSTALLED]
    assert before and after, (
        f"one arm is empty ({len(before)} before, {len(after)} after); the "
        f"before/after design has nothing to compare")


@pytest.mark.skipif(
    os.environ.get("CDSFL_SLOW_TESTS") != "1",
    reason=("the producer costs about 185 s and the cause is MEASURED, not "
            "guessed: the project's reserved 2-route interval helper `_iv(k, n)` "
            "runs an exact-binomial Clopper-Pearson bisection whose cost is "
            "about quadratic in n -- timed 1.72 s at n=100, 12.02 s at 1,000, "
            "26.29 s at 2,096, 66.27 s at 5,000 and 150.11 s at 10,537, which is "
            "this corpus's before-arm size. Limiting the transcript count does "
            "NOT help, because 1 transcript holds nearly every code: scan(limit=2) "
            "and scan(limit=3) both return 12,516 rows in about 15 s. The commit "
            "gate is already near 27 minutes, so this runs on demand with "
            "CDSFL_SLOW_TESTS=1. The 31 contract tests beside it need no corpus.")
)
def test_the_producer_exits_zero():
    """A SMALL trial count on purpose: this asserts the producer RUNS, not that
    its power figure is precise."""
    assert P.main(["--limit", "2", "--power-trials", "200"]) == 0
