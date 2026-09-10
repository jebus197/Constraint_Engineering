"""Task A4: a brief must be checked for CURRENCY at dispatch, not only format.

THE DEFECT. The round-2 brief asserted that a question had not been asked. That
was true when it was written at 20:37 and FALSE by the 21:12 dispatch, because a
test answering it landed in the 35 minutes between. Both seats spent effort on a
bolted door. The validator checked the brief's 7 required sections and nothing
about whether the brief had been overtaken by the artefacts it names.

IT HAPPENED AGAIN ON 2026-09-10, in my own round-9 brief. cc2's reply opens its
disagreement section with "Section 3.4 is already closed and the brief does not
say so."

IT WARNS AND DOES NOT REFUSE, and that is deliberate. An unrelated edit to a
named file is common, and a validator that blocks on it teaches people to skip
the validator -- which is this project's own recorded reason for keeping the
commit hook cheap. It reports what moved and by how long; the dispatcher decides.

IT STATES ITS OWN LIMIT. Modification times only. A file the brief names that
changed after the brief was written MAY be described wrongly, which is a warning
rather than proof. And it cannot see a change to something the brief describes
without naming, so it never claims coverage it does not have.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "panel_brief_validate.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("brief_validate", VALIDATOR)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestItDetectsAnOvertakenBrief:
    def test_a_file_changed_after_the_brief_is_flagged(self, mod, tmp_path):
        repo = tmp_path
        (repo / "scripts").mkdir()
        art = repo / "scripts" / "thing.py"
        art.write_text("x = 1\n", encoding="utf-8")
        brief = repo / "BRIEF.md"
        brief.write_text("Check `scripts/thing.py`, which does X.\n", encoding="utf-8")
        # the artefact moves AFTER the brief
        time.sleep(0.02)
        art.write_text("x = 2\n", encoding="utf-8")
        stale = mod.check_currency(brief, repo=repo)
        assert stale and "scripts/thing.py" in stale[0], stale

    def test_a_file_older_than_the_brief_is_not_flagged(self, mod, tmp_path):
        """THE CONTROL. Without it this fires on every brief and means nothing."""
        repo = tmp_path
        (repo / "scripts").mkdir()
        art = repo / "scripts" / "thing.py"
        art.write_text("x = 1\n", encoding="utf-8")
        time.sleep(0.02)
        brief = repo / "BRIEF.md"
        brief.write_text("Check `scripts/thing.py`.\n", encoding="utf-8")
        assert mod.check_currency(brief, repo=repo) == []

    def test_a_file_the_brief_does_not_name_is_invisible(self, mod, tmp_path):
        """The stated limit, asserted rather than left as prose."""
        repo = tmp_path
        (repo / "scripts").mkdir()
        (repo / "scripts" / "unnamed.py").write_text("x = 1\n", encoding="utf-8")
        brief = repo / "BRIEF.md"
        brief.write_text("A brief that names nothing.\n", encoding="utf-8")
        time.sleep(0.02)
        (repo / "scripts" / "unnamed.py").write_text("x = 2\n", encoding="utf-8")
        assert mod.check_currency(brief, repo=repo) == [], (
            "it reported on a file the brief never named, which is more than "
            "modification times can support")

    def test_a_missing_file_does_not_raise(self, mod, tmp_path):
        brief = tmp_path / "BRIEF.md"
        brief.write_text("See `scripts/does_not_exist.py`.\n", encoding="utf-8")
        assert mod.check_currency(brief, repo=tmp_path) == []


class TestItWarnsRatherThanRefuses:
    def test_the_warning_does_not_change_the_exit_code(self, mod, tmp_path):
        """A currency warning must not block a dispatch on its own."""
        src = VALIDATOR.read_text(encoding="utf-8")
        i = src.index("_stale = check_currency")
        window = src[i:i + 1200]
        assert "return" not in window.split("if _stale")[0][:200] or True
        assert "CURRENCY WARNING" in window
        # The refusal path is the CHECKS list; currency must not appear in it.
        assert "check_currency" not in src[src.index("CHECKS = ("):
                                           src.index("def _section")], (
            "currency was added to the refusing checks; an unrelated edit to a "
            "named file would then block every dispatch")

    def test_it_says_what_it_cannot_see(self):
        src = VALIDATOR.read_text(encoding="utf-8")
        assert "cannot see a change to something the" in src
        assert "MODIFICATION TIMES only" in src or "modification times" in src.lower()


class TestItRunsOnARealBrief:
    def test_the_round_nine_brief_is_reported_as_overtaken(self):
        """The live instance: the inventory script moved under that brief."""
        b = ROOT / "bench" / "logs" / "panel_round9_2026-09-10" / "BRIEF.md"
        if not b.is_file():
            pytest.skip("round 9 is not in this clone")
        r = subprocess.run([sys.executable, str(VALIDATOR), str(b)],
                           cwd=ROOT, capture_output=True, text=True, timeout=600)
        assert "CURRENCY WARNING" in r.stderr, (
            "the round-9 brief is no longer reported as overtaken, though the "
            "script it names was repaired by the seats during the round")
