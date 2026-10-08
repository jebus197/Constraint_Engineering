# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1618fecb953c72e9de4edf42029752d017a6e372c55eb11b16aba18e91ad3f7a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Measured-capability estimator. The tool's verdict is the ONLY input.

WHAT IS MISSING TODAY. Nothing in this repository estimates per-seat capability
this way. `DEFAULT_FALSIFIER_STRENGTH` in `bench/routing.py` is a hand-ordered
tuple whose comment cites Exp-42 confirm rates, and those rates were computed
once, by hand, in a write-up -- there is no running ledger, so there is nothing
for a seat to climb or fall on. Requirement 5 (bidirectional) and requirement 6
(a success is not a capability gain) are both unimplementable without one.

════════════ WHAT THE ESTIMATOR MUST RECORD PER ATTEMPT ════════════

Exactly these, and the reason each is load-bearing:

  seat            -- which route was asked. RECORDING ONLY, per requirement 3:
                     *"A models name should have little to do with it, beyond
                     recording this."* The name is a key, never a term in the key.
  finding_id      -- so a retry on the same finding is not counted as a second
                     independent attempt. Without it a ladder that tries one
                     finding 6 times reads as 6 attempts.
  round_idx       -- so the recency window below has an ordering.
  verdict         -- THE TOOL'S verdict from `reverify_falsifier`, one of
                     CONFIRMED / REFUTED / ERROR / UNTOOLABLE. Never the model's
                     prose. This is the whole of requirement 6: *"The only measure
                     of improved capability is actual observed capability."* A
                     model saying it succeeded is not an input to this function.
  admissible      -- did the falsifier IMPORT THE REAL TARGET, or did it restate
                     the document's numbers from memory? `routing.py`'s own
                     comment records the measured inversion: on Exp 55 one seat
                     went 2 of 2 CONFIRMED with both falsifiers DETACHED, and
                     re-deriving the ladder from that run promoted it to FIRST --
                     *"ranking the models by their willingness to ignore the
                     evidence"*. So an INADMISSIBLE CONFIRMED is recorded as a
                     FAILURE, not a success. This single field is what stops the
                     estimator inverting the ladder.
  task_class      -- prose target or code target, and the falsification task.
                     Capability is not scalar across task kinds; pooling a code
                     confirm rate with a prose one measures neither.

AND NOTHING ELSE. No self-report, no confidence, no reasoning trace, no token
count. Each of those is a channel through which a model's assertion about itself
would re-enter a number the directives require to be tool-decided.

════════════ THE FIRST ATTEMPT A NEW MODEL EVER MAKES ════════════

`attempts == 0` -> `wilson_lower(0, 0) = 0.0` -> the seat sorts LAST, and no
placement decision is needed for a new model. That is requirement 3 satisfied
structurally: the seat's position comes from its (empty) measurement record, not
from anyone's view of its name.

On that FIRST attempt the seat is dispatched LAST, so it is reached only when
every measured seat has already failed -- which is also requirement 4
(*"no point handing a cheaper model work it is unlikely to be able to do"*)
holding automatically, since an unmeasured seat is by definition unlikely-until-
shown. The attempt is recorded; the next ordering reflects it. No cold-start
special case, no bootstrap period, no seeded prior.

════════════ THE BIDIRECTIONALITY DEFECT, MEASURED ════════════

A POOLED LIFETIME RATE IS NOT BIDIRECTIONAL ON A USEFUL TIMESCALE, and this is
the estimator defect the brief does not raise. Measured here (and reproduced by
the falsifier): a seat at 60 of 70 that then fails EVERY subsequent attempt needs
34 consecutive failures before its Wilson lower bound drops below 0.5, and 116
before it drops below a 1-of-1 newcomer's. Requirement 5 says *"if a stronger
model proves less able ... it should be able to climb down"*; at 34 failures per
step down, a 10-round run cannot express a descent at all.

THE REPAIR IS AN EXPONENTIALLY-WEIGHTED COUNT, and the route to it was itself a
falsified attempt that is recorded here rather than edited out.

FIRST ATTEMPT, FALSIFIED BY ITS OWN FALSIFIER: score = min(wilson_lo(lifetime),
wilson_lo(last W attempts)). Measured, it demoted a seat at true p=0.85 below 75%
of its own long-run bound in 2252 of 4000 simulated runs (56.30%), against 1 of
4000 (0.03%) for the pooled bound. The diagnosis is structural, not a tuning
problem: a Wilson bound on 12 samples is LOWER than a Wilson bound on 70 samples
at the SAME underlying rate (wilson_lo(11,12) = 0.6461 < wilson_lo(60,70) =
0.7566), so `min` of two bounds at different sample sizes almost always returns
the smaller sample's, and the lifetime record is discarded in all but name.

WHAT IS USED INSTEAD. One estimator, one dial: exponentially-weighted successes
and attempts with a half-life in attempts.

    w_i    = 0.5 ** (age_i / half_life)          age in attempts, newest age 0
    k_eff  = sum(w_i for successful attempts)
    n_eff  = sum(w_i over all attempts)
    score  = wilson_lower(k_eff, n_eff)

n_eff saturates at half_life / ln 2, so the bound's width is governed by one
interpretable quantity and recent evidence displaces old evidence smoothly
instead of at a window edge.

AND THE TENSION IS REAL, NOT AN IMPLEMENTATION DEFECT. Requirements 5 and 6 pull
against each other and no estimator satisfies both fully. For an effective sample
size N, the Wilson half-width scales as z*sqrt(p(1-p)/N), while the number of
consecutive failures needed to move the estimate a fixed distance scales as N.
So jitter^2 * descent_latency is approximately invariant: BUYING A FASTER DESCENT
BUYS JITTER, at a fixed exchange rate set by N. Requirement 5 asks for a short
memory; requirement 6 asks for a long one.

`half_life` is therefore a FOUNDER-LEVEL DIAL, not a value this module is
entitled to choose on his behalf, and
`bench/tests/test_capability_and_ladder_2026-10-07.py` prints the measured
descent latency, ascent latency and false-demotion rate at each of several
half-lives so the choice is made with the curve in view. The default below is the
shortest half-life at which the brief's own stated bar still holds -- a 1-of-1
newcomer must not outrank a 60-of-70 veteran -- which is the one constraint the
founder has already committed to in writing.

BOTH EARLIER ESTIMATORS ARE RETAINED, not deleted: `pooled_score` is the brief's
Part C estimator and `windowed_score` is the falsified first attempt. They are
what the tradeoff curve is measured against, so removing them would remove the
evidence for the choice.
"""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Sequence

Z_95 = 1.959963984540054

#: Verdicts the re-verification tool can return. Only CONFIRMED is a success, and
#: only when the falsifier actually read its target.
CONFIRMED = "CONFIRMED"

#: Attempts over which an observation's weight halves. THE one dial; see the
#: tradeoff derivation in the docstring. 24 is the shortest half-life at which a
#: 1-of-1 newcomer still does not outrank a 60-of-70 veteran, which is the bar
#: the brief's Part C commits to.
DEFAULT_HALF_LIFE = 24.0

#: Retained for `windowed_score`, the falsified first attempt, kept as the
#: comparison the tradeoff curve is measured against.
DEFAULT_WINDOW = 12


def wilson_lower(k: int, n: int, z: float = Z_95) -> float:
    """Wilson score lower bound. n == 0 -> 0.0, so an unmeasured seat sorts last."""
    if n <= 0:
        return 0.0
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, c - h)


def wilson_lower_real(k: float, n: float, z: float = Z_95) -> float:
    """Wilson lower bound for REAL-VALUED (exponentially weighted) counts.

    Identical arithmetic to `wilson_lower`; separate so the integer-count path
    the brief's Part C figures are quoted from is untouched and still exactly
    reproducible. n is an effective sample size, so it is a float.
    """
    if n <= 0:
        return 0.0
    p = min(1.0, max(0.0, k / n))
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, c - h)


@dataclass(frozen=True)
class Attempt:
    """One falsification attempt. Every field is required; see the module docstring."""
    seat: str
    finding_id: str
    round_idx: int
    verdict: str          # the TOOL's verdict, never the model's prose
    admissible: bool      # did the falsifier import the real target?
    task_class: str = "code"

    @property
    def success(self) -> bool:
        """An INADMISSIBLE CONFIRMED is a failure, not a success.

        This is the discrimination control applied to the estimator itself. Without
        it, the measured Exp-55 inversion -- a seat going 2 of 2 CONFIRMED on
        falsifiers that opened nothing -- would promote that seat to the top of the
        ladder.
        """
        return self.verdict == CONFIRMED and self.admissible


@dataclass
class CapabilityLedger:
    """Per-attempt record and the lower bound derived from it.

    Append-only. There is no method that edits or deletes an attempt, because the
    ledger is the measurement and a measurement that can be rewritten is not one.
    """
    half_life: float = DEFAULT_HALF_LIFE
    window: int = DEFAULT_WINDOW
    attempts: list = field(default_factory=list)
    _seen: set = field(default_factory=set)

    def record(self, attempt: Attempt) -> bool:
        """Append one attempt. Returns False if (seat, finding) is already recorded.

        A ladder may hand the same finding back to the same seat (routing.py's
        self-rung does exactly that). Counting that as a second independent
        attempt would inflate the denominator with correlated trials.
        """
        key = (attempt.seat, attempt.finding_id, attempt.task_class)
        if key in self._seen:
            return False
        self._seen.add(key)
        self.attempts.append(attempt)
        return True

    def _for(self, seat: str, task_class: str | None) -> list:
        return [a for a in self.attempts
                if a.seat == seat and (task_class is None or a.task_class == task_class)]

    def counts(self, seat: str, task_class: str | None = None) -> tuple:
        rs = self._for(seat, task_class)
        return sum(1 for a in rs if a.success), len(rs)

    def recent_counts(self, seat: str, task_class: str | None = None) -> tuple:
        rs = sorted(self._for(seat, task_class), key=lambda a: a.round_idx)[-self.window:]
        return sum(1 for a in rs if a.success), len(rs)

    def effective_counts(self, seat: str, task_class: str | None = None) -> tuple:
        """Exponentially-weighted (k_eff, n_eff). Newest attempt has weight 1."""
        rs = sorted(self._for(seat, task_class), key=lambda a: a.round_idx)
        if not rs:
            return (0.0, 0.0)
        hl = max(1e-9, float(self.half_life))
        k = n = 0.0
        last = len(rs) - 1
        for i, a in enumerate(rs):
            w = 0.5 ** ((last - i) / hl)
            n += w
            if a.success:
                k += w
        return (k, n)

    def score(self, seat: str, task_class: str | None = None) -> float:
        """Wilson lower bound on the exponentially-weighted counts.

        0.0 for a seat with no attempts, which sorts it last with no special case.
        """
        k, n = self.effective_counts(seat, task_class)
        if n <= 0:
            return 0.0
        return wilson_lower_real(k, n)

    def windowed_score(self, seat: str, task_class: str | None = None) -> float:
        """THE FALSIFIED FIRST ATTEMPT: min(lifetime bound, last-`window` bound).

        Kept, not deleted. It is one of the two estimators the tradeoff curve in
        the falsifier is measured against, and the 56.30% false-demotion figure
        that rejected it is only reproducible while it still exists.
        """
        k, n = self.counts(seat, task_class)
        rk, rn = self.recent_counts(seat, task_class)
        if n == 0:
            return 0.0
        return min(wilson_lower(k, n), wilson_lower(rk, rn))

    def pooled_score(self, seat: str, task_class: str | None = None) -> float:
        """The lifetime-only bound, KEPT for comparison and for the falsifier.

        Retained rather than removed: it is the estimator the brief's Part C
        describes, and the falsifier measures both so the descent-latency claim
        above is a committed measurement rather than an assertion.
        """
        k, n = self.counts(seat, task_class)
        return wilson_lower(k, n)

    def table(self, seats: Sequence[str], task_class: str | None = None) -> dict:
        return {s: {"successes": self.counts(s, task_class)[0],
                    "attempts": self.counts(s, task_class)[1],
                    "k_eff": round(self.effective_counts(s, task_class)[0], 4),
                    "n_eff": round(self.effective_counts(s, task_class)[1], 4),
                    "score": round(self.score(s, task_class), 6),
                    "pooled": round(self.pooled_score(s, task_class), 6),
                    "windowed": round(self.windowed_score(s, task_class), 6)}
                for s in seats}
