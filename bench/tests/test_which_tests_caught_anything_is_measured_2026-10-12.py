"""The test-value measurement must match THIS project's filenames, and refuse a typo.

HIS QUESTION, 2026-10-12: *"there may be a question of if all these tests are necessary
to begin with?"* He approved the measurement and asked for it before any trim.

THE TWO DEFECTS THIS PINS, BOTH MADE IN THE MEASUREMENT'S OWN FIRST HOUR:

  1. **THE HYPHEN.** The first pattern was `test_[A-Za-z0-9_]+\\.py`, which cannot match
     a single DATED test file -- and dated is this project's naming convention. It
     reported 527 of 571 files "never named in any commit", 0.9229, against a true 401
     and 0.7023: an artefact of the instrument inflating the figure by 22 percentage
     points, withdrawn before it was acted on.
  2. **THE UNKNOWN FLAG.** It shipped accepting `--this-flag-does-not-exist` at exit 0
     AND running the whole 1,702-commit measurement -- the 4th script that day with the
     identical fault, after the fix already existed in `scripts/_cli_help.py`.

AND THE PROPERTY THAT MAKES THE FIGURE MEAN ANYTHING: a test is credited as having
CAUGHT something only when a commit names it, that message carries defect language, AND
it is not that file's own creation commit. Without the third condition every test scores
on the day it was written and the measurement says nothing.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "which_tests_have_ever_caught_anything_2026-10-12.py"

pytestmark = pytest.mark.skipif(not SCRIPT.is_file(), reason="producer absent")


def _mod():
    spec = importlib.util.spec_from_file_location("wt", str(SCRIPT))
    m = importlib.util.module_from_spec(spec)
    sys.modules["wt"] = m
    spec.loader.exec_module(m)
    return m


class TestItSeesThisProjectsFilenames:
    def test_the_pattern_matches_a_dated_test_file(self):
        """THE WITHDRAWN FIGURE IN ONE ASSERTION. Dated names carry hyphens."""
        m = _mod()
        hits = m.TEST_RE.findall(
            "Held by `bench/tests/test_wolfram_licence_renew_2026-09-17.py`, 15 tests")
        assert "test_wolfram_licence_renew_2026-09-17.py" in hits

    def test_it_matches_an_undated_name_too(self):
        m = _mod()
        assert "test_sv_commit.py" in m.TEST_RE.findall("see bench/tests/test_sv_commit.py")

    def test_it_matches_a_pytest_node_id(self):
        m = _mod()
        hits = m.TEST_RE.findall("bench/tests/test_foo_2026-01-02.py::TestX::test_y FAILED")
        assert "test_foo_2026-01-02.py" in hits

    def test_the_old_pattern_would_fail_this_very_test(self):
        """THE MUTATION. If a hyphen-free class still passed, the test above proves
        nothing."""
        import re
        old = re.compile(r"\b(test_[A-Za-z0-9_]+\.py)\b")
        assert not old.findall("bench/tests/test_wolfram_licence_renew_2026-09-17.py"), (
            "the hyphen-free pattern matches a dated file, so this guard is vacuous")

    def test_most_live_test_files_are_matchable_at_all(self):
        """An instrument that cannot see its own population measures nothing."""
        m = _mod()
        live = sorted(p.name for p in (REPO / "bench" / "tests").glob("test_*.py"))
        seen = [t for t in live if m.TEST_RE.findall(t)]
        assert len(seen) == len(live), (
            f"{len(live) - len(seen)} of {len(live)} live test files cannot be matched "
            f"by the pattern at all")


class TestTheCreditRuleIsNotVacuous:
    def test_defect_language_recognises_this_projects_vocabulary(self):
        m = _mod()
        for word in ("failed", "caught", "defect", "regression", "mutation", "refuted"):
            assert m.DEFECT_RE.search(f"the guard {word} on the first candidate")

    def test_an_ordinary_message_is_not_defect_language(self):
        m = _mod()
        assert not m.DEFECT_RE.search("sv: state saved and pushed")

    def test_creation_commits_are_resolved_for_most_live_files(self):
        """Credit EXCLUDES a file's own creation commit, so that mapping must exist."""
        m = _mod()
        created = m.creation_commit()
        live = {p.name for p in (REPO / "bench" / "tests").glob("test_*.py")}
        known = live & set(created)
        assert len(known) / len(live) > 0.8, (
            f"only {len(known)} of {len(live)} live files have a creation commit, so "
            f"the credit rule cannot exclude it and every test would score on day one")


class TestItRefusesATypo:
    def test_an_unknown_flag_exits_non_zero(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--this-flag-does-not-exist"],
                           capture_output=True, text=True, timeout=300, cwd=str(REPO))
        assert r.returncode != 0, (
            "it ran the whole 1,702-commit measurement in answer to a typo")

    def test_help_is_answered_without_doing_the_work(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                           capture_output=True, text=True, timeout=300, cwd=str(REPO))
        assert r.returncode == 0 and "usage:" in r.stdout
        assert "commits scanned on all refs" not in r.stdout


class TestTheFigureTravelsWithItsNote:
    def test_the_note_exists_and_carries_the_withdrawal(self):
        note = (REPO / "experimental_notes"
                / "Which_Tests_Have_Ever_Caught_Anything_2026-10-12.md")
        assert note.is_file()
        text = note.read_text(encoding="utf-8")
        assert "0.9229" in text and "withdrawn" in text.lower(), (
            "the wrong first figure must stay recorded, not be quietly replaced")
        assert "UNKNOWN, not useless" in text, (
            "without that boundary the 401 reads as a deletion list")
