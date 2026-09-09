#!/usr/bin/env python3
"""UserPromptSubmit hook: give the assistant the wall clock AND the gap since the last prompt.

Written 2026-08-25 for the CDSFL founder.

THE FAILURE THIS PREVENTS. On 2026-08-24 the assistant wrote "it's gone five" at about
05:45, carried on, and the next time it actually read the clock it was 21:07 — roughly
fifteen hours later. It had been writing "tonight" and "in the morning" across two
different days. Nothing in a prompt distinguishes a fifteen-hour gap from a fifteen-second
one, so the gap is undetectable without being told.

WHY THE PREVIOUS RULE COULD NOT CATCH IT. Timestamp discipline was bound to ARTEFACT
production — capture the clock before a commit, a checkpoint, a memory write. The failures
were in conversational reference, which that rule does not cover. A companion "check every
25 turns" clause measures the wrong variable: two turns can be three seconds or fifteen
hours apart, so a turn counter cannot see elapsed time at all.

MUST ALWAYS EXIT 0. A hook that blocks a prompt is far worse than a missing timestamp.
"""
import json, sys, time, pathlib

PRUNE_AFTER = 30 * 86400


def human(sec):
    s = int(sec)
    if s < 90:
        return f"{s}s"
    if s < 5400:
        return f"{s // 60}m"
    if s < 172800:
        return f"{s // 3600}h{(s % 3600) // 60:02d}m"
    return f"{s // 86400}d {(s % 86400) // 3600}h"


def main():
    now = time.time()
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    # per-session state, so two concurrent sessions do not report each other's gaps
    sid = str(payload.get("session_id") or "default").replace("/", "_")[:128]
    d = pathlib.Path.home() / ".claude" / ".prompt_clock"
    gap = None
    try:
        d.mkdir(parents=True, exist_ok=True)
        f = d / sid
        if f.exists():
            prev = float(f.read_text().strip())
            if now > prev:
                gap = now - prev
        f.write_text(str(now))
        for p in d.iterdir():
            if p.is_file() and now - p.stat().st_mtime > PRUNE_AFTER:
                p.unlink()
    except Exception:
        pass

    stamp = time.strftime("%Y-%m-%d %H:%M:%S %Z (%A)", time.localtime(now))
    ctx = (f"[clock] {stamp} — first message of this session."
           if gap is None else
           f"[clock] {stamp} — {human(gap)} since the previous message.")
    print(json.dumps({
        "suppressOutput": True,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": ctx,
        },
    }))


try:
    main()
except Exception:
    pass
sys.exit(0)
