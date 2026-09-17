#!/usr/bin/env python3
"""The last task entry must not absorb the supplementary list appended after it.

FOUND 2026-09-17, in the assistant's own instrument. `blocker_triage` reported
that entry W1 "names ['verdict-tuple'] inside a declared dependency". W1 contains
0 occurrences of that term. Entry bodies are sliced from one heading to the next,
and the LAST entry runs to end of file -- so W1 swallowed the 7,612-character
SUPPLEMENTARY LIST added on 2026-09-11, including a row about the verdict-tuple
guard. W1's BLOCKED state then short-circuited the dependency check.

6 consumers carried the identical slice. They now share 1 definition,
`task_list_markers.end_of_entries`, because repairing 1 of 6 copies is how this
class survives being found.

THESE TESTS CALL THE CODE. A test that grepped for the bound would pass on a
module that described itself correctly and computed the wrong answer.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import task_list_markers as tlm  # noqa: E402


@pytest.fixture(scope="module")
def bt():
    spec = importlib.util.spec_from_file_location(
        "bt", ROOT / "scripts" / "blocker_triage.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheBoundary:
    def test_it_stops_at_the_marker(self):
        lines = ["**A1.** first", "body", "# SUPPLEMENTARY LIST", "| row |"]
        assert tlm.end_of_entries(lines) == 2

    def test_a_file_with_no_marker_runs_to_the_end(self):
        lines = ["**A1.** first", "body", "more body"]
        assert tlm.end_of_entries(lines) == 3

    def test_the_marker_line_itself_is_excluded(self):
        lines = ["x", "# SUPPLEMENTARY LIST"]
        assert "SUPPLEMENTARY" not in "\n".join(lines[:tlm.end_of_entries(lines)])


class TestTheRealTaskList:
    def test_the_last_entry_carries_no_supplementary_content(self):
        lines = tlm.LIST.read_text(encoding="utf-8").splitlines()
        es = sorted(tlm.parse_entries(), key=lambda e: e.line_no)
        body = "\n".join(lines[es[-1].line_no - 1:tlm.end_of_entries(lines)])
        assert tlm.SUPPLEMENTARY not in body, (
            f"entry {es[-1].ident} has absorbed the supplementary list again")
        assert "|" not in body or body.count("|") < 10, (
            f"entry {es[-1].ident} carries {body.count('|')} table pipes, which "
            f"is the supplementary table leaking in")

    def test_without_the_bound_it_WOULD_absorb_it(self):
        """ANTI-VACUITY. If the list ever stopped carrying a supplementary
        section, the test above would pass for a reason that has nothing to do
        with the boundary, and the guard would be silently inert."""
        lines = tlm.LIST.read_text(encoding="utf-8").splitlines()
        assert tlm.end_of_entries(lines) < len(lines), (
            "the task list no longer has a SUPPLEMENTARY LIST, so the boundary "
            "guards nothing -- point this at whatever now follows the entries "
            "rather than deleting it")


class TestTheConsumerThatBroke:
    def test_a_term_living_only_in_the_supplementary_list_is_not_a_dependency(self, bt):
        """The exact false positive, executed rather than described."""
        blocked, why = bt.blocks_progress("verdict-tuple guard")
        assert blocked is False, why

    def test_the_predicate_still_answers_yes_when_an_entry_really_waits(self, bt, tmp_path):
        """CONTROL: the fix must not have made the predicate unable to fire."""
        t = tmp_path / "L.md"
        t.write_text(
            "**Q9.** Blocked pending the `frobnicate_threshold` ruling; it "
            "cannot proceed until that is settled.\n"
            "<!-- task: Q9 | state: BLOCKED | status: PROPOSED -->\n",
            encoding="utf-8")
        blocked, why = bt.blocks_progress("frobnicate_threshold", tasks=t)
        assert blocked is True, why
