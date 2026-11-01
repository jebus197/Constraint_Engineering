"""v1.9's 2 enforceable rules must FIRE, and must not fire where he excluded them.

HIS INSTRUCTION, 2026-11-01: the format he endorsed on 2026-10-30 was to be
written into the standard *"so there is no future confusion, and no temptation
to again revert"*. v1.8's own substance was a CHECK rather than a restatement,
for the same reason, and this file is v1.9's.

WHY A GUARD AND NOT A PARAGRAPH. The rule being formalised was already written
down -- `feedback_the_report_format_he_endorsed_2026-10-30` states "Never an
identifier without its subject named in the same breath" -- and it was abandoned
anyway. A rule restated for the 3rd time and enforced by nothing is the
addition-reaching-nothing defect this project has confirmed 11 times.

THE SCOPE IS HIS AND THE TESTS HOLD BOTH HALVES: *"scoped to the documents you
read and binding going forward only"*. Unscoped the rule fires on 412 of 1,187
notes for 2,328 findings, worst on the master task list (119, where it is
circular because that file IS the dictionary) and on verbatim panel transcripts
(49, 45, 44, 40) which may not be edited at all. So the exclusions are tested as
hard as the inclusions.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))

import note_vagueness_lint as NVL  # noqa: E402


BARE = "BARE ENTRY CODE"
NOREC = "DECISIONS WITHOUT RECOMMENDATIONS"
NOSTD = "RECOMMENDATIONS NAME NO PROJECT STANDARD"
FOOT = "\n\nWritten under CDSFL note standard v1.9 (1 November 2026).\n"


def kinds(path: pathlib.Path) -> set[str]:
    counted, _ = NVL.partition(path)
    return {h[1].split(" (")[0] for h in counted}


@pytest.fixture(autouse=True)
def _clean_logical_path():
    NVL._LOGICAL_PATH = None
    yield
    NVL._LOGICAL_PATH = None


def _write(tmp_path: pathlib.Path, name: str, body: str) -> pathlib.Path:
    f = tmp_path / name
    f.write_text(body + FOOT, encoding="utf-8")
    NVL._LOGICAL_PATH = f"experimental_notes/{name}"
    return f


class TestTheVersionIsCurrentAndTheOldOneIsGrandfathered:
    def test_current_is_v19(self):
        assert NVL.CURRENT_NOTE_STANDARD == "v1.9"

    def test_v18_is_archival_so_existing_notes_stay_compliant(self):
        """191-plus notes carry an earlier stamp and every one is correct. A bump
        that made them wrong would be the retroactive editing he refused."""
        assert "v1.8" in NVL.ARCHIVAL_NOTE_STANDARDS
        for v in ("v1.4", "v1.6", "v1.7"):
            assert v in NVL.ARCHIVAL_NOTE_STANDARDS


class TestTheSubjectDictionaryComesFromTitles:
    def test_it_is_populated(self):
        d = NVL.entry_subjects()
        assert len(d) > 100, f"only {len(d)} identifiers carry a subject"

    def test_a_title_word_is_present_and_a_body_only_word_is_not(self):
        """ANTI-VACUITY WITH TEETH. Reading the whole entry BODY instead of its
        title gave B21 a subject set containing 'added', 'absent' and
        'accepted' -- words that sit near any identifier, so the rule would
        have passed on anything. The subject must be the TITLE."""
        subj = NVL.entry_subjects().get("B21")
        assert subj, "B21 has no subject words"
        assert "selection" in subj, sorted(subj)
        assert "added" not in subj, (
            "the subject set is reading the entry BODY, not its title, which "
            "makes the rule satisfiable by any nearby prose")


class TestRule32Fires:
    def test_a_bare_identifier_is_caught(self, tmp_path):
        f = _write(tmp_path, "Morning_Report_2026-11-01.txt",
                   "Entry B21 carries a ruling of yours dated 17 October.")
        assert BARE in kinds(f)

    def test_naming_the_subject_in_the_same_sentence_satisfies_it(self, tmp_path):
        f = _write(tmp_path, "Morning_Report_2026-11-01.txt",
                   "Entry B21, making model and role selection trivial, "
                   "carries a ruling of yours dated 17 October.")
        assert BARE not in kinds(f)

    def test_a_quoted_identifier_is_not_accused(self, tmp_path):
        """His words and a seat's words reach these files unedited."""
        f = _write(tmp_path, "Morning_Report_2026-11-01.txt",
                   'He wrote: "you should not simply print issue IDs like B21".')
        assert BARE not in kinds(f)


class TestRule32RespectsHisScope:
    def test_the_master_task_list_is_excluded_because_it_is_the_dictionary(self, tmp_path):
        f = tmp_path / "CDSFL_MASTER_TASK_LIST.md"
        f.write_text("Entry B21 carries a ruling of yours." + FOOT, encoding="utf-8")
        NVL._LOGICAL_PATH = "experimental_notes/CDSFL_MASTER_TASK_LIST.md"
        assert BARE not in kinds(f)

    def test_a_verbatim_panel_transcript_is_excluded(self, tmp_path):
        f = tmp_path / "Panel_Round5_FULL_RECORD_2026-09-10.md"
        f.write_text("Entry B21 carries a ruling of yours." + FOOT, encoding="utf-8")
        NVL._LOGICAL_PATH = "experimental_notes/Panel_Round5_FULL_RECORD_2026-09-10.md"
        assert BARE not in kinds(f)

    def test_a_document_he_is_not_delivered_is_excluded(self, tmp_path):
        f = tmp_path / "Exp29_Convergence_Analysis_2026-04-04.md"
        f.write_text("Entry B21 carries a ruling of yours." + FOOT, encoding="utf-8")
        NVL._LOGICAL_PATH = "experimental_notes/Exp29_Convergence_Analysis_2026-04-04.md"
        assert BARE not in kinds(f)

    def test_the_date_gate_exists_and_names_his_ruling_date(self):
        assert NVL.RULE_32_FROM == "2026-11-01"

    def test_an_archive_dated_note_is_not_held_to_it(self):
        """A real committed note from before his ruling must not be accused.

        NOT SKIPPABLE. The first version of this test named a file that lives
        only in the Desktop folder, so it skipped -- and a skipped test proves
        nothing about the single most important half of his scope. It now picks
        whatever committed delivered note the checkout actually has, and FAILS
        if there is none, rather than passing quietly on an absence.
        """
        notes = sorted((REPO / "experimental_notes").glob("Morning_Report_2026-0*.md"))
        dated = [(n, NVL.note_first_seen(n)) for n in notes]
        older = [(n, d) for n, d in dated if d and d < NVL.RULE_32_FROM]
        assert older, (
            "no committed delivered note predates his ruling in this checkout, "
            "so the date gate is untested -- do not let this pass on an absence")
        for n, d in older[:5]:
            NVL._LOGICAL_PATH = str(n.relative_to(REPO))
            assert not NVL.rule_32_applies(n), f"{n.name} (first seen {d})"

    def test_a_note_dated_from_his_ruling_IS_held_to_it(self):
        """The other side of the gate: without this, a gate that refuses
        everything would pass the test above."""
        now = REPO / "experimental_notes" / "Morning_Report_2026-11-01.txt"
        if not now.is_file():
            pytest.skip("today's report is absent from this checkout")
        NVL._LOGICAL_PATH = str(now.relative_to(REPO))
        assert NVL.rule_32_applies(now)


class TestRule33Fires:
    DECS = ("PART 7. WHAT NEEDS YOUR VERDICT\n\n"
            "1. THE FIRST THING. It does something.\n\n"
            "2. THE SECOND THING. It does something else.\n\n")

    def test_decisions_without_recommendations_are_caught(self, tmp_path):
        f = _write(tmp_path, "Decisions_Awaiting_You_2026-11-01.txt", self.DECS)
        assert NOREC in kinds(f)

    def test_recommendations_naming_no_standard_are_caught(self, tmp_path):
        f = _write(tmp_path, "Decisions_Awaiting_You_2026-11-01.txt",
                   self.DECS.replace("It does something.",
                                     "My recommendation is to do it.")
                            .replace("It does something else.",
                                     "My recommendation is to leave it."))
        assert NOSTD in kinds(f)

    def test_a_compliant_decisions_section_is_clean(self, tmp_path):
        """ANTI-VACUITY. If this fired too, the rule would be refusing
        everything and the tests above would prove nothing."""
        f = _write(tmp_path, "Decisions_Awaiting_You_2026-11-01.txt",
                   "PART 7. WHAT NEEDS YOUR VERDICT\n\n"
                   "1. THE FIRST THING. My recommendation is to do it, as the "
                   "simplest sufficient fix.\n\n"
                   "2. THE SECOND THING. My recommendation is to leave it, "
                   "since it is additive as it stands.\n\n")
        k = kinds(f)
        assert NOREC not in k and NOSTD not in k, k


class TestRule34IsStatedAndNotClaimedAsEnforced:
    def test_no_over_narration_check_exists(self):
        """Honesty about reach. Every proxy considered would accuse correct
        prose, so Rule 34 is a judgement and must not be presented as checked."""
        src = (SCRIPTS / "note_vagueness_lint.py").read_text(encoding="utf-8")
        assert "OVER-NARRATION" not in src.upper().replace("AVOID OVER-NARRATION", ""), (
            "a Rule 34 checker has appeared; if it is real, update the standard "
            "and this test rather than leaving the standard claiming it is unenforced")


class TestRule33CannotPassOnAnEmptyWindow:
    """★ THE CHECK THAT WOULD HAVE CAUGHT 2 DEFECTS IN RULE 33 ITSELF.

    On 2026-11-01, the first real document judged by Rule 33 reported 0
    findings while measuring NOTHING. Two faults, and both returned 0 rather
    than failing:

      * `_DECISION_SECTION` listed the decisions file's own TITLE, so the search
        anchored on line 1 and the next `PART` heading closed the window 2 lines
        later. The scan found 0 numbered items, and `if items and recs < items`
        is False when items is 0.
      * `_NUMBERED_ITEM` knew only a bare `3.` and not the `DECISION 3.` form
        the file actually uses, so even a correctly anchored window scored 0.

    EVERY FIXTURE-BASED TEST IN THIS FILE PASSED THROUGHOUT, because the
    fixtures use the bare form and a 2-line document. A rule that returns 0 on
    an empty window is indistinguishable from a rule that returns 0 on a
    compliant document, and only driving it over a REAL delivered file told them
    apart. So this class asserts NON-VACUITY against whatever decisions file the
    checkout holds, and fails rather than skipping when there is none.
    """

    def _delivered(self):
        cands = sorted((REPO / "experimental_notes").glob("Decisions_*.txt"))
        return [c for c in cands if NVL._DECISION_SECTION.search(
            c.read_text(errors="ignore"))]

    def test_a_real_decisions_file_exists_to_test_against(self):
        got = self._delivered()
        assert got, (
            "no delivered decisions file carries a section Rule 33 recognises, "
            "so this class cannot establish non-vacuity — do not let it pass "
            "on an absence")

    def test_rule_33_finds_real_numbered_decisions_in_it(self):
        """THE NON-VACUITY ASSERTION. If the window is empty this fails, where
        the rule itself would silently report no findings."""
        import re as _re
        for f in self._delivered():
            text = f.read_text(errors="ignore")
            NVL._LOGICAL_PATH = str(f)
            hits = list(NVL._DECISION_SECTION.finditer(text))
            sect = text[hits[-1].end():]
            nxt = _re.search(r"^(?:#+\s*)?(?:PART\s+\d+)[.:]", sect, _re.M)
            if nxt:
                sect = sect[:nxt.start()]
            items = set(NVL._NUMBERED_ITEM.findall(sect))
            assert items, (
                f"{f.name}: Rule 33's window holds 0 numbered decisions, so its "
                f"verdict on this file is vacuous. Either the section anchor is "
                f"matching a title instead of the section, or the item pattern "
                f"does not know the form this file uses.")

    def test_the_anchor_prefers_the_section_over_an_earlier_mention(self):
        """The specific repair: the LAST match, not the first. A document may
        legitimately name itself after its subject."""
        doc = ("DECISIONS AWAITING YOU, 1 November\n\nPART 1. SETTLED\n\n"
               "Nothing here.\n\nPART 5. THE DECISIONS THAT ARE STILL YOURS\n\n"
               "DECISION 1. A THING. My recommendation is to do it, as the "
               "simplest sufficient fix.\n")
        hits = list(NVL._DECISION_SECTION.finditer(doc))
        assert hits, "neither the title nor the section matched"
        assert "STILL YOURS" in doc[hits[-1].start():hits[-1].end()].upper(), (
            "the last match is not the decisions section, so the window will "
            "start in the wrong place")

    def test_the_item_pattern_knows_both_forms_a_report_uses(self):
        for form in ("1. A bare numbered item\n",
                     "DECISION 1. A LABELLED ONE\n",
                     "**2.** A bold one\n"):
            assert NVL._NUMBERED_ITEM.findall(form), form

    def test_the_recommendation_pattern_knows_the_label_this_project_uses(self):
        """It was narrowed to 3 phrasings and accused a compliant file, which is
        the guard-accusing-correct-material class."""
        for phrasing in ("My recommendation is to wait.",
                         "I recommend waiting.",
                         "Recommendation, and why. Wait.",
                         "Keep the inventory running, which is my recommendation."):
            assert NVL._RECOMMENDS.search(phrasing), phrasing
