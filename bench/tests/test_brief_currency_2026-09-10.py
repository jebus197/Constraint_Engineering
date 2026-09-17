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


#: A brief that passes every refusing check and declares no figure, so its exit
#: code depends on currency alone. It names `gamma`, not `Wilson`: validate()
#: matches against the LOWERCASED text, so the `\bWilson\b`, `\bS_k\b` and
#: `\bDuane\b` instrument patterns cannot match (a separate, open defect).
_VALID_BRIEF = (
    "# Brief 2026-09-17\n\n"
    "Review `scripts/thing.py`. Each seat must run it and execute the tests.\n"
    "Use gamma, the depletion exponent, to say whether findings are drying up, "
    "and report any rate with its interval and the script that produced it.\n"
    "The artefact is small, so the review should be short, but every claim must "
    "rest on command output rather than on reading the source.\n"
    "Propose a fix, and an executed falsifier with its output.\n"
    # The delivery rule became the validator's 8th check on 2026-09-17 (task P4),
    # so a fixture brief that omits it is no longer a VALID brief.
    "Write each fix into the sandbox repository tree at its real path, so it is delivered as a file rather than left in prose.\n"
    "State what would refute your answer.\n"
    "## Output\n\n- verdict\n- fix\n- falsifier_result\n\n"
    "Stop at diminishing returns.\n")


def _run_copied_validator(tmp_path, artefact_offset_s: float):
    """Run a COPY of the validator in tmp_path/scripts/, so its REPO is tmp_path.

    The named artefact's modification time is set to the brief's plus
    `artefact_offset_s` with os.utime, so the ordering is exact rather than
    dependent on a sleep outlasting the filesystem's timestamp resolution."""
    import os
    import shutil
    (tmp_path / "scripts").mkdir()
    copy = tmp_path / "scripts" / "panel_brief_validate.py"
    shutil.copy(VALIDATOR, copy)
    art = tmp_path / "scripts" / "thing.py"
    art.write_text("x = 1\n", encoding="utf-8")
    brief = tmp_path / "BRIEF.md"
    brief.write_text(_VALID_BRIEF, encoding="utf-8")
    b = brief.stat().st_mtime
    os.utime(art, (b + artefact_offset_s, b + artefact_offset_s))
    return subprocess.run([sys.executable, str(copy), str(brief)],
                          cwd=tmp_path, capture_output=True, text=True, timeout=120)


class TestItWarnsRatherThanRefuses:
    def test_an_overtaken_valid_brief_warns_and_exits_zero(self, tmp_path):
        """A currency warning must not block a dispatch on its own.

        EXECUTED, not read (panel round 16, 2026-09-17). The test this replaces
        sliced the validator's source and ended in `or True`, so a validator that
        printed the warning and then returned 1 passed the whole file. This runs
        the validator on a brief whose named file moved 60 s after it was
        written and reads the exit code."""
        r = _run_copied_validator(tmp_path, artefact_offset_s=60.0)
        assert "CURRENCY WARNING" in r.stderr, (
            f"the overtaken brief was not reported at all:\n{r.stderr}")
        assert "REFUSED" not in r.stderr, (
            f"a valid brief was refused once a named file moved:\n{r.stderr}")
        assert r.returncode == 0, (
            f"a currency warning changed the exit code to {r.returncode}; an "
            f"unrelated edit to a named file would then block every dispatch")

    def test_the_same_brief_unovertaken_exits_zero_with_no_warning(self, tmp_path):
        """THE CONTROL for the test above. If the fixture brief failed a refusing
        check, both runs would exit 1 and the exit-code assertion would be read
        off a broken fixture; here it must pass with no warning at all."""
        r = _run_copied_validator(tmp_path, artefact_offset_s=-60.0)
        assert r.returncode == 0, f"the fixture brief is not valid:\n{r.stderr}"
        assert "CURRENCY WARNING" not in r.stderr, r.stderr

    def test_currency_is_not_one_of_the_refusing_checks(self, mod):
        """The refusal path is CHECKS plus declared figures; read CHECKS as data."""
        assert mod.CHECKS, "the refusing checks did not load"
        assert not any("currency" in label.lower() for label, _, _ in mod.CHECKS), (
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
