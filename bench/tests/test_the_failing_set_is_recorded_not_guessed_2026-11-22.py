#!/usr/bin/env python3
"""A recorded failing set must come from the log, and an absent tally must stay empty.

`scripts/record_the_failing_set_2026-11-22.py` landed in commit 37b87d10 with NO
production caller. Its own note in `test_todays_producers_run_2026-11-22.py` says
so and names the reason: it needs a pytest log as input and wants a fixture.
Under `additive-standard` an addition nothing reaches is not additive, so this
file supplies the fixture and EXECUTES it.

★ IT DOES NOT WIRE THE BOARD. `hooks/pre-commit:1147` reads the board log and
`:1148` deletes it, so the real wiring is 1 line between them -- and that changes
the commit gate, which goes to a free panel before adoption under the founder's
standing rule. This guard makes the module reached by a test; it does not make
that decision.

WHAT IS PINNED, and each is a property the module's own docstring claims:

  1. the failing SET is read from the log's FAILED/ERROR lines
  2. the tally is read ONLY from pytest's final summary line
  3. ★ an absent summary leaves the tally EMPTY rather than filled from prose,
     because "an empty tally is visibly unknown while a wrong one is
     indistinguishable from a right one" -- the module's own words
  4. `tally_vs_set_agree` reports the DISAGREEMENT between pytest's case count
     and the summary-line count, rather than hiding it
  5. `tree_dirty_files` counts LINES of porcelain output, which is the correct
     predicate: every line porcelain prints means something is not clean
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import subprocess
import sys

import pytest


def _find_repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for c in [here.parent, *here.parents]:
        if (c / "bench" / "tests").is_dir() and (c / "hooks").is_dir():
            return c
    return pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"


REPO = _find_repo()
MODULE = pathlib.Path(os.environ.get(
    "CDSFL_FAILING_SET", REPO / "scripts" / "record_the_failing_set_2026-11-22.py"))

CLEAN = """\
........................................                                 [ 50%]
........................................                                 [100%]

5403 passed, 21 skipped, 3 warnings in 2838.00s (0:47:18)
"""

RED = """\
.....F..........E.......................                                 [100%]

=========================== short test summary info ============================
FAILED bench/tests/test_alpha.py::TestOne::test_a_thing
ERROR bench/tests/test_beta.py::test_another
1 failed, 1 error, 40 passed in 12.34s
"""

TRUNCATED = """\
.....F..........                                                         [ 30%]
FAILED bench/tests/test_alpha.py::TestOne::test_a_thing
"""


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("failing_set", MODULE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["failing_set"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def repo(tmp_path):
    """A real git repository, because `build` shells out to git and a fake
    would be testing the double rather than the module."""
    d = tmp_path / "r"
    d.mkdir()
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    for args in (["init", "-q"],
                 ["config", "user.email", "t@t"],
                 ["config", "user.name", "t"]):
        subprocess.run(["git", *args], cwd=d, env=env, check=True,
                       capture_output=True)
    (d / "a.txt").write_text("1\n")
    subprocess.run(["git", "add", "a.txt"], cwd=d, env=env, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "x", "--no-verify"],
                   cwd=d, env=env, check=True, capture_output=True)
    return d


def _log(tmp_path, text, name="board.log"):
    p = tmp_path / name
    p.write_text(text)
    return p


class TestTheSetComesFromTheLog:
    def test_failed_and_error_lines_are_both_collected(self, mod, tmp_path, repo):
        r = mod.build(_log(tmp_path, RED), repo)
        assert r["failing_count"] == 2, r["failing_set"]
        joined = " ".join(r["failing_set"])
        assert "test_alpha.py::TestOne::test_a_thing" in joined
        assert "test_beta.py::test_another" in joined

    def test_a_clean_log_records_an_empty_set(self, mod, tmp_path, repo):
        """ANTI-VACUITY: if the set were never empty, a non-empty one would
        prove nothing."""
        r = mod.build(_log(tmp_path, CLEAN), repo)
        assert r["failing_set"] == []
        assert r["failing_count"] == 0


class TestTheTallyIsReadNotInvented:
    def test_the_tally_comes_from_the_summary_line(self, mod, tmp_path, repo):
        r = mod.build(_log(tmp_path, RED), repo)
        assert r["reported_tally"].get("passed") == 40
        assert r["reported_tally"].get("failed") == 1

    def test_a_truncated_log_leaves_the_tally_EMPTY(self, mod, tmp_path, repo):
        """★ THE PROPERTY THE MODULE ARGUES FOR IN ITS OWN COMMENT: an empty
        tally is visibly unknown, a wrong one is indistinguishable from right."""
        r = mod.build(_log(tmp_path, TRUNCATED), repo)
        assert r["reported_tally"] == {}, (
            f"a log with no summary line invented a tally: {r['reported_tally']}")
        assert r["failing_count"] == 1, "but the SET is still readable"

    def test_a_large_count_with_separators_parses(self, mod, tmp_path, repo):
        r = mod.build(_log(tmp_path, CLEAN), repo)
        assert r["reported_tally"].get("passed") == 5403


class TestItReportsDisagreementRatherThanHidingIt:
    def test_agreement_is_reported_when_they_agree(self, mod, tmp_path, repo):
        """★ THE FIRST VERSION OF THE `RED` FIXTURE FAILED THIS, CORRECTLY. It
        claimed "2 failed, 1 error" in its summary while carrying only 1 FAILED
        and 1 ERROR line, so the tally said 3 and the set said 2 and the module
        reported the disagreement -- which is the property the NEXT test pins.
        The fixture was wrong and the module was right; it is written down here
        because a fixture quietly corrected teaches nothing."""
        r = mod.build(_log(tmp_path, RED), repo)
        assert r["tally_vs_set_agree"] is True

    def test_disagreement_is_reported_when_they_differ(self, mod, tmp_path, repo):
        """A truncated log has 1 summary line and no tally, so the 2 disagree.
        The module must SAY so rather than reconcile them."""
        r = mod.build(_log(tmp_path, TRUNCATED), repo)
        assert r["tally_vs_set_agree"] is False


class TestTheCleanlinessPredicateIsTheCorrectOne:
    def test_it_counts_LINES_of_porcelain_not_a_shape(self, mod, tmp_path, repo):
        """★ PINNED BECAUSE THE OBVIOUS WRONG VERSION WAS USED ELSEWHERE ON
        2026-11-22: a pattern matching only `^ M` and `^??` misses `MM`, `AM`
        and `RM`, which all mean STAGED AND CHANGED SINCE. Counting lines is
        correct because every line porcelain prints means something is dirty."""
        before = mod.build(_log(tmp_path, CLEAN), repo)["tree_dirty_files"]
        assert before == 0

        # a STAGED-and-modified-since file: porcelain prints `MM`
        (repo / "a.txt").write_text("2\n")
        subprocess.run(["git", "add", "a.txt"], cwd=repo, check=True, capture_output=True)
        (repo / "a.txt").write_text("3\n")
        after = mod.build(_log(tmp_path, CLEAN), repo)["tree_dirty_files"]
        assert after == 1, (
            "a file staged and then modified again must count as dirty; a "
            "predicate keyed on `^ M` would score this 0")


class TestItRecordsWhereItCameFrom:
    def test_the_record_names_its_log_and_commit(self, mod, tmp_path, repo):
        log = _log(tmp_path, RED)
        r = mod.build(log, repo)
        assert r["log"] == str(log)
        assert len(r["commit"]) >= 7, "a record with no commit cannot be differenced"
        assert r["schema"] == 1
