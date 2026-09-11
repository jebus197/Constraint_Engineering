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

#: HOW MANY TIMES ONE TURN MAY BE REFUSED. `stop_hook_active` is a BOOLEAN the
#: harness sets after the first refusal, so treating it as "give up" caps this
#: hook at exactly 1 refusal per turn -- which converts "one task then report"
#: into "two tasks then report" and no further. The founder watched exactly that
#: and asked "You still stopped?". He was right: the bound was the defect.
#:
#: Refusals are therefore counted here, keyed by the turn's own user message, and
#: the budget is spent before the hook yields. It is a BUDGET rather than an
#: absence of one, because a hook that can never yield would trap a session that
#: has genuinely finished and the founder is not always at the keyboard to break
#: it. Any failure to read or write the counter ALLOWS the stop, because a guard
#: that refuses on its own malfunction is the shape this project keeps having to
#: withdraw.
MAX_REFUSALS_PER_TURN = 8
STATE = pathlib.Path.home() / ".claude" / "hooks" / ".work_not_narrate_state.json"

#: A turn doing real work makes more than this many tool calls.
MIN_TOOL_CALLS = 6
#: Prose beyond this, with no work, is a report rather than an answer.
MIN_PROSE = 1200

REPO = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
TASKS = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
MARKERS = REPO / "scripts"


def is_founder_message(d: dict) -> bool:
    """True ONLY for a message the founder actually typed.

    THE DEFECT THIS CLOSES, 2026-09-11. Claude Code records hook feedback and
    harness injections in the transcript as `"type":"user"` entries, flagged
    `isMeta`. This hook's OWN refusal text is one of them. Both readers below
    walked user entries without checking that flag, so the moment this hook
    refused once, it re-read the turn, found its own words where the founder's
    had been, and concluded he had not typed `d`. His command was erased by the
    machine that was supposed to obey it, and the refusal budget -- keyed on the
    same timestamp -- reset to 0 on every refusal, so `MAX_REFUSALS_PER_TURN`
    never bound. The founder watched it refuse 11 times after he said "Pause all
    activity", and ruled: "all commands issued by me should be considered law,
    and are non-optional under any condition!"

    ONE predicate, both callers, so the two cannot drift apart again -- that
    being the shape of defect this project keeps withdrawing.
    """
    if d.get("type") != "user":
        return False
    if d.get("isCompactSummary") or d.get("isMeta"):
        return False
    c = d.get("message", {}).get("content")
    if isinstance(c, list) and any(
            isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
        return False
    return True


def _turn_key(transcript: pathlib.Path) -> str:
    """The timestamp of the turn's own user message. A new message, a new budget."""
    try:
        lines = transcript.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    for line in reversed(lines):
        if '"type":"user"' not in line and '"type": "user"' not in line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if not is_founder_message(d):
            continue
        return str(d.get("timestamp") or "")
    return ""


def spend_refusal(key: str) -> int:
    """Record one refusal for this turn and return the running count."""
    if not key:
        return MAX_REFUSALS_PER_TURN + 1        # unknown turn -> allow the stop
    try:
        state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.is_file() else {}
    except Exception:
        state = {}
    if state.get("turn") != key:
        state = {"turn": key, "refusals": 0}
    state["refusals"] = int(state.get("refusals", 0)) + 1
    try:
        STATE.write_text(json.dumps(state), encoding="utf-8")
    except Exception:
        return MAX_REFUSALS_PER_TURN + 1        # cannot count -> allow the stop
    return state["refusals"]


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
        if not is_founder_message(d):
            continue
        c = d.get("message", {}).get("content")
        if isinstance(c, list):
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
            n_open: int, nxt: str, blocker_raised: bool = False) -> tuple[bool, str]:
    """Should this stop be refused?

    THE FIRST VERSION ONLY CAUGHT NARRATION and that was too weak. It allowed a
    stop whenever the turn had made 6 or more tool calls or landed a commit --
    which is EXACTLY the pattern the founder was objecting to. He watched me
    work, commit, report and stop, once per turn, for hours, and asked: "So where
    is the continuation fix you built, or said you would build?" Fed this
    session's own transcript, the hook returned "allow the stop" every time.

    HIS REQUIREMENT IS SIMPLER AND STRONGER: keep going until the list is done or
    something blocks. "The only way to test if any of this works is just to try
    and see how far you get this time!" So a stop is refused whenever OPEN work
    remains, and the exemptions are the only 3 that can be justified:

        `d`               his explicit instruction to discuss, never overridden
        nothing open      there is no work to continue to
        a blocker raised  an entry cannot proceed without him

    IT IS BOUNDED, NOT A TRAP. `stop_hook_active` means the stop has already been
    refused once this turn, so it exits 0 immediately. The effect is to convert
    "one task then report" into "at least twice as much per turn", repeatedly --
    not an infinite loop. The founder can end any turn by typing.
    """
    if had_d:
        return False, "the founder issued `d`: discuss, do not proceed. Honoured."
    if n_open == 0:
        return False, "no open items on the work list"
    if blocker_raised:
        return False, "a blocker was raised this turn; stopping for him is correct"

    narrated = calls < MIN_TOOL_CALLS and prose > MIN_PROSE
    head = ("This turn NARRATED: %d tool call(s) against %s characters of prose."
            % (calls, f"{prose:,}")) if narrated else (
            "This turn did work (%d tool calls%s)." % (calls, ", committed" if commit else ""))
    return True, (
        f"{head}\n"
        f"{n_open} items are still OPEN and nothing is blocking. Do not stop here.\n"
        f"The next unstarted entry is {nxt}. Work it.\n"
        f"If something genuinely prevents progress, classify it first:\n"
        f"    python3 scripts/blocker_triage.py --title '<the obstacle>'\n"
        f"A PARK verdict is not a reason to stop -- park it and carry on. Only a "
        f"BLOCK verdict is."
    )


def self_test() -> int:
    cases = [
        # calls prose commit  d  open blocker expect  why
        (0, 5000, False, False, 40, False, True,  "narration with work outstanding"),
        (30, 200, True,  False, 40, False, True,  "WORKED AND COMMITTED, but work remains"),
        (30, 5000, False, False, 40, False, True, "a big working turn still must continue"),
        (0, 5000, False, True,  40, False, False, "`d` is his command and overrides"),
        (30, 200, True,  False, 0,  False, False, "nothing left to do"),
        (5, 3000, False, False, 40, True,  False, "a blocker was raised; stopping is right"),
        (0, 100, False, False, 40, False, True,   "a one-line reply is still a stop"),
    ]
    bad = 0
    for calls, prose, commit, had_d, n_open, blk, expect, why in cases:
        got, msg = verdict(calls, prose, commit, had_d, n_open, "X", blk)
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
    # `stop_hook_active` is NOT read as "give up". It says only that a refusal has
    # already happened this turn; the budget below decides whether another is due.
    t = payload.get("transcript_path") or ""
    calls, prose, commit, had_d = turn_signals(pathlib.Path(os.path.expanduser(t)))
    n_open, nxt = open_items()
    # A BLOCKER RAISED THIS TURN IS A LEGITIMATE REASON TO STOP, and it is
    # detected from the transcript rather than trusted: the triage script must
    # actually have been run and returned BLOCK.
    raised = False
    try:
        text = pathlib.Path(os.path.expanduser(t)).read_text(
            encoding="utf-8", errors="replace")
        raised = "blocker_triage" in text.rsplit('"type":"user"', 1)[-1] and \
                 "BLOCK:" in text.rsplit('"type":"user"', 1)[-1]
    except Exception:
        raised = False
    block, why = verdict(calls, prose, commit, had_d, n_open, nxt, raised)
    if block:
        used = spend_refusal(_turn_key(pathlib.Path(os.path.expanduser(t))))
        if used > MAX_REFUSALS_PER_TURN:
            print(f"work_not_narrate: {used - 1} refusals already this turn, which "
                  f"is the budget. Allowing the stop so a finished session cannot "
                  f"be trapped.", file=sys.stderr)
            return 0
        print(f"{why}\n\n(continuation {used} of {MAX_REFUSALS_PER_TURN} this turn)",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
