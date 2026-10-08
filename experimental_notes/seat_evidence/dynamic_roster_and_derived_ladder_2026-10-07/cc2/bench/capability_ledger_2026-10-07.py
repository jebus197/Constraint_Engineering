# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 098778cc6da0a6de8e832e67f2c34b9d8e1e939d18dc8168a9d5e74038344e87
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Measured-capability allocation: the estimator (req 3, 6) and the order (req 4, 7).

WHAT IS MISSING TODAY. `rank_falsifier_writers` (bench/routing.py:118) orders seats
by their index in `DEFAULT_FALSIFIER_STRENGTH`, a hand-written 6-tuple. Nothing in
the repository estimates per-seat resolve rate from attempts, so founder
requirement 3 -- *"the only thing that should impact on capability is measured
capability"* -- has no estimator behind it. This module is that estimator plus the
ordering it feeds.

REQUIREMENT 6 IS AN ESTIMATOR PROPERTY, NOT AN ORDERING ONE. *"what we need to
guard against is simply counting when a model is successful as an 'improvement in
capability'."* Two distinct guards, both here:

  (a) CAPABILITY IS A LOWER CONFIDENCE BOUND, never a point estimate. One success
      from one attempt gives point 1.0 but Wilson lower bound 0.2065, so a single
      success cannot promote a seat. A seat needs 12 consecutive successes before
      its lower bound passes a seat sitting at 60 of 70.
  (b) AN INADMISSIBLE SUCCESS IS NOT A SUCCESS. A CONFIRMED whose falsifier never
      read its target is not evidence of capability -- it is evidence of
      willingness to ignore the evidence, which is the Exp 55 inversion recorded at
      bench/routing.py:44 (Gemini 2 of 2 CONFIRMED with both falsifiers DETACHED;
      re-deriving the ladder from that run promotes it to FIRST). So
      `record_attempt` REFUSES to count a success whose attempt is not admissible,
      and counts it as an attempt with no success. Without this guard the ledger
      ranks seats by exactly the behaviour the falsifier-integrity directive exists
      to detect.

WHAT THE ESTIMATOR MUST RECORD PER ATTEMPT -- the `Attempt` fields below, and the
reason each is load-bearing is in its comment. The verdict field must come from the
runner's independent re-execution (`falsifier_verify.reverify_falsifier`), never
from the model's prose: tools decide, not votes.

THE FIRST ATTEMPT A NEW MODEL EVER MAKES. 0 attempts -> Wilson lower bound exactly
0.0 -> the seat sorts LAST, with no placement decision by anyone. It then climbs on
evidence. This is already how Fable was placed (bench/routing.py:70).

ON `DEFAULT_FALSIFIER_STRENGTH`: IT SITS BESIDE THE DERIVED KEY, IT IS NOT REPLACED.
The derived key alone is insufficient on the very first run, when EVERY seat has 0
attempts: all lower bounds are 0.0, the key is a total tie, and the resulting order
is whatever `labels` happened to be in -- unmeasured and unstable. The hand-written
tuple is the only ordering information that exists at that moment, so it is kept as
the TIE-BREAK. It is consulted only where measurement is silent, and measurement
overrides it the moment any seat has an attempt. This satisfies the additive
standard (nothing is removed) and is a composition justified by a measured property
the single fix lacks -- determinism on run 1 -- demonstrated in the falsifier.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import cmp_to_key
from typing import Optional, Sequence

#: Normal quantile for a 95% one-sided Wilson lower bound, matching the committed
#: `allocation_by_measured_capability_2026-10-07.py`.
Z = 1.959963984540054


@dataclass
class Attempt:
    """One dispatch of one seat against one finding. Every field is load-bearing."""
    seat: str
    finding_id: str          # so duplicate credit for the same defect is detectable
    round_idx: int           # so capability can be windowed; a ladder is bidirectional
    task_class: str          # code / prose / maths. A seat strong on code may be weak
                             # on prose; one pooled rate hides that (Exp 55).
    rung_depth: int          # how many seats already failed this finding. THE
                             # DIFFICULTY SIGNAL, and the basis of "hardest" for the
                             # reserve seat -- no human classifies anything.
    verdict: str             # from the runner's re-execution, NOT the model's prose.
    admissible: bool         # did the falsifier import and read the REAL target?
                             # An inadmissible CONFIRMED is not a success.
    wall_clock_s: float      # the researcher's cost (req 7). Money alone is not it.
    money: float             # the other half of cost.

    def is_success(self) -> bool:
        return self.verdict == "CONFIRMED" and self.admissible


def wilson_lower(successes: int, attempts: int, z: float = Z) -> float:
    """One-sided Wilson lower bound. 0 attempts -> 0.0 (sorts last, climbs later)."""
    if attempts <= 0:
        return 0.0
    phat = successes / attempts
    d = 1.0 + z * z / attempts
    centre = phat + z * z / (2 * attempts)
    half = z * math.sqrt(phat * (1 - phat) / attempts + z * z / (4 * attempts ** 2))
    return max(0.0, (centre - half) / d)


@dataclass
class SeatStats:
    seat: str
    attempts: int = 0
    successes: int = 0
    inadmissible_successes: int = 0   # recorded, so the guard is auditable
    money_total: float = 0.0
    seconds_total: float = 0.0

    def p_lower(self, z: float = Z) -> float:
        return wilson_lower(self.successes, self.attempts, z)

    def p_point(self) -> float:
        return self.successes / self.attempts if self.attempts else 0.0

    def mean_money(self, fallback: float) -> float:
        return self.money_total / self.attempts if self.attempts else fallback

    def mean_seconds(self, fallback: float) -> float:
        return self.seconds_total / self.attempts if self.attempts else fallback


class CapabilityLedger:
    """Per-seat, per-task-class measured capability. Bidirectional by construction.

    REQUIREMENT 5 NEEDS NO EXTRA MACHINERY: *"A ladder is bidirectional."* The
    ordering reads `p_lower()`, which is a function of the running counts. A seat
    that starts failing has its successes/attempts ratio fall, so its lower bound
    falls and it descends; a seat that starts succeeding ascends. There is no stored
    rank to edit, which is what makes this roster-size agnostic as well (req 1).
    """

    def __init__(self) -> None:
        self.attempts: list = []
        self._by: dict = {}

    def record_attempt(self, a: Attempt) -> SeatStats:
        key = (a.seat, a.task_class)
        st = self._by.setdefault(key, SeatStats(a.seat))
        st.attempts += 1
        st.money_total += a.money
        st.seconds_total += a.wall_clock_s
        if a.verdict == "CONFIRMED" and not a.admissible:
            # REQUIREMENT 6's SHARP EDGE. Counted as an attempt, NOT as a success.
            st.inadmissible_successes += 1
        elif a.is_success():
            st.successes += 1
        self.attempts.append(a)
        return st

    def stats(self, seat: str, task_class: str) -> SeatStats:
        return self._by.get((seat, task_class), SeatStats(seat))

    def p_lower(self, seat: str, task_class: str) -> float:
        return self.stats(seat, task_class).p_lower()

    def has_any_measurement(self) -> bool:
        return any(s.attempts > 0 for s in self._by.values())


def effective_cost(money: float, seconds: float, latency_weight: float) -> float:
    """Cost in a single currency: money + latency_weight * seconds.

    `latency_weight` is the researcher's exchange rate between spend and waiting,
    and it is the ONLY new parameter the repair introduces (req 7). At 0 this is the
    money-only ordering the design proposes; the committed artefact measures the
    crossing to capability-first at a weight of 2.
    """
    return money + latency_weight * seconds


def order_seats(labels: Sequence[str],
                ledger: CapabilityLedger,
                task_class: str,
                *,
                latency_weight: float = 0.0,
                money_by_seat: Optional[dict] = None,
                seconds_by_seat: Optional[dict] = None,
                strength_order: Sequence[str] = (),
                exclude: Sequence[str] = ()) -> list:
    """Order seats to minimise expected cost to the first CONFIRMED verdict.

    THE EXCHANGE RULE, DERIVED. For an order s_1..s_n the expected cost to the first
    CONFIRMED is  E = sum_j c_j * prod_{i<j} (1 - p_i).  Swapping adjacent seats j,
    j+1 changes E by  W * [c_j + (1-p_j) c_{j+1} - c_{j+1} - (1-p_{j+1}) c_j]
    = W * [p_{j+1} c_j - p_j c_{j+1}], where W = prod_{i<j}(1-p_i) >= 0. So the swap
    does not help iff  p_j * c_{j+1} >= p_{j+1} * c_j.  Sorting on that comparator
    (a ratio rule: descending p/c) is therefore optimal, and it is a comparison over
    2 measured numbers rather than a stored list -- roster-size agnostic (req 1) and
    bidirectional (req 5). This is Smith's ratio rule; the falsifier brute-forces it
    against all permutations and z3-checks the exchange step.

    TIE-BREAK: `strength_order` index, then input order. Consulted ONLY when the
    derived key ties, which on run 1 is every pair. See the module docstring.
    """
    money_by_seat = money_by_seat or {}
    seconds_by_seat = seconds_by_seat or {}
    excl = set(exclude)
    cand = [m for m in labels if m not in excl]

    def rank_in_strength(m: str) -> int:
        try:
            return list(strength_order).index(m)
        except ValueError:
            return len(strength_order)

    def key_parts(m: str):
        st = ledger.stats(m, task_class)
        p = st.p_lower()
        c = effective_cost(st.mean_money(money_by_seat.get(m, 1.0)),
                           st.mean_seconds(seconds_by_seat.get(m, 1.0)),
                           latency_weight)
        return p, max(c, 1e-12)

    def cmp(m1: str, m2: str) -> int:
        p1, c1 = key_parts(m1)
        p2, c2 = key_parts(m2)
        # descending p/c, cross-multiplied so a zero cost cannot divide
        lhs, rhs = p1 * c2, p2 * c1
        if lhs > rhs:
            return -1
        if lhs < rhs:
            return 1
        r1, r2 = rank_in_strength(m1), rank_in_strength(m2)
        if r1 != r2:
            return -1 if r1 < r2 else 1
        i1, i2 = cand.index(m1), cand.index(m2)
        return -1 if i1 < i2 else (1 if i1 > i2 else 0)

    return sorted(cand, key=cmp_to_key(cmp))


def expected_cost(order: Sequence[str], p: dict, c: dict) -> float:
    """E = sum_j c_j * prod_{i<j} (1 - p_i)."""
    total, reach = 0.0, 1.0
    for m in order:
        total += reach * c[m]
        reach *= (1.0 - p[m])
    return total


def expected_dispatches(order: Sequence[str], p: dict) -> float:
    return expected_cost(order, p, {m: 1.0 for m in order})


def probability_reached(order: Sequence[str], seat: str, p: dict) -> float:
    """P(the ladder reaches `seat`) = prod of (1 - p_i) over seats before it.

    THIS IS HOW "HARDEST" IS DECIDED WITH NO HUMAN CLASSIFYING ANYTHING (req 5 of
    the brief's fix list, the reserve seat). A finding reaches a late rung exactly
    when every seat with a better measured p/c ratio has already failed on it. That
    IS the operational definition of hard, it is measured per finding at dispatch
    time as `Attempt.rung_depth`, and it needs no classifier and no new rule: an
    expensive seat has a large c, so the derived key places it late by itself, and
    under `max_rungs=0` (exhaust) it is still reached when the finding warrants it.
    The reserve behaviour is an EMERGENT PROPERTY of the ordering, not a mechanism
    added beside it.
    """
    reach = 1.0
    for m in order:
        if m == seat:
            return reach
        reach *= (1.0 - p[m])
    return 0.0
