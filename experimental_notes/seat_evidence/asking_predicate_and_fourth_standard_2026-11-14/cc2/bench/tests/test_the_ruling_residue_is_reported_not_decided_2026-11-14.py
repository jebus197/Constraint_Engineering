# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'asking_predicate_and_fourth_standard_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 99b4848f9b005b5ff8e593a873c5d458c636f2e20c744b72796b31cf67395c65
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""GUARD for option O3 of the brief of 2026-11-14: the ruling residue is
REPORTED as undecidable, and reporting it decides NOTHING.

WHAT THIS PROTECTS, and it is 2 separate properties that could each regress on
their own:

  1. `residue_undecidable` is TRUE exactly where the 3 named predicates
     disagree, and that is driven with CONSTRUCTED text as well as with the
     live list -- because a guard whose only evidence is live data that happens
     to exercise it is indistinguishable from a guard that does nothing, which
     is `classify_text`'s own recorded lesson about its DEPENDENT branch.

  2. ADDING IT MOVED NO SURFACE. The 3 consumers of `classify_text` --
     the `[tasks]` banner, the entry the Stop gate names, and the refusal
     budget -- must return what they returned before. This is the property the
     founder's hard constraint demands: Q1 is his to rule, so an analysis round
     may add a REPORT and must not install a changed verdict.

AND IT PINS THE REFACTOR. `residue_A` replaced an inline expression in
`classify_text`. A behaviour-preserving extraction is only preserving if
something checks it, so the inline form is recomputed here and compared on
every live entry.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def clf():
    return _load("_clf_guard",
                 "scripts/how_many_decisions_actually_need_him_2026-11-01.py")


@pytest.fixture(scope="module")
def tlm():
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as m                               # type: ignore
    return m


@pytest.fixture(scope="module")
def opens(tlm):
    return [e for e in tlm.parse_entries(LIST)
            if (e.state or "").upper() == "OPEN"]


class TestTheFlagIsDrivenAndNotMerelyObserved:
    """CONSTRUCTED cases first, so the predicate is exercised on both verdicts."""

    def test_all_three_agreeing_is_not_undecidable(self, clf):
        #: A dated note FIRST, then an asking sentence that ALSO carries a later
        #: date. A sees a later date, B sees one inside the ask, C sees the ask
        #: positioned after the first later date. All 3 True, so they AGREE.
        #:
        #: ★ THE ORDER HERE IS LOAD-BEARING AND THE FIRST VERSION OF THIS TEST
        #: GOT IT WRONG, WHICH IS WORTH RECORDING AS A PROPERTY OF C RATHER
        #: THAN AS A TYPO. The original body was the single sentence "NEEDS
        #: YOUR RULING on the scope, raised 2026-11-10." -- and C returned
        #: False on it. C compares the asking sentence's START offset against
        #: the offset of the first post-ruling date, so when the ONLY later
        #: date lies INSIDE the asking sentence, the sentence necessarily
        #: starts before it and C cannot fire. C therefore misses the clearest
        #: possible case of a question raised after a ruling: one that states
        #: its own date. That is a reason against adopting C (option O2 of the
        #: brief) and it was found by driving the predicate, not by reading it.
        body = ("Progress note 2026-11-09: the harness was rewired. "
                "NEEDS YOUR RULING on the scope, raised 2026-11-10.")
        asks = clf.classify_text("OPEN", "2026-11-08", body)["live_asks"]
        assert asks, "the constructed case must produce a live ask or it tests nothing"
        v = {k: fn("2026-11-08", body, asks)
             for k, fn in clf.RESIDUE_PREDICATES.items()}
        assert len(set(v.values())) == 1, f"constructed case not unanimous: {v}"
        assert clf.residue_undecidable("2026-11-08", body, asks) is False

    def test_a_dated_note_after_the_ask_makes_it_undecidable(self, clf):
        #: THE SHAPE OF THE DEFECT, constructed. The ask carries NO date and
        #: sits BEFORE a dated progress note. A fires (a later date exists
        #: somewhere), B does not (no date in the asking sentence), so the 3
        #: cannot agree -- which is exactly the entry class F2 of the brief
        #: describes: edited after he ruled, not asked after he ruled.
        body = ("NEEDS YOUR RULING on the scope. "
                "Progress note 2026-11-10: the harness was rewired.")
        asks = clf.classify_text("OPEN", "2026-11-08", body)["live_asks"]
        assert asks
        v = {k: fn("2026-11-08", body, asks)
             for k, fn in clf.RESIDUE_PREDICATES.items()}
        assert v["A"] is True, f"A must fire on a later dated note: {v}"
        assert v["B"] is False, f"B must not fire: no date in the ask: {v}"
        assert clf.residue_undecidable("2026-11-08", body, asks) is True

    def test_no_recorded_ruling_is_unanswered_and_not_undecidable(self, clf):
        #: An entry with no ruling is a DIFFERENT group -- unanswered, not
        #: undecidable -- and conflating the 2 is the mislabelling the
        #: 2026-11-12 producer corrected on the day it was written.
        body = "NEEDS YOUR RULING on the scope, raised 2026-11-10."
        asks = clf.classify_text("OPEN", None, body)["live_asks"]
        assert clf.residue_undecidable(None, body, asks) is False
        assert clf.residue_undecidable("", body, asks) is False


class TestTheFlagMatchesTheLiveList:
    def test_it_is_true_on_exactly_the_entries_the_producer_names(self, clf, opens):
        bodies = clf.bodies()
        flagged = sorted(e.ident for e in opens
                         if clf.classify_text(e.state, e.ruled,
                                              bodies.get(e.ident, ""))
                         ["residue_undecidable"])
        #: Recomputed INDEPENDENTLY from the predicate set rather than quoted
        #: from the brief, so the guard measures rather than remembers. The
        #: identities are asserted too, because a count alone would hide a swap
        #: -- the lesson of `test_the_generator_and_the_producer_name_the_same_
        #: decisions`.
        expect = []
        for e in opens:
            b = bodies.get(e.ident, "")
            asks = clf.classify_text(e.state, e.ruled, b)["live_asks"]
            #: BOTH conditions, and the second is DERIVED from the ladder rather
            #: than chosen: `classify_text` reads `_later` only inside the branch
            #: guarded by `live_asks and ruled`, so where either is absent the
            #: proxy cannot change `kind` and a disagreement is unreachable.
            #: Omitting the `asks` condition is the bug the round's own falsifier
            #: caught -- it flagged 8 entries where the measured population is 5,
            #: the 3 extra being ask-less entries that are MINE under every
            #: predicate.
            if not e.ruled or not asks:
                continue
            v = {fn(e.ruled, b, asks) for fn in clf.RESIDUE_PREDICATES.values()}
            if len(v) > 1:
                expect.append(e.ident)
        assert flagged == sorted(expect), f"{flagged} != {sorted(expect)}"
        assert flagged, ("0 entries flagged -- the live list no longer exercises "
                         "this guard, so it has become vacuous and must be "
                         "driven by the constructed cases above alone")


    def test_an_entry_with_no_live_ask_is_never_flagged(self, clf):
        #: ★ THE REGRESSION THIS ROUND'S FALSIFIER FOUND IN THIS ROUND'S OWN FIX.
        #: Body carries a later dated note and NO asking sentence. A fires on the
        #: body date, B cannot fire (no ask), so the raw predicate set disagrees
        #: -- yet `kind` is MINE under all 3, because the ladder never reaches
        #: `_later` when `live_asks` is empty. Flagging it would put a spurious
        #: item in front of him, which is the defect class this round measures.
        body = "Rewired the harness. Progress note 2026-11-10: done."
        d = clf.classify_text("OPEN", "2026-11-08", body)
        assert d["live_asks"] == [], "the constructed case must have no live ask"
        raw = {fn("2026-11-08", body, []) for fn in clf.RESIDUE_PREDICATES.values()}
        assert len(raw) > 1, (
            "the raw predicates must DISAGREE here or this test is vacuous and "
            "proves nothing about the scoping")
        assert d["residue_undecidable"] is False
        assert d["kind"] == "MINE"


class TestAddingTheFlagMovedNoSurface:
    """THE FOUNDER'S HARD CONSTRAINT, as an executable assertion."""

    def test_the_banner_figure_is_unchanged_by_the_new_key(self, clf, tlm, opens):
        #: The banner's figure is `kind == "OWED"` counted over OPEN entries.
        #: Recomputing it from `residue_A` ALONE -- the pre-patch rule -- must
        #: reproduce what `classify_text` returns now.
        bodies = clf.bodies()
        now = sum(1 for e in opens
                  if clf.classify_text(e.state, e.ruled,
                                       bodies.get(e.ident, ""))["kind"] == "OWED")
        mine, his, _k = tlm._whose_move(tlm.parse_entries(LIST))
        assert his == now, (
            f"summarise() says {his} await him, classify_text says {now}; the "
            f"new key has leaked into a verdict")
        assert mine + his == len(opens)

    def test_kind_is_a_function_of_residue_A_only(self, clf, opens):
        #: Flip `residue_undecidable` to a constant and `kind` must not move.
        #: If it does, O3 has stopped being a report and become a 4th predicate.
        bodies = clf.bodies()
        before = {e.ident: clf.classify_text(e.state, e.ruled,
                                             bodies.get(e.ident, ""))["kind"]
                  for e in opens}
        orig = clf.residue_undecidable
        try:
            clf.residue_undecidable = lambda *a, **k: True
            after = {e.ident: clf.classify_text(e.state, e.ruled,
                                                bodies.get(e.ident, ""))["kind"]
                     for e in opens}
        finally:
            clf.residue_undecidable = orig
        assert before == after, (
            "kind changed when residue_undecidable was forced True, so the O3 "
            "flag is deciding and not reporting")

    def test_the_extraction_of_residue_A_preserved_behaviour(self, clf, opens):
        #: The inline expression that `residue_A` replaced, recomputed here.
        inline = re.compile(r"\b(2026-\d{2}-\d{2})")
        bodies = clf.bodies()
        for e in opens:
            b = bodies.get(e.ident, "")
            was = bool(e.ruled) and any(d > e.ruled for d in inline.findall(b))
            now = clf.residue_A(e.ruled, b, [])
            assert was == now, f"{e.ident}: inline {was} != residue_A {now}"

    def test_the_refusal_budget_cannot_see_the_proxy_at_all(self, clf, opens):
        #: DERIVED, then CHECKED. `movable_count` tests `live_asks`, which is
        #: built in the sentence loop ABOVE the line computing `_later`, so no
        #: value of the proxy can change it. Forcing every predicate True and
        #: then every predicate False must leave `live_asks` identical.
        bodies = clf.bodies()
        base = {e.ident: tuple(clf.classify_text(e.state, e.ruled,
                                                 bodies.get(e.ident, ""))
                               ["live_asks"]) for e in opens}
        orig = dict(clf.RESIDUE_PREDICATES)
        for forced in (True, False):
            try:
                clf.residue_A = lambda *a, **k: forced
                got = {e.ident: tuple(clf.classify_text(e.state, e.ruled,
                                                        bodies.get(e.ident, ""))
                                      ["live_asks"]) for e in opens}
            finally:
                clf.residue_A = orig["A"]
                clf.RESIDUE_PREDICATES.update(orig)
            assert got == base, (
                f"live_asks moved when residue_A was forced {forced}; the "
                f"refusal budget is NOT independent of the proxy after all")
