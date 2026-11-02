"""The blocker predicate must answer HIS question, and must be able to say both.

Founder criterion, verbatim, 2026-09-10: *"My criteria is very simple. Does it
prevent further progress on the task list? If so, then yes, it's a blocker. If
not, then append to the closing/final report."*

THE FIRST VERSION ANSWERED A DIFFERENT QUESTION. It used 4 category rules --
IRREVERSIBLE, NEEDS_HIS_HANDS, FROZEN_ARTEFACT, WOULD_WASTE_WORK -- and 3 of them
say nothing about progress. It called editing his desktop config a BLOCK when
that edit blocked nothing, and reported `sk_enabled` to him as a blocker when no
entry waited on it. Two orthogonal questions had been folded into one:

    does it stop progress?   -> blocker    -> raise it now
    is it his to authorise?  -> permission -> park it, and do not do it

MEASURED ACCURACY, stated rather than claimed: 9 of 9 on the labelled set below,
Wilson [70.0855%, 100.0000%], Clopper-Pearson [66.3733%, 100.0000%], statsmodels
and scipy agreeing to 0.0e+00.

RE-LABELLED 2026-09-17, AND THE DENOMINATOR WAS WRONG BEFORE THAT. The previous
line read "9 of 10" over a set holding 9 items -- a stated denominator that never
matched the set it described, predating this re-labelling.

I23 AND I31 MOVED FROM True TO False BECAUSE THE WORLD CHANGED, NOT THE TOOL.
Both were genuine blockers when labelled: entries declared dependence on them.
The founder ruled on both on 2026-09-16, the valve threshold was set to 6 and the
drift detector was wired, and A11 closed -- so nothing on the list waits on
either now. The labels are judgements made against the task list and then
compared with the predicate, never read off it; setting a ground truth from the
tool's own output would make this measurement circular.

EVERY LABEL IS NOW False, WHICH IS ITSELF INFORMATION: the backlog holds no item
that stops progress. It also means this set can no longer demonstrate a BLOCK
verdict, so `test_it_can_say_BLOCK` uses a synthetic fixture rather than a live
item -- an anti-vacuity check pointed at real state breaks every time that state
is resolved, which is exactly what happened here.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "blocker_triage.py"


@pytest.fixture(scope="module")
def B():
    spec = importlib.util.spec_from_file_location("triage", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


LABELLED = [
    # Both were True until 2026-09-16. The founder ruled, the valve was set to 6
    # and the detector wired, so no entry waits on either -- judged against the
    # list, not read from the predicate.
    # ★ RELABELLED False -> True, 2026-11-02, AND THE RECORD MOVED RATHER THAN
    # THE PREDICATE. This label was written 2026-09-10, when B21 named
    # `max_rounds` but declared no dependency. Commit 9a5c06aa added
    # `[NEEDS YOUR RULING]` to B21, which already discussed `max_rounds` twice --
    # "2 sources of truth for `max_rounds` disagree with every experiment ever
    # run" -- so an item about `max_rounds` defaulting wrongly now GENUINELY
    # waits on B21's ruling. Bisected across a59fc3ac, cf215aa8, 0414d6f9,
    # c1ea2443 and 9a5c06aa: PARK at the first 4 and BLOCK at the 5th. HEAD's
    # UNEDITED tool reproduces it, so the 2 repairs made to `blocker_triage.py`
    # the same evening are NOT the cause.
    #
    # THIS IS A RELABEL BECAUSE THE SUBJECT CHANGED, NOT A TEST BENT TO MATCH
    # CODE, and the distinction is checkable: the predicate is byte-identical at
    # 9a5c06aa and the task list is not.
    #
    # ★ AND IT WENT UNNOTICED FOR 5 COMMITS BECAUSE THIS FILE IS OUTSIDE THE
    # COMMIT GATE. `hooks/pre-commit`'s guard list holds 120 files and this is
    # not 1 of them, so 21 tests that exist to keep the triage tool honest are
    # never run by the mechanism that refuses a red commit. That is the
    # "a guard nothing reaches" half of the additive standard, applied to a
    # guard rather than to a feature. Putting it in the gate raises the gate's
    # cost, which is entry B81's subject and his decision, so it is recorded
    # here and not done unilaterally.
    ("I23: exhausted_round_threshold defaults to 8 while max_rounds is 8", True),
    ("I31: update_drift has no production caller, wire it or retire it", False),
    ("sk_enabled is false in the exp56 arms", False),
    ("bench/reference_runner_v3.py has a stale line citation", False),
    ("scripts/note_vagueness_lint.py has a quote-scope defect", False),
    ("hardened_gate_enabled has no recorded reason", False),
    ("The verdict-tuple guard matches names across the repository", False),
    ("Repair the experimental notes for reproducibility", False),
    ("bench/panel_sandbox.py loses its tree mid-review", False),
]


class TestItAnswersTheRightQuestion:
    @pytest.mark.parametrize("text,expect", LABELLED)
    def test_the_labelled_set(self, B, text, expect):
        got, why = B.blocks_progress(text)
        assert got is expect, f"{text!r}: {why}"

    def test_it_can_say_BLOCK(self, B, tmp_path):
        """A predicate that can only park is a guard that cannot fail.

        FIXTURE, NOT A LIVE ITEM (2026-09-17). This pointed at I23 on the real
        task list, so when the founder ruled on I23 and nothing waited on it any
        more, the anti-vacuity check went red -- reporting a cleared backlog as
        a broken predicate. An anti-vacuity test must depend on its own fixture,
        never on the state it happens to be surrounded by.
        """
        tasks = tmp_path / "LIST.md"
        tasks.write_text(
            "**Q9.** Rebuild the widget pipeline. BLOCKED ON the "
            "`frobnicate_threshold` ruling; it cannot proceed until that is "
            "settled.\n"
            "<!-- task: Q9 | state: BLOCKED | status: PROPOSED -->\n"
            "**Q8.** Something unrelated entirely.\n"
            "<!-- task: Q8 | state: DONE | status: COMMITTED -->\n",
            encoding="utf-8")
        got, why = B.blocks_progress("frobnicate_threshold needs a ruling",
                                     tasks=tasks)
        assert got is True, why

    def test_the_block_fixture_is_not_vacuous(self, B, tmp_path):
        """CONTROL on the control: the same fixture without the dependency must
        NOT block, or the test above would pass on any input at all."""
        tasks = tmp_path / "LIST.md"
        tasks.write_text(
            "**Q9.** Rebuild the widget pipeline. Mentions "
            "`frobnicate_threshold` in passing and waits on nothing.\n"
            "<!-- task: Q9 | state: OPEN | status: PROPOSED -->\n",
            encoding="utf-8")
        got, why = B.blocks_progress("frobnicate_threshold needs a ruling",
                                     tasks=tasks)
        assert got is False, why

    def test_it_can_say_PARK(self, B):
        got, _ = B.blocks_progress("sk_enabled is false in the exp56 arms")
        assert got is False


class TestPermissionIsSeparateFromBlocking:
    def test_an_irreversible_item_that_blocks_nothing_still_parks(self, B):
        verdict, why, perm = B.classify("Spend money on a paid seat for round 8")
        assert verdict == "PARK", why
        assert perm.startswith("IRREVERSIBLE"), (
            "the permission gate must still fire; it stops the ACTION, not the work")

    def test_a_harmless_item_carries_no_permission_flag(self, B):
        _, _, perm = B.classify("The verdict-tuple guard matches names across the repo")
        assert perm == ""

    def test_the_two_are_returned_separately(self, B):
        """Folding them is the defect the first version shipped."""
        out = B.classify("Delete the exp39-experimental git ref")
        assert len(out) == 3, "classify must return (verdict, why, permission)"


class TestThePaidGateMatchesTheWordsItIntends:
    """★ ADDED 2026-10-30. The gate missed the plainest phrasing of the act.

    HIS RULING: *"This is declined. No paid dispatch can happen without my
    express authorisation."* Measured by calling `classify` rather than by
    reading the pattern: `"Dispatch the paid panel to 4 seats for this round."`
    returned NO permission flag, while the same sentence with "paid dispatch"
    was caught. The IRREVERSIBLE pattern required `paid` to be followed by one
    of exactly 4 nouns -- seat, dispatch, model, run -- so whether the gate
    fired depended on which noun the sentence used for the same act.

    A paid panel IS a paid dispatch, so this widens an existing category rather
    than inventing one. The negative cases are load-bearing: a FREE panel and an
    ordinary mention of a panel must still pass, or the gate becomes the
    interruption it was built to prevent.
    """

    @pytest.mark.parametrize("text", [
        "Dispatch the paid panel to 4 seats for this round.",
        "Run a paid review of the maths model.",
        "A paid dispatch to the Gemini seat.",
        "Start the paid experiment arm.",
        "Authorise the paid seat for round 3.",
    ])
    def test_a_paid_act_needs_permission_however_it_is_worded(self, B, text):
        _, _, reason = B.classify(text)
        assert reason, (
            f"no permission flag for {text!r}. His decline covers the ACT, not "
            f"a particular noun for it")

    @pytest.mark.parametrize("text", [
        "Dispatch the free panel on his brief.",
        "The panel reviewed the brief and returned 3 verdicts.",
        "Rewrite the paragraph about convergence.",
    ])
    def test_an_unpaid_act_is_not_flagged(self, B, text):
        """THE CONTROL. Without it, flagging everything would pass the above."""
        _, _, reason = B.classify(text)
        assert not reason, (
            f"{text!r} was flagged as needing permission. Whether a FREE "
            f"dispatch should need it is a 4th category and the founder's to "
            f"rule on; it must not arrive by a widened pattern")


class TestItCannotBeTrickedByACommonTerm:
    def test_a_file_named_by_many_entries_is_not_a_dependency(self, B):
        """`reference_runner_v3.py` is central to the project. Naming it says
        what work is ABOUT, not what it waits on."""
        got, why = B.blocks_progress("bench/reference_runner_v3.py has a typo")
        assert got is False, why

    def test_an_ordinary_capitalised_word_is_not_a_subject(self, B):
        """An earlier filter matched entry 7.1 on the word 'Repair'."""
        got, why = B.blocks_progress("Repair the experimental notes")
        assert got is False, why


class TestTheParkingFileIsRealAndAppendOnly:
    def test_parking_appends_rather_than_rewrites(self, B, tmp_path, monkeypatch):
        f = tmp_path / "PARKED.md"
        monkeypatch.setattr(B, "PARKED", f)
        B.park("first item", "detail one", stamp="2026-09-10T00:00:00+01:00")
        B.park("second item", "detail two", stamp="2026-09-10T00:00:01+01:00")
        text = f.read_text(encoding="utf-8")
        assert "first item" in text and "second item" in text, (
            "parking must never overwrite what is already queued for him")
        assert text.index("first item") < text.index("second item"), "newest last"

class TestParkingIsIdempotent:
    """A queue that grows a heading on every re-triage inflates the workload.

    MEASURED 2026-09-11, minutes after the founder asked whether the workload set
    out for him was significant. Two duplicate headings had just been merged by
    hand -- one decision written twice as an analysis and a triage stub, and an
    A8 question superseded by a smaller one -- and re-running the triage
    immediately appended a THIRD A8 heading. The count of DECISIONS was growing
    with copies of one decision, which is the opposite of what the file is for.
    """

    def test_an_already_parked_item_is_not_appended_again(self, B, tmp_path,
                                                          monkeypatch):
        parked = tmp_path / "PARKED.md"
        monkeypatch.setattr(B, "PARKED", parked)
        first = B.park("A8: re-point 20 citations, or leave them", "detail")
        assert first is not None
        again = B.park("A8: re-point 20 citations, or leave them", "detail")
        assert again is None, "the same title was parked twice"
        assert parked.read_text(encoding="utf-8").count("## A8") == 1

    def test_a_wording_difference_is_not_a_new_decision(self, B, tmp_path,
                                                        monkeypatch):
        """The pair this was found on differed by the word "the"."""
        parked = tmp_path / "PARKED.md"
        monkeypatch.setattr(B, "PARKED", parked)
        B.park("A8: re-point 20 note citations, or leave them", "detail")
        again = B.park("A8: re-point the 20 note citations, or leave them", "detail")
        assert again is None, "one question parked twice over one article"

    def test_a_status_note_on_a_heading_is_not_a_new_decision(self, B, tmp_path,
                                                              monkeypatch):
        """Headings in that file gain notes such as "SUPERSEDED" after an em
        dash; a heading that gained a note is still the same item."""
        parked = tmp_path / "PARKED.md"
        monkeypatch.setattr(B, "PARKED", parked)
        B.park("10.2: should the shell service be on — SAME AS THE STUB BELOW", "d")
        again = B.park("10.2: should the shell service be on", "d")
        assert again is None

    def test_a_genuinely_different_item_is_still_parked(self, B, tmp_path,
                                                        monkeypatch):
        """ANTI-VACUITY. A check that refused everything would silently drop new
        decisions, which is far worse than listing one twice."""
        parked = tmp_path / "PARKED.md"
        monkeypatch.setattr(B, "PARKED", parked)
        B.park("A8: re-point 20 citations, or leave them", "detail")
        other = B.park("A19: enable the prose-listing flag, or leave it off", "detail")
        assert other is not None, "a new decision was refused"
        assert parked.read_text(encoding="utf-8").count("## ") == 2


class TestTheThirdQuestionIsAnswered:
    """ADDED 2026-10-12. The script answered 2 of the 3 questions its own header names.

    Both free seats of the 2026-10-12 panel found this independently and
    neither wrote the fix. The cost was concrete: A8's committed text ends
    "NEEDS A POLICY RULING: track them, relocate them, or accept and label
    them", it triaged as a bare PARK, and `hooks/work_not_narrate.py` reads
    PARK as "carry on" -- so the hook pushed the assistant to DO a thing the
    entry itself says is the founder's to decide.
    """

    def test_an_entry_that_declares_a_policy_ruling_is_flagged(self, B):
        got = B.decision_required(
            "A8 orphan clones: track them, relocate them, or accept and "
            "label them. NEEDS A POLICY RULING")
        assert got, "the entry declares itself a decision and was not flagged"

    def test_the_other_declaring_forms_are_caught(self, B):
        for text in ("NEEDS YOUR RULING on the flag",
                     "NEEDS HIS RULING before the run",
                     "that is his call to make, not ours",
                     "awaiting the founder's ruling"):
            assert B.decision_required(text), text

    def test_an_ordinary_item_is_NOT_flagged(self, B):
        """The guard against a predicate that flags everything."""
        for text in ("sk_enabled is false in the exp56 arms",
                     "wire the 3 orphan scripts to a caller",
                     "the docstring is stale and says severity >= threshold"):
            assert B.decision_required(text) == "", text

    def test_it_is_a_THIRD_FLAG_and_not_a_third_verdict(self, B):
        """Folding the questions together is the defect the first version shipped."""
        text = "A8 orphan clones. NEEDS A POLICY RULING"
        verdict, why, perm = B.classify(text)
        assert verdict == "PARK", (
            "a decision is not a blocker; nothing on the list waits on it")
        assert B.decision_required(text), "and it must still carry the flag"

    def test_classify_still_returns_exactly_three(self, B):
        """A shape change here would break every caller silently."""
        out = B.classify("anything at all")
        assert isinstance(out, tuple) and len(out) == 3


class TestABareWordCannotDeclareADependency:
    """The word `precondition` alone must not make an entry block.

    THE DEFECT, 2026-11-02, AND THE TOOL HAD BECOME WHAT ITS OWN DOCSTRING
    WARNS AGAINST. `DECLARES` listed `precondition` as a bare alternative, so a
    sentence DISCUSSING a precondition declared one. B20 gained the sentence
    "concluded the precondition held" that evening and the tool returned BLOCK
    on an entry that declares no dependency at all -- while B20 at the previous
    commit matched the pattern 0 times. The docstring's own standard: "Anything
    looser reports a mention as an obstruction, which is how a triage tool
    becomes the interruption it was built to prevent."

    MEASURED BEFORE NARROWING, so the repair is not a guess: of the OPEN and
    BLOCKED entries on the live list, 2 use the word (B20 and B77) and 0 use it
    in a declaring construction. Narrowing therefore loses 0 detections and
    removes 2 false-positive sources.

    EVERY TEST HERE BUILDS ITS OWN LIST, for the reason the file already
    records: an anti-vacuity test that points at a live entry goes red when the
    founder rules on that entry, reporting a cleared backlog as a broken
    predicate.
    """

    TERM = "acting_loop_pause"

    def _list(self, tmp_path, body: str, state: str = "OPEN"):
        p = tmp_path / "LIST.md"
        p.write_text(f"**Q9.** {body}\n"
                     f"<!-- task: Q9 | state: {state} | status: PROPOSED -->\n",
                     encoding="utf-8")
        return p

    def test_the_bare_word_does_NOT_block(self, B, tmp_path):
        tasks = self._list(
            tmp_path,
            f"Traced `{self.TERM}` and concluded the precondition held, which "
            f"the P-pass then refuted. Nothing waits on it.")
        got, why = B.blocks_progress(f"{self.TERM} needs a decision", tasks=tasks)
        assert got is False, (
            f"a sentence DISCUSSING a precondition was read as declaring one: {why}")

    def test_a_DECLARING_construction_still_blocks(self, B, tmp_path):
        """ANTI-VACUITY. Without this, deleting the word entirely would satisfy
        the test above, and the capability would be removed rather than narrowed.
        """
        for phrasing in (f"`{self.TERM}` is a precondition and nothing can proceed "
                         f"until it is settled.",
                         f"This is BLOCKED ON `{self.TERM}` and cannot proceed.",
                         f"Preconditions: `{self.TERM}` must be settled first."):
            tasks = self._list(tmp_path, phrasing, state="BLOCKED")
            got, why = B.blocks_progress(f"{self.TERM} needs a decision",
                                         tasks=tasks)
            assert got is True, f"{phrasing!r} should declare a dependency: {why}"

    def test_the_narrowed_forms_are_matched_on_an_OPEN_entry_too(self, B, tmp_path):
        """A BLOCKED state short-circuits the pattern, so the declaring forms
        must be shown to work where the state does NOT already say it."""
        tasks = self._list(
            tmp_path,
            f"A single registration point is a precondition for `{self.TERM}`, "
            f"so this cannot proceed. It also needs a non-path identifier to "
            f"match, which `{self.TERM}` supplies.")
        got, why = B.blocks_progress(f"{self.TERM} needs a decision", tasks=tasks)
        assert got is True, f"a declaring form on an OPEN entry must block: {why}"

    def test_the_other_declaring_phrases_are_untouched(self, B, tmp_path):
        """The narrowing must not have disturbed the alternatives beside it."""
        for phrasing in (f"`{self.TERM}` is the founder's call.",
                         f"This awaits his ruling on `{self.TERM}`.",
                         f"`{self.TERM}` is reserved to him.",
                         f"NEEDS YOUR RULING on `{self.TERM}`."):
            tasks = self._list(tmp_path, phrasing)
            got, why = B.blocks_progress(f"{self.TERM} needs a decision",
                                         tasks=tasks)
            assert got is True, f"{phrasing!r} must still declare: {why}"
