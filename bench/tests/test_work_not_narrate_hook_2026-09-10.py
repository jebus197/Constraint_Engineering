"""The Stop hook must refuse a narration turn, and must never trap the session.

The founder, 2026-09-10: "Can you not write some kind of mechanical 'is blocker'
/ 'is not blocker' ... script ... to prevent this? You can't self-diagnose/repair
the exact cause beyond this?"

Measured that day: turns carrying `d` made a median of 3 tool calls against 13
without it, Mann-Whitney p = 0.0097 -- so `d` genuinely suppresses work. But 8 of
16 turns carrying NO `d` still stopped after 12 calls or fewer, Wilson
[28.00%, 72.00%]. Half the stops had nothing telling them to stop.

WHY THIS FILE MATTERS MORE THAN THE HOOK. Before it, all 4 installed hooks were
UserPromptSubmit context injectors that made 0 subprocess calls, emitted 0
blocking decisions, and always exited 0 -- the shape task 1.1 named as "a guard
that cannot fail is not a guard". These tests exist to prove this one CAN fail.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "hooks" / "work_not_narrate.py"
LIVE = Path.home() / ".claude" / "hooks" / "work_not_narrate.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("wnn", HOOK)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestItCanActuallyFail:
    def test_the_self_test_passes(self):
        r = subprocess.run([sys.executable, str(HOOK), "--self-test"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "8 of 8 correct" in r.stdout

    def test_it_blocks_pure_narration(self, mod):
        block, why = mod.verdict(0, 5000, False, False, 40, "L1")
        assert block and "narration" in why and "L1" in why

    def test_it_returns_exit_code_2_which_is_what_blocks(self, mod, tmp_path):
        """Exit 0 would make it another guard that cannot fail."""
        assert mod.MIN_TOOL_CALLS > 0 and mod.MIN_PROSE > 0
        src = HOOK.read_text(encoding="utf-8")
        assert "return 2" in src, "the hook has no path that blocks a stop"


class TestItHonoursHisCommand:
    def test_d_overrides_everything(self, mod):
        block, why = mod.verdict(0, 99999, False, True, 999, "L1")
        assert not block and "`d`" in why, (
            "a hook that overrode his own discuss command would be worse than "
            "the defect it treats")


class TestItCannotFireOnTheOrdinaryCase:
    @pytest.mark.parametrize("calls,prose,commit,n_open,why", [
        (30, 5000, False, 40, "a working turn"),
        (0, 5000, True, 40, "a turn that committed"),
        (0, 200, False, 40, "a short direct answer"),
        (0, 5000, False, 0, "nothing left to do"),
    ])
    def test_it_stays_silent(self, mod, calls, prose, commit, n_open, why):
        block, _ = mod.verdict(calls, prose, commit, False, n_open, "X")
        assert not block, why


class TestItCannotTrapTheSession:
    def test_stop_hook_active_exits_immediately(self):
        r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(
            {"stop_hook_active": True, "transcript_path": "/nonexistent"}),
            capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, (
            "the loop guard failed; a Stop hook that blocks twice traps the session")

    def test_a_broken_payload_never_breaks_the_session(self):
        r = subprocess.run([sys.executable, str(HOOK)], input="not json at all",
                           capture_output=True, text=True, timeout=30)
        assert r.returncode == 0

    def test_a_missing_transcript_is_survivable(self, mod):
        assert mod.turn_signals(Path("/nonexistent/x.jsonl")) == (0, 0, False, False)


class TestItIsVersionedAndWired:
    def test_the_repo_copy_matches_the_live_one(self):
        """3 of the 4 earlier hooks existed in NO repository. Not this one."""
        if not LIVE.is_file():
            pytest.skip("no live hook on this machine")
        assert HOOK.read_bytes() == LIVE.read_bytes(), (
            "the versioned copy has drifted from the one that actually runs")

    def test_it_is_registered_as_a_Stop_hook(self):
        s = Path.home() / ".claude" / "settings.json"
        if not s.is_file():
            pytest.skip("no settings.json on this machine")
        d = json.loads(s.read_text())
        assert "work_not_narrate" in json.dumps(d.get("hooks", {}).get("Stop", [])), (
            "the hook exists and nothing calls it, which is the unwired-addition "
            "half of the additive standard")

    def test_the_five_existing_hooks_still_run(self):
        s = Path.home() / ".claude" / "settings.json"
        if not s.is_file():
            pytest.skip("no settings.json")
        d = json.loads(s.read_text())
        # COUNT THE INNER HOOKS, not the matcher entries. The first version of
        # this assertion counted `len(hooks["UserPromptSubmit"])`, which is 1 --
        # one matcher holding 5 hooks. It fired during the settings edit and
        # correctly REFUSED to write, which is a pre-write P-pass doing its job
        # on a file whose corruption would break every session.
        n = sum(len(m.get("hooks", [])) for m in d["hooks"]["UserPromptSubmit"])
        assert n == 5, f"wiring the Stop hook changed the 5 prompt hooks to {n}"
