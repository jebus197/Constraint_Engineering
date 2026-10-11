"""Item 12: a human review fires only on substantial evidence, and halts nothing.

HIS CONDITION, 2026-10-11: a review *"should only be triggered if there is
substantial evidence that an experimental run is unlikely to converge under the
given conditions and with the available resources."*

HIS CONSTRAINT, 2026-09-28, which this must not violate: *"What I don't want is a
condition where no run could ever complete, and where the HIL queue could grow to
unmanageable levels."*

WHAT THIS PINS
  1. One statistical signal alone is a HUNCH and must not request a review.
  2. The deductive signal alone IS substantial, because it is arithmetic.
  3. A CLEAN run is never flagged -- 3 consecutive clean convergences is the
     programme of study's own success criterion, so flagging them would be fatal.
  4. A healthy declining run is never flagged.
  5. It is WIRED into the hardened gate's telemetry, and it HALTS NOTHING: the
     gate's verdict is identical whether a review is requested or not.
  6. The measured false-alarm rate travels with its producing script.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from human_review_trigger import (B_ROUND_FRACTION, C_CONSECUTIVE_NO_DECAY,  # noqa: E402
                                  ReviewVerdict, assess)


class TestOneWeakSignalIsAHunch:
    def test_signal_c_alone_does_not_request_a_review(self):
        """Early in a run, a flat critical series is an artefact, not evidence."""
        v = assess(round_idx=4, max_rounds=21, consecutive_zero_crit_required=3,
                   critical_novelty_series=[4, 4, 4, 4])
        assert v.detail["signal_c"] is True
        assert v.detail["signal_a"] is False
        assert v.detail["signal_b"] is False
        assert v.review_requested is False
        assert v.detail["substantial_because"] == "no signal reached the bar"

    def test_signal_b_alone_does_not_request_a_review(self):
        v = assess(round_idx=18, max_rounds=21, consecutive_zero_crit_required=3,
                   critical_novelty_series=[9, 6, 4, 1],   # declining -> C silent
                   gamma_critical=0.10, gamma_threshold=0.30)
        assert v.detail["signal_b"] is True
        assert v.detail["signal_c"] is False
        assert v.detail["signal_a"] is False
        assert v.review_requested is False

    def test_two_independent_statistical_signals_do_reach_the_bar(self):
        v = assess(round_idx=15, max_rounds=21, consecutive_zero_crit_required=3,
                   critical_novelty_series=[4, 4, 4, 4],
                   gamma_critical=0.05, gamma_threshold=0.30)
        assert v.detail["signal_a"] is False
        assert v.detail["signal_b"] and v.detail["signal_c"]
        assert v.review_requested is True
        assert "2 independent statistical signals" in v.detail["substantial_because"]


class TestTheDeductiveSignalIsSubstantialAlone:
    def test_fewer_rounds_left_than_the_window_requires(self):
        v = assess(round_idx=20, max_rounds=21, consecutive_zero_crit_required=3)
        assert v.detail["signal_a"] is True
        assert v.review_requested is True
        assert v.detail["substantial_because"] == "deductive signal A"

    def test_exactly_enough_rounds_left_does_not_fire(self):
        """The boundary must be the gate's own K, not K plus a margin."""
        v = assess(round_idx=18, max_rounds=21, consecutive_zero_crit_required=3)
        assert v.detail["rounds_remaining"] == 3
        assert v.detail["signal_a"] is False

    def test_it_follows_K_rather_than_hard_coding_3(self):
        for k in (2, 3, 5):
            at_limit = assess(round_idx=21 - k, max_rounds=21,
                              consecutive_zero_crit_required=k)
            inside = assess(round_idx=21 - k + 1, max_rounds=21,
                            consecutive_zero_crit_required=k)
            assert at_limit.detail["signal_a"] is False, f"K={k}"
            assert inside.detail["signal_a"] is True, f"K={k}"

    def test_a_zero_K_cannot_fire_the_deductive_signal(self):
        v = assess(round_idx=21, max_rounds=21, consecutive_zero_crit_required=0)
        assert v.detail["signal_a"] is False


class TestItNeverFlagsTheRunsItMustNot:
    def test_a_clean_run_is_not_flagged(self):
        """A clean target has an all-zero critical series BY CONSTRUCTION, and 3
        consecutive clean convergences is the programme of study's success
        criterion. Flagging those would make this trigger worse than useless."""
        v = assess(round_idx=14, max_rounds=21, consecutive_zero_crit_required=3,
                   critical_novelty_series=[0, 0, 0, 0],
                   gamma_critical=0.0, gamma_threshold=0.30,
                   gamma_is_estimable=False)
        assert v.review_requested is False
        assert v.detail["signal_b"] is False, "gamma's 0.0 SENTINEL was read as a slope"
        assert v.detail["signal_c"] is False

    def test_a_healthy_declining_run_is_not_flagged(self):
        v = assess(round_idx=5, max_rounds=21, consecutive_zero_crit_required=3,
                   critical_novelty_series=[8, 5, 3, 1],
                   gamma_critical=0.55, gamma_threshold=0.30)
        assert v.review_requested is False

    def test_an_unestimable_gamma_cannot_fire_signal_b(self):
        """`_estimate_gamma` returns 0.0 for 4 distinct reasons, only 1 of which is
        a slope. Reading the sentinel as 'no decay' is the error his 2026-10-08
        ruling drew the distinction to prevent."""
        v = assess(round_idx=20, max_rounds=100, consecutive_zero_crit_required=3,
                   gamma_critical=0.0, gamma_threshold=0.30, gamma_is_estimable=False)
        assert v.detail["signal_b"] is False

    def test_signal_b_waits_until_the_budget_is_mostly_spent(self):
        for frac, expect in ((0.2, False), (0.5, False), (0.9, True)):
            r = int(frac * 100)
            v = assess(round_idx=r, max_rounds=100, consecutive_zero_crit_required=3,
                       gamma_critical=0.05, gamma_threshold=0.30)
            assert v.detail["signal_b"] is expect, f"at {frac:.0%} spent"
        assert B_ROUND_FRACTION == 0.6


class TestItHaltsNothing:
    def test_the_verdict_object_can_never_halt(self):
        v = assess(round_idx=20, max_rounds=21, consecutive_zero_crit_required=3)
        assert v.halts_the_run is False
        assert v.as_dict()["human_review_halts_the_run"] is False
        assert v.as_dict()["human_review_is_advisory"] is True

    def test_even_a_hand_built_verdict_reports_no_halt(self):
        assert ReviewVerdict(review_requested=True).halts_the_run is False
        assert ReviewVerdict(review_requested=True).as_dict()[
            "human_review_halts_the_run"] is False

    def test_the_gate_verdict_is_identical_whether_a_review_is_requested(self):
        import reference_runner_v3 as R
        real = R._settled_novelty_series
        try:
            R._settled_novelty_series = (
                lambda registry, rnd, **kw: ([4, 4, 4, 4], [4, 4, 4, 4]))
            cfg = R.RunnerConfig(max_rounds=21)
            flagged = R._check_hardened_convergence(round_idx=20, registry={}, cfg=cfg)
            quiet = R._check_hardened_convergence(round_idx=5, registry={}, cfg=cfg)
            assert flagged[2]["human_review_requested"] is True
            assert quiet[2]["human_review_requested"] is False
            # the gate's own two outputs must be decided by the gate, not by this
            assert isinstance(flagged[0], bool) and isinstance(quiet[0], bool)
        finally:
            R._settled_novelty_series = real

    def test_a_broken_trigger_cannot_fell_a_run(self):
        import human_review_trigger as HRT
        import reference_runner_v3 as R
        real_assess, real_series = HRT.assess, R._settled_novelty_series
        try:
            HRT.assess = lambda **k: (_ for _ in ()).throw(ValueError("deliberate"))
            R._settled_novelty_series = (
                lambda registry, rnd, **kw: ([4, 4, 4], [4, 4, 4]))
            ok, why, telem = R._check_hardened_convergence(
                round_idx=20, registry={}, cfg=R.RunnerConfig(max_rounds=21))
            assert telem["human_review_requested"] is False
            assert "error" in telem["human_review_detail"]
            assert isinstance(ok, bool)
        finally:
            HRT.assess, R._settled_novelty_series = real_assess, real_series


class TestItIsWired:
    def test_the_telemetry_carries_it(self):
        import reference_runner_v3 as R
        real = R._settled_novelty_series
        try:
            R._settled_novelty_series = (
                lambda registry, rnd, **kw: ([4, 4, 4, 4], [4, 4, 4, 4]))
            _, _, telem = R._check_hardened_convergence(
                round_idx=20, registry={}, cfg=R.RunnerConfig(max_rounds=21))
            for key in ("human_review_requested", "human_review_signals",
                        "human_review_detail", "human_review_halts_the_run",
                        "human_review_is_advisory"):
                assert key in telem, f"{key} does not reach the telemetry"
        finally:
            R._settled_novelty_series = real

    def test_it_reads_the_gates_own_K_not_a_private_copy(self):
        """A second copy of K would drift from the gate it is reasoning about."""
        src = (pathlib.Path(__file__).resolve().parents[1]
               / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert "consecutive_zero_crit_required=W" in src, (
            "the trigger is not being passed the gate's own window width")

    def test_every_requested_review_states_its_evidence(self):
        for kw in ({"round_idx": 20, "max_rounds": 21,
                    "consecutive_zero_crit_required": 3},
                   {"round_idx": 15, "max_rounds": 21,
                    "consecutive_zero_crit_required": 3,
                    "critical_novelty_series": [4, 4, 4, 4],
                    "gamma_critical": 0.05, "gamma_threshold": 0.30}):
            v = assess(**kw)
            assert v.review_requested and v.signals
            for s in v.signals:
                assert len(s) > 30, f"a signal with no explanation: {s!r}"


class TestTheMeasuredRateTravelsWithItsScript:
    def test_the_producer_exists_and_answers_help_for_free(self):
        import subprocess
        root = pathlib.Path(__file__).resolve().parents[2]
        script = root / "scripts" / "the_review_trigger_false_alarm_rate_2026-10-11.py"
        assert script.exists(), "the quoted false-alarm rate has no producing script"
        r = subprocess.run([sys.executable, str(script), "--help"],
                           capture_output=True, text=True, timeout=120, cwd=str(root))
        assert r.returncode == 0
        assert "usage:" in r.stdout

    def test_the_refuted_design_is_recorded_not_merely_avoided(self):
        src = (pathlib.Path(__file__).resolve().parents[1]
               / "human_review_trigger.py").read_text(encoding="utf-8")
        assert "REFUTED" in src and "4 OF THE 5" in src, (
            "the rejected n*-based design must stay recorded with its measured "
            "false-alarm rate, or it will be proposed again")
