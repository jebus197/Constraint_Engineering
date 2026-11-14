"""B195's producer must RUN, and its 2 arms must disagree in the stated direction.

WHY THIS FILE EXISTS. `scripts/the_board_is_unwatchable_2026-11-14.py` carries the
figures B195 puts to the founder, and `measured-rate-travels-with-its-script`
makes a figure without a re-runnable producer a claim about evidence rather than
evidence. The commit board refused the batch that added it, correctly, under the
addition-nothing-reaches half of the additive standard -- 11 confirmed defects of
that shape against 0 confirmed removals of something needed.

★ IT EXECUTES RATHER THAN NAMES. The surveyor behind that refusal detects a
producer by whether any test file NAMES it, so a mention would have silenced the
refusal while proving nothing -- `a-substring-is-not-a-call`. The guard's own
remediation says *"Either have a test execute them"*, and that is what this does.

★ NO FIGURE IS PINNED, DELIBERATELY. The ledger it reads is unversioned and gains
a row per board: inside 1 session on 2026-11-14 it moved n = 63 -> 74 -> 75 and
the mean 1612.619048 -> 1709.270270 -> 1721.386667 s. So the assertions are on
STRUCTURE and AGREEMENT -- that the arms disagree in the stated direction, that
4 interval routes agree, that the counts are floors -- never on a value.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "the_board_is_unwatchable_2026-11-14.py"


@pytest.fixture(scope="module")
def mod():
    if not PRODUCER.is_file():
        pytest.skip("the producer is not in this checkout")
    spec = importlib.util.spec_from_file_location("_board_watch", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_board_watch"] = m
    spec.loader.exec_module(m)
    return m


class TestTheHelpFlagCostsNothing:
    def test_help_exits_zero_and_runs_no_measurement(self):
        """A help flag must never cost anything. Driven, not assumed."""
        if not PRODUCER.is_file():
            pytest.skip("the producer is not in this checkout")
        r = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                           cwd=REPO, capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr[-400:]
        assert "usage:" in r.stdout
        assert "mean" not in r.stdout, (
            "`--help` printed a measurement, so it ran the work it exists to skip")

    def test_main_called_in_process_does_not_inherit_the_callers_argv(self, mod):
        """THE FAULT THAT REFUSED THE FIRST BOARD, pinned so it cannot return.

        A sibling producer exited 2 here because `parse_args(None)` reads
        `sys.argv[1:]`, which under pytest is PYTEST's argv. This asserts the
        in-process call parses nothing instead.
        """
        saved = sys.argv[:]
        try:
            sys.argv = ["x", "-q", "-p", "no:cacheprovider", "bench/tests/"]
            rc = mod.main(["--skip-arms"])
        finally:
            sys.argv = saved
        assert rc == 0, f"main() returned {rc!r} under a poisoned argv"


class TestTheTwoArmsDisagreeInTheStatedDirection:
    def test_the_buffered_arm_shows_nothing_and_the_streamed_arm_shows_all(self, mod):
        """THE SUBSTANTIVE CLAIM. Both arms are driven; neither is reasoned about."""
        buf = mod.arm_buffered()
        stm = mod.arm_streamed()
        assert buf["lines_produced"] == stm["lines_produced"] > 0, (
            "the 2 arms did not run the same child, so their comparison is void")
        assert buf["lines_observable_before_exit"] == 0, (
            "the buffered arm became observable, which would mean "
            "`PIPE + communicate` no longer hides the board and B195 is moot")
        assert stm["lines_observable_before_exit"] == stm["lines_produced"], (
            "the streamed arm did not observe every line, so the proposed repair "
            "does not deliver what B195 claims for it")
        assert buf["watcher_wakeups_finding_nothing"] >= 1, (
            "no watcher wake-up was recorded, so the arm did not actually watch")
        assert stm["full_text_recoverable"] is True, (
            "streaming lost the text, so the return value would not survive the "
            "repair and every caller of the git helper would break")
        assert stm["first_observable_at_s"] is not None
        assert stm["first_observable_at_s"] < buf["elapsed_s"], (
            "the first streamed line did not arrive before the buffered arm "
            "finished, so streaming buys no earliness")


class TestTheCostHalfIsStructurallySound:
    def test_four_interval_routes_agree_and_nothing_is_pinned(self, mod):
        c = mod.cost()
        if "determinate_n" not in c:
            pytest.skip(f"the ledger is too small on this machine: {c}")
        assert c["determinate_n"] >= 3, c
        assert c["ledger_rows"] >= c["determinate_n"]
        assert (c["ledger_rows"] - c["determinate_n"]
                == c["excluded_under_floor"]), (
            "the excluded count does not reconcile with the rows and the "
            "determinate set, so 1 of the 3 is being computed differently")
        #: AGREEMENT, not a value. 3 parametric routes must coincide to a
        #: numerical tolerance; the bootstrap is a 4th and may differ.
        assert c["ci_max_disagreement"] < 1e-6, (
            f"the interval routes disagree by {c['ci_max_disagreement']}, so at "
            f"least 1 of scipy, statsmodels and mpmath is wrong")
        lo, hi = c["ci_scipy"]
        assert lo < c["mean_s"] < hi, "the mean sits outside its own interval"
        blo, bhi = c["ci_bootstrap"]
        assert blo < c["mean_s"] < bhi, "the mean sits outside the bootstrap interval"
        assert abs(c["t_quantile_scipy"] - c["t_quantile_mpmath"]) < 1e-9

    def test_both_proportion_routes_agree_on_the_refusal_share(self, mod):
        c = mod.cost()
        if "determinate_n" not in c:
            pytest.skip("ledger too small")
        assert 0 <= c["refused"] <= c["determinate_n"]
        for a, b in (("wilson_statsmodels", "wilson_handrolled"),
                     ("cp_beta", "cp_exact_tails")):
            x, y = c[a], c[b]
            gap = max(abs(x[0] - y[0]), abs(x[1] - y[1]))
            assert gap < 1e-9, f"{a} and {b} disagree by {gap}"
        wlo, whi = c["wilson_statsmodels"]
        assert wlo <= c["refused_share"] <= whi, (
            "the refusal share sits outside its own Wilson interval")

    def test_the_silent_total_reconciles_with_the_mean(self, mod):
        """A SUM AND A MEAN CANNOT DISAGREE. Catches a population computed twice."""
        c = mod.cost()
        if "determinate_n" not in c:
            pytest.skip("ledger too small")
        implied = c["mean_s"] * c["determinate_n"]
        assert abs(implied - c["total_silent_s"]) < 1.0, (
            f"mean x n = {implied} against a reported total of "
            f"{c['total_silent_s']}, so the 2 are over different populations")
        assert abs(c["total_silent_h"] * 3600.0 - c["total_silent_s"]) < 1.0
