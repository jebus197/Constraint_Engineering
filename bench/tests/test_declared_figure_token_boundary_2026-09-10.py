"""The declared-figure guard must refuse a number the script did not print,
AND must accept one it did. The round-6 repair got both directions wrong.

WHY THIS FILE EXISTS. `check_declared_figures` is the only mechanism in this
repository that re-executes a figure quoted in a panel brief instead of
trusting it. It has now been wrong twice. Round 6 found it matching by
SUBSTRING -- a declared `0.29` reproduced against a printed `0.294998`. The
repair expressed "whole token" as a fixed character class,
`(?<![0-9A-Za-z.\\-])` ... `(?![0-9A-Za-z.\\-])`, and that class is wrong in
BOTH directions. Panel round 7 measured both by execution:

  * STILL PASSES WRONG NUMBERS. `,` is not in the class, so a declared `234`
    reproduces against a script printing `entries = 1,234`. That is the round-6
    defect with a thousands separator instead of a decimal point, and the
    figure it lets through is wrong by a factor of 5. `elapsed 12:345` against
    a declared `345` goes through the same hole.
  * REFUSES RIGHT NUMBERS. `.` is in the class unconditionally, so a script
    printing `gamma is 0.294998.` -- the figure at the end of a sentence --
    cannot be declared at all. A guard that refuses a correct brief is a guard
    that gets bypassed, and this one blocks a PAID dispatch.

THE MEASUREMENT THAT MOTIVATED IT, and the one this file argues with. The
round-6 change is reported as scoring "8 of 8" over the table in
`test_panel_brief_format_2026-09-09.py`. Four of those 8 cases (`0.2`, `0.4`,
`1`, `9`) are refused by the 3-significant-character rule and never reach the
token rule at all, and 2 more (`0.451`, `0.415413`) are simply absent from the
output and would be refused by a plain substring test. Exactly ONE case,
`0.29`, exercises the token boundary. The token rule's real support is 1 of 1,
Wilson [20.6549%, 100.0000%] -- an interval that contains almost everything.
The cases below are the ones that were missing.

Nothing here is removed. The final test re-runs the whole round-6 table
against the new predicate, so a future repair cannot buy these cases by
giving back the ones already paid for.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "pbv_boundary", ROOT / "scripts" / "panel_brief_validate.py")
pbv = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(pbv)


# ---------------------------------------------------------------------------
# The predicate, directly. No subprocess, so a failure here names the rule
# rather than the plumbing.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("want,haystack,found,why", [
    # --- must NOT be found: the declared figure is not the printed one ------
    ("234", "entries = 1,234", False,
     "a thousands separator: 234 against a printed 1,234 is wrong by 5x"),
    ("345", "elapsed 12:345", False,
     "a colon binds a number the same way a comma does"),
    ("0.29", "gamma (Duane slope) : 0.294998", False,
     "the round-6 defect itself must stay refused"),
    ("294998", "gamma = 0.294998", False,
     "the fractional part of a decimal is not the decimal"),
    ("0.25", "delta = -0.25", False,
     "a sign changes the number; the magnitude alone must not reproduce"),
    ("2026", "dated 2026-09-10", False,
     "a date field is not a count"),
    ("0.294998", "gamma_0.294998", False,
     "an underscore joins an identifier to its value; that is one token"),
    ("1,234", "total 11,234 rows", False,
     "a grouped number inside a longer grouped number"),
    # --- MUST be found: the script really did print this figure -------------
    ("0.294998", "gamma is 0.294998.", True,
     "a figure at the end of a sentence must still be declarable"),
    ("0.294998", "gamma (0.294998)", True,
     "brackets are not part of the number"),
    ("0.294998", "  gamma (Duane slope)    : 0.294998\n", True,
     "the live format of the script this guard is pointed at"),
    ("-0.25", "delta = -0.25 units", True, "a negative figure is declarable"),
    ("42.5%", "rate = 42.5% of runs", True, "a percentage is declarable"),
    ("entries = 84", "entries = 84\n", True,
     "the remedy the guard's own message recommends must work"),
    ("234", "entries, 234 rows", True,
     "a comma with a space after it is punctuation, not a thousands separator"),
    ("1,234", "entries = 1,234\n", True,
     "a grouped number declared in full still reproduces"),
])
def test_the_figure_boundary_is_decided_by_context(want, haystack, found, why):
    assert pbv._figure_token_found(want, haystack) is found, (
        f"{want!r} in {haystack!r}: {why}")


# ---------------------------------------------------------------------------
# End to end, through check_declared_figures, with a real subprocess.
# ---------------------------------------------------------------------------

def _decl(script: str, value: str) -> str:
    return f"<!-- figure: probe | {script} | {value} -->"


def test_a_thousands_separator_no_longer_launders_a_wrong_count(tmp_path):
    (tmp_path / "s.py").write_text("print('entries = 1,234')\n", encoding="utf-8")
    problems = pbv.check_declared_figures(_decl("s.py", "234"), repo=tmp_path,
                                          timeout=60)
    assert problems, (
        "a brief declaring 234 reproduced against a script printing 1,234; the "
        "guard exists to refuse exactly this")
    assert not pbv.check_declared_figures(_decl("s.py", "entries = 1,234"),
                                          repo=tmp_path, timeout=60), (
        "the true figure must still reproduce, or the guard blocks correct work")


def test_a_figure_at_the_end_of_a_sentence_is_declarable(tmp_path):
    (tmp_path / "s.py").write_text("print('gamma is 0.294998.')\n", encoding="utf-8")
    assert pbv.check_declared_figures(_decl("s.py", "0.294998"), repo=tmp_path,
                                       timeout=60) == [], (
        "a full stop after the figure made a correct brief unrefusable-by-any-"
        "other-means and refused it; a guard that refuses right answers is "
        "bypassed within a day")


def test_a_figure_is_not_manufactured_in_the_seam_between_two_streams(tmp_path):
    """`r.stdout + r.stderr` spliced the streams with no separator."""
    (tmp_path / "s.py").write_text(
        "import sys\n"
        "sys.stdout.write('rate = 0.2')\n"
        "sys.stderr.write('9 done')\n", encoding="utf-8")
    problems = pbv.check_declared_figures(_decl("s.py", "rate = 0.29"),
                                          repo=tmp_path, timeout=60)
    assert problems, (
        "neither stream printed 'rate = 0.29'; it existed only where the two "
        "were concatenated, and the guard reported the figure as reproduced")


def test_stderr_only_output_still_counts(tmp_path):
    """The join must not cost the stderr case the guard already handled."""
    (tmp_path / "s.py").write_text(
        "import sys; print('gamma = 0.294998', file=sys.stderr)\n", encoding="utf-8")
    assert pbv.check_declared_figures(_decl("s.py", "gamma = 0.294998"),
                                       repo=tmp_path, timeout=60) == []


# ---------------------------------------------------------------------------
# Nothing paid for is given back.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("want,haystack,found", [
    ("0.294998", "gamma (Duane slope)    : 0.294998", True),
    ("0.451", "gamma (Duane slope)    : 0.294998", False),
    ("0.29", "gamma (Duane slope)    : 0.294998", False),
    ("0.2", "gamma (Duane slope)    : 0.294998", False),
    ("0.4", "gamma (Duane slope)    : 0.294998", False),
    ("0.415413", "gamma (Duane slope)    : 0.294998", False),
])
def test_the_round_six_table_still_holds_under_the_new_predicate(want, haystack, found):
    """The 6 round-6 cases that reach the token rule at all.

    `1` and `9` are excluded here because they never reach it -- the
    3-significant-character rule refuses them first, which is precisely the
    point made in this file's docstring about the '8 of 8' figure.
    """
    assert pbv._figure_token_found(want, haystack) is found
