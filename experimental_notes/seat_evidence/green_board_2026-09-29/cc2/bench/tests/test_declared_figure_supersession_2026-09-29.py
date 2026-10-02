# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'green_board_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 74a9e146a5c42e9a8a8db799bc70a84e22222832e574bd969808b36d32591610
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""An archived brief's figure drifts when the corpus grows, and the guard must
neither refuse the record nor stop checking it (panel item 1, 2026-09-29).

WHAT WENT RED AND WHY IT WAS NOT A CODE DEFECT. `bench/logs/panel_round11_
2026-09-11/BRIEF.md` declares `real-rejection rate : 2/640 = 0.3125%`. The
producer, `scripts/archived_falsifier_rejections_2026-09-10.py`, now prints
`2/716 = 0.2793%`. The SAME 2 real rejections; 76 more archived sources under
them. The brief was correct on 2026-09-11 and
`test_brief_figure_coverage_2026-09-11.py::test_it_does_not_refuse` went red
because the artefact pair (brief, growing archive) moved, not because the
validator broke.

THE 2 OBVIOUS REPAIRS ARE BOTH FORBIDDEN. Editing BRIEF.md falsifies the record
of what 2 seats were given. Exempting archived briefs deletes the check for every
brief that has ever been dispatched.

WHAT IS TESTED HERE is the third option: a `FIGURE_DRIFT.md` sidecar beside the
brief whose superseding value is RE-EXECUTED with the same predicate. Every test
below is an EXECUTION of `check_declared_figures`, never an assertion about the
validator's source text. The 5 refusal tests are what stop this from being an
exemption: each one is a way someone could try to silence the guard, and each is
still refused.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts" / "panel_brief_validate.py"
ROUND11 = ROOT / "bench" / "logs" / "panel_round11_2026-09-11"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("pbv_supersede", VALIDATE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["pbv_supersede"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def bed(tmp_path):
    """A miniature repo: 1 script printing 1 figure, 1 dated brief directory."""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "producer.py").write_text(
        "print('rate : 2/716 = 0.2793%')\n")
    bdir = repo / "bench" / "logs" / "panel_roundZ_2026-01-01"
    bdir.mkdir(parents=True)
    brief = bdir / "BRIEF.md"
    brief.write_text(
        "<!-- figure: the rate | scripts/producer.py | rate : 2/640 = 0.3125% -->\n")
    return {"repo": repo, "brief": brief, "dir": bdir,
            "text": brief.read_text()}


def _sidecar(bed, body):
    (bed["dir"] / "FIGURE_DRIFT.md").write_text(body)


class TestTheGuardStillRefuses:
    """5 ways to try to silence it. All 5 still refuse."""

    def test_with_no_sidecar_a_drifted_figure_is_refused(self, mod, bed):
        problems = mod.check_declared_figures(
            bed["text"], repo=bed["repo"], brief_path=bed["brief"])
        assert len(problems) == 1, problems
        assert "does not print it" in problems[0], problems[0]

    def test_a_caller_that_passes_no_brief_path_keeps_the_old_strictness(
            self, mod, bed):
        """The parameter is opt-in, so no existing caller was loosened."""
        _sidecar(bed, "<!-- figure-superseded: 2026-09-29 | the rate | "
                      "scripts/producer.py | rate : 2/716 = 0.2793% -->\n")
        problems = mod.check_declared_figures(bed["text"], repo=bed["repo"])
        assert len(problems) == 1, problems
        assert "does not print it" in problems[0]

    def test_a_supersession_the_script_does_not_print_is_refused(self, mod, bed):
        """THE TEETH. A sidecar cannot assert a number into existence."""
        _sidecar(bed, "<!-- figure-superseded: 2026-09-29 | the rate | "
                      "scripts/producer.py | rate : 2/999 = 0.2002% -->\n")
        problems = mod.check_declared_figures(
            bed["text"], repo=bed["repo"], brief_path=bed["brief"])
        assert len(problems) == 1, problems
        assert "prints NEITHER" in problems[0], problems[0]

    @pytest.mark.parametrize("when", ["2026-01-01", "2025-12-31"])
    def test_a_supersession_that_does_not_postdate_the_brief_is_refused(
            self, mod, bed, when):
        """A brief being validated the day it is written -- the guard's real
        subject -- has no reconciliation available."""
        _sidecar(bed, f"<!-- figure-superseded: {when} | the rate | "
                      f"scripts/producer.py | rate : 2/716 = 0.2793% -->\n")
        problems = mod.check_declared_figures(
            bed["text"], repo=bed["repo"], brief_path=bed["brief"])
        assert len(problems) == 1, problems
        assert "does not postdate the brief" in problems[0], problems[0]

    def test_a_malformed_record_refuses_instead_of_vanishing(self, mod, bed):
        """The FIGURE_OPENER lesson, applied to the new grammar."""
        _sidecar(bed, "<!-- figure-superseded: 2026-09-29 | the rate -->\n")
        problems = mod.check_declared_figures(
            bed["text"], repo=bed["repo"], brief_path=bed["brief"])
        assert any("do not parse" in p for p in problems), problems

    def test_two_records_for_one_figure_refuse(self, mod, bed):
        _sidecar(bed, "<!-- figure-superseded: 2026-09-29 | the rate | "
                      "scripts/producer.py | rate : 2/716 = 0.2793% -->\n"
                      "<!-- figure-superseded: 2026-09-30 | the rate | "
                      "scripts/producer.py | rate : 2/716 = 0.2793% -->\n")
        problems = mod.check_declared_figures(
            bed["text"], repo=bed["repo"], brief_path=bed["brief"])
        assert any("2 supersession records" in p for p in problems), problems

    def test_an_unspecific_supersession_is_refused(self, mod, bed):
        """The 3-significant-character rule reaches the new value too."""
        (bed["repo"] / "scripts" / "producer.py").write_text("print('pass 2:')\n")
        _sidecar(bed, "<!-- figure-superseded: 2026-09-29 | the rate | "
                      "scripts/producer.py | 2 -->\n")
        problems = mod.check_declared_figures(
            bed["text"], repo=bed["repo"], brief_path=bed["brief"])
        assert any("fewer than 3 significant characters" in p for p in problems), \
            problems


class TestTheGuardReconciles:
    def test_a_re_executed_supersession_clears_the_refusal_and_is_reported(
            self, mod, bed):
        _sidecar(bed, "<!-- figure-superseded: 2026-09-29 | the rate | "
                      "scripts/producer.py | rate : 2/716 = 0.2793% -->\n")
        notes: list[str] = []
        problems = mod.check_declared_figures(
            bed["text"], repo=bed["repo"], brief_path=bed["brief"], notes=notes)
        assert problems == [], problems
        assert len(notes) == 1, notes
        assert "2/640" in notes[0] and "2/716" in notes[0], notes[0]

    def test_a_figure_that_still_reproduces_needs_no_sidecar(self, mod, bed):
        text = ("<!-- figure: the rate | scripts/producer.py | "
                "rate : 2/716 = 0.2793% -->\n")
        notes: list[str] = []
        assert mod.check_declared_figures(
            text, repo=bed["repo"], brief_path=bed["brief"], notes=notes) == []
        assert notes == [], notes


class TestItIsWiredToTheRealBrief:
    """Executed against the repository's own round-11 brief, end to end."""

    def test_the_round_eleven_figure_really_has_drifted(self, mod):
        """ANTI-VACUITY. Without the sidecar the declaration still fails, so the
        mechanism below is load-bearing rather than decorative."""
        brief = ROUND11 / "BRIEF.md"
        if not brief.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        problems = mod.check_declared_figures(brief.read_text())
        assert len(problems) == 1, problems
        assert "2/640 = 0.3125%" in problems[0], problems[0]

    def test_the_sidecar_exists_and_the_brief_is_not_edited(self):
        brief = ROUND11 / "BRIEF.md"
        if not brief.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        assert (ROUND11 / "FIGURE_DRIFT.md").is_file()
        assert "2/640 = 0.3125%" in brief.read_text(), (
            "the archived brief was edited; it is the record of what the seats "
            "were given and the drift belongs in the sidecar")

    def test_the_validator_exits_zero_and_names_both_numbers(self):
        brief = ROUND11 / "BRIEF.md"
        if not brief.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        r = subprocess.run([sys.executable, str(VALIDATE), str(brief)],
                           cwd=ROOT, capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
        assert r.returncode == 0, out[-800:]
        assert "FIGURE DRIFT" in out, out[-800:]
        assert "2/640 = 0.3125%" in out and "2/716 = 0.2793%" in out, out[-800:]
