"""The board-share producer must be EXECUTED by something, and this is it.

`scripts/what_share_of_the_suite_does_the_board_run_2026-11-13.py` produces the
figure for how much of the test suite the commit board actually runs. It was
written on 2026-11-13 and the suite immediately reported it as a producer reached
by NO test, which is the symmetric half of `additive-standard`: an addition that
nothing reaches is not additive, and this project has confirmed that defect 11
times.

★ IT DOES NOT RUN A FULL COLLECTION. `main()` collects the whole of bench/tests/
twice, which on the founder's machine is minutes of work for a figure no
assertion here needs. The functions are exercised individually instead, and
`_collect` is proved on a single file. That keeps the guard honest without
spending his 8 cores to re-derive a number the producer already prints.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
PRODUCER = REPO / "scripts" / "what_share_of_the_suite_does_the_board_run_2026-11-13.py"


@pytest.fixture(scope="module")
def mod():
    assert PRODUCER.is_file(), f"the producer is gone: {PRODUCER}"
    spec = importlib.util.spec_from_file_location("board_share", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["board_share"] = m
    spec.loader.exec_module(m)
    return m


class TestBoardFilesComesFromTheHook:
    def test_it_returns_real_files_and_is_not_empty(self, mod):
        files = mod.board_files()
        assert files, "board_files() returned nothing; the figure would be degenerate"
        for f in files:
            assert f.startswith("bench/tests/"), f"{f} is not a suite test file"
            assert (REPO / f).is_file(), f"{f} is named by the hook but does not exist"

    def test_it_agrees_with_an_INDEPENDENT_read_of_the_hook(self, mod):
        """Derived here from the hook, not copied from the producer's own result.

        A guard that re-implements the producer compares 2 copies of 1 idea and
        tests only itself -- the defect recorded on 2026-11-12. This re-derives
        from the SOURCE the producer claims to read, so a producer that stopped
        reading the hook would be caught.
        """
        txt = (REPO / "hooks" / "pre-commit").read_text(errors="replace")
        named = {f for f in re.findall(r"bench/tests/[A-Za-z0-9_./-]+\.py", txt)
                 if (REPO / f).is_file()}
        assert set(mod.board_files()) == named, (
            "board_files() no longer matches the files hooks/pre-commit names")

    def test_the_board_is_a_strict_subset_of_the_suite(self, mod):
        """The producer's whole claim is that the board is PART of the suite."""
        files = set(mod.board_files())
        every = {f"bench/tests/{p.name}" for p in (REPO / "bench" / "tests").glob("test_*.py")}
        assert files <= every, f"the board names files outside the suite: {sorted(files - every)}"
        assert files < every, "the board covers the WHOLE suite; the figure is meaningless"


class TestTheSupersededFiguresAreNamed:
    def test_both_memory_files_are_recorded_with_their_figures(self, mod):
        rec = mod.RECORDED
        assert set(rec) == {
            "feedback_a_gate_board_is_not_the_suite_2026-11-04",
            "feedback_the_gates_board_is_a_sixth_of_the_suite_2026-11-04",
        }, f"the superseded figures are no longer named: {sorted(rec)}"
        for name, (board, total) in rec.items():
            assert 0 < board < total, f"{name} records a degenerate pair"
            assert 0.10 < board / total < 0.25, (
                f"{name} records {board}/{total}, which is not the 'about a sixth' "
                f"claim these entries exist to carry")


class TestCollectWorksWithoutRunningTheSuite:
    def test_it_returns_a_positive_count_for_one_file(self, mod):
        n = mod._collect([f"bench/tests/{pathlib.Path(__file__).name}"])
        assert isinstance(n, int) and n > 0, (
            f"_collect could not read a collection count: {n!r}. Its regex or its "
            f"pytest invocation has drifted.")

    def test_it_returns_None_rather_than_guessing_when_collection_fails(self, mod):
        assert mod._collect(["bench/tests/does_not_exist_9f3a.py"]) is None, (
            "_collect invented a count for a target that cannot be collected")
