#!/usr/bin/env python3
"""`sv` cites the last full-suite measurement instead of re-running it. Executed.

FOUNDER, 2026-09-20: *"sv normally takes minutes? ... This is clearly
impractical for what should be a simple 'save state' operation."* It had become
23 minutes because I re-ran the whole suite to make the state block's figure
fresh. The A23 guard asks a suite figure to NAME A PRODUCER, not to be new.

Every test drives the real module against constructed logs; none re-runs a suite.
The negative controls are the point: a record that cannot go STALE would let a
launcher green-light a run against a measurement of a different tree.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "suite_record.py"

GREEN = "8011 passed, 5 skipped, 1 xfailed, 20 warnings in 1399.53s (0:23:19)\nPYTEST_EXIT=0\n"
RED = "5 failed, 8029 passed, 6 skipped, 1 xfailed in 1692.80s (0:28:12)\nPYTEST_EXIT=1\n"
COMMA = "8,011 passed, 5 skipped in 1399.53s\nPYTEST_EXIT=0\n"


@pytest.fixture
def mod(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("srec", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    monkeypatch.setattr(m, "RECORD", tmp_path / "suite_record.json")
    return m


class TestItReadsWhatPytestActuallyPrints:
    def test_a_green_tail(self, mod):
        got = mod.parse(GREEN)
        # Field-wise rather than dict-equal: the parser gained `errors`,
        # `xpassed` and `deselected` on 2026-09-20, and an equality assertion
        # would have to be rewritten every time pytest grows an outcome --
        # which is an incentive to stop modelling outcomes.
        for k, v in {"passed": 8011, "failed": 0, "skipped": 5, "xfailed": 1,
                     "errors": 0, "seconds": 1399.53}.items():
            assert got[k] == v, f"{k}: expected {v}, got {got[k]}"

    def test_a_red_tail_with_failures_first(self, mod):
        got = mod.parse(RED)
        assert got["failed"] == 5 and got["passed"] == 8029

    def test_a_thousands_separator(self, mod):
        assert mod.parse(COMMA)["passed"] == 8011

    def test_a_log_with_no_summary_is_refused_not_guessed(self, mod, tmp_path):
        log = tmp_path / "x.log"
        log.write_text("collecting ...\ninterrupted\n", encoding="utf-8")
        assert mod.parse(log.read_text()) == {}
        with pytest.raises(SystemExit):
            mod.record(log, None, None)


class TestTheCitationNamesItsProducer:
    """What the A23 guard actually demands."""

    def _rec(self, mod, tmp_path, text=GREEN, clean=True):
        log = tmp_path / "s.log"
        log.write_text(text, encoding="utf-8")
        return mod.record(log, None, clean)

    def test_the_sentence_carries_a_figure_and_the_command(self, mod, tmp_path):
        self._rec(mod, tmp_path)
        line = mod.cite()
        assert "8,011 passed" in line
        assert "python3 -m pytest bench/tests/ -q --netguard-strict" in line

    def test_it_says_when_the_tree_was_dirty(self, mod, tmp_path):
        self._rec(mod, tmp_path, RED, clean=False)
        assert "NOT clean" in mod.cite()
        assert "5 FAILED" in mod.cite()

    def test_with_no_record_it_says_so_rather_than_inventing_one(self, mod):
        line = mod.cite()
        assert "No full-suite record exists" in line
        assert "passed" not in line.split("Run")[0]


class TestItCanGoStale:
    """A record that could never be stale would let a launcher approve a run
    against a measurement of a different tree."""

    def test_a_record_at_head_is_current(self, mod, tmp_path, monkeypatch):
        log = tmp_path / "s.log"; log.write_text(GREEN, encoding="utf-8")
        mod.record(log, None, True)
        is_stale, why = mod.stale()
        assert is_stale is False and "recorded at HEAD" in why

    def test_a_record_at_an_older_commit_is_stale(self, mod, tmp_path, monkeypatch):
        log = tmp_path / "s.log"; log.write_text(GREEN, encoding="utf-8")
        mod.record(log, None, True)
        data = json.loads(mod.RECORD.read_text())
        data["commit"] = "0000000"
        mod.RECORD.write_text(json.dumps(data), encoding="utf-8")
        is_stale, why = mod.stale()
        assert is_stale is True and "0000000" in why

    def test_no_record_at_all_is_stale(self, mod):
        is_stale, why = mod.stale()
        assert is_stale is True and "no full-suite record" in why

    def test_check_exits_3_when_stale(self, tmp_path):
        r = subprocess.run([sys.executable, str(SCRIPT), "check"], cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        assert r.returncode in (0, 3)
        assert ("STALE" in r.stdout) == (r.returncode == 3)


class TestItWritesNothingUnlessRecording:
    def test_cite_and_check_do_not_create_the_record(self, mod):
        assert not mod.RECORD.exists()
        mod.cite(); mod.stale()
        assert not mod.RECORD.exists()


class TestSvCitesItInsteadOfReRunningTheSuite:
    """The reason this record exists at all. FOUNDER, 2026-09-20: *"sv normally
    takes minutes? Hopefully we aren't looking at hours?"* It was 23 minutes,
    because writing a suite figure into the SESSION STATE block was taken to
    mean re-running the suite. The record removes the reason to re-run, and
    these 3 tests require sv to actually reach it."""

    @staticmethod
    def _sv_source() -> str:
        return (ROOT / "scripts" / "cdsfl_sv.py").read_text(encoding="utf-8")

    def test_sv_main_calls_the_citation_printer(self):
        tree = ast.parse(self._sv_source())
        main = next(n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        assert any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                   and n.func.id == "_print_suite_citation"
                   for n in ast.walk(main)), (
            "main() no longer calls _print_suite_citation, so the record is "
            "written by nothing and read by nobody")

    def test_the_printer_emits_the_command_the_guard_looks_for(self, capsys):
        sys.path.insert(0, str(ROOT / "scripts"))
        import cdsfl_sv                                            # noqa: PLC0415
        cdsfl_sv._print_suite_citation(ROOT)
        out = capsys.readouterr().out
        assert "pytest bench/tests/" in out, (
            "the citation does not name a runnable producer, which is exactly "
            "what the A23 guard requires of a suite figure")
        assert "Record currency" in out

    def test_the_printer_never_raises_when_the_record_is_missing(self, tmp_path,
                                                                 capsys):
        """A failed lookup must read as a failed lookup, not as a green suite,
        and must never turn a completed save into a traceback."""
        sys.path.insert(0, str(ROOT / "scripts"))
        import cdsfl_sv                                            # noqa: PLC0415
        import suite_record                                        # noqa: PLC0415
        original = suite_record.RECORD
        try:
            suite_record.RECORD = tmp_path / "absent.json"
            cdsfl_sv._print_suite_citation(ROOT)
        finally:
            suite_record.RECORD = original
        out = capsys.readouterr().out
        assert "No full-suite record exists yet" in out
        assert "GREEN" not in out


class TestAnErroredRunIsRED:
    """THE DEFECT THAT DEFEATED THE SPEND GATE, found 2026-09-20 by an
    adversarial audit of the same night's commits and reproduced before it was
    touched.

    pytest reports a fixture or teardown failure as a separate ERROR category,
    printed AFTER the passes. The old pattern had no group for it, so
    `3 passed, 1 error in 0.17s` parsed as failed=0, `record` derived exit code
    0, `cite` printed GREEN, and `gate` would have released 4 paid seats
    against a run pytest exited 1 on. Every case below drives the real parser.
    """

    ERR_SINGULAR = "3 passed, 1 error in 0.17s\n"
    ERR_PLURAL = "5 passed, 3 errors in 0.13s\n"
    ERR_WITH_FAILURES = "2 failed, 5 passed, 3 errors in 9.10s\n"

    def test_a_single_error_is_counted(self, mod):
        got = mod.parse(self.ERR_SINGULAR)
        assert got["errors"] == 1, f"the error was dropped: {got}"

    def test_plural_errors_are_counted(self, mod):
        assert mod.parse(self.ERR_PLURAL)["errors"] == 3

    def test_an_errored_run_records_a_NONZERO_exit_code(self, mod, tmp_path):
        log = tmp_path / "err.log"
        log.write_text(self.ERR_SINGULAR, encoding="utf-8")
        out = mod.record(log, None, True)
        assert out["exit_code"] == 1, (
            "a run pytest exited 1 on was recorded with exit code 0; the spend "
            "gate reads exactly this field")

    def test_the_gate_REFUSES_an_errored_record(self, mod, tmp_path, capsys):
        log = tmp_path / "err.log"
        log.write_text(self.ERR_WITH_FAILURES, encoding="utf-8")
        mod.record(log, None, True)
        with pytest.raises(SystemExit) as e:
            mod.gate(spend="panel (4 of 6 seats paid)",
                     override_env="PANEL_SUITE_UNCHECKED", paid_seats=4)
        assert e.value.code == 2

    def test_cite_does_not_call_an_errored_run_GREEN(self, mod, tmp_path):
        log = tmp_path / "err.log"
        log.write_text(self.ERR_SINGULAR, encoding="utf-8")
        mod.record(log, None, True)
        assert "GREEN" not in mod.cite(), (
            "the sentence sv pastes into the RECOVERY.md state block calls an "
            "errored suite green")


class TestFailuresAfterPassesAreStillCounted:
    """The same rigidity, the other way round: the old pattern only matched a
    failure count BEFORE the passes, so a reordered tail read as 0 failed."""

    def test_failures_printed_after_the_passes(self, mod):
        assert mod.parse("8126 passed, 12 failed in 2124.59s\n")["failed"] == 12


class TestAnUnmodelledOutcomeIsLOUD:
    """The deeper half. Scoring a token the parser cannot name as 0 is exactly
    how a red suite was recorded green, so the next unmodelled outcome refuses
    rather than passing silently."""

    def test_an_unknown_count_word_refuses(self, mod):
        with pytest.raises(SystemExit) as e:
            mod.parse("3 passed, 2 quarantined in 0.5s\n")
        assert "does not model" in str(e.value)
        assert "quarantined" in str(e.value)

    def test_the_known_words_do_NOT_refuse(self, mod):
        """ANTI-VACUITY: a parser that refused every real tail would be worse
        than the defect. Every outcome pytest actually prints must pass."""
        ok = ("1 failed, 2 passed, 3 skipped, 4 xfailed, 5 xpassed, "
              "6 deselected, 7 warnings, 1 error in 3.00s\n")
        got = mod.parse(ok)
        assert got["failed"] == 1 and got["errors"] == 1 and got["xpassed"] == 5

