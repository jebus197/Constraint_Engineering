"""The Stop hook must never mistake its own output for the founder's words.

FOUNDER RULING 2026-09-11, verbatim: *"all commands issued by me should be
considered law, and are non-optional under any condition!"* and *"Also scrub the
'd' lock on me! There is only one boss here, and it is me who calls the shots!"*

THE DEFECT. Claude Code writes hook feedback into the transcript as a user entry
flagged `isMeta`. `work_not_narrate.py` read user entries without checking that
flag, so after its first refusal it re-read the turn, found ITS OWN refusal text
where the founder's message had been, and recomputed `had_d` from that text --
which never carries `d`. His pause command was erased by the hook enforcing it.
The same walk keyed the refusal budget, so `MAX_REFUSALS_PER_TURN = 8` reset to 0
on every refusal and never bound; the hook refused 11 consecutive stops after he
said "Pause all activity".

These tests CALL the hook's functions against transcripts on disk. They do not
assert on its source text -- `execute-do-not-grep`, and a source-text test could
not have caught this, because every line of the old code described itself
correctly.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "work_not_narrate.py"
LIVE = pathlib.Path.home() / ".claude" / "hooks" / "work_not_narrate.py"

HOOK_FEEDBACK = (
    "Stop hook feedback:\n"
    "[python3 ~/.claude/hooks/work_not_narrate.py]: This turn did work (9 tool calls, committed).\n"
    "2 items are still OPEN and nothing is blocking. Do not stop here.\n"
    "The next unstarted entry is A8. Work it.\n"
    "A PARK verdict is not a reason to stop -- park it and carry on. Only a BLOCK verdict is."
)


@pytest.fixture(scope="module")
def hook():
    spec = importlib.util.spec_from_file_location("wnn_under_test", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _entry(ts: str, text: str, *, meta: bool = False) -> str:
    d = {"type": "user", "timestamp": ts,
         "message": {"role": "user", "content": text}}
    if meta:
        d["isMeta"] = True
    return json.dumps(d)


def _transcript(tmp_path: pathlib.Path, *lines: str) -> pathlib.Path:
    p = tmp_path / "t.jsonl"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


FOUNDER_TS = "2026-09-11T22:07:00.000Z"
HOOK_TS = "2026-09-11T22:09:00.000Z"


def test_his_d_survives_the_hooks_own_refusal(hook, tmp_path):
    """The exact failing case: `a, d`, then the hook's own feedback after it."""
    t = _transcript(
        tmp_path,
        _entry(FOUNDER_TS, "Pause all activity.\n\na, d"),
        _entry(HOOK_TS, HOOK_FEEDBACK, meta=True),
    )
    assert hook.turn_signals(t)[3] is True, "his `d` was scrubbed by the hook's own words"


def test_the_budget_key_does_not_move_when_the_hook_speaks(hook, tmp_path):
    """If the key moves, `refusals` resets and MAX_REFUSALS_PER_TURN never binds."""
    before = _transcript(tmp_path, _entry(FOUNDER_TS, "carry on"))
    assert hook._turn_key(before) == FOUNDER_TS
    after = _transcript(
        tmp_path,
        _entry(FOUNDER_TS, "carry on"),
        _entry(HOOK_TS, HOOK_FEEDBACK, meta=True),
    )
    assert hook._turn_key(after) == FOUNDER_TS, "the hook's own message became the turn"


def test_the_refusal_budget_actually_counts(hook, tmp_path, monkeypatch):
    """With a stable key the budget increments, so the hook can yield."""
    monkeypatch.setattr(hook, "STATE", tmp_path / "state.json")
    assert [hook.spend_refusal(FOUNDER_TS) for _ in range(3)] == [1, 2, 3]


def test_a_fresh_founder_message_starts_a_fresh_budget(hook, tmp_path, monkeypatch):
    monkeypatch.setattr(hook, "STATE", tmp_path / "state.json")
    hook.spend_refusal(FOUNDER_TS)
    hook.spend_refusal(FOUNDER_TS)
    assert hook.spend_refusal("2026-09-11T23:00:00.000Z") == 1


def test_the_budget_still_yields_at_the_documented_bound(hook, tmp_path, monkeypatch):
    """It is a budget, not a trap: the founder is not always at the keyboard."""
    monkeypatch.setattr(hook, "STATE", tmp_path / "state.json")
    used = [hook.spend_refusal(FOUNDER_TS) for _ in range(hook.MAX_REFUSALS_PER_TURN + 1)]
    assert used[-1] > hook.MAX_REFUSALS_PER_TURN


def test_every_command_he_types_is_read_not_just_d(hook, tmp_path):
    """His words are law. Any trailing MC of his must reach the hook intact."""
    for msg in ("do the thing\n\na, d", "check it\n\nd", "look\n\np d e"):
        t = _transcript(
            tmp_path,
            _entry(FOUNDER_TS, msg),
            _entry(HOOK_TS, HOOK_FEEDBACK, meta=True),
        )
        assert hook.turn_signals(t)[3] is True, f"`d` lost from {msg!r}"


def test_the_hook_keeps_its_refusal_power(hook, tmp_path):
    """The fix restores his override. It must NOT weaken the hook otherwise."""
    t = _transcript(
        tmp_path,
        _entry(FOUNDER_TS, "carry on with the list"),
        _entry(HOOK_TS, HOOK_FEEDBACK, meta=True),
    )
    calls, prose, commit, had_d = hook.turn_signals(t)
    assert had_d is False
    block, _ = hook.verdict(calls, prose, commit, had_d, n_open=2, nxt="A8")
    assert block is True, "the hook must still refuse a stop with work outstanding"


def test_an_injected_non_hook_message_is_also_not_his(hook, tmp_path):
    """Skill bodies and 'Continue from where you left off' are injected too."""
    t = _transcript(
        tmp_path,
        _entry(FOUNDER_TS, "pause\n\nd"),
        _entry(HOOK_TS, "Continue from where you left off.", meta=True),
    )
    assert hook.turn_signals(t)[3] is True
    assert hook._turn_key(t) == FOUNDER_TS


def test_the_versioned_copy_is_the_one_that_runs(hook):
    """3 of the 4 earlier hooks existed in no repository at all."""
    assert LIVE.is_file(), "the running hook is missing"
    assert LIVE.read_bytes() == HOOK.read_bytes(), (
        "the repo copy and the running copy have diverged; the tested file is "
        "not the file that fires"
    )


def test_the_hooks_own_self_test_passes(hook):
    assert hook.self_test() == 0
