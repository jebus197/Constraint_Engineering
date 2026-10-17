#!/usr/bin/env python3
"""The ladder's order is measured inside the experiment, and frozen after.

HIS RULING, 2026-10-09: *"in reality there should probably be no distinction
between models participating in an experiment other than a 'ranking number' ...
the only things that should denote a model's ranking in any given experiment is
derived/demonstrable capability, either above that. Or below that of its
peers"*, with the timing fixed as *"one round of an experimental run could
potentially constitute a season, and players/teams should get demoted promoted
based on the evidence derived from this first experimental round. Then for the
rest of the rounds in an experiment the positions of these models in their
rankings stays fixed"*. Confirmed 2026-10-11: *"We measure at the start and keep
it."* The project's memory records the point being made 4 times.

WHAT THE ARCHIVE CAN AND CANNOT FOUND, measured by
`scripts/is_the_ladder_order_estimable_2026-10-17.py` over all 3,020 archived
entries. The only recorded quantity that measures falsification capability
rather than productivity is `falsifier_verdict` -- ranking on finding rate was
REFUTED by a free seat on 2026-10-06 because it measures productivity and
reproduces the inversion `competence_provenance` exists to prevent, and no
fingerprint field records a falsification outcome at all.

    Gemini    10 of 701   Wilson [0.7767%, 2.6058%]
    DeepSeek   6 of 521   Wilson [0.5288%, 2.4895%]
    ChatGPT    0 of 373   Wilson [0.0000%, 1.0194%]
    CC2        0 of 366   Wilson [0.0000%, 1.0387%]
    Codex      0 of 342   Wilson [0.0000%, 1.1108%]

26 refutations in the whole archive, ZERO for 3 of the 5 paid seats. The omnibus
test REJECTS equality -- chi2 = 14.5802, dof 4, p = 0.005656 -- so the seats
genuinely differ, and yet 0 of 10 pairwise comparisons survive Holm or
Bonferroni correction at 0.05. Heterogeneity is established; ORDER is not. Since
a ranking is a set of pairwise orderings, the archive cannot found one, which is
exactly why his season design measures inside the experiment that uses it.

AND WHY THE VENDOR TUPLE IS STILL THE FALLBACK: emptying it collides with his
EARLIER ruling of 2026-10-07, *"Then yes we should add it"*, which is implemented
as MEMBERSHIP of that tuple and verified by a guard asserting
`ladder_length == 6`. Separating membership from order changes recorded
behaviour, so it is put to him rather than taken.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import routing as RT  # noqa: E402


class _Reg:
    def __init__(self, entries):
        self.entries = entries


def _entries(seat: str, refuted: int, n: int) -> dict:
    return {f"{seat}_{i}": {"source_model": seat,
                            "falsifier_verdict":
                                "REFUTED" if i < refuted else "CONFIRMED"}
            for i in range(n)}


# --------------------------------------------------------------- the evidence

def test_the_evidence_reader_counts_refutations_not_findings():
    """Finding rate is PRODUCTIVITY and ranking on it was refuted 2026-10-06."""
    reg = _Reg({**_entries("A", 3, 10), **_entries("B", 0, 50)})
    ev = RT.falsification_evidence_from_registry(reg)
    assert ev["A"] == (3, 10)
    assert ev["B"] == (0, 50), (
        "B produced 5x as many findings as A and refuted none; if this reader "
        "ranked on volume it would rank B first")


def test_a_non_dict_entry_does_not_break_the_reader():
    reg = _Reg({"a": None, "b": "nonsense", "c": {"source_model": "A",
                                                  "falsifier_verdict": "REFUTED"}})
    assert RT.falsification_evidence_from_registry(reg) == {"A": (1, 1)}


# ------------------------------------------------------------- estimability

def test_the_real_archive_evidence_does_not_establish_an_order():
    """THE HEADLINE. It must refuse, because the evidence cannot support it."""
    archive = {"Gemini": (10, 701), "DeepSeek": (6, 521),
               "ChatGPT": (0, 373), "CC2": (0, 366), "Codex": (0, 342)}
    order, established, why = RT.strength_order_from_evidence(archive)
    assert established is False, (
        f"an order was declared established from 26 refutations across 3,020 "
        f"entries with 0 for 3 of 5 seats: {order}")
    assert order == ()
    assert "0 of 10" in why and "Holm" in why, why


def test_evidence_that_separates_does_establish_an_order():
    """ANTI-VACUITY. A function that always refused would pass the test above."""
    order, established, why = RT.strength_order_from_evidence(
        {"Strong": (60, 100), "Weak": (2, 100)})
    assert established is True, why
    assert order == ("Strong", "Weak"), order


def test_one_seat_cannot_be_ranked():
    order, established, why = RT.strength_order_from_evidence({"A": (5, 10)})
    assert established is False and order == ()
    assert "fewer than 2" in why


def test_labels_restrict_the_comparison():
    ev = {"A": (60, 100), "B": (2, 100), "C": (1, 100)}
    order, est, _ = RT.strength_order_from_evidence(ev, labels=["A", "B"])
    assert est is True and set(order) == {"A", "B"}, order


# ----------------------------------------------------------------- the season

def test_a_round_that_discriminates_sets_the_order():
    reg = _Reg({**_entries("A", 15, 20), **_entries("B", 0, 20)})
    order, est, why = RT.season_strength_order(reg, ["A", "B"])
    assert est is True and order == ("A", "B"), (order, why)


def test_a_round_that_does_not_discriminate_falls_back_AND_SAYS_SO():
    """The part that was silent before: a default that looked like a measurement."""
    reg = _Reg({**_entries("A", 0, 20), **_entries("B", 0, 20)})
    order, est, why = RT.season_strength_order(reg, ["A", "B"])
    assert est is False
    assert tuple(order) == tuple(RT.DEFAULT_FALSIFIER_STRENGTH)
    assert "vendor order" in why and "no measurement" in why, why


def test_the_positions_stay_fixed_for_the_rest_of_the_experiment():
    """HIS RULING, literally: a season's positions do not move after round 1.

    The second round here carries evidence that REVERSES the ranking, and the
    frozen order must survive it. Without this, a late round could reshuffle the
    ladder mid-experiment, which is the thing he ruled against.
    """
    first = _Reg({**_entries("A", 15, 20), **_entries("B", 0, 20)})
    order, est, _ = RT.season_strength_order(first, ["A", "B"])
    assert est and order == ("A", "B")

    later = _Reg({**_entries("A", 0, 20), **_entries("B", 19, 20)})
    frozen, est2, why2 = RT.season_strength_order(later, ["A", "B"], frozen=order)
    assert tuple(frozen) == ("A", "B"), (
        f"the order moved to {frozen} on later evidence; a season's positions "
        f"must stay fixed")
    assert est2 is True
    assert "frozen" in why2 and "stay fixed" in why2, why2


# ------------------------------------------------------- the retained default

def test_the_vendor_order_is_retained_and_marked_unestablished():
    """Point, never prune -- and never silently presented as a measurement."""
    assert RT.VENDOR_ORDER_SUPERSEDED == RT.DEFAULT_FALSIFIER_STRENGTH
    assert RT.FALSIFIER_STRENGTH_IS_ESTABLISHED is False, (
        "the default order is flagged as resting on measured capability. The "
        "archive does not support that: 0 of 10 pairs separate under Holm.")
    assert len(RT.DEFAULT_FALSIFIER_STRENGTH) == 6, (
        "his ruling of 2026-10-07 put every free seat on the ladder and a guard "
        "asserts ladder_length == 6; changing that is his call, not a refactor")


def test_the_default_is_still_a_literal_the_source_probes_can_read():
    """`competence_provenance` reads this constant with ast.literal_eval.

    Moving the literal onto the alias was tried and reverted on 2026-10-17: 5
    guards failed with "malformed node or string" because literal_eval accepts a
    literal and not a name. Pinned so the next rename does not repeat it.
    """
    import ast
    src = (REPO / "bench" / "routing.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    found = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "DEFAULT_FALSIFIER_STRENGTH"):
            found = node.value
    assert found is not None, "the constant has gone missing"
    assert tuple(ast.literal_eval(found)) == tuple(RT.DEFAULT_FALSIFIER_STRENGTH), (
        "the assignment is not a literal the source probes can evaluate")


def test_the_season_is_wired_into_the_runner():
    """An addition nothing reaches is not additive."""
    import ast
    src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    assert "season_strength_order" in src, (
        "the runner does not use the season order, so measuring it changes "
        "nothing about any run")
    tree = ast.parse(src)
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and (
                 (isinstance(n.func, ast.Name) and n.func.id == "_season"))]
    assert calls, "the season helper is imported but never called"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
