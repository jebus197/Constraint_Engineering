#!/usr/bin/env python3
"""The 2 directive-composition repairs he ruled must be GUARDED, not just made.

HIS RULING, 2026-11-01, annotation 8 of `Closing_Report_2026-11-01.txt`, verbatim:
*"Repair the two as you suggest."* The 2 are the ones that silently alter what a
model is told: the directive DE-DUPLICATOR (audit code C0037) and the directive
CONFLICT DETECTOR (C0036, raised twice, the second code being C0054).

★ WHY THIS FILE EXISTS, AND IT IS THE REASON NEITHER ENTRY COULD BE MARKED DONE.
Both repairs landed on 2026-11-02 and BOTH WERE UNGUARDED. The 2 existing test
files are FALSIFIERS written on 2026-09-10 to demonstrate the original defects,
and they contain 0 references to the repairs -- measured, 0 occurrences of
`unarbitrated`, `conflict_arbitration` or the survivor rule across both. So
reverting either repair left both suites green, which is the `additive-standard`
symmetric failure: an addition nothing reaches is not an addition.

AND THAT GAP WAS DELIBERATE IN ONE DIRECTION, which is why it was easy to miss.
The de-duplicator repair states in its own comment that it leaves the PREDICATE
untouched precisely so the 2026-09-10 falsifier's mechanism assertions stay
green -- "so this repair cannot be mistaken for removing the finding's subject".
That was the right call and it means the old falsifier CANNOT cover the new
behaviour. The coverage had to come from somewhere else, and this is it.

WHAT IS NOT CLAIMED HERE. C0001, the coherence pruner that raises the density it
exists to lower, is NOT repaired. Its subject is retired by default --
`compose(coherence_pruning=False)`, verified by executing the signature -- on his
ruling of 2026-10-13, so the inversion cannot fire. That matches the scope he
chose: repair the 2 that mislead a model, record the others.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.cdsfl_registry import composer as co   # noqa: E402


# ───────────────────────── C0037: the de-duplicator ─────────────────────────
GENERAL = ("safety stock equals z times sigma times square root of "
           "lead time demand variance")
SPECIAL = "safety stock equals z times sigma times square root of lead time"


#: ★ THE PRODUCT'S OWN FUNCTION, AND THE FIRST VERSION OF THIS FILE GOT IT WRONG
#: IN THE WORST AVAILABLE WAY. It REPRODUCED the dedup loop here and asserted on
#: the copy, with a docstring explaining why that was reasonable. It was not:
#: reverting the repair in `composer.py` left this file GREEN, because the test
#: was running its own loop. A producer and a consumer describing the same thing
#: separately, each individually correct -- the defect class `execute-do-not-grep`
#: names, and the SECOND time it was committed in this session, an hour after
#: correcting the identical mistake in the per-round clock guard.
#:
#: The loop was therefore EXTRACTED from `compose` into `_dedupe_lines` so it can
#: be called, which is the project's own recorded remedy: "Extract before
#: guarding. 6 lines inside a 3,400-line function cannot be called, so they could
#: not be tested." The extraction was verified behaviour-preserving against the
#: inline form over 2,072 orderings with 0 disagreements before this file changed.
_dedupe = co._dedupe_lines


def test_the_pair_is_still_SEEN_as_duplicate_so_the_test_is_not_vacuous():
    """THE CONTROL. If the predicate stopped matching, every assertion below
    would pass for the wrong reason -- the lines would simply both survive."""
    assert co._semantically_duplicate(SPECIAL, GENERAL), (
        "the containment predicate no longer matches this pair, so the survivor "
        "rule is never exercised and this file proves nothing")


def test_the_GENERAL_formula_survives_whichever_order_it_arrives_in():
    """THE REPAIR. The survivor is decided by CONTENT, not by position.

    The named harm was a safety-stock formula deleted because its own
    single-parameter special case appeared first and contained enough overlap.
    """
    for label, order in (("special first", [SPECIAL, GENERAL]),
                         ("general first", [GENERAL, SPECIAL])):
        out = _dedupe(order)
        assert len(out) == 1, f"{label}: the pair should collapse, got {out}"
        assert out[0] == GENERAL, (
            f"{label}: the SPECIAL CASE survived and the general formula was "
            f"deleted. The survivor must be the member carrying more distinct "
            f"tokens ({len(co._normalise_tokens(GENERAL))} against "
            f"{len(co._normalise_tokens(SPECIAL))}).")


def test_nothing_is_WEAKENED_the_pair_still_collapses():
    """The repair must not become a licence to keep both.

    "Nothing is weakened: the same pairs are still collapsed and the line count
    after dedup is unchanged. Only the retained member moves." Asserted here so
    a future relaxation of the predicate cannot hide behind this repair.
    """
    assert len(_dedupe([SPECIAL, GENERAL])) == 1
    assert len(_dedupe([GENERAL, SPECIAL])) == 1
    # and 2 genuinely different lines must BOTH survive
    both = _dedupe(["use metric A for scoring", "never infer missing data"])
    assert len(both) == 2, f"unrelated lines were collapsed: {both}"


# ───────────────────── C0036 / C0054: the conflict detector ─────────────────
def _composed(texts_layers):
    P = co.DirectivePacket
    pkts = [P(layer=l, name=f"p{i}", text=t, constraint_class="SOFT",
              domain=("d" if l == "domain" else None), model=None, tags=[])
            for i, (t, l) in enumerate(texts_layers)]
    return co.ComposedDirectiveSet(
        packets=pkts, rendered_text="", policy={}, cid="x",
        constraint_count=len(pkts), token_estimate=0, constraint_density=0.0,
        coherence_budget=0.02, pruned_soft=[], manifest={"model": "test"})


def test_an_unarbitrated_contradiction_is_RECORDED_not_silent():
    """THE REPAIR. `0 conflicts` must be distinguishable from `0 arbitrated`.

    The resolver asks a helper what each directive is ABOUT, and that helper
    recognises exactly 4 topics -- verbosity, examples, rationale, table -- and
    returns `(None, None)` for everything else. It is blind to 95.6120% of the
    directive blocks it is meant to arbitrate, and the helper's OWN documented
    examples, these 2 included, all return nothing.
    """
    out, conflicts = co.resolve_layer_conflicts(_composed([
        ("Never infer missing data.", "universal"),
        ("Fill missing values with defaults.", "domain"),
    ]))
    assert len(conflicts) == 0, "these 2 are unclassifiable; 0 is expected here"
    rec = (out.manifest or {}).get("conflict_arbitration")
    assert rec, (
        "the blind spot is NOT recorded. `conflicts` being empty is then "
        "indistinguishable from there being no conflict, which is the defect.")
    assert rec["total_blocks"] == 2
    assert rec["classifiable_blocks"] == 0
    assert rec["unarbitrated_blocks"] == 2, (
        f"both blocks are unclassifiable and must be counted: {rec}")
    assert rec["conflicts_found"] == 0


def test_the_record_names_the_blocks_it_could_not_arbitrate():
    """A count alone does not let a reader find what was missed."""
    out, _ = co.resolve_layer_conflicts(_composed([
        ("Never infer missing data.", "universal"),
        ("Fill missing values with defaults.", "domain"),
    ]))
    rec = (out.manifest or {})["conflict_arbitration"]
    texts = " ".join(str(u.get("text", "")) for u in rec.get("unarbitrated", []))
    assert "infer missing data" in texts and "defaults" in texts, (
        f"the unarbitrated blocks are not named: {rec.get('unarbitrated')}")


def test_neither_side_of_an_unarbitrated_contradiction_is_DELETED():
    """A resolver must not delete what it cannot arbitrate."""
    out, _ = co.resolve_layer_conflicts(_composed([
        ("Never infer missing data.", "universal"),
        ("Fill missing values with defaults.", "domain"),
    ]))
    assert len(out.packets) == 2, (
        f"a block was dropped without being arbitrated: "
        f"{[p.text for p in out.packets]}")


def test_a_CLASSIFIABLE_pair_still_arbitrates_so_the_record_is_not_vacuous():
    """THE CONTROL FOR THE RECORD. If nothing is ever classifiable, the counts
    above would hold trivially and the detector could be entirely broken."""
    out, _conflicts = co.resolve_layer_conflicts(_composed([
        ("Keep the output minimal and concise.", "universal"),
        ("Give an exhaustive detailed formal proof.", "domain"),
    ]))
    rec = (out.manifest or {})["conflict_arbitration"]
    assert rec["classifiable_blocks"] == 2, (
        f"the helper's own 4 topics no longer classify a verbosity pair, so the "
        f"detector is broken rather than merely blind: {rec}")


# ───────────────── and what is NOT repaired, stated rather than implied ─────
def test_C0001s_subject_is_retired_by_default_and_that_is_not_a_repair():
    """The coherence pruner inversion still exists and cannot fire.

    Marked here so no reader mistakes the 2 repairs above for 4. His ruling of
    2026-10-13 retired the pruner from the default path; the density inversion
    inside it is untouched.
    """
    import inspect
    p = inspect.signature(co.compose).parameters.get("coherence_pruning")
    assert p is not None, "the switch is gone; C0001's status must be re-derived"
    assert p.default is False, (
        f"the coherence pruner is no longer off by default (default="
        f"{p.default!r}), so the density inversion CAN fire and C0001 is live")
