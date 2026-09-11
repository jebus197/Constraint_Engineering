"""Two DONE entries whose artefact lives outside this repository, checked properly.

FOUND 2026-09-11 by the fable seat answering Section 3.2 of the round-11 brief:
*"name a DONE entry whose evidence passes for a reason unrelated to the claim"*.

  Entry 4.2 claims a sentence was removed from a memory file and marks itself
  COMMITTED. Its named evidence, `test_recovery_memory_doc_repairs.py`, contains
  ZERO references to that file or that sentence -- `grep -c` returns 0 -- and the
  file itself lives at `~/.claude/projects/.../memory/`, outside this repository,
  never committed in 1,161+ revisions. The evidence is green with the fix fully
  reverted, by construction.

  Entry 7.3 is the same shape, found the same night by the V2 sweep, which the
  reviewer's own list of 11 had not named.

WHY NO TEST OF THE MEMORY FILE IS WRITTEN. It is out of tree and exists on 1
machine. A test asserting on it would pass on the maintainer's laptop and fail or
skip everywhere else -- the environment-assumption class that task A2 spent a day
removing -- and a test that skips everywhere is the vacuous-guard class this
project has confirmed 11 times. The seat declined to write one for exactly that
reason and it was right.

WHAT IS CHECKABLE IS WHAT THIS REPOSITORY ACTUALLY COMMITS: the record. Both
entries now quote the substance verbatim and state plainly that the artefact is
not carried here. That is a real assertion about real committed bytes, and it
fails the moment either entry is trimmed back to a bare "Status COMMITTED".
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import task_list_markers as tlm  # noqa: E402

LIST = ROOT / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"


def _block(ident: str) -> str:
    lines = LIST.read_text(encoding="utf-8").splitlines()
    es = sorted(tlm.parse_entries(LIST), key=lambda e: e.line_no)
    for k, e in enumerate(es):
        if e.ident == ident:
            end = es[k + 1].line_no - 1 if k + 1 < len(es) else len(lines)
            return "\n".join(lines[e.line_no - 1:end])
    raise AssertionError(f"entry {ident} is gone from the task list")


class TestEntry42KeepsTheRecordItCommits:
    def test_it_quotes_the_removed_sentence_verbatim(self):
        assert ("Prefer extending machinery that exists and is already trusted "
                "over inventing a new component.") in _block("4.2"), (
            "4.2 no longer quotes the sentence it removed, so this repository "
            "no longer records WHAT was corrected -- only that something was")

    def test_it_says_the_artefact_is_not_carried_here(self):
        b = _block("4.2")
        assert "does not carry" in b and "0" in b, (
            "4.2 claims COMMITTED without saying that the repaired file lives "
            "outside this repository")

    def test_it_keeps_the_three_axis_analysis(self):
        b = _block("4.2")
        for axis in ("Sufficiency", "Simplicity", "Additivity"):
            assert axis in b, f"the {axis} axis is gone from the committed record"


class TestEntry73KeepsTheRulingItCommits:
    def test_it_quotes_the_founder_ruling(self):
        b = _block("7.3")
        assert "intended for the technical reader" in b, (
            "7.3 no longer carries the ruling verbatim, so the only committed "
            "copy of it is gone")

    def test_it_says_the_memory_file_is_not_carried_here(self):
        assert "does not carry" in _block("7.3")


class TestTheClaimAboutTheOldEvidenceIsTrue:
    """The finding itself, checked rather than repeated.

    If `test_recovery_memory_doc_repairs.py` ever DID start asserting on the
    memory file, this file's whole premise would be wrong and should be revised
    rather than left standing.
    """

    def test_the_old_evidence_file_says_nothing_about_the_memory_file(self):
        src = (ROOT / "bench" / "tests"
               / "test_recovery_memory_doc_repairs.py").read_text(encoding="utf-8")
        assert "feedback_simplest_sufficient" not in src
        assert "Prefer extending machinery" not in src

    def test_the_memory_file_is_absent_from_this_repository(self):
        assert not (ROOT / "memory").exists(), (
            "a `memory/` directory now exists in the repository; if the files "
            "are committed, 4.2 and 7.3 can be guarded directly and this file "
            "should be replaced rather than kept")
        matches = list(ROOT.rglob("feedback_simplest_sufficient.md"))
        assert not matches, matches
