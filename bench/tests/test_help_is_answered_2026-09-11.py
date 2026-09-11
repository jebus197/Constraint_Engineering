"""`--help` must be ANSWERED, not merely survived.

MEASURED 2026-09-11. `scripts/measurement_scripts_only_2026-09-11.py --run`
executes every script it classes as a measurement with `--help` and reports how
many "did not answer --help cleanly". It decided that on the EXIT CODE alone.

A script with no argument parser does not answer `--help`: it ignores the flag,
runs its entire measurement, and exits 0. Exit 0 and an answer are
indistinguishable to an exit-code test. Requiring a `usage:` line instead, over
the 53 scripts then classed as measurements:

    answered --help with a usage line : 23
    exited 0 but printed NO usage line: 30
    not answering: 30/53 = 56.6038%
      Wilson 95%          : [43.2654%, 69.0496%]  (statsmodels)
      Clopper-Pearson 95% : [42.2826%, 70.1608%]  (statsmodels/beta; scipy
                                                   agrees to 1.1e-16)

Producing script: `scripts/help_is_answered_2026-09-11.py`.

HOW IT SURFACED. In the maintainer's tree all 53 exited 0. In a fresh clone 2
of them failed -- `build_experiment_report.py` on an archived log that
`.gitignore` excludes, and `check_model_keys.py` because a clone has no .env --
and those were 2 of the 3 failures that made task A2's "a fresh clone is green"
untrue. The other 28 carried the same defect silently.

THE CONTROL THAT MAKES THIS FILE MEAN SOMETHING. The repository now reports
0 of 54, so a test asserting "0" would pass whether or not the criterion works.
`TestTheCriterionCanFail` builds a script that ignores the flag and requires the
criterion to catch it.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec.loader.exec_module(m)
    finally:
        sys.path.remove(str(SCRIPTS))
    return m


@pytest.fixture(scope="module")
def cli_help():
    return _load("cli_help", SCRIPTS / "_cli_help.py")


@pytest.fixture(scope="module")
def prober():
    return _load("help_is_answered", SCRIPTS / "help_is_answered_2026-09-11.py")


class TestTheHelperIsANoOpWithoutTheFlag:
    """The property that makes it safe to drop into a script that parses
    nothing: any other argv, including none, reaches the same code as before."""

    def test_no_arguments_returns_none(self, cli_help, capsys):
        assert cli_help.answer_help("doc", "x.py", argv=[]) is None
        assert capsys.readouterr().out == ""

    def test_an_unrelated_argument_is_refused_rather_than_returned(
            self, cli_help, capsys):
        """THIS TEST ASSERTED THE OPPOSITE FOR AN HOUR and was right to be
        changed. The first contract was "a no-op unless a help flag is present",
        so `--run 7` returned None and the script ran its measurement as though
        nothing had been typed -- an unrecognised argument reading as success,
        which is the defect class the project already names. The contract is now
        "this script takes no arguments", and the refusal is asserted below in
        TestAnUnrecognisedArgumentIsRefused."""
        with pytest.raises(SystemExit) as e:
            cli_help.answer_help("doc", "x.py", argv=["--run", "7"])
        assert e.value.code == 2
        assert capsys.readouterr().out == "", (
            "a refusal belongs on stderr, so a caller piping stdout still sees it")

    @pytest.mark.parametrize("flag", ["-h", "--help"])
    def test_a_help_flag_exits_zero_with_usage(self, cli_help, capsys, flag):
        with pytest.raises(SystemExit) as e:
            cli_help.answer_help("What it does.", "thing.py", argv=[flag])
        assert e.value.code == 0
        out = capsys.readouterr().out
        assert out.splitlines()[0] == "usage: thing.py [-h]"
        assert "What it does." in out

    def test_a_missing_docstring_still_produces_usage(self, cli_help, capsys):
        """A script with no docstring must still answer, or the helper would
        hand back an empty page and look like a failure."""
        with pytest.raises(SystemExit):
            cli_help.answer_help(None, "thing.py", argv=["--help"])
        out = capsys.readouterr().out
        assert out.startswith("usage: thing.py [-h]")
        assert "no description" in out


class TestThePredicate:
    @pytest.mark.parametrize("blob,expected", [
        ("usage: x.py [-h]\n", True),
        ("   usage: x.py\n", True),          # argparse may indent
        ("USAGE: x.py\n", True),             # case
        ("Usage of the tool\n", False),      # not a usage LINE
        ("some output\nand more\n", False),
        ("", False),
        (None, False),
    ])
    def test_it_reads_a_usage_line(self, cli_help, blob, expected):
        assert cli_help.usage_line_present(blob) is expected

    def test_the_survey_and_the_prober_share_one_definition(self, prober):
        """2 copies of this predicate would be 2 representations of 1 truth with
        no comparator -- and the weaker exit-code copy inside the survey is
        exactly how 30 scripts passed while ignoring the flag."""
        sys.path.insert(0, str(SCRIPTS))
        try:
            from _cli_help import usage_line_present as shared
            survey_src = (SCRIPTS / "measurement_scripts_only_2026-09-11.py") \
                .read_text(encoding="utf-8")
            assert "from _cli_help import usage_line_present" in survey_src, (
                "the survey has stopped importing the shared predicate")
            _ok, _why = prober.answers_help(SCRIPTS / "_cli_help.py")
            assert _ok, "the helper does not answer its own --help"
            assert shared("usage: x\n") is True
        finally:
            sys.path.remove(str(SCRIPTS))


class TestTheCriterionCanFail:
    """ANTI-VACUITY. The repository now reports 0 of 54, so every assertion
    about the current state passes whether or not the criterion works."""

    def _script(self, tmp_path: Path, body: str) -> Path:
        p = tmp_path / "probe_script.py"
        p.write_text(body, encoding="utf-8")
        return p

    def test_a_script_that_ignores_the_flag_is_caught(self, prober, tmp_path):
        p = self._script(tmp_path,
                         "print('doing the whole measurement')\n")
        ok, why = prober.answers_help(p)
        assert ok is False, (
            "a script that ignores --help, does its work and exits 0 was read "
            "as having answered -- which is the 2026-09-11 defect exactly")
        assert "no usage line" in why

    def test_a_script_with_argparse_is_accepted(self, prober, tmp_path):
        p = self._script(tmp_path,
                         "import argparse\n"
                         "argparse.ArgumentParser(description='d').parse_args()\n")
        ok, why = prober.answers_help(p)
        assert ok is True, why

    def test_a_script_using_the_helper_is_accepted(self, prober, tmp_path):
        p = self._script(
            tmp_path,
            '"""A probe."""\n'
            "import sys\n"
            f"sys.path.insert(0, {str(SCRIPTS)!r})\n"
            "from _cli_help import answer_help\n"
            "answer_help(__doc__, __file__)\n"
            "print('work')\n")
        ok, why = prober.answers_help(p)
        assert ok is True, why

    def test_a_script_that_crashes_is_caught(self, prober, tmp_path):
        p = self._script(tmp_path, "raise SystemExit(3)\n")
        ok, why = prober.answers_help(p)
        assert ok is False
        assert "exit 3" in why


class TestTheWiringIsReal:
    def test_every_measurement_script_is_covered(self, prober):
        """Structural where it is decidable, EXECUTED where it is not.

        The first version asked only whether each script mentions `argparse` or
        `answer_help`, and named 5 that do neither: competence_provenance.py,
        materiality_population_2026-09-10.py, note_vagueness_lint.py,
        quote_exemption_effect_2026-09-09.py and
        target_mutation_arrival_2026-09-08.py. All 5 answer `--help` perfectly
        well with a hand-rolled check -- note_vagueness_lint.py's exists because
        it once consumed the flag as a FILENAME. A structural test that fails on
        a working script is manufacturing the defect it exists to find, which is
        a fault this repository has already recorded once, in
        test_line_citations_resolve_2026-09-01.py's hyphen note.

        So the structural check is kept as the cheap path and anything it cannot
        vouch for is RUN. That is a handful of subprocesses, not 54.
        """
        unvouched = []
        for p in prober.measurement_scripts():
            src = p.read_text(encoding="utf-8")
            if "answer_help(" in src or "argparse" in src:
                continue
            unvouched.append(p)
        failures = []
        for p in unvouched:
            ok, why = prober.answers_help(p)
            if not ok:
                failures.append(f"{p.name}: {why}")
        assert not failures, (
            f"{len(failures)} measurement script(s) neither parse arguments nor "
            f"answer --help when run, so the flag runs the whole "
            f"measurement: {failures}")

    def test_the_unvouched_path_is_actually_exercised(self, prober):
        """ANTI-VACUITY for the test above. If every script mentioned argparse,
        the executed branch would never run and the test would be structural
        only -- passing on a premise it never checked."""
        unvouched = [p.name for p in prober.measurement_scripts()
                     if "answer_help(" not in p.read_text(encoding="utf-8")
                     and "argparse" not in p.read_text(encoding="utf-8")]
        assert unvouched, (
            "no script now takes the executed path; the test above has become "
            "a pure text check. That is not a failure -- delete this assertion "
            "deliberately if it is what you intend.")

    def test_the_set_is_not_empty(self, prober):
        """ANTI-VACUITY for the test above: an empty set would pass it."""
        assert len(prober.measurement_scripts()) >= 40


class TestAnUnrecognisedArgumentIsRefused:
    """The founder's rule, in this project's own words: "a script that accepts
    `--fix-timestamps` and does nothing with it is the 118-day no-op again"."""

    def test_an_unknown_flag_exits_two(self, cli_help, capsys):
        with pytest.raises(SystemExit) as e:
            cli_help.answer_help("doc", "thing.py", argv=["--nope"])
        assert e.value.code == 2
        err = capsys.readouterr().err
        assert "unrecognised argument(s): --nope" in err

    def test_a_stray_positional_exits_two(self, cli_help, capsys):
        with pytest.raises(SystemExit) as e:
            cli_help.answer_help("doc", "thing.py", argv=["somefile.md"])
        assert e.value.code == 2
        assert "somefile.md" in capsys.readouterr().err

    def test_help_still_wins_when_mixed_with_junk(self, cli_help, capsys):
        """A request to be told what the script does is answerable even when the
        rest of the command line is wrong, and answering costs nothing."""
        with pytest.raises(SystemExit) as e:
            cli_help.answer_help("doc", "thing.py", argv=["--nope", "--help"])
        assert e.value.code == 0
        assert capsys.readouterr().out.startswith("usage: thing.py [-h]")

    def test_the_refusal_can_be_switched_off_for_a_parsing_caller(self, cli_help):
        assert cli_help.answer_help("doc", "thing.py", argv=["file.md"],
                                    takes_no_arguments=False) is None

    def test_a_wired_script_really_refuses(self):
        """EXECUTED, on a real wired script, because the property that matters is
        the exit code of the command a person would type."""
        import subprocess
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "track_record_audit.py"),
             "--this-flag-does-not-exist"],
            capture_output=True, text=True, timeout=600, cwd=REPO)
        assert r.returncode == 2, (
            "an unrecognised argument ran the whole audit and reported success")
        assert "unrecognised argument" in r.stderr


class TestTheArgvScanSeesTheHelper:
    """test_operational_scripts.py decides whether a parser-less script must
    refuse an unknown flag by scanning its TEXT for `sys.argv`. A script that
    reads argv only through the helper names no `sys.argv` at all, so it would
    read as argv-free and inherit a pass. That clause is load-bearing only while
    such scripts exist."""

    def test_scripts_exist_that_read_argv_only_through_the_helper(self, prober):
        via_helper = []
        for p in prober.measurement_scripts():
            src = p.read_text(encoding="utf-8")
            if "answer_help(" in src and "sys.argv" not in src \
                    and "argparse" not in src:
                via_helper.append(p.name)
        assert len(via_helper) >= 10, (
            f"only {via_helper} read argv solely through the helper; if this "
            f"reaches 0 the extra clause in test_operational_scripts.py's argv "
            f"scan is no longer doing anything and can be retired deliberately")

    def test_the_scan_clause_is_present(self):
        src = (REPO / "bench" / "tests" / "test_operational_scripts.py") \
            .read_text(encoding="utf-8")
        assert '"answer_help(" not in src' in src, (
            "the argv scan no longer counts answer_help as reading argv, so "
            "every helper-wired script inherits a pass it has not earned")
