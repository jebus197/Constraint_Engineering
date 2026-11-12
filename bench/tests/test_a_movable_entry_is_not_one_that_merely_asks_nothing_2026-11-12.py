#!/usr/bin/env python3
"""An entry parked on HIS PERMISSION is not movable, even if it asks nothing.

★ THE FAULT, AND IT IS THE MIRROR OF ONE ALREADY REPAIRED. `_first_movable`
skips entries whose text still ASKS him something, added 2026-11-10 after the
gate spent a whole day naming an entry that awaited his ruling. It does NOT
catch an entry whose residue is his PERMISSION, stated without a question. B56
says in its own body, in capitals, that its residue "IS STILL HIS
AUTHORISATION", because wiring the rule changes which seats the harness
dispatches, against his standing rule never to bench a model. So the gate named
B56 on 14 consecutive stop attempts.

★ THE FIRST FIGURE WRITTEN FOR THIS WAS WRONG AND IS NAMED HERE DELIBERATELY. A
note prepared before measuring claimed 1 of 11 movable entries was really his.
Deriving the language from the entries themselves gives 3 of 11 -- B56, B104 and
B140 -- Wilson 95% [0.097461, 0.565645].

★ IT IS A POLARITY TEST, NOT A KEYWORD TEST, which the measurement forced. B146
carries a ruling ALREADY GIVEN -- "if it holds then you should implement it" --
an instruction TO ME, not a residue. A phrase-presence list excludes it and
loses a movable entry. B56 and B104 each carry BOTH a past ruling and a live
residue, so "has he ruled?" cannot be the question.

Costs nothing: imports the hook, reads local files, runs no pytest of its own.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "work_not_narrate.py"


@pytest.fixture(scope="module")
def WNN():
    assert HOOK.is_file(), f"the hook is missing: {HOOK}"
    spec = importlib.util.spec_from_file_location("wnn_perm_guard", HOOK)
    m = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("wnn_perm_guard", m)
    spec.loader.exec_module(m)
    return m


class TestTheResiduePredicate:
    def test_a_forward_looking_residue_is_his(self, WNN):
        for s in ("That is a behaviour change for the founder to authorise.",
                  "B56'S OWN RESIDUE IS UNCHANGED AND IS STILL HIS AUTHORISATION",
                  "WHY THIS IS HIS AND NOT MINE: both clauses change routing.",
                  "amending it unprompted would widen his own scope for him",
                  "This awaits his permission before anything is wired."):
            assert WNN._residue_is_his(s), s

    def test_the_clauses_added_after_the_B144_MISS_are_covered(self, WNN):
        """★ THIS TEST EXISTS BECAUSE A MUTATION FOUND IT MISSING.

        The first version of the predicate caught B56, B104 and B140 and MISSED
        B144, whose body says "THE DESIGN CONSEQUENCE IS HIS AND IS HELD UNDER
        HIS `d`". 2 clauses were added for it -- and reverting them left this
        guard fully GREEN, so the repair for a measured miss was itself tested
        by nothing. That is the project's own recorded fault: the passing input
        cannot test a defence.
        """
        for s in ("NO RULING IS REQUESTED FOR THE MEASUREMENT; THE DESIGN "
                  "CONSEQUENCE IS HIS AND IS HELD UNDER HIS `d`.",
                  "the decision is his",
                  "that call is his to make",
                  "it is held under his d"):
            assert WNN._residue_is_his(s), s

    def test_B144_is_excluded_on_the_LIVE_record(self, WNN):
        """Not synthetic: the entry that exposed the miss must be excluded from
        the movable set as the gate actually computes it."""
        sys.path.insert(0, str(REPO / "scripts"))
        spec = importlib.util.spec_from_file_location(
            "wnn_live_bodies",
            REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        body = mod.bodies().get("B144", "")
        if not body:
            pytest.skip("B144 is not in this checkout's task list")
        assert WNN._residue_is_his(body), (
            "B144 says its design consequence is his and is held under his `d`, "
            "and the predicate does not see it")

    def test_a_ruling_already_given_is_NOT_a_residue(self, WNN):
        """★ THE FALSIFIER. B146's only permission-shaped sentence is an
        instruction TO ME. A keyword list excludes it and loses a movable item."""
        for s in ("HIS RULING: on the Greek lettering fix, if it holds then you "
                  "should implement it.",
                  "This needed his permission and he gave it on 2026-11-08, so "
                  "it is mine to build.",
                  "He ruled B21 tonight, so that dependency is discharged.",
                  "ALREADY SATISFIED WHEN HE RULED."):
            assert not WNN._residue_is_his(s), s

    def test_ordinary_prose_is_untouched(self, WNN):
        assert not WNN._residue_is_his(
            "The producer reads the ledger and reports 39 unclassified files.")

    def test_it_fails_safe_on_rubbish(self, WNN):
        """A predicate that raises would cost the GATE, not the preference."""
        for bad in (None, "", 12345):
            assert WNN._residue_is_his(bad) in (True, False)


class TestBothHalvesAgree:
    """★ THESE 2 TESTS WERE REWRITTEN ON THE DAY THEY WERE INSTALLED, and both
    faults are ones this project has already recorded against itself.

    The first asserted on the hook's SOURCE TEXT -- `src.count("_residue_is_his(")
    >= 3` -- which is exactly the defect `execute-do-not-grep` names: a test on
    source text asserts only that a module describes itself consistently, and
    cannot detect a producer and a consumer that disagree, because each
    description is individually correct. It is now an EXECUTING test: the shared
    predicate is flipped and BOTH halves must move. A half that ignored the
    predicate would not move, which a count of occurrences can never show.

    The second SKIPPED whenever nothing was movable -- and after the night's
    closures nothing is, so the invariant it exists for never ran once. It now
    drives the case where something IS movable by flipping the same predicate,
    so it asserts on every record rather than only on a record that happens to
    hold a movable entry.
    """

    @staticmethod
    def _opens(WNN):
        sys.path.insert(0, str(REPO / "scripts"))
        from task_list_markers import parse_entries           # type: ignore
        return [e for e in parse_entries(WNN.TASKS) if e.state == "OPEN"]

    def test_flipping_the_predicate_moves_BOTH_halves(self, WNN, monkeypatch):
        """If either half ignored the residue predicate, its answer would not
        move when the predicate does. This is the producer-consumer divergence
        test, done by execution rather than by counting call sites."""
        opens = self._opens(WNN)
        if not opens:
            pytest.skip("no OPEN entries in this checkout, so neither half can "
                        "be driven against the live record")

        monkeypatch.setattr(WNN, "_residue_is_his", lambda body: True)
        count_all_his = WNN.movable_count()
        named_all_his = WNN._first_movable(opens)

        monkeypatch.setattr(WNN, "_residue_is_his", lambda body: False)
        count_none_his = WNN.movable_count()
        named_none_his = WNN._first_movable(opens)

        assert count_all_his == 0, (
            f"every entry's residue was declared his and the BUDGET half still "
            f"counts {count_all_his} movable, so movable_count() is not "
            f"consulting the residue predicate")
        assert named_all_his == "", (
            f"every entry's residue was declared his and the NAMING half still "
            f"names {named_all_his}, so _first_movable() is not consulting the "
            f"residue predicate")
        assert count_none_his > count_all_his, (
            f"no entry's residue was declared his and the budget half still "
            f"counts {count_none_his}, unchanged from {count_all_his}; the "
            f"predicate is reaching neither branch")
        assert named_none_his != "", (
            "no entry's residue was declared his and the naming half still "
            "names nothing, so the 2 halves cannot be compared")

    def test_the_named_entry_is_a_member_of_the_counted_set(self, WNN, monkeypatch):
        """★ NO LONGER SKIPS. The live record currently holds 0 movable entries,
        so this invariant was never once checked; it is now driven by flipping
        the shared predicate, which guarantees a movable entry exists."""
        opens = self._opens(WNN)
        if not opens:
            pytest.skip("no OPEN entries in this checkout")
        monkeypatch.setattr(WNN, "_residue_is_his", lambda body: False)
        named = WNN._first_movable(opens)
        n = WNN.movable_count()
        assert named, "the naming half named nothing with the residue test off"
        assert n >= 1, (
            f"the gate names {named} as movable while the budget counts {n} "
            f"movable entries, so the 2 halves disagree")

    def test_the_two_halves_agree_on_the_UNMODIFIED_record(self, WNN):
        """And the live state, stated rather than skipped: a named entry
        requires a non-zero count, and a zero count forbids a named entry."""
        opens = self._opens(WNN)
        named, n = WNN._first_movable(opens), WNN.movable_count()
        assert bool(named) == (n >= 1), (
            f"on the live record the naming half says {named!r} and the budget "
            f"half says {n}; one of them is wrong")

    def test_the_budget_still_has_a_floor_and_a_ceiling(self, WNN):
        b = WNN.refusal_budget()
        assert WNN.MAX_REFUSALS_PER_TURN <= b <= WNN.MAX_REFUSALS_CEILING, b

    def test_the_budget_sits_at_its_floor_when_nothing_is_movable(self, WNN, monkeypatch):
        """His ruling of 2026-11-12 in its own terms: 8 when nothing can move
        without him. Driven, so it holds whatever the live record happens to be."""
        monkeypatch.setattr(WNN, "movable_count", lambda: 0)
        assert WNN.refusal_budget() == WNN.MAX_REFUSALS_PER_TURN


class TestItIsNotVacuousOnTheLiveRecord:
    def test_at_least_one_live_entry_is_caught_by_it(self, WNN):
        """If 0 live entries matched, every case above would be synthetic."""
        sys.path.insert(0, str(REPO / "scripts"))
        spec = importlib.util.spec_from_file_location(
            "wnn_bodies",
            REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        caught = [k for k, v in mod.bodies().items() if WNN._residue_is_his(v)]
        assert caught, ("no entry in the whole task list states a residue that "
                        "is his, so this predicate is asserting on nothing")


def _top_level_clauses(pattern: str) -> list[str]:
    """The predicate's own alternatives, DERIVED from its compiled pattern.

    ★ DERIVED, NEVER LISTED. A hand-kept copy of the clause list in a test is a
    second declaration of the same thing, and this project's record is that 2
    declarations drift and the test then agrees with itself. The verbose
    comments are stripped and the split is at `|` tokens outside parentheses, so
    a clause added to the hook appears here on the next run with no edit.
    """
    clean = re.sub(r"(?m)#:?.*$", "", pattern).strip()
    assert clean.startswith("(") and clean.endswith(")"), clean[:80]
    inner, depth, cur, parts = clean[1:-1], 0, "", []
    for ch in inner:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "|" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


#: One probe per clause, each written to match THAT clause and no other. A probe
#: matching 2 clauses is why a mutation SURVIVED on the day this guard shipped:
#: the B56 string carried both "IS STILL HIS AUTHORISATION" and "OWN RESIDUE IS
#: UNCHANGED", so deleting either clause left the other matching and the harness
#: reported a redundancy as full coverage.
_ISOLATING_PROBES = (
    "the wiring is still his authorisation",
    "its own residue is unchanged by tonight's work",
    "that is for the founder to authorise",
    "this is his and not mine",
    "amending it would widen his own scope for him",
    "it needs his permission first",
    "the threshold is his to authorise",
    #: ★ CHANGED 2026-11-12 TO A DEFINITE OBJECT. This read "only he may
    #: reject a feature request", and that sentence NO LONGER MATCHES, by
    #: design: the clause was narrowed under B169 because it was reading
    #: B168's record of his rule about feature requests IN GENERAL as a
    #: claim on that entry. A probe must isolate the clause by its real
    #: meaning -- his authority over THIS item -- so the object is now
    #: definite. The indefinite form is asserted NOT to match, in
    #: `TestTheClassStatementIsNotAClaim` below.
    "only he may approve this particular change",
    "that is a behaviour change for the founder",
    "the design consequence is his",
    "it is held under his d",
)

#: Clause 4 is clause 5 with a `wh(y|ich)` prefix, so under `re.search` every
#: string matching 4 contains a factor matching 5 and no probe can isolate it.
#: Asserted below rather than excused: 112,500 strings over a bounded generated
#: language give 0 matching 4 but not 5, and 25,000 matching 5 but not 4, so the
#: containment is strict and clause 4 can never be the deciding clause.
_SUBSUMED = {r"wh(y|ich)\s+this\s+is\s+his\s+and\s+not\s+mine":
             r"this\s+is\s+his\s+and\s+not\s+mine"}


class TestEveryClauseIsUniquelyReached:
    """★ THIS CLASS CLOSED A SURVIVING MUTATION, and the mutation found it.

    `scripts/the_permission_predicate_mutations_2026-11-12.py` removes each
    clause and requires this file to go red. On the first run the B56
    authorisation clause SURVIVED -- not because the clause is wrong, but
    because the only probe exercising it also matched a sibling clause. A clause
    no test reaches uniquely is an addition nothing reaches, which this
    project's additive standard forbids in its symmetric form.
    """

    def test_every_probe_matches_the_predicate(self, WNN):
        for probe in _ISOLATING_PROBES:
            assert WNN._residue_is_his(probe), probe

    def test_every_probe_isolates_exactly_one_clause(self, WNN):
        clauses = _top_level_clauses(WNN._HIS_RESIDUE.pattern)
        compiled = [(c, re.compile(c, re.I)) for c in clauses]
        for probe in _ISOLATING_PROBES:
            hit = [c for c, rx in compiled if rx.search(probe)]
            hit = [c for c in hit if c not in _SUBSUMED]
            assert len(hit) == 1, (
                f"probe {probe!r} matches {len(hit)} clauses ({hit}); a probe "
                f"matching more than one cannot kill either when it is removed")

    def test_every_clause_has_a_probe_or_is_provably_subsumed(self, WNN):
        clauses = _top_level_clauses(WNN._HIS_RESIDUE.pattern)
        unreached = []
        for c in clauses:
            if c in _SUBSUMED:
                continue
            rx = re.compile(c, re.I)
            if not any(rx.search(p) for p in _ISOLATING_PROBES):
                unreached.append(c)
        assert not unreached, (
            "these clauses are reached by no probe, so removing any of them "
            f"leaves this guard green: {unreached}")

    def test_the_subsumed_clause_really_is_subsumed(self, WNN):
        """A declared subsumption is a claim and is checked, not taken on trust.
        Exhaustive over a bounded generated language, and the bound is stated:
        9 prefixes x 5 separators^5 x 4 suffixes = 112,500 strings."""
        import itertools
        for sub, sup in _SUBSUMED.items():
            rx_sub = re.compile(sub, re.I)
            rx_sup = re.compile(sup, re.I)
            pre = ["", "why ", "which ", "WHY  ", "but why\t", "xwhy ",
                   "whythis ", "and why\n", "Why\t\t"]
            mid = [" ", "  ", "\t", "\n", " \t "]
            suf = ["", " suffix", ".", "\n"]
            n = sub_only = sup_only = 0
            for p in pre:
                for ms in itertools.product(mid, repeat=5):
                    for s in suf:
                        cand = (f"lead {p}this{ms[0]}is{ms[1]}his{ms[2]}and"
                                f"{ms[3]}not{ms[4]}mine{s}")
                        n += 1
                        a, b = bool(rx_sub.search(cand)), bool(rx_sup.search(cand))
                        if a and not b:
                            sub_only += 1
                        elif b and not a:
                            sup_only += 1
            assert n == 112500, n
            assert sub_only == 0, (
                f"{sub_only} of {n} strings match {sub!r} but not {sup!r}, so "
                f"the declared subsumption is false and the clause is live")
            assert sup_only > 0, (
                f"no string matches {sup!r} without {sub!r}, so the containment "
                f"is not strict and the 2 clauses are the same clause")


class TestTheClassStatementIsNotAClaim:
    """★ B169. A sentence reporting his authority over a KIND of thing is not a
    sentence claiming this entry.

    THE DEFECT: `only he (may|can)` matched B168's own record of his
    2026-10-17 rule -- that a feature request stays open until implemented,
    merged or rejected, and that only he may reject one -- and so classified
    that entry as needing his permission when it is mine to build. The
    direction is the harmful one: a false positive moves an item OFF the
    movable set, so the gate goes quiet about work the session can do, which is
    the inverse of the fault the predicate was installed to fix.

    ★ 2 OF MY OWN ATTEMPTS AT THIS FIX WERE WORSE THAN THE DEFECT, AND BOTH ARE
    PINNED HERE AS CASES. The first excused any sentence "citing a rule", and
    driven over the live entries it wrongly excused B170 by matching ACROSS A
    BRACKET in "[NEEDS HIS RULING] ON THE MERGE, which is" -- silencing his own
    merge decision. The second checked only the FIRST match in a sentence, so a
    class statement earlier in a chunk excused a genuine residue later in it.
    Both were caught by driving the predicate over the live task list before
    anything was applied.
    """

    def test_an_indefinite_object_means_a_class_and_is_not_a_residue(self, WNN):
        for s in ("only he may reject a feature request",
                  "only he may REJECT one",
                  "only he can withdraw any entry"):
            assert not WNN._residue_is_his(s), s

    def test_a_definite_object_is_still_a_residue(self, WNN):
        """THE DISCRIMINATION HALF. Without this the narrowing could have
        disabled the clause entirely and this file would not have noticed."""
        for s in ("only he may approve this particular change",
                  "only he can authorise the merge",
                  "only he may rule on that threshold"):
            assert WNN._residue_is_his(s), s

    def test_a_mixed_sentence_keeps_its_GENUINE_residue(self, WNN):
        """★ THE CASE THAT KILLED MY SECOND ATTEMPT. A class statement and a
        real residue in one sentence must resolve to RESIDUE."""
        assert WNN._residue_is_his(
            "only he may reject one, but this entry NEEDS HIS PERMISSION too")

    def test_the_bracketed_ruling_that_my_first_attempt_silenced(self, WNN):
        """★ B170's own words. My first fix excused this and it is the single
        most consequential residue in the queue."""
        assert WNN._residue_is_his(
            "[NEEDS HIS RULING] ON THE MERGE, which is not mine to take.")

    def test_no_other_clause_was_narrowed(self, WNN):
        """The narrowing is surgical: every other clause still fires."""
        for s in ("the wiring is still his authorisation",
                  "its own residue is unchanged",
                  "that is for the founder to authorise",
                  "this is his and not mine",
                  "amending it would widen his own scope",
                  "it needs his permission first",
                  "the threshold is his to authorise",
                  "that is a behaviour change for the founder",
                  "the design consequence is his",
                  "it is held under his d"):
            assert WNN._residue_is_his(s), s
