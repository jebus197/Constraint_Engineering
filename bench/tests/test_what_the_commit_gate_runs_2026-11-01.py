#!/usr/bin/env python3
"""The gate's coverage share must have a producer, and the GUARDS list must be live.

WHY. On 2026-11-01 the gate's figure was reported twice as "the full suite is
green". It is a GUARDS list of about a sixth of the suite, and nothing measured
the slice, so the phrase went unchallenged. The share now travels with
`scripts/what_the_commit_gate_actually_runs_2026-11-01.py` rather than as prose,
which is what `measured-rate-travels-with-its-script` requires.

AND THE LIST ITSELF IS CHECKED. A GUARDS entry naming a file that no longer
exists silently shrinks the gate: pytest is handed a path that does not resolve,
and the hook's own list stops describing what runs. Nothing verified that before.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TOOL = REPO / "scripts" / "what_the_commit_gate_actually_runs_2026-11-01.py"


@pytest.fixture(scope="module")
def mod():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("gate_cov", TOOL)
    m = importlib.util.module_from_spec(spec)
    sys.modules["gate_cov"] = m
    spec.loader.exec_module(m)
    return m


class TestTheGuardsListIsLive:
    def test_no_guards_entry_names_a_missing_file(self, mod):
        """★ THE CHECK NOTHING PERFORMED. A dead entry shrinks the gate silently."""
        live, dead = mod.guard_files()
        assert not dead, (
            "hooks/pre-commit names guard files that do not exist, so the gate "
            "runs less than its own list claims:\n  " + "\n  ".join(dead))
        assert len(live) > 50, (
            f"only {len(live)} guard files parsed; the GUARDS block is "
            f"probably not being read correctly")

    def test_a_dead_entry_is_actually_detected(self, mod, tmp_path,
                                                monkeypatch):
        """★ NON-VACUITY. The test above passes when the list is clean, which it
        is; this one proves the check can SEE a dead entry, by pointing the real
        parser at a hook that has one."""
        fake = tmp_path / "pre-commit"
        fake.write_text(
            'GUARDS="bench/tests/test_what_the_commit_gate_runs_2026-11-01.py\n'
            'bench/tests/test_this_file_does_not_exist_2026-11-01.py"\n',
            encoding="utf-8")
        monkeypatch.setattr(mod, "HOOK", fake)
        live, dead = mod.guard_files()
        assert dead == ["bench/tests/test_this_file_does_not_exist_2026-11-01.py"]
        assert live == ["bench/tests/test_what_the_commit_gate_runs_2026-11-01.py"]

    def test_a_hook_with_no_guards_block_refuses(self, mod, tmp_path,
                                                 monkeypatch):
        """Failing open here would report 0 of 759 as a real measurement."""
        fake = tmp_path / "pre-commit"
        fake.write_text("#!/bin/sh\necho nothing here\n", encoding="utf-8")
        monkeypatch.setattr(mod, "HOOK", fake)
        with pytest.raises(SystemExit):
            mod.guard_files()

    def test_the_parse_is_not_matching_the_whole_hook(self, mod):
        """A pattern that swallowed the file would report every test as a guard."""
        live, _ = mod.guard_files()
        all_files = list((REPO / "bench" / "tests").glob("test_*.py"))
        assert len(live) < len(all_files), (
            f"{len(live)} guards against {len(all_files)} test files: the "
            f"GUARDS parse is matching more than the GUARDS block")


class TestTheShareIsReportedWithBothTools:
    def test_the_interval_names_four_implementations(self, mod):
        out = mod.interval(3, 10)
        for tool in ("statsmodels", "mpmath", "scipy"):
            assert tool in out, (tool, out)
        assert "Wilson" in out and "Clopper" in out
        assert "agree to" in out

    def test_the_two_wilson_implementations_actually_agree(self, mod):
        """Parsed back out of the string, so a divergence cannot hide in prose."""
        out = mod.interval(120, 759)
        nums = [float(x) for x in re.findall(r"\[([\d.]+), ([\d.]+)\]", out)[0]]
        sm_lo, sm_hi = nums
        mp_lo, mp_hi = [float(x) for x in
                        re.search(r"mpmath \[([\d.]+), ([\d.]+)\]", out).groups()]
        assert abs(sm_lo - mp_lo) < 1e-9 and abs(sm_hi - mp_hi) < 1e-9

    def test_a_degenerate_denominator_does_not_crash(self, mod):
        """0 of n is a real state once every guard file is a guard."""
        assert "0 of 10" in mod.interval(0, 10)


class TestItRuns:
    def test_help_is_answered_for_free(self):
        r = subprocess.run([sys.executable, str(TOOL), "--help"],
                           capture_output=True, text=True, cwd=REPO)
        assert r.returncode == 0
        assert "usage:" in r.stdout
        assert "WHAT THE COMMIT GATE ACTUALLY RUNS" not in r.stdout

    def test_the_producer_reports_both_denominators(self):
        """Runs 2 pytest collections, about 18 s.

        ★ THIS DOCSTRING SAID THE FILE IS NOT IN THE HOOK'S GUARDS LIST AND
        COSTS THE COMMIT GATE NOTHING. That was true until 2026-11-09, when
        B103 added every guard dated 2026-10-29 or later to the gate on his
        instruction, and this file qualified. It now costs the gate these 2
        collections. The claim is corrected rather than deleted, because the
        reason it was kept off the gate was stated in it, and a reader
        comparing the gate's membership against this sentence would otherwise
        conclude one of them was wrong.

        It is still not a nested BOARD: a collection is not a run.
        """
        r = subprocess.run([sys.executable, str(TOOL)], capture_output=True,
                           text=True, cwd=REPO)
        assert r.returncode == 0, r.stdout[-1200:]
        assert "by FILE" in r.stdout and "by CASE" in r.stdout
        shares = re.findall(r"= (0\.\d{6})", r.stdout)
        assert len(shares) >= 2, r.stdout
        for s in shares:
            assert 0.0 < float(s) < 1.0, s
        assert "A SHARE OF TESTS IS NOT A SHARE OF RISK" in r.stdout
