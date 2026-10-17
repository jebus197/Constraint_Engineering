#!/usr/bin/env python3
"""When a human-review stop is WARRANTED, and why -- entry B27.

HIS DESIGN, 2026-10-11, verbatim:

    "A human review stop anywhere in the run should only be triggered if there is
    substantial evidence that a an experimental run is unlikely to converge under
    the given conditions and with the available resources. This includes all the
    factors that might influence this outcome, including mechanical errors, number
    of rounds in any given experiment, available compute resources etc."

WHAT WAS THERE BEFORE. Both call sites in `bench/reference_runner_v3.py` fired on
`cfg.hil_review` ALONE -- a flag, consulted with no evidence whatsoever. Enabling
the facility therefore halted EVERY round, which is what entry C9 established
turns 1 autonomous run into N sequential sessions and destroys the very
autonomous-convergence measurement the run exists to produce. That is why the
facility has been off in every shipped config and why 0 archived runs have ever
paused: as built it was unusable, so it was never used.

WHY A CONJUNCTION RATHER THAN A SET OF THRESHOLDS. A stop that interrupts a run
which was going to converge costs the whole measurement, so the expensive error is
a FALSE PAUSE, not a missed one -- the run ends by itself at `max_rounds` if
nothing fires. A disjunction over single signals ("gamma is low", "a seat failed")
over-fires on noise. So each clause below requires SEVERAL of the factors he named
to agree, and a single noisy signal cannot pause anything.

THE TWO CLAUSES, each a distinct way a run becomes unlikely to converge:

  STALLED_AND_OUT_OF_ROOM -- the run is making no convergence progress and does
      not have the room left to make it. Requires: past the earliest round at
      which convergence is even assessable, a substantial share of the round
      budget already spent, the convergence measure still short of its threshold,
      no meaningful improvement across the recent window, AND the observed rate of
      improvement unable to close the remaining gap in the rounds or wall clock
      that remain. This is his phrase "unlikely to converge UNDER THE GIVEN
      CONDITIONS AND WITH THE AVAILABLE RESOURCES" read literally: convergence and
      resources are one joint judgement, not two separate alarms.

  MECHANICALLY_BROKEN -- the run's findings are dominated by mechanical faults
      rather than substantive ones. More rounds cannot help a run whose output is
      mostly its own malfunction, which is the distinct case his "mechanical
      errors" names. Requires enough findings for a share to mean anything, so a
      single fault in a single finding cannot fire it.

THE THRESHOLDS ARE DEFAULTS, AND THEY ARE UNMEASURED. No run has ever paused, so
there is no archive of pauses against which to calibrate "substantial". Rather
than present a chosen number as if it were derived, every threshold is a named
field with a stated default, `thresholds_are_calibrated` is False, and
`Verdict.caveat` says so in any report that records a pause. When runs exist that
either paused or burned to `max_rounds`, the defaults can be fitted to them and
that flag flipped by measurement. Until then a reader is told the number is a
judgement.

This module DECIDES. It is called by both call sites and it returns the reasons,
so the report records WHY a stop fired and a reader can tell a principled
interruption from an arbitrary one.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

#: Fraction of the round budget that must be spent before a stall can be called.
#: Below this the run has not had a fair chance and "no progress yet" is normal.
DEFAULT_MIN_ROUND_FRACTION = 0.5

#: Improvement in the convergence measure, per round across the recent window,
#: at or below which the run counts as making no meaningful progress.
DEFAULT_STALL_EPSILON = 0.01

#: How many recent rounds the progress window spans. Fewer than 2 gammas cannot
#: show a trend at all, so this is the floor as well as the default.
DEFAULT_WINDOW = 3

#: Share of findings that must be mechanical faults before the run counts as
#: broken rather than slow, with a floor on the denominator.
DEFAULT_MECHANICAL_SHARE = 0.5
DEFAULT_MECHANICAL_MIN_FINDINGS = 6


@dataclass(frozen=True)
class Thresholds:
    """Every number this decision depends on, in one place, all overridable."""
    min_round_fraction: float = DEFAULT_MIN_ROUND_FRACTION
    stall_epsilon: float = DEFAULT_STALL_EPSILON
    window: int = DEFAULT_WINDOW
    mechanical_share: float = DEFAULT_MECHANICAL_SHARE
    mechanical_min_findings: int = DEFAULT_MECHANICAL_MIN_FINDINGS
    #: False until fitted to runs that actually paused or burned out. Never set
    #: this True from a judgement; set it from a measurement and say which.
    calibrated: bool = False


@dataclass(frozen=True)
class RunEvidence:
    """What the runner knows at a candidate stop. Every field is already to hand."""
    round_idx: int
    max_rounds: int
    gamma_critical: float
    gamma_critical_threshold: float
    earliest_round: int = 3
    #: ★ THE CRITICAL SERIES, per completed round, OLDEST FIRST -- NOT the
    #: all-findings gamma. Every recorded convergence in the archive names the
    #: critical measure: STATE_CONVERGED, CRITICAL_QUIESCENCE_CONVERGED and
    #: HARDENED_CONVERGED all decide on gamma_critical. Measured 2026-10-17:
    #: feeding the all-findings series instead produced 2 false pauses out of 28
    #: converged runs, because exp44's all-findings gamma sat flat while its
    #: critical gamma climbed 0.1803 -> 0.4316 on the way to converging at round
    #: 12. The fields carry `critical` in their names so that substitution cannot
    #: be made silently. May be shorter than round_idx after a resume; the window
    #: adapts.
    gamma_critical_history: tuple[float, ...] = ()
    mechanical_faults: int = 0
    total_findings: int = 0
    elapsed_s: float = 0.0
    wall_clock_cap_s: float = 0.0

    def round_fraction(self) -> float:
        if self.max_rounds <= 0:
            return 0.0
        return min(1.0, max(0.0, self.round_idx / float(self.max_rounds)))

    def rounds_remaining(self) -> int:
        return max(0, int(self.max_rounds) - int(self.round_idx))

    def clock_fraction(self) -> Optional[float]:
        """Share of the wall-clock cap used, or None when no cap is in force."""
        if self.wall_clock_cap_s and self.wall_clock_cap_s > 0:
            return min(1.0, max(0.0, self.elapsed_s / float(self.wall_clock_cap_s)))
        return None


@dataclass(frozen=True)
class Verdict:
    """The decision, the clause that produced it, and the evidence behind it."""
    should_pause: bool
    clause: Optional[str]
    reasons: tuple[str, ...] = ()
    measured: dict = field(default_factory=dict)
    caveat: str = ""

    def as_report_fields(self) -> dict:
        """What the runner writes into the report when a stop fires or does not."""
        return {
            "hil_should_pause": self.should_pause,
            "hil_clause": self.clause,
            "hil_reasons": list(self.reasons),
            "hil_measured": dict(self.measured),
            "hil_threshold_caveat": self.caveat,
        }


UNCALIBRATED_CAVEAT = (
    "The thresholds behind this decision are DEFAULTS, not measurements: no run "
    "has ever paused, so there is no archive of pauses to calibrate 'substantial' "
    "against. Read the clause and the measured values, not the verdict alone."
)


def _progress_per_round(history: tuple[float, ...], window: int) -> Optional[float]:
    """Mean improvement per round across the last `window` rounds, or None.

    None means the question could not be asked -- fewer than 2 observations is
    not a trend of zero, and conflating the two is how a run with no history gets
    called stalled. The caller must treat None as 'unknown', never as 'stalled'.
    """
    if len(history) < 2:
        return None
    span = history[-max(2, int(window)):]
    return (span[-1] - span[0]) / float(len(span) - 1)


def assess(evidence: RunEvidence, thresholds: Thresholds | None = None) -> Verdict:
    """Decide whether a human-review stop is warranted. Pauses nothing by itself."""
    th = thresholds or Thresholds()
    caveat = "" if th.calibrated else UNCALIBRATED_CAVEAT

    measured = {
        "round_idx": evidence.round_idx,
        "max_rounds": evidence.max_rounds,
        "round_fraction": round(evidence.round_fraction(), 4),
        "rounds_remaining": evidence.rounds_remaining(),
        "gamma_critical": evidence.gamma_critical,
        "gamma_critical_threshold": evidence.gamma_critical_threshold,
        "mechanical_faults": evidence.mechanical_faults,
        "total_findings": evidence.total_findings,
    }
    clock = evidence.clock_fraction()
    if clock is not None:
        measured["clock_fraction"] = round(clock, 4)
    rate = _progress_per_round(evidence.gamma_critical_history, th.window)
    measured["gamma_critical_progress_per_round"] = None if rate is None else round(rate, 6)

    # ── MECHANICALLY_BROKEN ───────────────────────────────────────────────────
    # Checked FIRST and without the earliest-round guard: a run that is mostly
    # malfunction is broken from its first rounds, and waiting for round 3 to say
    # so spends paid dispatch on a run already known to be producing noise.
    if evidence.total_findings >= th.mechanical_min_findings:
        share = evidence.mechanical_faults / float(evidence.total_findings)
        measured["mechanical_share"] = round(share, 4)
        if share >= th.mechanical_share:
            return Verdict(
                True, "MECHANICALLY_BROKEN",
                reasons=(
                    f"{evidence.mechanical_faults} of {evidence.total_findings} findings "
                    f"are mechanical faults, {100.0 * share:.4f}%, at or above the "
                    f"{100.0 * th.mechanical_share:.4f}% share at which a run counts as "
                    f"broken rather than slow",
                    "more rounds cannot help a run whose output is mostly its own "
                    "malfunction, so the remaining round budget would be spent for nothing",
                ),
                measured=measured, caveat=caveat,
            )

    # ── Too early to assess convergence at all ────────────────────────────────
    if evidence.round_idx < evidence.earliest_round:
        return Verdict(
            False, None,
            reasons=(
                f"round {evidence.round_idx} is before round {evidence.earliest_round}, "
                f"the earliest at which the convergence measure is assessable, so there "
                f"is no evidence either way and a stop would be arbitrary",
            ),
            measured=measured, caveat=caveat,
        )

    # ── STALLED_AND_OUT_OF_ROOM ───────────────────────────────────────────────
    failed: list[str] = []
    if evidence.round_fraction() < th.min_round_fraction:
        failed.append(
            f"only {100.0 * evidence.round_fraction():.4f}% of the round budget is spent, "
            f"below the {100.0 * th.min_round_fraction:.4f}% at which a stall can be called"
        )
    if evidence.gamma_critical >= evidence.gamma_critical_threshold:
        failed.append(
            f"the convergence measure {evidence.gamma_critical:.4f} already meets its threshold "
            f"{evidence.gamma_critical_threshold:.4f}, so the run is converging, not stalling"
        )
    if rate is None:
        failed.append(
            "fewer than 2 rounds of convergence history, so the rate of progress is "
            "UNKNOWN rather than zero and no stall can be established"
        )
    elif rate > th.stall_epsilon:
        failed.append(
            f"the convergence measure is improving at {rate:.6f} per round, above the "
            f"{th.stall_epsilon:.6f} below which progress counts as absent"
        )

    if not failed:
        gap = evidence.gamma_critical_threshold - evidence.gamma_critical
        remaining = evidence.rounds_remaining()
        # rate <= stall_epsilon here, so a non-positive rate never closes the gap.
        if rate is not None and rate > 0:
            needed = gap / rate
            closes_in_rounds = needed <= remaining
        else:
            needed, closes_in_rounds = float("inf"), False
        measured["rounds_needed_at_observed_rate"] = (
            None if needed == float("inf") else round(needed, 2)
        )
        clock_exhausted = clock is not None and clock >= th.min_round_fraction

        if not closes_in_rounds:
            reasons = [
                f"{100.0 * evidence.round_fraction():.4f}% of the round budget is spent "
                f"with the convergence measure at {evidence.gamma_critical:.4f} against a threshold "
                f"of {evidence.gamma_critical_threshold:.4f}",
                (f"progress is {rate:.6f} per round, at or below the {th.stall_epsilon:.6f} "
                 f"stall floor" if rate is not None else "progress is unknown"),
                (f"closing the remaining {gap:.4f} at the observed rate needs "
                 f"{needed:.2f} rounds against {remaining} remaining"
                 if needed != float("inf") else
                 f"the observed rate cannot close the remaining {gap:.4f} at all, so no "
                 f"number of remaining rounds suffices"),
            ]
            if clock_exhausted:
                reasons.append(
                    f"{100.0 * clock:.4f}% of the wall-clock cap is also spent, so the "
                    f"shortfall is in resources as well as in rounds"
                )
            return Verdict(True, "STALLED_AND_OUT_OF_ROOM",
                           reasons=tuple(reasons), measured=measured, caveat=caveat)
        failed.append(
            f"the remaining {remaining} rounds are enough to close the {gap:.4f} gap at "
            f"the observed rate ({needed:.2f} rounds needed), so the run may still converge"
        )

    return Verdict(
        False, None,
        reasons=tuple(["no clause is satisfied; a stop would not be evidence-based"] + failed),
        measured=measured, caveat=caveat,
    )
