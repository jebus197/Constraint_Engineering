"""The ranking is DETERMINISTIC and EXCHANGEABLE, and now something checks it.

HIS CONDITIONAL APPROVAL, 2026-10-09, quoted in task C21: *"if the models
recommend both, then we should go with both, providing this still makes sense
when considered against my most recent reframing"*. Both seats of the panel of
2026-10-08 recommended determinism AND exchangeability, the measured price was
**0 additional attempts** at the committed operating point, and the condition he
attached is satisfied because thresholds on COUNTS are compatible with a 1-round
season.

WHAT THE PANEL ACTUALLY SETTLED, AND WHY EXCHANGEABILITY IS THE LOAD-BEARING
HALF. A gate reading WHICH attempts succeeded reaches power 0.9833784264 at size
0.0099919656 against a randomised optimum of 0.9834296545 -- a shortfall of
5.1e-5 -- while a gate reading only the COUNT reaches 0.9298091736. So the
order-reading gate is very slightly more powerful. It was rejected anyway,
because reading the order violates exchangeability and is in the panel's words
*"a concealed coin toss"*: 2 seats with identical records would be ranked by
which of their successes happened to land first, which is not capability.

BOTH PROPERTIES ARE ALREADY TRUE BY CONSTRUCTION, AND THAT IS PRECISELY WHY THIS
FILE EXISTS. `falsification_evidence_from_registry` reduces each seat to a
`(refuted, total)` PAIR, `falsification_evidence_by_identity` pools those pairs,
and `strength_order_from_evidence` ranks on the pairs alone -- so no permutation
of the underlying outcomes can reach the ranking, and ties break on the seat
label rather than on dict iteration order. **An invariant that holds only by
construction is an invariant that can be removed by a refactor without anything
objecting.** Adopting determinism and exchangeability therefore means making
them CHECKABLE, which is what this file does; it changes no behaviour.

ANTI-VACUITY IS BUILT IN, because a test that permutes inputs and finds the
output unchanged would also pass against a function that always returns the same
thing. Every exchangeability assertion here is paired with a DISCRIMINATION
assertion showing the same function does respond when the COUNTS differ.

Written under CDSFL note standard v1.8.
"""
from __future__ import annotations

import itertools
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.routing import (  # noqa: E402
    falsification_evidence_from_registry,
    season_strength_order,
    strength_order_from_evidence,
)


class _Reg:
    """The smallest thing `falsification_evidence_from_registry` reads."""

    def __init__(self, entries):
        self.entries = {e["canonical_id"]: e for e in entries}


def _entry(cid, seat, refuted):
    return {"canonical_id": cid, "source_model": seat,
            "falsifier_verdict": "REFUTED" if refuted else "CONFIRMED",
            "severity": 0.9, "open_since_round": 0, "status": "CONFIRMED"}


def _outcomes(seat, refuted, total, offset=0):
    """`total` entries for `seat`, of which `refuted` are REFUTED."""
    return [_entry(f"C{offset + i:04d}", seat, i < refuted) for i in range(total)]


class TestDeterminism:
    """The same evidence must always give the same answer, including `why`."""

    def test_repeated_calls_agree_exactly(self):
        ev = {"A": (30, 30), "B": (15, 30), "C": (0, 30)}
        first = strength_order_from_evidence(ev)
        for _ in range(5):
            assert strength_order_from_evidence(ev) == first, (
                "the ranking is not reproducible on identical input")
        assert first[1] is True, "the fixture no longer separates; it must, or "
        "every assertion here is vacuous"

    def test_a_tie_is_broken_by_a_stable_rule_not_by_iteration_order(self):
        """2 seats with IDENTICAL records must not be ordered by which the dict
        happened to yield first. That is the 'concealed coin toss'.

        ★ THE FIXTURE MATTERS AND MY FIRST ONE WAS VACUOUS. It used
        `{"A": (5, 10), "B": (5, 10)}` alone -- 2 tied seats and nothing else --
        and that evidence SEPARATES NO PAIR, so the function returns an empty
        order BEFORE reaching the sort. The test then compared `()` with `()`
        and passed against a mutation that deleted the tiebreak entirely.
        Caught by mutating the code and finding the test still green.

        The fixture now carries a THIRD seat that does separate, which is what
        makes the order non-empty and the tie reachable: at least 1 pair must
        separate for a ranking to be returned at all.
        """
        ev = {"A": (30, 30), "B": (5, 10), "C": (5, 10)}
        a = strength_order_from_evidence(ev)
        b = strength_order_from_evidence({"C": (5, 10), "B": (5, 10), "A": (30, 30)})
        assert a[1] is True and a[0], (
            f"the fixture does not produce a ranking ({a[0]}, {a[1]}), so the "
            f"tie is unreachable and this test would be vacuous")
        assert set(a[0]) == {"A", "B", "C"}, a[0]
        assert a[0] == b[0], (
            f"the tied seats B and C came back as {a[0]} and {b[0]} depending "
            f"on dict insertion order; the tie is being broken by iteration "
            f"order, which is the concealed coin toss")


class TestExchangeability:
    """The order may depend on the COUNTS and on nothing else."""

    def test_the_seat_insertion_order_cannot_reach_the_ranking(self):
        base = {"A": (30, 30), "B": (15, 30), "C": (0, 30)}
        expected = strength_order_from_evidence(base)
        assert expected[1] is True, "fixture does not separate"
        for perm in itertools.permutations(base.items()):
            got = strength_order_from_evidence(dict(perm))
            assert got == expected, (
                f"permuting the evidence dict changed the ranking: "
                f"{got[0]} against {expected[0]}")

    def test_permuting_which_outcomes_refuted_cannot_reach_the_ranking(self):
        """THE PANEL'S OWN POINT, executed. 2 registries with the same (refuted,
        total) per seat but the refusals in DIFFERENT POSITIONS must rank the
        same. If the ranking read WHICH attempts succeeded, these would differ."""
        early = _Reg(_outcomes("A", 30, 30) + _outcomes("B", 15, 30, 100)
                     + _outcomes("C", 0, 30, 200))
        # Same counts, refusals moved to the END of each seat's run.
        def _late(seat, refuted, total, offset):
            return [_entry(f"C{offset + i:04d}", seat, i >= total - refuted)
                    for i in range(total)]
        late = _Reg(_late("A", 30, 30, 0) + _late("B", 15, 30, 100)
                    + _late("C", 0, 30, 200))
        assert (falsification_evidence_from_registry(early)
                == falsification_evidence_from_registry(late)), (
            "the 2 fixtures do not carry the same counts, so this test would "
            "prove nothing")
        a = season_strength_order(early, ["A", "B", "C"])
        b = season_strength_order(late, ["A", "B", "C"])
        assert a[0] == b[0], (
            f"moving WHICH attempts were refuted changed the order: "
            f"{a[0]} against {b[0]} -- the ranking is reading order, which the "
            f"panel called a concealed coin toss")

    def test_entry_id_order_cannot_reach_the_ranking(self):
        ents = _outcomes("A", 30, 30) + _outcomes("B", 0, 30, 100)
        fwd = season_strength_order(_Reg(ents), ["A", "B"])
        rev = season_strength_order(_Reg(list(reversed(ents))), ["A", "B"])
        assert fwd[0] == rev[0], (
            f"reversing the registry's entry order changed the ranking: "
            f"{fwd[0]} against {rev[0]}")


class TestItStillDiscriminates:
    """ANTI-VACUITY. Every test above would pass on a function that ignored its
    input entirely, so the same function must be shown to RESPOND to counts."""

    def test_different_counts_give_a_different_order(self):
        up = strength_order_from_evidence({"A": (30, 30), "B": (0, 30)})
        down = strength_order_from_evidence({"A": (0, 30), "B": (30, 30)})
        assert up[1] and down[1], "neither fixture separates"
        assert up[0] != down[0], (
            "swapping which seat refuted everything did not change the order, "
            "so the ranking is not reading the counts either")
        assert up[0] == ("A", "B") and down[0] == ("B", "A")

    def test_it_ranks_on_the_RATE_and_not_on_the_raw_count(self):
        """★ THE SECOND FIXTURE DEFECT, caught the same way. Every fixture in
        the first version of this file used `total=30` for every seat, so
        rate-order and count-order COINCIDED and a mutation ranking on the raw
        refutation count passed unnoticed.

        Ranking on the count measures PRODUCTIVITY, which a free seat refuted on
        2026-10-06 because it reproduces the inversion `competence_provenance`
        exists to prevent. The totals here differ, so the 2 orders disagree and
        the distinction is observable: A refuted 10 of 10 and B refuted 20 of 40,
        so A leads on rate and B leads on raw count.
        """
        order, established, _ = strength_order_from_evidence(
            {"A": (10, 10), "B": (20, 40)})
        assert established is True, "the fixture does not separate"
        assert order == ("A", "B"), (
            f"ranked {order}; B leads only on the RAW COUNT (20 against 10) "
            f"while A leads on the RATE (1.0 against 0.5). Ranking on the count "
            f"is the productivity inversion refuted on 2026-10-06.")

    def test_it_refuses_to_rank_when_no_pair_separates(self):
        """The refusal is the designed behaviour and must not be eroded: a
        ranking read off evidence that does not separate would be noise wearing
        the authority of a measurement."""
        order, established, why = strength_order_from_evidence(
            {"A": (1, 10), "B": (0, 10)})
        assert order == () and established is False
        assert "separate" in why.lower()


class TestTheSeasonFreezeIsStillHonoured:
    """His season design: measured once, then kept. A frozen order must come
    back unchanged no matter what later evidence says, or the freeze is a
    suggestion rather than a rule."""

    def test_a_frozen_order_survives_contradicting_evidence(self):
        ents = _outcomes("A", 0, 30) + _outcomes("B", 30, 30, 100)
        frozen = ("A", "B")
        order, established, why = season_strength_order(
            _Reg(ents), ["A", "B"], frozen=frozen)
        assert order == frozen and established is True, (
            "a later round reshuffled a frozen season order")
        assert "fixed" in why.lower() or "frozen" in why.lower()
