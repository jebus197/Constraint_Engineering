#!/usr/bin/env python3
"""The `Feedback` bullets merge under the bold sub-headings the index already carries.

HIS RULING, 2026-10-29, annotation 7 of
`Responses/Decisions_Awaiting_You_2026-10-29.txt`: *"Group them as you suggest. fr"*.

WHY A SEPARATE MECHANISM FROM THE DATED GROUPER. `group_dated_index_entries`
states in its own docstring why it leaves this section alone: grouping must
follow a semantic key and 0 of the section's 78 lines carry a date. The key it
DOES carry is the bold sub-heading, of which there are 8 plus an unheaded leading
block, so the merge collapses a grouping the index already asserts instead of
merging by position.

EVERY TEST CALLS THE FUNCTION. None reads its source, because a test that asserts
on source text can only establish that a module describes itself consistently.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SV = REPO / "scripts" / "cdsfl_sv.py"


def _sv():
    spec = importlib.util.spec_from_file_location("cdsfl_sv_under_test", SV)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_sv_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


sv = _sv()

INDEX = """# Index

## Project State
- **29 Oct** — [a](one.md) first
- **28 Oct** — [b](two.md) second

## Feedback (applies to all work)
- [lead one](lead1.md) the first unheaded pointer
- [lead two](lead2.md) the second unheaded pointer

**EVIDENCE DISCIPLINE.**
- [ev one](ev1.md) the first evidence pointer
- [ev two](ev2.md) the second evidence pointer
- [ev three](ev3.md) the third evidence pointer
**INSTRUMENTS.**
- [in one](in1.md) the first instrument pointer
- [in two](in2.md) the second instrument pointer

## Later Section
- [after](after.md) a pointer in the section that follows
"""


@pytest.fixture()
def mem(tmp_path):
    (tmp_path / "MEMORY.md").write_text(INDEX, encoding="utf-8")
    return tmp_path


def _pointers(text: str) -> list[str]:
    return sorted(tgt for ln in text.splitlines()
                  for _t, tgt, _n in sv._memory_index_pointers(ln))


class TestItFreesLinesAndLosesNothing:
    def test_it_merges_each_group_onto_one_line(self, mem):
        before = (mem / "MEMORY.md").read_text(encoding="utf-8")
        report = sv.group_feedback_index_entries(mem, dry_run=False)
        after = (mem / "MEMORY.md").read_text(encoding="utf-8")
        assert report["ok"], report["reason"]
        # 7 bullets in 3 groups of 2, 3 and 2 -> 3 lines, so 4 merges.
        assert report["merged"] == 4, report
        assert report["freed_lines"] == 4
        assert before.count("\n") - after.count("\n") == 4

    def test_no_pointer_is_lost(self, mem):
        before = (mem / "MEMORY.md").read_text(encoding="utf-8")
        sv.group_feedback_index_entries(mem, dry_run=False)
        after = (mem / "MEMORY.md").read_text(encoding="utf-8")
        assert _pointers(before) == _pointers(after)
        #: 10, not 8: 2 in Project State, 7 in Feedback, 1 in Later Section.
        #: The first figure written here was 8 and the test caught it, which is
        #: the cheap kind of mistake -- the code was right and the assertion was
        #: not.
        assert len(_pointers(after)) == 10

    def test_every_pointers_own_note_survives_verbatim(self, mem):
        sv.group_feedback_index_entries(mem, dry_run=False)
        after = (mem / "MEMORY.md").read_text(encoding="utf-8")
        for note in ("the first unheaded pointer", "the second unheaded pointer",
                     "the first evidence pointer", "the second evidence pointer",
                     "the third evidence pointer", "the first instrument pointer",
                     "the second instrument pointer"):
            assert note in after, f"lost: {note}"

    def test_a_dry_run_writes_nothing(self, mem):
        before = (mem / "MEMORY.md").read_text(encoding="utf-8")
        report = sv.group_feedback_index_entries(mem, dry_run=True)
        assert report["merged"] == 4
        assert (mem / "MEMORY.md").read_text(encoding="utf-8") == before
        assert report["backup"] is None
        assert not list(mem.glob(f"{sv._MEMORY_BACKUP_PREFIX}*"))

    def test_it_writes_a_backup_before_changing_anything(self, mem):
        before = (mem / "MEMORY.md").read_text(encoding="utf-8")
        report = sv.group_feedback_index_entries(mem, dry_run=False)
        backups = list(mem.glob(f"{sv._MEMORY_BACKUP_PREFIX}*"))
        assert len(backups) == 1
        assert backups[0].name == report["backup"]
        assert backups[0].read_text(encoding="utf-8") == before

    def test_it_is_idempotent(self, mem):
        sv.group_feedback_index_entries(mem, dry_run=False)
        once = (mem / "MEMORY.md").read_text(encoding="utf-8")
        second = sv.group_feedback_index_entries(mem, dry_run=False)
        assert second["merged"] == 0
        assert "no two" in second["reason"]
        assert (mem / "MEMORY.md").read_text(encoding="utf-8") == once


class TestItRespectsTheBoundaries:
    def test_it_leaves_other_sections_alone(self, mem):
        sv.group_feedback_index_entries(mem, dry_run=False)
        after = (mem / "MEMORY.md").read_text(encoding="utf-8")
        assert "- **29 Oct** — [a](one.md) first" in after
        assert "- **28 Oct** — [b](two.md) second" in after
        assert "- [after](after.md) a pointer in the section that follows" in after

    def test_a_heading_does_not_claim_a_bullet_from_the_next_section(self, mem):
        """THE PROPERTY HOLDS; THE RESET THAT APPEARS TO ENFORCE IT DOES NOT.

        This docstring first claimed the `heading = ""` reset on a `## ` line was
        REACHABLE, unlike the dated grouper's equivalent. Mutation testing
        refuted that: deleting the reset leaves all 14 tests green. The property
        is carried by 2 other things -- `first_line_of` is cleared at the same
        boundary, so a following bullet starts a fresh group whatever the stale
        heading says, and the `section != _MEMORY_HEADED_SECTION` guard appends
        every line outside the section untouched. The reset is retained with
        this honest note, exactly as the dated grouper retains its own
        unreachable reset, because it becomes load-bearing the moment a second
        section is made groupable. An unreached line with an accurate comment is
        not the same fault as one whose comment overstates it.
        """
        sv.group_feedback_index_entries(mem, dry_run=False)
        after = (mem / "MEMORY.md").read_text(encoding="utf-8")
        later = [ln for ln in after.splitlines() if "after.md" in ln]
        assert len(later) == 1
        assert "in1.md" not in later[0] and "in2.md" not in later[0]

    def test_bullets_under_different_headings_do_not_merge(self, mem):
        sv.group_feedback_index_entries(mem, dry_run=False)
        after = (mem / "MEMORY.md").read_text(encoding="utf-8")
        ev = [ln for ln in after.splitlines() if "ev1.md" in ln]
        assert len(ev) == 1
        assert "in1.md" not in ev[0], "an instrument pointer merged into evidence"
        assert "lead1.md" not in ev[0], "the unheaded block merged into evidence"

    def test_the_headings_themselves_are_kept(self, mem):
        sv.group_feedback_index_entries(mem, dry_run=False)
        after = (mem / "MEMORY.md").read_text(encoding="utf-8")
        assert "**EVIDENCE DISCIPLINE.**" in after
        assert "**INSTRUMENTS.**" in after

    def test_it_uses_the_separator_the_index_already_uses(self, mem):
        sv.group_feedback_index_entries(mem, dry_run=False)
        after = (mem / "MEMORY.md").read_text(encoding="utf-8")
        assert sv._MEMORY_POINTER_JOIN in after
        assert sv._MEMORY_POINTER_JOIN.strip() == "·"

    def test_it_creates_no_over_long_entry_or_preamble(self, mem):
        """The audit's own limit, applied to the result rather than assumed."""
        sv.group_feedback_index_entries(mem, dry_run=False)
        audit = sv._audit_memory_index(mem)
        assert audit.over_long == [], audit.over_long
        assert audit.error == ""


class TestItRefusesRatherThanDamages:
    def test_a_missing_index_is_reported_not_raised(self, tmp_path):
        report = sv.group_feedback_index_entries(tmp_path, dry_run=False)
        assert not report["ok"]
        assert "no index" in report["reason"]

    def test_a_section_with_no_repeats_changes_nothing(self, tmp_path):
        (tmp_path / "MEMORY.md").write_text(
            "## Feedback (applies to all work)\n"
            "**ONLY ONE.**\n"
            "- [solo](solo.md) the only pointer under this heading\n",
            encoding="utf-8")
        before = (tmp_path / "MEMORY.md").read_text(encoding="utf-8")
        report = sv.group_feedback_index_entries(tmp_path, dry_run=False)
        assert report["ok"] and report["merged"] == 0
        assert (tmp_path / "MEMORY.md").read_text(encoding="utf-8") == before


class TestTheRefusalPathIsReachable:
    """The pointer-set check cannot be falsified by valid input, so it is driven
    directly. Mutation 4 of 6 on 2026-10-29 -- dropping the check -- left all 14
    tests green, which means nothing exercised the refusal. A guard no test can
    reach is the addition the additive standard forbids, so it is reached here.
    """

    def test_a_merge_that_would_lose_a_pointer_is_refused(self, mem, monkeypatch):
        real = sv._memory_index_pointers
        state = {"calls": 0}

        def lossy(line):
            """Report the truth, except drop 1 pointer from the merged result.

            The check compares the pointer set before and after, so making the
            SECOND reading short is what a merge losing a pointer would look
            like.
            """
            out = real(line)
            state["calls"] += 1
            if state["calls"] > 10 and out:
                return out[:-1]
            return out

        monkeypatch.setattr(sv, "_memory_index_pointers", lossy)
        before = (mem / "MEMORY.md").read_text(encoding="utf-8")
        report = sv.group_feedback_index_entries(mem, dry_run=False)
        assert not report["ok"], "a pointer-losing merge was accepted"
        assert "REFUSED" in report["reason"]
        assert (mem / "MEMORY.md").read_text(encoding="utf-8") == before, (
            "the index was changed despite the refusal")
        assert not list(mem.glob(f"{sv._MEMORY_BACKUP_PREFIX}*")), (
            "a backup was written for a change that was refused")
