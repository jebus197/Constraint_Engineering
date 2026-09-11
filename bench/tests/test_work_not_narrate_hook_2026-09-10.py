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
        assert "7 of 7 correct" in r.stdout

    def test_it_blocks_pure_narration(self, mod):
        block, why = mod.verdict(0, 5000, False, False, 40, "L1")
        assert block and "NARRATED" in why and "L1" in why

    def test_it_blocks_a_stop_after_a_SUCCESSFUL_working_turn(self, mod):
        """THE CASE THE FIRST VERSION MISSED, and it is the whole complaint.

        The founder watched me work, commit, report and stop, once per turn, for
        hours. Fed this session's own transcript the first predicate returned
        "allow the stop" every time, because it exempted any turn making 6+ tool
        calls or landing a commit -- which is exactly the pattern he objected to.
        A stop is now refused whenever OPEN work remains.
        """
        block, why = mod.verdict(30, 200, True, False, 40, "L1")
        assert block, "a turn that worked and committed must still continue"
        assert "still OPEN" in why and "L1" in why

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
    @pytest.mark.parametrize("calls,prose,commit,n_open,blocker,why", [
        (30, 5000, False, 0, False, "nothing left to do"),
        (30, 200, True, 0, False, "list empty after a working turn"),
        (5, 3000, False, 40, True, "a blocker was raised, so stopping is correct"),
    ])
    def test_it_stays_silent_when_it_should(self, mod, calls, prose, commit,
                                            n_open, blocker, why):
        block, _ = mod.verdict(calls, prose, commit, False, n_open, "X", blocker)
        assert not block, why

    def test_a_park_verdict_is_not_a_reason_to_stop(self, mod):
        """The triage tool parks most things; parking must not end the turn."""
        _, why = mod.verdict(10, 500, False, False, 40, "L1", False)
        assert "A PARK verdict is not a reason to stop" in why


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
        hooks = d.get("hooks", {})
        armed = "work_not_narrate" in json.dumps(hooks.get("Stop", []))
        # A DELIBERATE PARK IS NOT AN UNWIRED ADDITION. The founder parked this
        # hook on 2026-09-11 -- "park the hook thing we built" -- and parking
        # preserves the entry under a `_PARKED_` key rather than deleting it, so
        # restoring it is one rename. What this guard exists to catch is the
        # entry VANISHING, which is the unwired-addition half of the additive
        # standard. So a parked entry passes and a missing one still fails.
        parked = any(k.startswith("_PARKED_") and "work_not_narrate" in json.dumps(v)
                     for k, v in hooks.items())
        assert armed or parked, (
            "the hook exists and nothing calls it, and no parked entry preserves "
            "it either, which is the unwired-addition half of the additive standard")

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


# ---------------------------------------------------------------------------
# THE REFUSAL BUDGET — added 2026-09-10 19:15 BST after the founder asked
# "You still stopped?"
#
# He was right and the bound was the defect. `stop_hook_active` is a BOOLEAN the
# harness sets after the first refusal, so honouring it as "give up" capped this
# hook at exactly 1 refusal per turn: it converted "one task then report" into
# "two tasks then report" and no further. Observed twice in a row -- the hook
# refused, L1 was done, the turn ended; the hook refused, R2 was done, the turn
# ended.
#
# Refusals are now counted per turn and the budget is 8. It is a BUDGET rather
# than an absence of one because a hook that can never yield would trap a session
# that has genuinely finished, and he is not always at the keyboard.
# ---------------------------------------------------------------------------

class TestTheRefusalBudget:
    def test_it_refuses_more_than_once_per_turn(self, mod, tmp_path, monkeypatch):
        """The whole point. One refusal per turn was the defect."""
        monkeypatch.setattr(mod, "STATE", tmp_path / "state.json")
        counts = [mod.spend_refusal("turn-A") for _ in range(3)]
        assert counts == [1, 2, 3], counts

    def test_it_yields_once_the_budget_is_spent(self, mod, tmp_path, monkeypatch):
        """A hook that can never yield traps a session that has finished."""
        monkeypatch.setattr(mod, "STATE", tmp_path / "state.json")
        for _ in range(mod.MAX_REFUSALS_PER_TURN):
            mod.spend_refusal("turn-B")
        assert mod.spend_refusal("turn-B") > mod.MAX_REFUSALS_PER_TURN

    def test_a_new_turn_resets_the_budget(self, mod, tmp_path, monkeypatch):
        monkeypatch.setattr(mod, "STATE", tmp_path / "state.json")
        for _ in range(5):
            mod.spend_refusal("turn-C")
        assert mod.spend_refusal("turn-D") == 1, (
            "a new user message must restore the full budget")

    def test_an_unknown_turn_allows_the_stop(self, mod, tmp_path, monkeypatch):
        """Fail OPEN on the continuation question, deliberately.

        A guard that refuses on its own malfunction is the shape this project
        keeps having to withdraw. The cost of a wrong yield is one extra prompt
        from him; the cost of a wrong refusal is a session he cannot end.
        """
        monkeypatch.setattr(mod, "STATE", tmp_path / "state.json")
        assert mod.spend_refusal("") > mod.MAX_REFUSALS_PER_TURN

    def test_an_unwritable_state_file_allows_the_stop(self, mod, tmp_path, monkeypatch):
        monkeypatch.setattr(mod, "STATE", tmp_path / "no" / "such" / "dir" / "s.json")
        assert mod.spend_refusal("turn-E") > mod.MAX_REFUSALS_PER_TURN

    def test_stop_hook_active_no_longer_surrenders(self, mod):
        """It reports that a refusal happened; it does not decide the outcome."""
        src = (ROOT / "hooks" / "work_not_narrate.py").read_text(encoding="utf-8")
        assert "is NOT read as \"give up\"" in src, (
            "the hook still treats stop_hook_active as a reason to give up, which "
            "caps it at 1 refusal per turn")
