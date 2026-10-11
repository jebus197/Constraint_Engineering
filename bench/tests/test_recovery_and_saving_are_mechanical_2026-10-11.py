"""Compaction recovery RUNS itself, and a long save gap REFUSES the turn.

HIS RULING, 2026-10-11: *"You compacted, detected it after the compaction completed, and ran rs
without my intervention at all. If you could do this after every compaction event (again perhaps
mechanically?), with sv also ran at every significant milestone, that would be a significant
advancement in our working practices. So if you can implement these features mechanically
somehow, I would suggest that you do this too."*

WHY THE TWO HALVES DIFFER. The restore is READ-ONLY, so `compaction_watch.py` now executes it
unasked. `sv` WRITES, COMMITS AND PUSHES, so `sv_milestone_gate.py` refuses the turn instead of
running it -- pushing half-finished work on every turn end is worse than the gap it closes.

EVERY ASSERTION CALLS THE HOOK. A source-text assertion would only prove a hook describes itself
consistently (`execute-do-not-grep`), and this session has already caught one check that was
added where the command line never calls it.
"""
from __future__ import annotations

import datetime
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOKS = Path.home() / ".claude" / "hooks"
WATCH = HOOKS / "compaction_watch.py"
SVGATE = HOOKS / "sv_milestone_gate.py"
SETTINGS = Path.home() / ".claude" / "settings.json"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class TestCompactionRecoveryRunsItself:
    def test_the_hook_exists(self):
        if not WATCH.is_file():
            pytest.skip(f"the compaction hook is not installed here: {WATCH}")

    def test_auto_restore_actually_executes_the_restore(self):
        if not WATCH.is_file():
            pytest.skip("hook not installed")
        m = _load(WATCH, "cw_guard")
        out = m._auto_restore(REPO)
        assert "AUTO-RESTORE RAN AND SUCCEEDED" in out, out[:400]
        assert "FIRST READ" in out, "the restore ran but named none of the canonical resources"

    def test_it_returns_a_message_rather_than_raising_when_the_script_is_absent(self):
        """A recovery mechanism that can fell the session it protects is worse than none."""
        if not WATCH.is_file():
            pytest.skip("hook not installed")
        m = _load(WATCH, "cw_guard2")
        with tempfile.TemporaryDirectory() as d:
            out = m._auto_restore(Path(d))
        assert "DID NOT RUN" in out and "owed manually" in out

    def test_a_simulated_compaction_fires_the_hook_and_restores(self, tmp_path):
        """End to end through the real entry point, with a transcript carrying the marker."""
        if not WATCH.is_file():
            pytest.skip("hook not installed")
        now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        t = tmp_path / "transcript.jsonl"
        t.write_text(json.dumps(
            {"type": "user", "isCompactSummary": True, "timestamp": now}) + "\n",
            encoding="utf-8")
        state = Path.home() / ".claude" / ".compaction_watch"
        marker = state / "last_recovery"
        backup = marker.read_text(encoding="utf-8") if marker.is_file() else None
        sess = "pytest-compaction-guard"
        sf = state / sess
        try:
            if marker.exists():
                marker.unlink()
            if sf.exists():
                sf.unlink()
            r = subprocess.run([sys.executable, str(WATCH)],
                               input=json.dumps({"session_id": sess,
                                                 "transcript_path": str(t),
                                                 "prompt": "continue"}),
                               capture_output=True, text=True, timeout=400)
            assert r.returncode == 0
            ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
            assert "AUTO-RESTORE RAN AND SUCCEEDED" in ctx, (
                "a compaction fired the notice but did NOT run the restore")
            assert marker.is_file(), "the restore did not record itself, so it will repeat"
        finally:
            if sf.exists():
                sf.unlink()
            if backup is not None:
                marker.write_text(backup, encoding="utf-8")

    def test_it_stays_silent_when_no_compaction_is_outstanding(self, tmp_path):
        if not WATCH.is_file():
            pytest.skip("hook not installed")
        t = tmp_path / "quiet.jsonl"
        t.write_text(json.dumps({"type": "user", "timestamp": "2026-01-01T00:00:00Z"}) + "\n",
                     encoding="utf-8")
        r = subprocess.run([sys.executable, str(WATCH)],
                           input=json.dumps({"session_id": "pytest-quiet",
                                             "transcript_path": str(t), "prompt": "hi"}),
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0 and not r.stdout.strip()

    def test_malformed_input_never_fells_it(self):
        if not WATCH.is_file():
            pytest.skip("hook not installed")
        r = subprocess.run([sys.executable, str(WATCH)], input="not json",
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0


class TestTheSaveGateIsDerivedNotShipped:
    def test_the_gate_exists_and_is_wired_as_a_stop_hook(self):
        if not SVGATE.is_file():
            pytest.skip("the sv gate is not installed here")
        if not SETTINGS.is_file():
            pytest.skip("no settings.json")
        d = json.loads(SETTINGS.read_text(encoding="utf-8"))
        cmds = [hk.get("command", "")
                for e in d.get("hooks", {}).get("Stop", []) for hk in e.get("hooks", [])]
        assert any("sv_milestone_gate.py" in c for c in cmds), (
            "an unwired gate is not a gate")

    def test_the_threshold_comes_from_the_repository_not_a_constant(self):
        """He objected to a shipped constant of 10 for the round cap on exactly this ground."""
        if not SVGATE.is_file():
            pytest.skip("gate not installed")
        m = _load(SVGATE, "svg_guard")
        assert m._threshold([1, 1, 1, 1]) != m._threshold([20, 30, 40, 50]), (
            "the threshold does not vary with the history, so it is a constant in disguise")

    def test_the_threshold_is_clamped_at_both_ends(self):
        if not SVGATE.is_file():
            pytest.skip("gate not installed")
        m = _load(SVGATE, "svg_guard2")
        assert m._threshold([]) == m.FLOOR
        assert m._threshold([0, 0, 0]) == m.FLOOR, "a tight history must not nag below the floor"
        assert m._threshold([500, 600, 700]) == m.CEILING, (
            "a pathological history must not disarm the gate")

    def test_it_refuses_when_the_gap_exceeds_the_derived_threshold(self):
        if not SVGATE.is_file():
            pytest.skip("gate not installed")
        m = _load(SVGATE, "svg_guard3")
        marker = m.STATE / "last_refusal"
        backup = marker.read_text(encoding="utf-8") if marker.is_file() else None
        real = m._gaps_and_current
        try:
            if marker.exists():
                marker.unlink()
            m._gaps_and_current = lambda: ([1, 2, 3, 4, 5, 10, 11, 12], 25)
            sys.stdin = io.StringIO("{}")
            err, old = io.StringIO(), sys.stderr
            sys.stderr = err
            rc = m.main()
            sys.stderr = old
            assert rc == 2, "a gap far past the threshold did not refuse"
            assert "sv-gate" in err.getvalue()
            assert "cdsfl_sv.py" in err.getvalue(), "the refusal must name the command to run"
        finally:
            m._gaps_and_current = real
            if marker.exists():
                marker.unlink()
            if backup is not None:
                marker.write_text(backup, encoding="utf-8")

    def test_it_refuses_at_most_once_per_head(self):
        """A gate that refuses forever is a gate that gets switched off."""
        if not SVGATE.is_file():
            pytest.skip("gate not installed")
        m = _load(SVGATE, "svg_guard4")
        marker = m.STATE / "last_refusal"
        backup = marker.read_text(encoding="utf-8") if marker.is_file() else None
        real = m._gaps_and_current
        try:
            if marker.exists():
                marker.unlink()
            m._gaps_and_current = lambda: ([1, 2, 3], 99)
            old = sys.stderr
            sys.stdin = io.StringIO("{}")
            sys.stderr = io.StringIO()
            first = m.main()
            sys.stdin = io.StringIO("{}")
            sys.stderr = io.StringIO()
            second = m.main()
            sys.stderr = old
            assert first == 2 and second == 0, (first, second)
        finally:
            m._gaps_and_current = real
            if marker.exists():
                marker.unlink()
            if backup is not None:
                marker.write_text(backup, encoding="utf-8")

    def test_it_is_silent_when_the_save_rhythm_is_normal(self):
        if not SVGATE.is_file():
            pytest.skip("gate not installed")
        m = _load(SVGATE, "svg_guard5")
        real = m._gaps_and_current
        try:
            m._gaps_and_current = lambda: ([1, 2, 3, 4, 5, 10, 11, 12], 1)
            sys.stdin = io.StringIO("{}")
            old, sys.stderr = sys.stderr, io.StringIO()
            rc = m.main()
            sys.stderr = old
            assert rc == 0, "the gate fired on a normal save gap, which makes it noise"
        finally:
            m._gaps_and_current = real
