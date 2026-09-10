"""check_declared_figures: the holes the whole-token fix left open.

Panel round 7, 2026-09-10. The round-6 hardening moved the guard from substring
to whole-token matching and added the 3-significant-character floor. Driving the
guard adversarially found 6 residual holes, each demonstrated by EXECUTION
before this file was written:

  1. NUMERIC SEPARATORS ARE TOKEN DELIMITERS. Declared ``234`` reproduced
     against a printed ``total = 1,234`` and declared ``294998`` against
     ``n = 1_294998`` -- the comma and underscore fall outside the token
     character class, so a truncated (wrong) number passes the guard whose one
     job is refusing wrong numbers.
  2. THE SCRIPT PATH IS NOT CONFINED. ``repo / rel`` with ``rel`` starting
     ``../`` or absolute executes an arbitrary script OUTSIDE the repository
     and accepts its output as evidence. A figure must be re-executable from
     the repository, or it is not a committed measurement.
  3. A MALFORMED DECLARATION IS SILENTLY IGNORED. ``<!-- figure: g | s.py -->``
     (value field missing) does not match the FIGURE regex, so the guard skips
     it and the brief PASSES -- a declaration that announces itself and then
     escapes checking, which is the guard failing silently in the exact
     direction it exists to check.
  4. STREAM SPLICE. ``r.stdout + r.stderr`` with no separator can manufacture
     a token neither stream printed: stdout ending ``0.2`` (no newline) and
     stderr starting ``94998`` matched a declared ``0.294998``.

Every test here CALLS the guard; none asserts on source text.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "pbv_figures_under_test", REPO / "scripts" / "panel_brief_validate.py")
pbv = importlib.util.module_from_spec(_spec)
sys.modules["pbv_figures_under_test"] = pbv
_spec.loader.exec_module(pbv)


@pytest.fixture()
def figrepo(tmp_path):
    (tmp_path / "scripts").mkdir()
    return tmp_path


def _script(figrepo: Path, name: str, body: str) -> str:
    p = figrepo / "scripts" / name
    p.write_text(body, encoding="utf-8")
    return f"scripts/{name}"


def _check(figrepo: Path, brief: str) -> list[str]:
    return pbv.check_declared_figures(brief, repo=figrepo, timeout=60)


class TestWhatMustStillPass:
    """The round-6 behaviour the hardening must not regress."""

    def test_exact_figure_reproduces(self, figrepo):
        rel = _script(figrepo, "s.py", "print('gamma = 0.294998')")
        assert _check(figrepo, f"<!-- figure: g | {rel} | 0.294998 -->") == []

    def test_truncated_figure_refused(self, figrepo):
        """The original round-6 defect: 0.29 must not ride on 0.294998."""
        rel = _script(figrepo, "s.py", "print('gamma = 0.294998')")
        assert _check(figrepo, f"<!-- figure: g | {rel} | 0.29 -->")

    def test_figure_followed_by_prose_comma_still_accepted(self, figrepo):
        """A comma AFTER a number is punctuation, not a digit separator.

        The separator fix must not refuse 'gamma = 0.294998, which fails' --
        that is the common shape of a sentence quoting a figure.
        """
        rel = _script(figrepo, "s.py", "print('gamma = 0.294998, which fails')")
        assert _check(figrepo, f"<!-- figure: g | {rel} | 0.294998 -->") == []

    def test_stderr_only_figure_accepted(self, figrepo):
        rel = _script(figrepo, "s.py",
                      "import sys; sys.stderr.write('gamma = 0.294998\\n')")
        assert _check(figrepo, f"<!-- figure: g | {rel} | 0.294998 -->") == []

    def test_nonzero_exit_refused(self, figrepo):
        rel = _script(figrepo, "s.py",
                      "print('gamma = 0.294998'); raise SystemExit(3)")
        probs = _check(figrepo, f"<!-- figure: g | {rel} | 0.294998 -->")
        assert probs and "exited 3" in probs[0]


class TestNumericSeparators:
    def test_comma_separated_thousands_do_not_leak_a_suffix(self, figrepo):
        """Declared 234 must NOT reproduce against a printed 1,234."""
        rel = _script(figrepo, "s.py", "print('total = 1,234')")
        assert _check(figrepo, f"<!-- figure: t | {rel} | 234 -->"), (
            "declared 234 reproduced against printed 1,234: the comma acts as "
            "a token delimiter and a wrong number passes the guard")

    def test_underscore_separated_literal_does_not_leak_a_suffix(self, figrepo):
        """Declared 294998 must NOT reproduce against a printed 1_294998."""
        rel = _script(figrepo, "s.py", "print('n = 1_294998')")
        assert _check(figrepo, f"<!-- figure: n | {rel} | 294998 -->"), (
            "declared 294998 reproduced against printed 1_294998")

    def test_a_declared_value_containing_a_comma_still_matches_itself(self, figrepo):
        rel = _script(figrepo, "s.py", "print('total = 1,234')")
        assert _check(figrepo, f"<!-- figure: t | {rel} | 1,234 -->") == []


class TestPathConfinement:
    def test_dotdot_escape_is_refused_and_not_executed(self, figrepo, tmp_path_factory):
        outside_dir = tmp_path_factory.mktemp("outside")
        evil = outside_dir / "evil.py"
        marker = outside_dir / "executed.marker"
        evil.write_text(
            f"import pathlib\n"
            f"pathlib.Path({str(marker)!r}).write_text('ran')\n"
            f"print('999888777')\n", encoding="utf-8")
        depth = len(figrepo.resolve().parts) - 1
        rel = ("../" * depth) + str(evil.resolve()).lstrip("/")
        probs = _check(figrepo, f"<!-- figure: e | {rel} | 999888777 -->")
        assert probs, "a ../ escape produced a passing figure"
        assert not marker.exists(), (
            "the validator EXECUTED a script outside the repository; "
            "confinement must refuse before running, not after")

    def test_absolute_path_is_refused_and_not_executed(self, figrepo, tmp_path_factory):
        outside_dir = tmp_path_factory.mktemp("outside_abs")
        evil = outside_dir / "evil.py"
        marker = outside_dir / "executed.marker"
        evil.write_text(
            f"import pathlib\n"
            f"pathlib.Path({str(marker)!r}).write_text('ran')\n"
            f"print('999888777')\n", encoding="utf-8")
        probs = _check(figrepo, f"<!-- figure: e | {evil} | 999888777 -->")
        assert probs, "an absolute path produced a passing figure"
        assert not marker.exists(), (
            "the validator EXECUTED a script at an absolute path outside the repo")


class TestMalformedDeclarations:
    def test_a_declaration_missing_its_value_field_is_refused(self, figrepo):
        """A comment that says 'figure:' and does not parse must refuse, not skip."""
        rel = _script(figrepo, "s.py", "print('gamma = 0.294998')")
        assert _check(figrepo, f"<!-- figure: g | {rel} -->"), (
            "a malformed figure declaration was silently ignored and the brief "
            "passed; opt-in means an ABSENT declaration passes, not a broken one")

    def test_a_wellformed_declaration_is_not_double_counted(self, figrepo):
        rel = _script(figrepo, "s.py", "print('gamma = 0.294998')")
        assert _check(figrepo, f"<!-- figure: g | {rel} | 0.294998 -->") == []


class TestStreamSplice:
    def test_token_spliced_across_stdout_and_stderr_is_refused(self, figrepo):
        rel = _script(
            figrepo, "s.py",
            "import sys\n"
            "sys.stdout.write('x = 0.2')\n"
            "sys.stdout.flush()\n"
            "sys.stderr.write('94998 warnings')\n")
        assert _check(figrepo, f"<!-- figure: g | {rel} | 0.294998 -->"), (
            "stdout ending '0.2' and stderr starting '94998' were concatenated "
            "into a token neither stream printed")
