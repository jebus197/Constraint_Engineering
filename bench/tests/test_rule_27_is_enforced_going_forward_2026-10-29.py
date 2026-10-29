"""Rule 27 in full, on his ruling of 2026-10-19: enforce going forward only.

ENTRY B24. HIS RULING, 2026-10-19, verbatim: *"Verdict: Enforce going forward
only."* The archive is left as written.

WHAT WAS UNDER-ENFORCED. `WORD_NUMBER` required a MULTI-WORD number, so a
hyphenated compound was caught while a SINGLE number word standing before a noun
was not. His ruling of 2026-09-04 admits no such distinction: *"Digits only, in
every context without exception."* Found 2026-10-17 by linting a note written to
his standard -- 0 findings reported on a file holding 22 of them.

WHY DATE-GATED. A bare detector over all 562 notes returns about 16,743
occurrences across 522 of them, which would block every commit or force a
re-baseline -- and re-baselining a ratchet to accommodate a detector change is
lowering a number by changing the policy rather than the work, which entry C29
exists to refuse.

AND THE ENFORCED SCOPE IS FAR SMALLER THAN THE HEADLINE, measured 2026-10-29
through the command line rather than re-derived: across the 20 notes dated from
his ruling there are 165 COUNTED findings and 317 EXEMPTED inside verbatim
regions. Rule 27 governs what this project WRITES, not a record of another
model's words, and the panel FULL RECORDS fall from 102, 89 and 67 raw
occurrences to 5, 2 and 2 counted.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LINT = REPO / "scripts" / "note_vagueness_lint.py"


@pytest.fixture(scope="module")
def L():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("_lint_r27", LINT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheBareFormIsCaughtNow:

    def test_a_single_number_word_before_a_noun_is_a_finding(self, L, tmp_path):
        f = tmp_path / "New_Note_2026-10-29.md"
        f.write_text("The panel found three defects in the producer.\n\n"
                     "Written under CDSFL note standard v1.8\n", encoding="utf-8")
        kinds = [k for _p, k, _t, _s in L.lint(f)]
        assert any("Rule 27 in full" in k for k in kinds), (
            f"a bare spelled number was not caught; got {kinds}")

    def test_the_compound_form_still_fires_and_only_once(self, L, tmp_path):
        """One sentence must not yield 2 spelled-number findings."""
        f = tmp_path / "New_Note_2026-10-29.md"
        # AT LEAST 5 WORDS, because `sentences()` skips a shorter segment by
        # design -- a 4-word fragment is a heading or a label, not prose. My
        # first fixture was 4 words and reported 0 findings, which looked like a
        # detector fault and was a FIXTURE fault. The floor is the linter being
        # right.
        f.write_text("The run took twenty-nine separate attempts to finish.\n\n"
                     "Written under CDSFL note standard v1.8\n", encoding="utf-8")
        hits = [k for _p, k, _t, _s in L.lint(f) if "SPELLED NUMBER" in k]
        assert len(hits) == 1, f"expected 1 spelled-number finding, got {hits}"
        assert "in full" not in hits[0], (
            "the compound detector should have claimed this, not the bare one")

    def test_an_idiom_is_not_a_number(self, L, tmp_path):
        f = tmp_path / "New_Note_2026-10-29.md"
        f.write_text("No one reached it, and one of the 3 seats declined.\n\n"
                     "Written under CDSFL note standard v1.8\n", encoding="utf-8")
        hits = [t for _p, k, t, _s in L.lint(f) if "SPELLED NUMBER" in k]
        assert not hits, (
            f"an English idiom was read as a number: {hits}. The whitelist is "
            f"consulted on a WINDOW around the match, because every forgiving "
            f"idiom is a phrase")

    def test_an_ordinal_is_not_a_number(self, L, tmp_path):
        f = tmp_path / "New_Note_2026-10-29.md"
        f.write_text("On the twenty-sixth of August he ruled on it.\n\n"
                     "Written under CDSFL note standard v1.8\n", encoding="utf-8")
        hits = [t for _p, k, t, _s in L.lint(f) if "SPELLED NUMBER" in k]
        assert not hits, f"an ordinal date was read as data: {hits}"


class TestTheGateReadsTheLOGICALPathNotTheTempCopy:
    """`hooks/pre-commit` lints a STAGED COPY and names the real file with --as.

    FOUND BY FOLLOW, NOT BY READING, 2026-10-29. The pre-commit hook writes the
    staged content to a temporary path and invokes the linter as
    `note_vagueness_lint.py --as <real path> <temp copy>`. A date gate reading
    the path ON DISK asks git about a file with no history, falls back to the
    TEMP name, and -- the moment that name carries no date -- holds an ARCHIVED
    note to a rule he confined to new ones. `_LOGICAL_PATH` exists for exactly
    this and 2 other rules in the module already read it.
    """

    def test_the_hook_still_passes_as_to_the_linter(self):
        """If the hook stops using --as, this coupling is gone and the comment
        above is stale -- which is worth failing on."""
        hook = REPO / "hooks" / "pre-commit"
        if not hook.is_file():
            pytest.skip("no pre-commit hook in this checkout")
        assert "note_vagueness_lint.py --as" in hook.read_text(
            encoding="utf-8", errors="replace"), (
            "the hook no longer lints a staged copy with --as, so the logical "
            "path indirection may no longer be needed")

    def test_an_archived_note_linted_through_a_temp_copy_is_still_ARCHIVED(
            self, L, tmp_path):
        """The defect itself: temp name with no date, logical name old."""
        archived = REPO / "experimental_notes" / "Morning_Roundup_2026-09-03.md"
        if not archived.is_file():
            pytest.skip("that archived note is not in this checkout")
        copy = tmp_path / "after_staged_blob.md"          # NO date in the name
        copy.write_text(archived.read_text(encoding="utf-8"), encoding="utf-8")
        assert L.rule_27_in_full(copy) is True, (
            "fixture is wrong: an undated temp copy must look NEW on its own")
        prev = L._LOGICAL_PATH
        try:
            L._LOGICAL_PATH = str(archived)
            kinds = [k for _p, k, _t, _s in L.lint(copy)]
        finally:
            L._LOGICAL_PATH = prev
        assert not any("Rule 27 in full" in k for k in kinds), (
            "an ARCHIVED note linted through an undated temp copy was held to "
            "the full rule, because the gate dated the copy instead of the note")

    def test_a_new_note_through_a_temp_copy_is_still_NEW(self, L, tmp_path):
        """The gate must not become permissive in the other direction."""
        real = tmp_path / "Brand_New_2026-10-29.md"
        real.write_text("The run took three separate attempts to finish.\n\n"
                        "Written under CDSFL note standard v1.8\n",
                        encoding="utf-8")
        copy = tmp_path / "after_blob.md"
        copy.write_text(real.read_text(encoding="utf-8"), encoding="utf-8")
        prev = L._LOGICAL_PATH
        try:
            L._LOGICAL_PATH = str(real)
            kinds = [k for _p, k, _t, _s in L.lint(copy)]
        finally:
            L._LOGICAL_PATH = prev
        assert any("Rule 27 in full" in k for k in kinds), (
            "a NEW note linted through a temp copy escaped the full rule")


class TestTheGateIsDatedAndFailsOpenForNewFiles:

    def test_the_cutoff_is_his_ruling_date(self, L):
        assert L.RULE_27_FULL_FROM == "2026-10-29", (
            "the cutoff is the date ENFORCEMENT began, not the date he ruled. The "
            "20 notes written between the 2 dates had no checker to be held to, "
            "and holding them to one now is the retrospection his ruling refused. "
            "Moving this needs his word, not an edit")

    def test_a_dated_filename_is_read_before_failing_open(self, L, tmp_path):
        """A DATED NAME IS EVIDENCE, and consulting it is the repair.

        "Uncommitted means new" was too crude: it held 3 generated morning
        reports dated 2026-10-16, 2026-10-19 and 2026-10-28 to a rule that
        begins on 2026-10-29, purely because they had never been committed.
        This project dates its note names, so the name is a better witness to
        when a note was written than the absence of a git record is.
        """
        old_name = tmp_path / "Not_In_Git_2026-09-03.md"
        old_name.write_text("x\n", encoding="utf-8")
        assert L.note_first_seen(old_name) == "2026-09-03"
        assert L.rule_27_in_full(old_name) is False, (
            "an uncommitted note whose NAME predates the cutoff is still an "
            "old note")

    def test_a_file_with_no_date_at_all_fails_OPEN(self, L, tmp_path):
        """Neither a git record nor a dated name: treat it as being written
        now, because that is the one case the rule certainly covers."""
        f = tmp_path / "untitled_scratch.md"
        f.write_text("x\n", encoding="utf-8")
        assert L.note_first_seen(f) is None
        assert L.rule_27_in_full(f) is True

    def test_an_archived_note_is_NOT_held_to_the_full_rule(self, L):
        """His ruling leaves the archive as written. This is the half of the
        ruling that is easy to break by widening a detector without a gate."""
        old = REPO / "experimental_notes" / "Morning_Roundup_2026-09-03.md"
        if not old.is_file():
            pytest.skip("that archived note is not in this checkout")
        assert L.rule_27_in_full(old) is False, (
            "a note first committed in September is being held to a rule he "
            "ruled on in October, which is the retrospection he refused")
        kinds = [k for _p, k, _t, _s in L.lint(old)]
        assert not any("Rule 27 in full" in k for k in kinds), (
            "the full rule fired on an archived note")

    def test_the_date_comes_from_git_and_not_the_mtime(self, L):
        """An mtime moves on every touch, so it would hold an old note to a new
        rule the moment anything edited it -- exactly the retrospection
        refused."""
        old = REPO / "experimental_notes" / "Morning_Roundup_2026-09-03.md"
        if not old.is_file():
            pytest.skip("that archived note is not in this checkout")
        seen = L.note_first_seen(old)
        assert seen is not None and seen < "2026-10-01", (
            f"first-seen date {seen!r} does not look like a git add date")
