"""A declared figure is a claim about evidence AS OF the brief's date.

ADDED 2026-09-29 (panel, green-board item 1). The round-11 brief declared
`real-rejection rate : 2/640 = 0.3125%`; the 4 commissioning rehearsals of
2026-09-21/22 grew the corpus to 716 with the NUMERATOR unchanged, and the
declared figure stopped re-executing. The brief was true when sent.

THE RULING THESE TESTS PIN. The guard's refusal subject is a brief about to
be DISPATCHED; an archived brief is a record, and its figure carries the
denominator as of its date. Neither horn of the brief's dilemma is taken:
the record is NOT edited, and archived briefs are NOT exempted. The figure is
still RE-EXECUTED -- against the corpus its own date names, via the
producer's `--as-of` -- so it stays decidable by a tool forever. The
acceptance is gated on evidence that the brief EXISTED at the date it claims
(its mtime), which is what closes the dodge a bare date cut would open.

EXECUTE, DO NOT GREP: every case below runs the producer or the predicate;
none asserts on source text.
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts" / "panel_brief_validate.py"
PRODUCER = ROOT / "scripts" / "archived_falsifier_rejections_2026-09-10.py"
BRIEF = ROOT / "bench" / "logs" / "panel_round11_2026-09-11" / "BRIEF.md"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("pbv_asof", VALIDATE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["pbv_asof"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def archive_grew():
    """These tests are about a corpus that has moved past the brief's date.
    If the commissioning rehearsals are absent the corpus is back at 640 and
    the strict check passes on its own -- nothing here is exercised."""
    if not sorted((ROOT / "bench" / "logs").glob("commissioning_*")):
        pytest.skip("archive has not grown past 2026-09-11 in this checkout")


class TestTheProducerAsOf:
    def test_as_of_the_briefs_date_reproduces_the_declared_figure(self):
        """The historical figure is DECIDABLE, not trusted: 2/640 = 0.3125%
        re-executes against the corpus as it stood."""
        r = subprocess.run(
            [sys.executable, str(PRODUCER), "--as-of", "2026-09-11"],
            cwd=ROOT, capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stderr[-600:]
        assert "real-rejection rate : 2/640 = 0.3125%" in r.stdout, (
            "the archive as of 2026-09-11 no longer yields the round-11 "
            "figure; the historical record itself is now in question:\n"
            + r.stdout[-600:])

    def test_unrestricted_still_reports_the_live_corpus(self, archive_grew):
        """The flag must not have bent the live measurement (additive check:
        the default path is byte-identical in what it measures)."""
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           cwd=ROOT, capture_output=True, text=True,
                           timeout=600)
        assert r.returncode == 0, r.stderr[-600:]
        assert "real-rejection rate : 2/640 " not in r.stdout, (
            "the unrestricted run reports the 2026-09-11 corpus, so --as-of "
            "leaked into the default path")

    def test_a_malformed_as_of_is_refused_loudly(self):
        r = subprocess.run(
            [sys.executable, str(PRODUCER), "--as-of", "yesterday"],
            cwd=ROOT, capture_output=True, text=True, timeout=120)
        assert r.returncode != 0
        assert "yesterday" in (r.stdout + r.stderr)


class TestTheValidatorRuling:
    def test_the_archived_brief_is_not_refused(self, archive_grew):
        """Item 1's failing assertion, now green for the RIGHT reason: the
        figure re-executed as of the brief's date, was accepted loudly, and
        the record was not edited (the 2/640 text is intact on disk)."""
        if not BRIEF.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        assert "2/640 = 0.3125%" in BRIEF.read_text(), (
            "the archived brief was EDITED -- that falsifies the record of "
            "what the seats were given, and is exactly the fix this ruling "
            "forbids")
        r = subprocess.run([sys.executable, str(VALIDATE), str(BRIEF)],
                           cwd=ROOT, capture_output=True, text=True,
                           timeout=1200)
        assert r.returncode == 0, (r.stdout + r.stderr)[-800:]
        assert "HISTORICAL FIGURE" in (r.stdout + r.stderr), (
            "the acceptance was silent; a quiet historical acceptance is how "
            "an exemption rots into a hole")

    def test_a_fresh_brief_claiming_a_past_date_is_still_refused(
            self, mod, tmp_path, archive_grew):
        """THE DODGE, executed. A brief written TODAY that carries only past
        dates and declares last week's figure must be refused: its mtime
        post-dates the date it claims, so the historical gate stays shut.
        This is the test that proves the guard was not weakened at dispatch.
        """
        if not BRIEF.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        dodge = tmp_path / "BRIEF.md"
        shutil.copyfile(BRIEF, dodge)   # same text, same past dates; mtime NOW
        text = dodge.read_text()
        problems = mod.check_declared_figures(text, brief_path=dodge)
        assert any("2/640" in p and "does not print it" in p
                   for p in problems), (
            f"a freshly written brief re-declared a stale figure and was not "
            f"refused: {problems}")

    def test_a_figure_that_never_was_true_is_refused_even_archived(
            self, mod, archive_grew):
        """The other unsafe direction: the historical path re-executes, it
        does not exempt. A wrong figure fails as-of its date too."""
        if not BRIEF.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        text = BRIEF.read_text().replace(
            "real-rejection rate : 2/640 = 0.3125%",
            "real-rejection rate : 3/640 = 0.4688%")
        problems = mod.check_declared_figures(text, brief_path=BRIEF)
        assert any("3/640" in p and "does not print it" in p
                   for p in problems), (
            f"a figure false at EVERY date passed the historical path: "
            f"{problems}")

    def test_a_producer_without_as_of_fails_closed(self, mod, tmp_path):
        """A declared figure whose producer has no --as-of keeps the original
        refusal untouched: the retry exits non-zero and is discarded."""
        script = ROOT / "scripts" / "_asof_probe_2026-09-29_tmp.py"
        script.write_text(
            "import sys\n"
            "if len(sys.argv) > 1: sys.exit(2)\n"
            "print('probe rate : 5/999')\n")
        try:
            brief = tmp_path / "B.md"
            brief.write_text("dated 2026-09-11\n")
            text = ("<!-- figure: probe | scripts/_asof_probe_2026-09-29_tmp.py"
                    " | probe rate : 4/999 -->\ndated 2026-09-11\n")
            problems = mod.check_declared_figures(text, brief_path=brief)
            assert any("4/999" in p for p in problems), problems
        finally:
            script.unlink()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
