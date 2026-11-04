#!/usr/bin/env python3
"""The producer behind B20's reachability finding is EXECUTED here, never read.

WHY THIS FILE EXISTS. Before 2026-11-04 **0 test files named this producer at
all.** It was "reached" only by citation, which satisfies the reachability
ratchet and satisfies nothing else: the additive standard requires an addition
to be wired to a caller AND executed by a test, and B20's reachability claim
rested on a script no test ran. A repair was then made to it -- the swallowed
exception around its P1 parse -- and that repair would also have shipped with
nothing executing it.

THE PIN THAT MATTERS IS THE SENSITIVITY ONE. The producer now reports how many
files the P1 predicate could NOT evaluate, and today that count is 0. A 0 from a
counter that never counts is indistinguishable from a 0 from a counter that
works, so a malformed file is PLANTED under a temporary archive and the count
must rise. Without that, "0 unevaluable, so P1's 0 is complete" would be
unfalsifiable.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "the_unattended_loop_has_never_been_reachable_2026-11-04.py"


@pytest.fixture(scope="module")
def mod():
    if not PRODUCER.is_file():
        pytest.skip("the producer is absent from this checkout")
    sys.path.insert(0, str(PRODUCER.parent))
    spec = importlib.util.spec_from_file_location("_loop", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _plant(root: pathlib.Path, name: str, text: str) -> pathlib.Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    f = d / "runner_state.json"
    f.write_text(text, encoding="utf-8")
    return f


class TestTheUnevaluableCounterActuallyCounts:
    def test_a_malformed_file_is_counted_not_swallowed(self, mod, tmp_path, capsys):
        """THE SENSITIVITY PIN. Without this, a 0 from a dead counter reads the
        same as a 0 from a working one, and the completeness claim the producer
        now prints would be unfalsifiable."""
        _plant(tmp_path, "run_broken", '{"hil_review": tru')   # deliberately invalid
        original = mod.LOGS
        try:
            mod.LOGS = tmp_path
            r = mod.section_2_the_archive()
        finally:
            mod.LOGS = original
        capsys.readouterr()
        assert len(r["unreadable"]) == 1, (
            f"a deliberately malformed file was not recorded: "
            f"{r['unreadable']}. The handler is swallowing again.")
        where, exc = r["unreadable"][0]
        assert "run_broken" in where
        assert exc in ("JSONDecodeError", "ValueError"), exc
        assert r["cfg_true"] == 0, (
            "an unparseable file was counted as recording the flag TRUE")

    def test_a_well_formed_true_file_is_detected(self, mod, tmp_path, capsys):
        """THE OTHER DIRECTION. A counter that records everything as unevaluable
        would pass the test above and measure nothing."""
        _plant(tmp_path, "run_true", json.dumps({"config": {"hil_review": True}}))
        original = mod.LOGS
        try:
            mod.LOGS = tmp_path
            r = mod.section_2_the_archive()
        finally:
            mod.LOGS = original
        capsys.readouterr()
        assert r["unreadable"] == [], r["unreadable"]
        assert r["cfg_true"] == 1, (
            "a well-formed file recording hil_review TRUE was not detected, so "
            "the P1 predicate is dead and its 0 means nothing")

    def test_a_false_file_is_neither_true_nor_unevaluable(self, mod, tmp_path, capsys):
        _plant(tmp_path, "run_false", json.dumps({"config": {"hil_review": False}}))
        original = mod.LOGS
        try:
            mod.LOGS = tmp_path
            r = mod.section_2_the_archive()
        finally:
            mod.LOGS = original
        capsys.readouterr()
        assert r["cfg_true"] == 0
        assert r["unreadable"] == []


class TestTheRealArchive:
    @pytest.fixture(scope="class")
    def real(self, mod):
        if not mod.LOGS.is_dir():
            pytest.skip("no archive in this checkout")
        return mod.section_2_the_archive()

    def test_the_deciding_predicate_is_still_zero(self, real):
        """B20 rests on this. If it ever becomes nonzero that is a FINDING --
        the loop became reachable -- and this test should be read, not relaxed."""
        assert real["cfg_true"] == 0, (
            f"{real['cfg_true']} archived run(s) now record hil_review TRUE. "
            f"The unattended loop became reachable at some point; B20 and "
            f"decision 27 both rest on this having been 0.")

    def test_the_zero_states_its_own_completeness(self, real):
        assert "unreadable" in real, (
            "the producer no longer reports how many files P1 could not "
            "evaluate, so its 0 is a claim rather than a measurement")

    def test_the_archive_is_not_empty(self, real):
        assert real["n"] > 100, (
            f"only {real['n']} run directories were walked, so the measurement "
            f"is not over the archive it claims")


class TestItRunsAndItsHelpDoesNot:
    def test_it_exits_zero_and_prints_all_three_predicates(self):
        p = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                           capture_output=True, text=True, timeout=1800)
        assert p.returncode == 0, p.stderr[-700:]
        for needle in ("P1 recorded config hil_review TRUE",
                       "P2 text holds --hil-review",
                       "P3 mentions hil_review at all",
                       "files P1 could NOT evaluate"):
            assert needle in p.stdout, f"missing from the output: {needle!r}"

    def test_help_answers_without_measuring(self):
        p = subprocess.run([sys.executable, str(PRODUCER), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, p.stderr[-400:]
        assert "run directories examined" not in p.stdout, "`--help` measured"
        assert "usage:" in p.stdout
