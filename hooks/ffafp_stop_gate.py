#!/usr/bin/env python3
"""Stop hook: refuse ONE stop when the turn changed code and left no ANALYSE or
P-PASS trace. This is the narrow BLOCK the founder asked for, shaped to survive
his own false-positive objection.

WHAT THE FOUNDER ASKED AND WHAT THIS DOES ABOUT IT
==================================================
2026-09-22: "All I want is for you never to skip the full 'f' (5 step protocol),
or to skip sy, on any element of your output that might be accessible to this."
Asked BLOCK or REPORT he said "Block rather than report", then that he does not
know what block means and wants only that the protocol is never skipped.

The ex-ante reminder (`mc_commands.py`, every prompt since 2026-08-30) measurably
did not close the gap. The ex-post reporter (`ffafp_audit.py`) is one-sided and
report-only BY DESIGN, and its docstring's objection to blocking is correct: a
hook that blocked on a heuristic that soft would be switched off within a day.
So this file blocks ONLY on the two signals whose false-positive cost is one
bounced stop, not a trapped session:

  * ANALYSE missing -- code changed and NO STEM tool and NO test ran in the
    entire turn. That is the `sy` skip, verbatim.
  * P-PASS missing  -- code changed and nothing failable ran after the last
    edit. A fix never tried against failure is a hypothesis.

THE DOMINANT FALSE POSITIVE of the trace detector -- "the check runs next turn"
-- is exactly what this gate converts into "the check runs NOW", which is the
outcome the founder asked for. The cost of a wrong refusal is bounded: Claude
Code sets `stop_hook_active` after one refusal and this exits 0 immediately, so
the gate interrupts at most ONE stop per turn. On the bounce the model either
produces the owed trace or states in one line why none is owed, then stops.

FOLLOW and FIND are NOT gated: their false positives (investigate on turn N,
edit on N+1) are legitimate practice, and blocking on them is how a gate gets
parked. Wolfram is NOT gated either: the founder's 2026-09-17 ruling says a
Wolfram call that cannot run is not a blocker, so Wolfram stays on the REPORT
side (see the window line in ffafp_audit.render).

A BROKEN GATE FAILS OPEN AND SAYS SO. The trace detector's blanket `except:
pass` cost 2 days of silence indistinguishable from health (2026-09-20 KeyError,
frozen offset). Here every failure path allows the stop AND prints why to
stderr, so breakage is visible the moment it happens.

Exit contract (same as work_not_narrate.py): exit 2 + reason on stderr refuses
the stop; exit 0 allows it.

INSTALL: copy beside ffafp_audit.py in ~/.claude/hooks/ and wire in
~/.claude/settings.json under "Stop":
    {"type": "command", "command": "python3 ~/.claude/hooks/ffafp_stop_gate.py",
     "timeout": 20}
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ffafp_audit as fa  # noqa: E402  the ONE copy of the trace rules

#: The Stop event needs only the CURRENT turn, so scan a bounded tail rather
#: than 196 MB. 8 MB held every turn in the surveyed corpus (largest turn
#: serialised to 135 kB; the margin is x60). A turn larger than the tail
#: under-counts mutations and can only UNDER-block, which is the safe side.
TAIL_BYTES = 8 * 1024 * 1024

#: ★ ALL 5 STEPS ARE GATED, 2026-10-24, ON HIS RULING. His words: *"Fix the
#: missing 'f' steps also, so that the full 5 step process always triggers,
#: rather than randomly/selectively, as appears to be the case now. They should
#: not be regarded as optional when an issue is encountered, or when
#: assessing/implementing a fix. They should preferably be mechanical so you
#: can't skip them."*
#:
#: IT WAS ("ANALYSE", "P-PASS") -- 2 of 5 -- and the docstring above gives the
#: reason FIND and FOLLOW were left out: "investigate on turn N, edit on N+1".
#: THAT REASON WAS SOUND AND IS ADDRESSED RATHER THAN OVERRIDDEN. The gate scanned
#: the CURRENT turn only, so a FOLLOW performed one turn before the edit was
#: invisible to it. `WINDOW_TURNS` widens the scan so a trace in any recent turn
#: counts, which removes the false positive the exclusion existed for. Measured
#: before the change: FOLLOW reported missing in 22 of the last 40 turns,
#: 55.0000%, Wilson [39.8291%, 69.2947%] -- too high to be all real, which is
#: exactly what a narrow window produces.
#:
#: WOLFRAM STAYS UNGATED on his ruling of 2026-09-17: a Wolfram call that cannot
#: run is not a blocker. It remains on the report side.
GATED = ("FIND", "FOLLOW", "ANALYSE", "FIX", "P-PASS")

#: How many recent turns a trace may have come from. 3 covers the
#: investigate-then-edit pattern without letting an unrelated trace count forever.
WINDOW_TURNS = 3

#: ★ THE ONE-SHOT YIELD IS REPLACED BY A BOUNDED ONE. `stop_hook_active` is Claude
#: Code's OWN loop protection, not a marker this file owns, so ignoring it
#: outright could trap the session -- worse than any missed trace. The gate counts
#: its own refusals per turn and yields after this many, loudly. Producing the
#: owed check is self-limiting: running a test changes the transcript the next
#: scan reads.
MAX_REFUSALS_PER_TURN = 3


def last_turn_verdict(tpath: pathlib.Path):
    """Audit the turn now ending, from a fresh bounded scan of the transcript."""
    size = tpath.stat().st_size
    state = {"offset": 0, "open": None, "seq": 0, "reads": {}}
    closed = []
    with tpath.open("r", errors="ignore") as fh:
        if size > TAIL_BYTES:
            fh.seek(size - TAIL_BYTES)
            fh.readline()                      # discard the partial line
            state["offset"] = fh.tell()
        fa.scan(fh, state, on_close=closed.append)
    if state.get("open"):                      # the turn being stopped is open
        v = fa.audit(state["open"], fa.prior_read_paths(state))
    else:
        v = closed[-1] if closed else None
    if not v:
        return None
    # ★ A TRACE FROM A RECENT TURN COUNTS, which is what makes gating FIND and
    # FOLLOW honest: one FFAFP cycle often spreads across turns, and a
    # current-turn-only scan calls that a miss.
    # ★ `audit()` RETURNS NO "present" KEY, and the first version of this window
    # read one. `c.get("present")` was always empty, so the window credited
    # NOTHING and was an addition reaching nothing -- which the additive standard
    # forbids in exactly those words. The steps are derived from the booleans the
    # audit does return: `found`, `followed`, `analysed` and `verified_after`.
    _FLAG = {"FIND": "found", "FOLLOW": "followed",
             "ANALYSE": "analysed", "P-PASS": "verified_after"}
    seen = set()
    for c in [x for x in closed[-WINDOW_TURNS:] if x]:
        for step, flag in _FLAG.items():
            if c.get(flag):
                seen.add(step)
    if seen:
        v = {**v,
             "missing": [m for m in (v.get("missing") or []) if m not in seen],
             "window_credited": sorted(seen)}
    return v


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:                          # noqa: BLE001
        return 0                               # bad payload: never trap a session
    # ★ NOT A ONE-SHOT YIELD ANY MORE (his ruling 2026-10-24). It read
    # `if stop_hook_active: return 0`, which is how a turn that changed code could
    # stop with the owed check never run.
    STATE_DIR = pathlib.Path.home() / ".claude" / ".ffafp_gate"
    counter = None
    refusals = 0
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        counter = STATE_DIR / f"{payload.get('session_id') or 'session'}.refusals"
        if payload.get("stop_hook_active") and counter.is_file():
            refusals = int(counter.read_text(encoding="utf-8").strip() or "0")
        if refusals >= MAX_REFUSALS_PER_TURN:
            print(f"[ffafp-gate] {refusals} refusal(s) already issued, which is the "
                  f"ceiling. ALLOWING the stop so the session cannot be trapped -- "
                  f"but the owed trace was never produced, and that is a real gap, "
                  f"not a pass.", file=sys.stderr)
            counter.write_text("0", encoding="utf-8")
            return 0
    except Exception as e:                     # noqa: BLE001
        print(f"[ffafp-gate SELF-CHECK] refusal counter unusable "
              f"({type(e).__name__}: {e}); falling back to the one-shot yield so a "
              f"broken counter cannot trap the session.", file=sys.stderr)
        if payload.get("stop_hook_active"):
            return 0
    t = str(payload.get("transcript_path") or "")
    tpath = pathlib.Path(os.path.expanduser(t))
    if not tpath.is_file():
        return 0
    try:
        v = last_turn_verdict(tpath)
    except Exception as e:                     # noqa: BLE001
        print(f"[ffafp-gate SELF-CHECK] scan failed ({type(e).__name__}: {e}); "
              f"failing OPEN and allowing the stop. The gate is broken, not the work.",
              file=sys.stderr)
        return 0
    if not v or not v.get("code"):
        return 0
    owed = [m for m in (v.get("missing") or []) if m in GATED]
    if not owed:
        return 0
    files = ", ".join(v.get("files") or []) or "unnamed files"
    why = {m: fa._WHY[m] for m in owed}
    print(
        f"[ffafp-gate] This turn changed code ({files}) and left NO OBSERVABLE "
        f"TRACE of: {', '.join(owed)}.\n"
        + "".join(f"  {m}: {w}\n" for m, w in why.items())
        + "Before stopping, either RUN the owed check now (a failable test or a "
          "STEM-tool computation on the changed code), or state in one line why "
          "none is owed (doc-only reasoning, founder-verified, check deferred to a "
          "named next step). \u2605 This gate now refuses up to "
        + str(MAX_REFUSALS_PER_TURN) + " times per turn, not once (his "
          "ruling 2026-10-24); producing the owed check is what stops it, "
          "because running a test changes the transcript this gate reads.",
        file=sys.stderr,
    )
    # ★ THE COUNTER MUST BE WRITTEN OR THE CEILING IS UNREACHABLE. A first
    # version read the counter and never wrote it, so `refusals` stayed 0,
    # `refusals >= MAX_REFUSALS_PER_TURN` was never true, and the gate would
    # have refused EVERY stop forever -- a trapped session, which is worse
    # than any missed trace. It was found because the replacement that added
    # this block silently no-opped on a mismatched anchor and the script did
    # not assert on it, which is the one shape this project keeps finding.
    if counter is not None:
        try:
            counter.write_text(str(refusals + 1), encoding="utf-8")
        except Exception:                      # noqa: BLE001
            pass                               # a lost count only weakens it
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
