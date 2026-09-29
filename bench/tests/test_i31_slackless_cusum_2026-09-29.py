"""The I31 slackless-CUSUM measurement, EXECUTED, with its claims cross-checked.

WHY THIS EXISTS. The founder asked on 2026-09-29 whether the drift detector *"will
fire after 3 consecutive rounds in any given experiment"* and whether anything is
needed *"to make it effective"*. The answer to the first is no; the answer to the
second is that the obvious repair -- persisting the accumulator across runs -- would
convert a detector that never fires into one that fires under a perfect null. That
claim is a measurement, so under `measured-rate-travels-with-its-script` it may only
be quoted alongside the code that produced it. This file executes that code.

IT ALSO GUARDS THE DEPLOYED CEILING AGAINST THE LIVE MODULE. The script's arithmetic
argument is only worth anything if its premises still hold in `bench/dm/_memory.py`:
threshold 2.0, a residual that is a difference of 2 probabilities, and a `save()` that
does not persist `self._drift`. Those are asserted against the real module here, not
restated -- `execute-do-not-grep`. If someone later persists the accumulator, the
ceiling test fails and points at this file's own conclusion.
"""
from __future__ import annotations

import importlib.util
import inspect
import math
import random
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "i31_slackless_cusum_2026-09-29.py"


@pytest.fixture(scope="module")
def mod():
    assert SCRIPT.is_file(), f"missing producer: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("i31_slackless", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def memory_mod():
    sys.path.insert(0, str(REPO))
    from bench.dm import _memory
    return _memory


class TestThePremisesStillHoldInTheLiveModule:
    """The script's argument is only sound while these remain true of production."""

    def test_the_threshold_the_script_assumes_is_the_deployed_default(self, mod, memory_mod):
        sig = inspect.signature(memory_mod.ImmuneMemory.__init__)
        deployed = sig.parameters["drift_threshold"].default
        assert mod.THRESHOLD == deployed, (
            f"the script assumes {mod.THRESHOLD}, production uses {deployed}")

    def test_save_still_does_not_persist_the_accumulator(self, memory_mod):
        """If this ever changes, the 'cannot fire' conclusion changes with it."""
        src = inspect.getsource(memory_mod.ImmuneMemory.save)
        assert "_drift" not in src, (
            "save() now persists the CUSUM accumulator, so the ceiling argument in "
            "scripts/i31_slackless_cusum_2026-09-29.py no longer holds -- and the "
            "false-alarm measurement in that script becomes the LIVE risk")

    def test_update_drift_still_has_no_slack_term(self, memory_mod):
        """The whole finding: this is a random walk, not a CUSUM."""
        src = inspect.getsource(memory_mod.ImmuneMemory.update_drift)
        assert "cusum_pos" in src and "cusum_neg" in src
        # A slack term would appear as a subtraction from the residual before the max().
        assert "max(0.0, ds.cusum_pos + residual)" in src, (
            "update_drift's accumulation changed; re-derive the false-alarm figures")


class TestTheCeilingArgument:
    def test_the_deployed_configuration_cannot_reach_the_threshold_in_one_run(self, mod):
        c = mod.ceiling()
        assert c["max_reachable_per_run"] < c["threshold"]
        assert c["updates_needed"] == 3, "the z3 result is 3 same-direction UPDATES"
        assert c["updates_supplied_per_run"] == 1
        assert c["accumulator_persisted"] is False

    def test_three_is_updates_not_rounds(self, mod):
        """The founder's question named rounds. The unit is updates per flaw class."""
        c = mod.ceiling()
        assert c["updates_needed"] > c["updates_supplied_per_run"], (
            "if 1 run could supply the needed updates, 'per round' would be the right unit")


class TestTheFalseAlarmMeasurement:
    """The claim that matters: persistence ALONE makes it worse."""

    @pytest.fixture(scope="class")
    def table(self, mod):
        return mod.false_alarm_table(trials=1500, sigma=0.15)

    def test_the_slackless_statistic_fires_under_a_perfect_null(self, table):
        long = [r for r in table if r["steps"] >= 200]
        assert long, "no long horizon measured"
        for r in long:
            assert r["no_slack_p"] > 0.5, (
                f"at {r['steps']} steps the slackless statistic fired only "
                f"{r['no_slack_p']:.2%} of the time under a null; the finding does not hold")

    def test_slack_suppresses_it_at_every_horizon(self, table):
        for r in table:
            assert r["slack_p"] <= r["no_slack_p"] + 1e-9, (
                f"slack made things WORSE at {r['steps']} steps")
        worst = max(r["slack_p"] for r in table)
        assert worst < 0.25, f"slacked false-alarm rate reached {worst:.2%}"

    def test_short_horizons_are_quiet_for_both(self, table):
        """A guard that fires everywhere distinguishes nothing."""
        for r in table:
            if r["steps"] <= 10:
                assert r["no_slack_p"] == 0.0 and r["slack_p"] == 0.0

    def test_every_rate_carries_a_wilson_interval_containing_it(self, table):
        for r in table:
            lo, hi = r["no_slack_ci"]
            assert lo <= r["no_slack_p"] <= hi, r
            lo, hi = r["slack_ci"]
            assert lo <= r["slack_p"] <= hi, r

    def test_the_wilson_formula_agrees_with_statsmodels(self, mod):
        """Cross-verification on 2 tools, as the standing rule requires."""
        from statsmodels.stats.proportion import proportion_confint
        worst = 0.0
        for k, n in [(0, 4000), (650, 4000), (3719, 4000), (4000, 4000), (118, 4000)]:
            a, b = mod.wilson(k, n)
            c, d = proportion_confint(k, n, method="wilson")
            worst = max(worst, abs(a - c), abs(b - d))
        assert worst < 1e-12, f"the 2 tools disagree by {worst:.3e}"


class TestTheScalingLaw:
    def test_crossing_follows_the_diffusive_square_law(self, mod):
        """Checked across 3 noise levels, not asserted from 1."""
        rows = mod.scaling_table()
        assert len(rows) == 3
        ratios = [r["ratio"] for r in rows]
        assert max(ratios) - min(ratios) < 0.20, (
            f"the ratio is not near-constant across sigma: {ratios}")
        for r in rows:
            assert 0.3 < r["ratio"] < 0.9, r

    def test_the_median_falls_as_noise_rises(self, mod):
        rows = sorted(mod.scaling_table(), key=lambda r: r["sigma"])
        meds = [r["median"] for r in rows]
        assert meds == sorted(meds, reverse=True), meds


class TestItIsRunnableAndCheap:
    def test_help_does_not_run_the_measurement(self, mod):
        """A --help must never do work. Project rule, and this script is read-only."""
        with pytest.raises(SystemExit) as e:
            mod.main(["--help"])
        assert e.value.code == 0

    def test_main_returns_zero_on_a_small_run(self, mod, capsys):
        assert mod.main(["--trials", "60"]) == 0
        out = capsys.readouterr().out
        assert "WHY IT CANNOT FIRE AS DEPLOYED" in out
        assert "Wilson" in out
