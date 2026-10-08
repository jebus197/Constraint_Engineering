# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 43cea0c3def5240f945226984ae7ca44dedea2568eb8c6344b7587e603dc7157
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Capability estimation and derived-key ordering for falsifier routing.

This is the estimator the derived-key design (Part B/Part C, 2026-10-07) requires
and that nothing in the repository previously implemented. It answers two of the
founder's requirements directly.

REQUIREMENT 6 -- "The only measure of improved capability is actual observed
capability." A success counts toward capability ONLY when (a) the runner's
independent re-verification returned CONFIRMED (tools decide, not the model's
own verdict) AND (b) the falsifier passed the provenance check -- it actually
read its target. The Exp 55 measurement is the reason (b) exists: Gemini went
2-of-2 CONFIRMED on falsifiers that opened nothing, and counting those would
rank models by their willingness to ignore the evidence
(`bench/routing.py`, comment block above DEFAULT_FALSIFIER_STRENGTH;
`scripts/competence_provenance.py`). An attempt with provenance_ok False or
None (unchecked) is recorded as an ATTEMPT but never as a success: it lowers
the Wilson bound exactly as a failure does, because a detached falsifier
demonstrated nothing.

REQUIREMENT 7 -- the researcher pays in time as well as money. The per-dispatch
cost in the ordering key is money + latency_weight * expected latency. A single
scalar weight is sufficient, and that is derived rather than judged: the
exchange rule p_i*c_j >= p_j*c_i is proved (z3, unsat both directions, in
`bench/allocation_by_measured_capability_2026-10-07.py`) to hold for any cost
that is a fixed non-negative linear combination of money and latency, so one
weight re-orders the whole ladder with no new rule. A per-task cost VECTOR
would add a dimension the ordering cannot consume -- the key uses one scalar
per seat -- so it fails the simplest-sufficient standard. latency_weight is a
per-run config value, researcher-set, defaulting to 1.0 (the researcher is
waiting; money-only is the degenerate case latency_weight=0).

THE LATENCY TERM ALSO REPAIRS A DEGENERACY money alone cannot: among free seats
money cost is 0, the cross-multiplied key compares 0 against 0, and
`bench/why_one_ordering_cannot_serve_both_objectives_2026-10-07.py` measures
the spend objective as vacuous there (distinct_expected_spends: 1, all_zero:
True). Every dispatch takes time > 0, so the latency-priced cost is strictly
positive and the key is informative over free seats too.

COLD START AND THE LADDER TUPLE (panel question 3): the derived key ORDERS;
`routing.DEFAULT_FALSIFIER_STRENGTH` remains as the TIE-BREAK among seats whose
Wilson lower bounds are equal -- which is every seat on the very first run,
when all bounds are 0. The tuple is not a name-based preference: it is itself a
committed measurement (the Exp-42 provenance-checked confirm rates recorded in
`bench/routing.py`). It is therefore not removed -- the additive standard
forbids removal without a committed measurement showing the replacement
dominates, and on a run with no attempt records the derived key demonstrably
does NOT dominate (it is uniformly 0). The moment measured bounds differ, they
decide, and the tuple decides nothing.

RESERVE SEATS (panel question 5, Kimi K3): "hardest" needs no human classifier.
A finding is hard exactly when every earlier rung has already failed on it, and
the key places an expensive seat deep in the ladder by arithmetic: its cost
enters the denominator, so Kimi is reached only with probability
prod(1 - p_i) over the seats ahead of it. Hardness is revealed by failure, not
predicted by classification. No reserve flag is added -- a flag nothing
computes would be the 12th addition nothing reaches.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Dict, Iterable, List, Optional, Sequence

Z_95 = 1.959963984540054  # two-sided 95% normal quantile


@dataclass(frozen=True)
class AttemptRecord:
    """One falsification attempt by one seat. The caller supplies every field
    from the run's own artefacts; nothing here is self-reported by the model.

    `verdict` is the runner's re-verification verdict (falsifier_verify), never
    the model's prose. `provenance_ok` is the result of the competence-provenance
    check (did the falsifier read its target); None means the check was not run,
    and None is treated as NOT ok -- an unchecked success must not raise a bound
    that decides routing (the Exp 55 inversion).
    """
    seat: str
    finding_id: str
    verdict: str                      # CONFIRMED / REFUTED / ERROR / UNTOOLABLE
    provenance_ok: Optional[bool]
    latency_s: float
    cost_money: float
    timestamp: str                    # ISO-8601, caller-stamped

    @property
    def success(self) -> bool:
        return self.verdict == "CONFIRMED" and self.provenance_ok is True


@dataclass
class SeatCapability:
    """Aggregated observed capability of one seat, with its uncertainty."""
    seat: str
    attempts: int = 0
    successes: int = 0
    total_latency_s: float = 0.0
    total_money: float = 0.0

    @property
    def wilson_lower(self) -> float:
        """95% Wilson score lower bound on the resolve rate. 0 attempts -> 0.0:
        a seat with no measurements sorts last and climbs on evidence."""
        n, k = self.attempts, self.successes
        if n == 0:
            return 0.0
        p = k / n
        z2 = Z_95 * Z_95
        centre = p + z2 / (2 * n)
        radius = Z_95 * sqrt(p * (1 - p) / n + z2 / (4 * n * n))
        return max(0.0, (centre - radius) / (1 + z2 / n))

    def mean_latency(self, default: float = 60.0) -> float:
        return self.total_latency_s / self.attempts if self.attempts else default

    def mean_money(self, default: float = 0.0) -> float:
        return self.total_money / self.attempts if self.attempts else default


class CapabilityEstimator:
    """Builds per-seat capability from attempt records and orders the ladder."""

    def __init__(self) -> None:
        self._by_seat: Dict[str, SeatCapability] = {}

    def record_attempt(self, rec: AttemptRecord) -> None:
        cap = self._by_seat.setdefault(rec.seat, SeatCapability(rec.seat))
        cap.attempts += 1
        cap.successes += 1 if rec.success else 0
        cap.total_latency_s += max(0.0, rec.latency_s)
        cap.total_money += max(0.0, rec.cost_money)

    def capability(self, seat: str) -> SeatCapability:
        return self._by_seat.get(seat, SeatCapability(seat))

    def dispatch_cost(self, seat: str, latency_weight: float = 1.0) -> float:
        """Per-dispatch cost: money + latency_weight * mean latency (seconds).
        Strictly positive whenever latency_weight > 0."""
        cap = self.capability(seat)
        return cap.mean_money() + latency_weight * cap.mean_latency()

    def order_seats(
        self,
        seats: Sequence[str],
        latency_weight: float = 1.0,
        strength_order: Sequence[str] = (),
        exclude: Iterable[str] = (),
    ) -> List[str]:
        """Order seats to minimise expected (money + weighted-wait) to the first
        CONFIRMED verdict.

        Exchange rule (derived; z3-proved in the 2026-10-07 artefacts): seat i
        belongs before seat j iff p_i * c_j >= p_j * c_i, which a sort on p/c
        descending realises when c > 0 (guaranteed by latency_weight > 0; at
        latency_weight = 0 free seats tie and the tie-breaks below decide).

        p is the Wilson LOWER bound (Part C): one lucky success does not
        promote. Ties (including the all-zero cold start) break by position in
        `strength_order` -- the measured Exp-42 prior -- then by label for
        determinism. Unlisted seats tie-break after listed ones, preserving the
        `rank_falsifier_writers` behaviour that a new model is tried, just last.
        """
        excl = set(exclude)
        pos = {name: i for i, name in enumerate(strength_order)}

        def sort_key(seat: str):
            p = self.capability(seat).wilson_lower
            c = self.dispatch_cost(seat, latency_weight)
            ratio = (p / c) if c > 0 else (float("inf") if p > 0 else 0.0)
            return (-ratio, pos.get(seat, len(pos)), seat)

        return sorted((s for s in seats if s not in excl), key=sort_key)

    def expected_dispatches(self, ordered: Sequence[str]) -> float:
        """E[number of dispatches to first CONFIRMED], using Wilson lower
        bounds. Diagnostic for reporting, not part of the ordering."""
        e, reach = 0.0, 1.0
        for s in ordered:
            e += reach
            reach *= (1 - self.capability(s).wilson_lower)
        return e


def first_attempt_of_a_new_model(estimator: CapabilityEstimator,
                                 seat: str) -> dict:
    """What happens on the first attempt a new model ever makes (Unsolved 2),
    stated as data: before the attempt its bound is 0.0 and it sorts last; the
    attempt is dispatched (the ladder reaches it under exhaustion,
    `max_rungs=0`); the record lands whatever the verdict; a single CONFIRMED
    with provenance lifts its bound only to 0.206549, which outranks nothing
    established -- 12 consecutive provenance-checked successes are needed to
    pass a seat at 60/70 (derived: n/(n+z^2) > wilson_lower(60,70))."""
    cap = estimator.capability(seat)
    return {"seat": seat, "attempts": cap.attempts,
            "wilson_lower": cap.wilson_lower, "sorts_last": cap.attempts == 0}
