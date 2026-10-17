"""Task C7: a rung order that rests on no measurement says so in the artefact.

HIS RULING, 2026-10-05: *"The routing ladder should be a measured statistic,
not simply a list of named vendors based on what you, or I may have read about
them on the internet."* And: *"The system shouldn't care at all what a model is
called, only what it can be statistically demonstrated to have done, as per its
capability fingerprint."*

THE ORDER IS NOT ESTIMABLE FROM THE ARCHIVE, measured by
scripts/is_the_ladder_order_estimable_2026-10-17.py: the omnibus test rejects
equality, so the seats really do differ, but 0 of 10 pairwise orderings survive
Holm or Bonferroni at 0.05 -- and a ranking IS a set of pairwise orderings. So
the archive supports "they differ" and supports no claim about which is
stronger. That is why his season design is the only sound founding: the order
must be measured INSIDE the run that uses it.

WHICH LEAVES THE DEFAULT AS A CONVENTION, and the defect was that a convention
was indistinguishable from a finding. `season_strength_order` already announces
its own fallback loudly, but 6 of 7 live `route` call sites never reach that
function -- 85.7143%, Wilson [48.6872%, 97.4320%] -- and take the module default
silently. Only `reference_runner_v3` passes a measured order, through
`**_route_kw`.

MY FIRST TWO MEASUREMENTS OF THAT WERE BOTH WRONG, and the corrections are
recorded because the method is the evidence:
  * the first treated `strength_order` as positional and counted 5 live sites
    with 1 passing; it is KEYWORD-ONLY, so no positional call passes it;
  * the second looked for a literal `strength_order=` keyword and reported
    7 of 7 = 100%, missing the runner's `**_route_kw` entirely. The corrected
    figure is 6 of 7.

THE REPAIR IS DETECTIVE AND COSTS NOTHING: one field, stamped in one place
inside `route` so all 6 callers are reached without touching any of them, and
carried into `routing_history` so it survives into the bundle. No routing
behaviour depends on it, so it cannot change a result.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import bench.routing as RT  # noqa: E402

FINDING = {"id": "X", "description": "a finding", "source_model": "Nobody",
           "falsifier_code": "print(1)"}


def _route(**kw):
    return RT.route(FINDING, ["CC2", "Codex"], [],
                    lambda m, x: "CONFIRMED", lambda c: "CONFIRMED",
                    lambda a, b: 0.0, **kw)


def test_the_archive_cannot_establish_the_order_and_the_module_says_so():
    """The premise. If this ever becomes True the whole entry needs redoing."""
    assert RT.FALSIFIER_STRENGTH_IS_ESTABLISHED is False, (
        "the module now claims the vendor order rests on measurement. If an "
        "experiment has established it, say which one and re-derive C7; do "
        "not simply flip the flag.")


def test_the_default_order_is_recorded_as_unestablished():
    assert _route().strength_order_was_unestablished is True, (
        "a routing pass ordered by the vendor tuple did not record that the "
        "order rests on no measurement, so a reader of the artefact cannot "
        "tell a convention from a finding")


def test_an_explicitly_measured_order_is_not_flagged():
    """THE OTHER DIRECTION. A flag that is always True says nothing."""
    assert _route(strength_order=("CC2", "Codex")).strength_order_was_unestablished is False


def test_a_duplicate_verdict_carries_the_same_answer():
    """A duplicate was still reached by a ladder, so the question has the same
    answer whichever verdict came back."""
    confirmed = [dict(FINDING, id="D")]
    out = RT.route(FINDING, ["CC2"], confirmed,
                   lambda m, x: "CONFIRMED", lambda c: "CONFIRMED",
                   lambda a, b: 1.0)
    assert out.verdict == "DUPLICATE"
    assert out.strength_order_was_unestablished is True


def test_the_vendor_alias_and_the_literal_cannot_disagree():
    assert RT.VENDOR_ORDER_SUPERSEDED == RT.DEFAULT_FALSIFIER_STRENGTH


def test_an_order_equal_to_the_default_is_flagged_however_it_was_passed():
    """Passing the vendor tuple explicitly is still the vendor tuple. The test
    is on the ORDER, not on how the caller spelled it."""
    out = _route(strength_order=tuple(RT.DEFAULT_FALSIFIER_STRENGTH))
    assert out.strength_order_was_unestablished is True
    out2 = _route(strength_order=list(RT.DEFAULT_FALSIFIER_STRENGTH))
    assert out2.strength_order_was_unestablished is True, (
        "a list of the same names escaped the check, so the comparison is on "
        "type rather than on content")


def test_the_fact_reaches_the_artefact_and_is_not_merely_on_the_object():
    """AN ADDITION NOTHING READS IS NOT ADDITIVE. The runner must copy the
    field into `routing_history`, or it dies on the object."""
    runner = (REPO / "bench" / "reference_runner_v3.py").read_text(
        encoding="utf-8", errors="replace")
    assert '"strength_order_was_unestablished":' in runner, (
        "the runner does not record the field into routing_history, so it "
        "never reaches a bundle and nothing can read it")


def test_the_live_runner_still_passes_a_measured_order_when_it_differs():
    """The one live site that does the right thing must keep doing it."""
    runner = (REPO / "bench" / "reference_runner_v3.py").read_text(
        encoding="utf-8", errors="replace")
    assert '_route_kw["strength_order"] = _order' in runner, (
        "the runner no longer forwards a measured order, so the only live "
        "caller that ranked on measurement has stopped")


# --------------------------------------------- the ladder that ranks nothing

LIVE_PANEL = ["cx", "cgpt", "ge", "ds", "cc2", "fable", "kimi"]


def test_the_one_matching_rule_is_what_the_ranking_actually_DOES():
    """BOTH FORMS EXECUTED AND COMPARED, which is the only way this class of
    defect is ever caught. The counter was written first as a lowercase set
    comparison and reported 2 of 7 matched while `rank_falsifier_writers`
    ranked 0 of 7: the ranking compares exactly, modulo `-SIM`, and does not
    fold case. Both implementations were individually consistent, so neither
    could be found by reading it."""
    for labels in (LIVE_PANEL, ["Codex", "CC2", "Gemini"],
                   ["CC2-SIM", "Codex-SIM"], [], ["Nobody"]):
        expected = RT.labels_the_order_ranks(labels,
                                             RT.DEFAULT_FALSIFIER_STRENGTH)
        ranked = RT.rank_falsifier_writers(labels)
        # MEMBERSHIP is the shared question; ORDER is the ranking's own. An
        # earlier version of this test compared them as sequences and failed on
        # ["CC2-SIM", "Codex-SIM"], where the rule returns label order and the
        # ranking returns strength order. Both were right.
        assert set(ranked[:len(expected)]) == set(expected), (
            f"for {labels}: rank_falsifier_writers ranked "
            f"{set(ranked[:len(expected)])} but the matching rule says "
            f"{set(expected)}. The counter and the ranking disagree about the "
            f"same question, which is the shape neither can be read to find.")
        assert len(expected) == len(set(expected)), "the rule duplicated a label"


def test_the_live_panel_roster_is_ranked_by_nothing_and_that_is_recorded():
    """THE SUBSTANTIVE HALF OF HIS RULING OF 2026-10-05.

    None of the live roster's keys matches a vendor name, so the "ladder"
    returns the roster unchanged: reverse the input and the ranking reverses
    with it. It looks like a ranking and is an identity function."""
    assert RT.labels_the_order_ranks(LIVE_PANEL,
                                     RT.DEFAULT_FALSIFIER_STRENGTH) == [], (
        "a live roster key now matches a vendor name; the figure 0 of 7 and "
        "everything derived from it must be re-measured")
    forward = RT.rank_falsifier_writers(LIVE_PANEL)
    backward = RT.rank_falsifier_writers(list(reversed(LIVE_PANEL)))
    assert forward == LIVE_PANEL
    assert backward == list(reversed(LIVE_PANEL)), (
        "the ranking no longer passes the roster through unchanged, so its "
        "behaviour on the live roster has changed and needs his ruling")
    out = _route()
    assert out.strength_order_matched == 2, (
        "the fixture roster CC2/Codex should match 2; if this moved, the "
        "counter or the order changed")
    live = RT.route({"id": "L", "description": "d", "source_model": "none",
                     "falsifier_code": "c"},
                    LIVE_PANEL, [], lambda m, x: "CONFIRMED",
                    lambda c: "CONFIRMED", lambda a, b: 0.0)
    assert live.strength_order_matched == 0, (
        "the live roster is recorded as ranked by something; it is ranked by "
        "nothing, and silently claiming otherwise is the defect")


def test_the_sim_suffix_still_ranks_as_its_vendor():
    """Fable's finding of 2026-08-30: without this, a simulated panel ranked
    EMPTY and every seat fell through to the unknown-model fallback, so ladder
    ORDER went unrehearsed by every simulation."""
    assert RT.labels_the_order_ranks(["CC2-SIM"],
                                     RT.DEFAULT_FALSIFIER_STRENGTH) == ["CC2-SIM"]


def test_the_match_count_reaches_the_artefact():
    runner = (REPO / "bench" / "reference_runner_v3.py").read_text(
        encoding="utf-8", errors="replace")
    assert '"strength_order_matched":' in runner, (
        "the count does not reach routing_history, so nothing can read it")
