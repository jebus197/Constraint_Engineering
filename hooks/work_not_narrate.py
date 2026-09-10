#!/usr/bin/env python3
"""Stop hook: refuse to end a turn that NARRATED while the work list has open items.

WHY THIS EXISTS, and it is the founder's diagnosis rather than the assistant's.
On 2026-09-10 he asked, repeatedly: *"Are you narrating or working?"*, then
*"That sounds more like you are issuing 'd' for yourself at the end of each
task"*, then *"Can you not write some kind of mechanical 'is blocker' / 'is not
blocker' script ... to prevent this? You can't self-diagnose/repair the exact
cause beyond this?"*

HE WAS RIGHT AND THE MEASUREMENT SAID SO. Over that day's 25 user messages: turns
whose message carried the `d` metacognitive command made a median of 3 tool calls;
turns without it made 13. Mann-Whitney U = 26.0, p = 0.0097 -- so `d` genuinely
suppresses work. BUT 8 of the 16 turns carrying NO `d` still stopped after 12 tool
calls or fewer, Wilson 95% [28.00%, 72.00%]. Half the stops had nothing telling
them to stop. The assistant's first explanation blamed his shorthand, which was
the half of the evidence that flattered it.

WHY A HOOK AND NOT A RESOLUTION. This project's own standing finding:
*"The failure was never the absence of a rule or a checker; it was never running
the checker."* And its audit of the 4 hooks that existed before this one: they are
*"UserPromptSubmit context injectors: they make 0 subprocess calls, emit 0
blocking decisions, and always exit 0."* An instruction arriving BEFORE a turn
competes with everything else in that turn. A Stop hook arrives at the only moment
that matters -- when the turn tries to end -- and can refuse.

WHAT IT REFUSES, and the predicate is deliberately narrow so it cannot become the
guard that fires on the ordinary case and teaches people to bypass it:

    the work list has OPEN items
    AND this turn closed no task and made no commit
    AND this turn ran fewer than MIN_TOOL_CALLS tools
    AND the assistant emitted more than MIN_PROSE characters
    AND the founder's message did NOT carry `d`

All 5 must hold. `d` is his explicit instruction to discuss rather than proceed,
so it is honoured absolutely: a hook that overrode his own command would be worse
than the defect it treats.

IT CANNOT LOOP. Claude Code sets `stop_hook_active` when a stop has already been
blocked once; this exits 0 immediately in that case. So it interrupts at most one
stop per turn, and never traps the session.

Self-test: `python3 work_not_narrate.py --self-test`
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

#: A turn doing real work makes more than this many tool calls.
MIN_TOOL_CALLS = 6
#: Prose beyond this, with no work, is a report rather than an answer.
MIN_PROSE = 1200

REPO = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
TASKS = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
MARKERS = REPO / "scripts"


def open_items() -> tuple[int, str]:
    """(open count, the next unstarted entry's identifier). (0, '') if unknown."""
    try:
        sys.path.insert(0, str(MARKERS))
        from task_list_markers import parse_entries          # type: ignore
        es = parse_entries(TASKS)
        opens = [e for e in es if e.state == "OPEN"]
        return len(opens), (opens[0].ident if opens else "")
    except Exception:
        return 0, ""


def turn_signals(transcript: pathlib.Path) -> tuple[int, int, bool, bool]:
    """(tool calls, prose chars, a commit ran, the user's message carried `d`).

    Only the CURRENT turn is read: everything after the last genuine user
    message. A tool_result is not a user message, and neither is a system
    reminder -- conflating them would measure the wrong span.
    """
    if not transcript.is_file():
        return 0, 0, False, False
    lines = transcript.read_text(encoding="utf-8", errors="replace").splitlines()
    start = 0
    had_d = False
    for i, line in enumerate(lines):
        if '"type":"user"' not in line and '"type": "user"' not in line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("type") != "user" or d.get("isCompactSummary"):
            continue
        c = d.get("message", {}).get("content")
        if isinstance(c, list):
            if any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
                continue
            c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
        if not isinstance(c, str) or "<system-reminder>" in c:
            continue
        start = i
        tail = c.strip().splitlines()[-1].strip().lower() if c.strip() else ""
        had_d = bool(re.fullmatch(r"[a-z, ]{1,20}", tail) and re.search(r"\bd\b", tail))

    calls = prose = 0
    commit = False
    for line in lines[start + 1:]:
        if "git commit" in line:
            commit = True
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("type") != "assistant":
            continue
        for blk in d.get("message", {}).get("content", []) or []:
            if not isinstance(blk, dict):
                continue
            if blk.get("type") == "tool_use":
                calls += 1
            elif blk.get("type") == "text":
                prose += len(blk.get("text", "") or "")
    return calls, prose, commit, had_d


def verdict(calls: int, prose: int, commit: bool, had_d: bool,
            n_open: int, nxt: str) -> tuple[bool, str]:
    if had_d:
        return False, "the founder issued `d`: discuss, do not proceed. Honoured."
    if n_open == 0:
        return False, "no open items on the work list"
    if commit:
        return False, "this turn made a commit"
    if calls >= MIN_TOOL_CALLS:
        return False, f"this turn made {calls} tool calls, which is work"
    if prose <= MIN_PROSE:
        return False, f"only {prose} characters of prose; not a report"
    return True, (
        f"This turn wrote {prose:,} characters and made {calls} tool call(s), "
        f"closed no task and made no commit, while {n_open} items are open.\n"
        f"That is narration. The next unstarted entry is {nxt}.\n"
        f"Work it, or classify the obstacle with "
        f"`python3 scripts/blocker_triage.py --title '...'` — if it PARKS, it is "
        f"not worth interrupting him for; if it BLOCKS, say so in one line and stop."
    )


def self_test() -> int:
    cases = [
        # calls prose commit  d   open  expect_block  why
        (0, 5000, False, False, 40, True,  "pure narration with work outstanding"),
        (0, 5000, False, True,  40, False, "`d` is his command and overrides"),
        (30, 5000, False, False, 40, False, "30 tool calls is work"),
        (0, 5000, True,  False, 40, False, "a commit landed"),
        (0, 200,  False, False, 40, False, "a short answer is not a report"),
        (0, 5000, False, False, 0,  False, "nothing left to do"),
        (5, 3000, False, False, 40, True,  "5 calls is below the floor"),
        (6, 3000, False, False, 40, False, "6 calls is at the floor"),
    ]
    bad = 0
    for calls, prose, commit, had_d, n_open, expect, why in cases:
        got, msg = verdict(calls, prose, commit, had_d, n_open, "X")
        ok = got == expect
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} block={got!s:5s} want={expect!s:5s}  {why}")
    print(f"\n  {len(cases) - bad} of {len(cases)} correct")
    return 1 if bad else 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0                      # never break the session on a bad payload
    if payload.get("stop_hook_active"):
        return 0                      # already blocked once this turn; never loop
    t = payload.get("transcript_path") or ""
    calls, prose, commit, had_d = turn_signals(pathlib.Path(os.path.expanduser(t)))
    n_open, nxt = open_items()
    block, why = verdict(calls, prose, commit, had_d, n_open, nxt)
    if block:
        print(why, file=sys.stderr)
        return 2                      # 2 blocks the stop and feeds stderr back
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
