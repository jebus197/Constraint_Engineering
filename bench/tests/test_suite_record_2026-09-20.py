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
        assert got == {"passed": 8011, "failed": 0, "skipped": 5, "xfailed": 1,
                       "seconds": 1399.53}

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
