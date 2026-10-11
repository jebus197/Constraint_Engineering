"""When should a run ask the founder to look? Only on substantial evidence.

HIS ORDER, 2026-10-11: *"12: Then build it and implement it."* And the condition,
in his own words, which is the whole specification: a human review *"should only be
triggered if there is substantial evidence that an experimental run is unlikely to
converge under the given conditions and with the available resources."*

HIS STANDING CONSTRAINT, 2026-09-28, which bounds it from the other side: *"What I
don't want is a condition where no run could ever complete, and where the HIL queue
could grow to unmanageable levels."* So this REQUESTS A LOOK. It halts nothing,
vetoes nothing and changes no verdict.

WHAT "UNLIKELY TO CONVERGE UNDER THE AVAILABLE RESOURCES" MEANS HERE
-------------------------------------------------------------------
The hardened gate requires, among other things, criterion (C): K consecutive
settled rounds with zero novel critical findings, K = `cfg.gamma_alt_consecutive_
zero_crit`. So once fewer than K rounds remain before `max_rounds`, (C) cannot be
satisfied even by a flawless run. That is ARITHMETIC, not a forecast -- which is
why it qualifies as substantial evidence rather than a hunch.

A NAIVE COMPOSITION WAS REFUTED BY THE ARCHIVE BEFORE THIS WAS BUILT. The obvious
design was to reuse item 9's round projection: trigger when n* exceeds the rounds
remaining. Measured over the 17 archived run reports carrying a per-round count
series and a round cap, n* ranges from 151.64 to 1.79969828506e20 rounds, so that
rule fires on 16 of 17 runs INCLUDING 4 OF THE 5 THAT CONVERGED -- a false-alarm
rate of 4/5 on exactly the runs it must not flag. The 5th escaped only because its
2-round series is too short to fit at all, which is not the rule working. The cause
is that convergence in this harness
is not "yield fell below theta"; it is the two-sided gate, which is about CRITICAL
findings reaching zero, not about total yield. n* answers a question the gate does
not ask. Producer: `scripts/the_review_trigger_false_alarm_rate_2026-10-11.py`.

MEASURED FALSE-ALARM RATE OF WHAT SHIPPED. Over the same 17 archived runs, 5
converged (stopped short of their cap) and 12 hit the cap. Signal A fires on 0 of
the 5 converged, Wilson 95% [0.0000, 0.4345], and on 12 of 12 that did not. The
interval's upper bound is wide because 5 is a small denominator: the honest claim
is 0 observed in 5, NOT a demonstrated low rate.

BOUNDED HONESTLY. Signal A establishes that the HARDENED GATE'S WINDOW is
unreachable. It does not establish that no convergence route exists, because the
runner also carries an EXHAUSTED bypass (`cfg.exhausted_round_threshold`) and a
sparsity branch. That is precisely why this is a review REQUEST and not a verdict.

A --help COSTS NOTHING: pure arithmetic over values already computed, no dispatch.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence

#: Signal B is statistical rather than deductive, so it only speaks once this
#: fraction of the round budget is spent. Before that, a flat critical series is
#: an early-round artefact rather than evidence about the run.
B_ROUND_FRACTION = 0.6

#: Signal C: consecutive rounds whose novelty series shows no decay at all. A run
#: that is not depleting cannot deplete to zero. 3 matches the gate's own window,
#: deliberately, so this adds no new tunable.
C_CONSECUTIVE_NO_DECAY = 3


@dataclass
class ReviewVerdict:
    """A request for the founder to look, with the evidence that earned it."""

    review_requested: bool
    signals: List[str] = field(default_factory=list)
    detail: Dict[str, Any] = field(default_factory=dict)
    #: ALWAYS False. Named explicitly so no caller can read this as a halt.
    halts_the_run: bool = False

    def as_dict(self) -> dict:
        return {
            "human_review_requested": self.review_requested,
            "human_review_signals": list(self.signals),
            "human_review_detail": dict(self.detail),
            "human_review_halts_the_run": False,
            "human_review_is_advisory": True,
        }

    def line(self) -> str:
        if not self.review_requested:
            return "  human review: not requested"
        return ("  human review REQUESTED — " + "; ".join(self.signals)
                + " (advisory: halts nothing)")


def _no_decay_run_length(novelty_counts: Sequence[float]) -> int:
    """Trailing rounds over which the series shows no decline at all.

    Counts the longest suffix on which every step is flat or rising. A declining
    series returns 0, so this cannot fire on a run that is depleting.
    """
    counts = [c for c in novelty_counts]
    if len(counts) < 2:
        return 0
    run = 1
    for i in range(len(counts) - 1, 0, -1):
        if counts[i] >= counts[i - 1]:
            run += 1
        else:
            break
    return run if run >= 2 else 0


def assess(
    round_idx: int,
    max_rounds: int,
    consecutive_zero_crit_required: int,
    critical_novelty_series: Sequence[float] | None = None,
    gamma_critical: float | None = None,
    gamma_threshold: float | None = None,
    gamma_is_estimable: bool = True,
) -> ReviewVerdict:
    """Decide whether the evidence is substantial enough to ask him to look.

    Every argument is a value the runner already has. Nothing here measures
    anything new, which is why it cannot slow a run down.
    """
    signals: List[str] = []
    detail: Dict[str, Any] = {
        "round_idx": round_idx,
        "max_rounds": max_rounds,
        "rounds_remaining": max_rounds - round_idx,
        "consecutive_zero_crit_required": consecutive_zero_crit_required,
    }

    # ── SIGNAL A, DEDUCTIVE ──────────────────────────────────────────────────
    remaining = max_rounds - round_idx
    if consecutive_zero_crit_required > 0 and remaining < consecutive_zero_crit_required:
        signals.append(
            f"A: {remaining} round(s) remain against the "
            f"{consecutive_zero_crit_required} consecutive zero-novel-critical "
            f"rounds the hardened gate requires, so that criterion cannot be met "
            f"even by a flawless run")
        detail["signal_a"] = True
    else:
        detail["signal_a"] = False

    # ── SIGNAL B, STATISTICAL AND GATED ON ROUNDS SPENT ──────────────────────
    spent = (round_idx / max_rounds) if max_rounds > 0 else 0.0
    detail["round_fraction_spent"] = round(spent, 4)
    if (gamma_critical is not None and gamma_threshold is not None
            and gamma_is_estimable and spent >= B_ROUND_FRACTION
            and gamma_critical < gamma_threshold):
        signals.append(
            f"B: {spent:.0%} of the round budget is spent and gamma_critical="
            f"{gamma_critical:.4f} is still below the gate's threshold of "
            f"{gamma_threshold:g}, so the critical curve has not flattened")
        detail["signal_b"] = True
    else:
        detail["signal_b"] = False

    # ── SIGNAL C, NO DEPLETION AT ALL ────────────────────────────────────────
    if critical_novelty_series:
        run = _no_decay_run_length(critical_novelty_series)
        detail["no_decay_run_length"] = run
        if run >= C_CONSECUTIVE_NO_DECAY and sum(critical_novelty_series) > 0:
            signals.append(
                f"C: the critical novelty series has not declined for {run} "
                f"consecutive rounds, so it is not depleting toward the zero the "
                f"gate requires")
            detail["signal_c"] = True
        else:
            detail["signal_c"] = False
    else:
        detail["no_decay_run_length"] = 0
        detail["signal_c"] = False

    # SUBSTANTIAL = the deductive signal alone, OR two independent weak ones.
    # One statistical signal on its own is a hunch, which is what he ruled out.
    weak = int(detail["signal_b"]) + int(detail["signal_c"])
    requested = bool(detail["signal_a"]) or weak >= 2
    detail["substantial_because"] = (
        "deductive signal A" if detail["signal_a"]
        else (f"{weak} independent statistical signals" if weak >= 2
              else "no signal reached the bar"))
    return ReviewVerdict(review_requested=requested, signals=signals, detail=detail)


def main(argv: Sequence[str]) -> int:
    if len(argv) > 1 and argv[1] in ("-h", "--help"):
        print(f"usage: {argv[0].split('/')[-1]} [-h|--help] "
              f"[round_idx max_rounds K]")
        print()
        print(__doc__)
        return 0
    a = argv[1:]
    r, m, k = (int(a[0]), int(a[1]), int(a[2])) if len(a) >= 3 else (19, 21, 3)
    v = assess(r, m, k, critical_novelty_series=[4, 4, 4, 4], gamma_critical=0.11,
               gamma_threshold=0.30)
    print(f"round {r} of {m}, K={k}")
    print(v.line())
    for s in v.signals:
        print(f"    {s}")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv))
