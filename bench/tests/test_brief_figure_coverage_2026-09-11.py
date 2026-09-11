"""A brief can state a false number beside a true declaration and pass every check.

TASK V6 REOPENED 2026-09-11 by BOTH panel seats in round 11, independently, in
separate sandboxes. `check_declared_figures` re-executes every DECLARED figure
and refuses when the producing script does not print it. That is sound, and the
defect that created V6 walks straight past it: round 4's brief said *"`gamma` is
0.451"* in PROSE and the value is **0.415413**. Declaring nothing keeps the gate
green.

Executed, on this very repository's round-11 brief:

    panel-brief: FIGURE COVERAGE — 5 numeric claim(s) in the prose are backed
    by no declared figure:
      0.451, 0.415413, 0.0, 1.0, 3.4

It names both numbers from the incident that created the task.

IT REPORTS AND DOES NOT REFUSE, deliberately. The precedent is `check_currency`
in the same module: refusing would refuse every brief in the archive, and this
module's own words are that a guard which refuses a correct brief teaches people
to skip the validator.

THE NUMBER BOUNDARY IS THE ROUND-7 DEFECT AGAIN and is tested for it: a trailing
`.` ends a sentence and must not be eaten, so `0.415413.` is the number
`0.415413`.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts" / "panel_brief_validate.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("pbv", VALIDATE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["pbv"] = m
    spec.loader.exec_module(m)
    return m


class TestUndeclaredFigures:
    def test_the_round_four_defect_is_named(self, mod):
        text = "Section 2: `gamma` is 0.451, which is strong depletion."
        assert "0.451" in mod.undeclared_figures(text)

    def test_a_declared_value_is_not_reported(self, mod):
        text = ("<!-- figure: g | scripts/x.py | gamma 0.415413 -->\n"
                "Section 2: `gamma` is 0.415413.")
        assert mod.undeclared_figures(text) == [], mod.undeclared_figures(text)

    def test_a_number_at_the_end_of_a_sentence_keeps_its_digits(self, mod):
        """THE ROUND-7 DEFECT, which this module documents 40 lines above the
        new pattern and which a careless boundary reproduces."""
        assert mod.undeclared_figures("The value is 0.415413.") == ["0.415413"]

    def test_a_declaration_comment_is_not_prose(self, mod):
        text = "<!-- figure: g | scripts/x.py | 0.415413 -->\nNo prose numbers.\n"
        assert mod.undeclared_figures(text) == []

    def test_each_value_is_reported_once(self, mod):
        text = "It is 0.451 here and 0.451 again and 0.451 once more."
        assert mod.undeclared_figures(text) == ["0.451"]


class TestItIsWiredAndVisible:
    def test_the_validator_prints_the_coverage_report(self):
        brief = ROOT / "bench" / "logs" / "panel_round11_2026-09-11" / "BRIEF.md"
        if not brief.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        r = subprocess.run([sys.executable, str(VALIDATE), str(brief)],
                           cwd=ROOT, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        assert "FIGURE COVERAGE" in out, out[-600:]
        assert "0.451" in out and "0.415413" in out, (
            "the report no longer names the 2 numbers from the incident that "
            "created this task")

    def test_it_does_not_refuse(self):
        """The design decision, pinned. A guard that refuses a correct brief
        gets bypassed, and then it guards nothing."""
        brief = ROOT / "bench" / "logs" / "panel_round11_2026-09-11" / "BRIEF.md"
        if not brief.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        r = subprocess.run([sys.executable, str(VALIDATE), str(brief)],
                           cwd=ROOT, capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, (r.stdout + r.stderr)[-600:]


class TestTheCheckIsNotVacuous:
    def test_a_brief_with_no_prose_numbers_reports_nothing(self, mod):
        assert mod.undeclared_figures("All words and no numerals here.") == []

    def test_the_live_brief_really_does_carry_undeclared_numbers(self, mod):
        """ANTI-VACUITY. If it did not, the wiring test above would pass on
        silence and prove nothing."""
        brief = ROOT / "bench" / "logs" / "panel_round11_2026-09-11" / "BRIEF.md"
        if not brief.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        assert len(mod.undeclared_figures(brief.read_text())) >= 3
