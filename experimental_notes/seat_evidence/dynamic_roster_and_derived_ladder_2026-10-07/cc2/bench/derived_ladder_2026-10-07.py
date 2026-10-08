# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b4aeb3a01c719438b0dad9cc282b43f4d34e6cc741b95366f733724e1f966b90
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The derived routing key: ordering by measured capability per unit of real cost.

It answers three of the brief's questions, and one of them has an answer that is
not a preference but a well-definedness requirement.

══════ UNSOLVED 1: IS A SINGLE SCALAR LATENCY WEIGHT SUFFICIENT? ══════

The brief asks whether pricing the wait with one scalar weight is the right repair
or whether cost must be a vector the researcher sets per task. The answer is BOTH,
and they are not alternatives: cost IS a vector of incommensurable components, and
a scalar weight per component is exactly what collapses it into the single number
the exchange rule needs. With m components you need m-1 weights, not one.

BUT THE DECISIVE POINT IS STRONGER THAN A PREFERENCE, and it comes straight out of
`bench/why_one_ordering_cannot_serve_both_objectives_2026-10-07.py`, which reports
on the free sub-panel:

    distinct_expected_spends: 1
    all_zero: True
    ordering_objective_is_informative: False

The exchange rule `p_i * c_j >= p_j * c_i` induces a total order via the ratio
p/c ONLY WHERE c > 0. The `claude_cli` seats cost 0 money, so on the free
sub-panel every product is 0, every pair compares equal, and the key is not a
weak order with ties -- it is UNDEFINED. Money alone therefore cannot order most
of this panel, and that is a property of the arithmetic, not a judgement about
what the researcher values.

So the cost function MUST carry at least one STRICTLY POSITIVE component. Wall
time is one: every dispatch takes seconds > 0. That single additional component
both repairs the degeneracy and gives requirement 7 its content -- *"problem in
(by the researcher, who then waits) -> problem computed efficiently by the models
-> solution out."* A third component (subscription quota) is wired here because
free seats are free in money and NOT free in Max-subscription headroom, which is
the resource the founder's requirement 8 names as a real cause of dropout.

══════ QUESTION 3: REPLACE `DEFAULT_FALSIFIER_STRENGTH` OR SIT BESIDE IT? ══════

SIT BESIDE IT, as the cold-start tie-break only. The reasoning is the additive
standard applied literally.

On the very first run no seat has any measurement, so every `wilson_lower(0,0)` is
0.0, every key is 0.0, and the sort is decided by whatever order the input list
happened to be in. That is not "ordered by measured capability"; it is arbitrary.
Meanwhile `DEFAULT_FALSIFIER_STRENGTH` encodes Exp-42 empirical confirm rates --
Codex 90%, CC2 75%, Gemini 80%-but-format-fragile, ChatGPT 67%, DeepSeek 28% --
which ARE measured capability. Requirement 3 is satisfied by them already; they
are measurements that happen to be stored as an order rather than as a ledger.

Removal would therefore delete a committed measurement and replace it with an
arbitrary order, with no measurement showing the replacement dominates on any
named property. That is precisely what the additive standard forbids. So:

  * seats WITH attempts are ordered by the derived key;
  * seats with 0 attempts are ordered among themselves by the tuple's position;
  * seats in neither are appended last, which is `rank_falsifier_writers`'s
    existing behaviour and is preserved.

As the ledger fills, the derived key dominates and the tuple becomes unreachable
for every measured seat without anyone editing it. That is the tuple becoming
redundant through measurement, which is the only route to removal the standard
allows -- and it is then a later decision with evidence, not this one.

══════ QUESTION 5: HOW IS "HARDEST" DECIDED WITHOUT A HUMAN? ══════

Kimi K3 is held in reserve for the hardest findings. "Hardest" needs no
classifier, because the ladder already measures it: a finding is hardest exactly
when EVERY non-reserve rung has been tried and none produced a CONFIRMED from
`reverify_falsifier`. That is an observed fact at the end of `resolve_via_routing`
-- `rungs_tried == len(rungs)` with `resolved is False` -- not a property anyone
has to predict in advance.

So the reserve rung is appended AFTER the ordinary ladder rather than placed
within it, and it is reached only on exhaustion. No human classifies any finding,
no difficulty model is trained, and the expensive seat cannot be reached by an
easy finding because an easy finding is resolved before the ladder runs out. This
is also the cheapest possible implementation of the founder's intent: it adds one
list, no new predicate, and nothing to tune.

TWO FACTS ABOUT KIMI THE WIRING MUST RESPECT, both observed:
  * `bench/confer_maths_panel_2026-09-05.py` line 385: `QUARANTINED_SEATS =
    {"kimi"}`. It is quarantined today. Lifting that is the founder's ruling, not
    this module's, so `reserve` defaults to EMPTY and the reserve path is inert
    until a caller passes a seat.
  * `bench/paid_dispatch_authorisations.py` line 41 lists it under the slug
    "kimi", while `DEFAULT_FALSIFIER_STRENGTH` holds display names. The two name
    spaces are reconciled by `normalise`, below, because an unreconciled label
    silently falls into `rank_falsifier_writers`'s unknown-model tail and the
    reserve rung would be dispatched FIRST among extras rather than last.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

#: Cost components. Money is NOT strictly positive on this panel (free
#: `claude_cli` seats), which is why it cannot be the only one -- see the docstring.
MONEY = "money_gbp"
SECONDS = "wall_seconds"
QUOTA = "quota_units"

#: The researcher's exchange rates, set per task. `SECONDS` must be > 0 for the
#: key to be a total order at all; that is asserted, not assumed.
DEFAULT_WEIGHTS = {MONEY: 1.0, SECONDS: 0.01, QUOTA: 0.0}

#: Slug <-> display-name reconciliation. The repository uses both: the panel
#: dispatcher and `paid_dispatch_authorisations.PAID_SEATS` use slugs, while
#: `DEFAULT_FALSIFIER_STRENGTH` uses display names.
SLUG_TO_DISPLAY = {
    "cx": "Codex", "cgpt": "ChatGPT", "ge": "Gemini", "ds": "DeepSeek",
    "cc2": "CC2", "fable": "Fable", "kimi": "Kimi",
}


def normalise(label: str) -> str:
    """Display name for a seat label, accepting a slug, a display name or `-SIM`.

    `-SIM` handling matches `rank_falsifier_writers`'s own `_base`, deliberately:
    two normalisers that disagree would reintroduce the empty-`ranked` bug its
    comment records.
    """
    s = str(label or "")
    if s.endswith("-SIM"):
        s = s[:-4]
    return SLUG_TO_DISPLAY.get(s.lower(), s)


@dataclass
class SeatCost:
    """One seat's cost vector for one dispatch."""
    money_gbp: float = 0.0
    wall_seconds: float = 0.0
    quota_units: float = 0.0

    def scalar(self, weights: dict) -> float:
        return (weights.get(MONEY, 0.0) * self.money_gbp
                + weights.get(SECONDS, 0.0) * self.wall_seconds
                + weights.get(QUOTA, 0.0) * self.quota_units)


def total_cost(cost: SeatCost, weights: dict) -> float:
    """Collapse the cost vector. Raises if the result is not strictly positive.

    A zero cost makes the exchange rule `p_i*c_j >= p_j*c_i` degenerate: every
    pair compares equal and the induced relation is not a total order. The free
    sub-panel hits this with money-only weights, measured in
    `why_one_ordering_cannot_serve_both_objectives_2026-10-07.py`
    (`all_zero: True`, `ordering_objective_is_informative: False`). Failing loudly
    beats emitting an arbitrary order that reads as a derived one.
    """
    c = cost.scalar(weights)
    if c <= 0:
        raise ValueError(
            f"cost collapsed to {c} -- the exchange rule is undefined at zero cost "
            f"and every seat would compare equal. Give a strictly positive weight "
            f"to a component that is itself strictly positive (wall_seconds is: "
            f"every dispatch takes time). Weights given: {weights}")
    return c


def derived_key(p: float, cost: SeatCost, weights: dict) -> float:
    """p / c. Seat i precedes j iff key_i >= key_j, which is p_i*c_j >= p_j*c_i.

    Equivalent to the brief's Part B exchange rule whenever both costs are
    positive, and a total order because it is a sort on a real number.
    """
    return p / total_cost(cost, weights)


@dataclass
class LadderSpec:
    """Everything needed to order one round's rungs. Roster-size agnostic."""
    weights: dict = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    #: Cold-start tie-break ONLY, for seats with 0 recorded attempts.
    cold_start_order: Sequence[str] = ()
    #: Appended AFTER the ordinary ladder; reached only on exhaustion. Empty by
    #: default because Kimi is quarantined and lifting that is the founder's call.
    reserve: Sequence[str] = ()


def rank_by_derived_key(
    labels: Sequence[str],
    ledger,
    costs: dict,
    spec: LadderSpec,
    task_class: str | None = None,
    exclude: Sequence[str] = (),
) -> list:
    """Order `labels` strongest-first by measured capability per unit of real cost.

    * seats with >= 1 recorded attempt: sorted by `derived_key`, descending;
    * seats with 0 attempts: after them, in `cold_start_order` position, then any
      remainder in input order -- the existing unknown-model tail;
    * `spec.reserve`: appended last, so it is reached only when every other rung
      has been tried and none confirmed. That exhaustion IS the definition of
      "hardest"; see the module docstring.

    Returns DISPLAY-normalised labels paired with their input labels so the caller
    dispatches the label it supplied, not a normalised one.
    """
    excl = {normalise(e) for e in exclude}
    reserve = [l for l in labels if normalise(l) in {normalise(r) for r in spec.reserve}]
    reserve_norm = {normalise(l) for l in reserve}
    body = [l for l in labels
            if normalise(l) not in excl and normalise(l) not in reserve_norm]

    measured, cold = [], []
    for l in body:
        n = ledger.counts(normalise(l), task_class)[1]
        (measured if n > 0 else cold).append(l)

    def _key(l):
        p = ledger.score(normalise(l), task_class)
        c = costs.get(normalise(l)) or costs.get(str(l)) or SeatCost(wall_seconds=1.0)
        return -derived_key(p, c, spec.weights)

    measured.sort(key=_key)

    cold_pos = {normalise(s): i for i, s in enumerate(spec.cold_start_order)}
    cold.sort(key=lambda l: (cold_pos.get(normalise(l), len(cold_pos)),
                             body.index(l)))

    out = measured + cold + [l for l in reserve if normalise(l) not in excl]
    return out


def is_hardest(result) -> bool:
    """Did this finding exhaust every ordinary rung without a CONFIRMED?

    Reads `RoutingResult` fields that `bench/routing.py` ALREADY records. No new
    measurement, no classifier, no human: the ladder's own exhaustion is the
    difficulty signal.
    """
    return (not getattr(result, "resolved", False)
            and getattr(result, "verdict", "") != "DUPLICATE")
