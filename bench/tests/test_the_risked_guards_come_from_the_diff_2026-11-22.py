#!/usr/bin/env python3
"""The risked-guard map must partition by the GATE'S list, not by its own taste.

DRAFTED 2026-11-22; destination `bench/tests/`, and onto `GUARDS`.

WHY. Before board 2 of 2026-11-22 the cheap checks were chosen by grepping
subject words: 13 guards, 169 passed in 2:59, and they omitted the guard OF the
file being rewritten -- which produced 4 of the board's 5 failures.
`scripts/which_guards_does_this_commit_risk_2026-11-22.py` derives the set from
the diff instead.

★ AND THE FIRST DERIVATION WAS ITSELF WRONG IN THE WAY B206 RECORDS. Every guard
naming any staged file is 215 -- most of the board. Restricted to
behaviour-changing files it is 119. But **42 of those are not on the gate's
`GUARDS` list**, so their failures cannot refuse a commit, and B203 records one
of them as red at HEAD with the note that the board does not run it. A predictor
that does not share its subject's population predicts nothing, which is the
defect this very batch exists to fix in the note pre-flight.

So the contract under test is the PARTITION:

    DECIDING  = guards naming changed code  ∩  the gate's own GUARDS list
    ADVISORY  = the rest

★ THE GATE'S LIST IS READ FROM THE HOOK, NOT COPIED. These tests drive the
module against a CONSTRUCTED hook and repository so the partition is checked on
known inputs, because a test that asserts on the module's source text asserts
only that it describes itself consistently.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest


def _find_repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for c in [here.parent, *here.parents]:
        if (c / "bench" / "tests").is_dir() and (c / "hooks").is_dir():
            return c
    return pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"


REPO = _find_repo()
TOOL = pathlib.Path(
    __import__("os").environ.get(
        "CDSFL_RISKMAP_PATH",
        REPO / "scripts" / "which_guards_does_this_commit_risk_2026-11-22.py"))


@pytest.fixture(scope="module")
def mod():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("riskmap", TOOL)
    m = importlib.util.module_from_spec(spec)
    sys.modules["riskmap"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def fake(tmp_path):
    """A repository whose hook names a known GUARDS list."""
    (tmp_path / "bench" / "tests").mkdir(parents=True)
    (tmp_path / "hooks").mkdir()
    (tmp_path / "scripts").mkdir()
    for name, body in [
        ("test_on_board.py", "touches scripts/subject.py\n"),
        ("test_off_board.py", "also touches scripts/subject.py\n"),
        ("test_unrelated.py", "mentions nothing at all\n"),
    ]:
        (tmp_path / "bench" / "tests" / name).write_text(body)
    (tmp_path / "hooks" / "pre-commit").write_text(
        'GUARDS="bench/tests/test_on_board.py\nbench/tests/test_unrelated.py"\n')
    return tmp_path


class TestTheFilter:
    def test_only_behaviour_changing_files_count(self, mod):
        got = mod.behaviour_changing([
            "scripts/a.py", "hooks/pre-commit", "hooks/b.py", "bench/c.py",
            "experimental_notes/note.md",       # a note is not behaviour
            "bench/tickets/tickets.jsonl",      # data, named by many guards
            "resources/RECOVERY.md",
            "docs/x.md",
        ])
        assert got == ["scripts/a.py", "hooks/pre-commit", "hooks/b.py", "bench/c.py"]

    def test_data_is_what_made_the_first_version_too_wide(self, mod):
        """ANTI-VACUITY: the excluded kinds must actually be present to exclude."""
        noisy = ["experimental_notes/CDSFL_MASTER_TASK_LIST.md",
                 "bench/tickets/tickets.jsonl"]
        assert mod.behaviour_changing(noisy) == [], (
            "the task list and the ticket store are named by about 100 guards "
            "each; including them is what turned 43 files into 215 guards")


class TestItReadsTheGatesOwnList:
    def test_the_list_comes_from_the_hook(self, mod, fake):
        got = mod.board_guards(fake)
        assert got == {"bench/tests/test_on_board.py",
                       "bench/tests/test_unrelated.py"}

    def test_a_hook_without_guards_refuses_rather_than_guessing(self, mod, tmp_path):
        (tmp_path / "hooks").mkdir()
        (tmp_path / "hooks" / "pre-commit").write_text("# no list here\n")
        with pytest.raises(SystemExit):
            mod.board_guards(tmp_path)


class TestThePartition:
    def test_deciding_is_on_the_board_and_advisory_is_not(self, mod, fake):
        code = ["scripts/subject.py"]
        naming = mod.guards_naming(fake, code)
        board = mod.board_guards(fake)
        deciding = (naming & board) - mod.CONTAINS_THE_BOARD
        advisory = naming - board - mod.CONTAINS_THE_BOARD

        assert deciding == {"bench/tests/test_on_board.py"}
        assert advisory == {"bench/tests/test_off_board.py"}
        assert not (deciding & advisory), "the 2 sets must be disjoint"
        assert "bench/tests/test_unrelated.py" not in naming, (
            "a guard naming nothing changed is not at risk, even though it IS "
            "on the board")

    def test_a_changed_guard_guards_itself(self, mod, fake):
        got = mod.guards_naming(fake, ["bench/tests/test_off_board.py"])
        assert "bench/tests/test_off_board.py" in got, (
            "the guard OF a changed file is the one that was omitted before "
            "board 2, and a changed guard is its own subject")


class TestTheBoardContainingGuardIsExcluded:
    def test_it_is_named_and_excluded(self, mod):
        assert ("bench/tests/test_precommit_gate_cost_2026-09-10.py"
                in mod.CONTAINS_THE_BOARD), (
            "that guard invokes --repeats 1, which TIMES the board by running "
            "the whole GUARDS list; including it costs the board these checks "
            "exist to avoid")

    def test_the_exclusion_is_a_set_not_a_pattern(self, mod):
        """A rule broad enough to catch it would catch guards that merely
        mention the gate. 1 known file, named once."""
        assert isinstance(mod.CONTAINS_THE_BOARD, (set, frozenset))
        assert len(mod.CONTAINS_THE_BOARD) == 1
