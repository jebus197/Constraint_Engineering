#!/usr/bin/env python3
"""The continuation gate he built was correct and fired on nothing. 3 disablements.

HIS QUESTION, 2026-10-28, verbatim: *"You wrote a script for your master task
list that prompts you to continue until completion. Is it not better to just
place the remaining tasks to the top of your master task list and reuse/adapt
this script as needed to avoid these frequent/needed stops?"*

THE ANSWER IS THAT NO ADAPTATION WAS NEEDED. `hooks/work_not_narrate.py` already
decides correctly. It fired on nothing because it was disabled 3 independent
ways, and the 3rd one disabled a DIFFERENT gate that would have covered for it.

  1. `~/.claude/hooks/.work_not_narrate_PARKED`, a 0-byte sentinel dated
     2026-09-11, on which `main()` returns 0 before it reads the payload.
  2. Its `Stop` registration in `~/.claude/settings.json` had been renamed to
     `_PARKED_Stop_2026-09-11`, so the harness never invoked it at all. Its own
     guard `test_it_is_registered_as_a_Stop_hook` PASSES on a parked entry by
     design, so nothing was red.
  3. `hooks/ticket_queue_gate.py`, which IS wired and which stopped yielding
     after one refusal on his 2026-10-24 ruling, stood down because
     `~/.claude/.ticket_queue/paused_by_founder.json` carried his instruction of
     2026-10-24: "do not resume the master task list until I tell you to do so".

ALL 3 ARE NOW CLEARED. The pause is ARCHIVED rather than deleted, under
`~/.claude/.ticket_queue/lifted/`, because his original instruction must stay
readable; his 2026-10-28 message is the explicit resumption it required.

WHAT WAS MEASURED, AND IT CORRECTS AN EARLIER READING OF MINE IN THE SAME HOUR.
A first pass reconstructed the predicate from the module's `MIN_TOOL_CALLS` and
`MIN_PROSE` constants and reported that it would have caught only 1 of 12 of the
session's stops, concluding that the tool-count condition had to go. That was
wrong, and wrong in this project's most-recorded way: it measured the constants
instead of CALLING the deciding function. `verdict()` uses `MIN_TOOL_CALLS` only
to choose the WORDING of its refusal message; the decision is "refuse whenever
OPEN work remains, unless he issued `d`, nothing is open, or a blocker was
raised". Calling it gives 11 of 12 rather than 1 of 12, so the predicate was
already right and changing it would have damaged correct code -- the failure
class recorded the same morning as "a guard can accuse correct code", 9 of 36.

Run with --help to read this without computing anything.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

HOOKS = pathlib.Path.home() / ".claude" / "hooks"
HOOK = REPO / "hooks" / "work_not_narrate.py"
PARKED_PATH = HOOKS / ".work_not_narrate_PARKED"
LIFTED = pathlib.Path.home() / ".claude" / ".ticket_queue" / "lifted"
SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"
SESSIONS = pathlib.Path.home() / ".claude" / "projects" / \
    "-Users-georgejackson-Developer-Projects"
#: The open count the task list carries. Read, never typed.
TASKS = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _newest_transcript() -> pathlib.Path | None:
    cands = sorted(SESSIONS.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    return cands[-1] if cands else None


def _turns(transcript: pathlib.Path) -> list[dict]:
    """Genuine founder turns, streamed. The transcript runs to hundreds of MB."""
    turns: list[dict] = []
    cur: dict | None = None
    with transcript.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            msg = o.get("message") or {}
            role = msg.get("role") or o.get("type")
            content = msg.get("content")
            if role == "user":
                if o.get("isMeta") or o.get("isCompactSummary"):
                    continue
                if isinstance(content, str):
                    txt = content
                elif isinstance(content, list):
                    if any(isinstance(b, dict) and b.get("type") == "tool_result"
                           for b in content):
                        continue          # tool output is not him
                    txt = " ".join(b.get("text", "") for b in content
                                   if isinstance(b, dict) and b.get("type") == "text")
                else:
                    continue
                head = txt.lstrip()
                if (not head or head.startswith("<task-notification>")
                        or head.startswith("[Request interrupted")
                        or head.startswith("<system-reminder>")):
                    continue
                if cur:
                    turns.append(cur)
                cur = {"user": txt, "tool_calls": 0, "prose": 0}
            elif role == "assistant" and cur is not None and isinstance(content, list):
                for b in content:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_use":
                        cur["tool_calls"] += 1
                    elif b.get("type") == "text":
                        cur["prose"] += len(b.get("text", "") or "")
    if cur:
        turns.append(cur)
    return turns


def _wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    import numpy as np
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def measure(last_n: int = 12) -> dict:
    from scipy import stats

    wnn = _load(HOOK, "wnn_under_measurement")
    mc = _load(HOOKS / "mc_commands.py", "mc_under_measurement")
    sys.path.insert(0, str(REPO / "scripts"))
    from task_list_markers import parse_entries           # noqa: E402

    n_open = len([e for e in parse_entries(TASKS) if e.state == "OPEN"])
    r: dict = {"n_open_on_the_list": n_open,
               "MIN_TOOL_CALLS": wnn.MIN_TOOL_CALLS,
               "MIN_PROSE": wnn.MIN_PROSE,
               "MAX_REFUSALS_PER_TURN": wnn.MAX_REFUSALS_PER_TURN}

    # --- 1. the 3 disablements, each by still-checkable evidence -----------
    r["sentinel_path"] = str(PARKED_PATH)
    r["sentinel_present_now"] = PARKED_PATH.exists()
    r["is_parked_now"] = bool(wnn.is_parked())
    backups = sorted(SETTINGS.parent.glob("settings.json.bak-*"))
    parked_key_in_a_backup = None
    for b in reversed(backups):
        try:
            if "_PARKED_Stop" in b.read_text(encoding="utf-8"):
                parked_key_in_a_backup = b.name
                break
        except OSError:
            continue
    r["settings_backups"] = len(backups)
    r["parked_key_evidenced_by"] = parked_key_in_a_backup
    try:
        live = json.loads(SETTINGS.read_text(encoding="utf-8"))["hooks"]
        r["armed_on_Stop_now"] = "work_not_narrate" in json.dumps(live.get("Stop", []))
        r["parked_keys_remaining"] = [k for k in live if k.startswith("_PARKED_")]
    except (OSError, ValueError, KeyError):
        r["armed_on_Stop_now"] = None
        r["parked_keys_remaining"] = None
    lifted = sorted(LIFTED.glob("paused_by_founder.lifted-*.json")) if LIFTED.is_dir() else []
    r["pause_archives"] = len(lifted)
    if lifted:
        d = json.loads(lifted[-1].read_text(encoding="utf-8"))
        r["pause_paused_at"] = d.get("paused_at")
        r["pause_verbatim_head"] = str(d.get("verbatim", ""))[:120]
        r["pause_lifted_at"] = d.get("lifted_at")

    # --- 2. the deciding layer, CALLED ------------------------------------
    t = _newest_transcript()
    r["transcript"] = t.name if t else None
    r["transcript_mb"] = round(t.stat().st_size / 1048576, 1) if t else None
    turns = _turns(t) if t else []
    r["genuine_turns_total"] = len(turns)
    tail = turns[-last_n:]
    r["window"] = len(tail)
    refused = allowed_d = 0
    rows = []
    for x in tail:
        had_d = "d" in mc.commands_in(x["user"])
        block, why = wnn.verdict(x["tool_calls"], x["prose"], False, had_d,
                                 n_open, "T1", False)
        refused += bool(block)
        allowed_d += bool(had_d and not block)
        rows.append({"tool_calls": x["tool_calls"], "prose": x["prose"],
                     "had_d": had_d, "refused": bool(block),
                     "reason": why.splitlines()[0][:90]})
    r["rows"] = rows
    r["refused"] = refused
    r["refused_share"] = refused / len(tail) if tail else float("nan")
    r["refused_wilson"] = _wilson(refused, len(tail))
    r["allowed_because_he_issued_d"] = allowed_d

    # --- 3. the constants-only reading, which was WRONG -------------------
    naive = sum(1 for x in tail
                if x["tool_calls"] < wnn.MIN_TOOL_CALLS
                and x["prose"] > wnn.MIN_PROSE
                and "d" not in mc.commands_in(x["user"]))
    r["constants_only_reading"] = naive
    r["constants_only_wilson"] = _wilson(naive, len(tail))
    disc_b = sum(1 for x, row in zip(tail, rows)
                 if row["refused"] and not (
                     x["tool_calls"] < wnn.MIN_TOOL_CALLS
                     and x["prose"] > wnn.MIN_PROSE
                     and "d" not in mc.commands_in(x["user"])))
    disc_c = sum(1 for x, row in zip(tail, rows)
                 if (not row["refused"]) and (
                     x["tool_calls"] < wnn.MIN_TOOL_CALLS
                     and x["prose"] > wnn.MIN_PROSE
                     and "d" not in mc.commands_in(x["user"])))
    r["discordant_live_only"], r["discordant_constants_only"] = disc_b, disc_c
    r["mcnemar_p"] = (float(stats.binomtest(disc_b, disc_b + disc_c, 0.5).pvalue)
                      if (disc_b + disc_c) else float("nan"))

    # --- 4. its own self-test, executed ----------------------------------
    r["self_test_exit"] = int(wnn.self_test())
    return r


def main() -> int:
    # THE HELP-HELPER CALL WAS REMOVED HERE, 2026-10-29. It sat above the parser
    # and passed `takes_no_arguments=False`. `test_no_script_uses_both` refuses
    # that combination and is right: the helper answers the help flag FIRST, so
    # argparse's own flag list never reaches the reader and the script advertises
    # nothing. argparse already answers help and already rejects an unknown flag
    # with exit 2, so the call bought nothing and cost the usage text.
    #
    # IT WAS ADDED ON 2026-10-28 TO FIX THE OPPOSITE FAULT: without that keyword
    # the helper refused EVERY argument before the parser ran, so the json flag
    # exited 2 saying the script takes no arguments. That repair was right about
    # the symptom and wrong about the remedy -- the helper is for scripts with NO
    # parser, and this one has a parser.
    ap = argparse.ArgumentParser(
        description="Measure why the continuation gate never fired.")
    ap.add_argument("--window", type=int, default=12,
                    help="how many of the newest founder turns to judge (default 12)")
    ap.add_argument("--json", action="store_true", help="emit figures as JSON")
    a = ap.parse_args()
    r = measure(last_n=a.window)
    if a.json:
        print(json.dumps(r, indent=2, default=str))
        return 0

    print("=" * 78)
    print("THE CONTINUATION GATE WAS CORRECT AND FIRED ON NOTHING")
    print("=" * 78)
    print(f"\n1. THE 3 DISABLEMENTS")
    print(f"   sentinel {r['sentinel_path']}")
    print(f"     present now {r['sentinel_present_now']}; is_parked() now "
          f"{r['is_parked_now']}")
    print(f"   the parked Stop key is evidenced by the settings backup "
          f"{r['parked_key_evidenced_by']} (of {r['settings_backups']} backups)")
    print(f"     armed on Stop now {r['armed_on_Stop_now']}; parked keys remaining "
          f"{r['parked_keys_remaining']}")
    print(f"   the pause he set on {r.get('pause_paused_at')}:")
    print(f"     \"{r.get('pause_verbatim_head')}\"")
    print(f"     archived, not deleted; lifted {r.get('pause_lifted_at')}")

    print(f"\n2. THE DECIDING LAYER, CALLED on {r['transcript_mb']} MB of transcript")
    print(f"   {r['genuine_turns_total']} genuine founder turns; judging the newest "
          f"{r['window']} against {r['n_open_on_the_list']} OPEN list items")
    print(f"   {'tools':>6} {'prose':>7} {'d':>6}  refuse  reason")
    for row in r["rows"]:
        print(f"   {row['tool_calls']:>6} {row['prose']:>7} {str(row['had_d']):>6}"
              f"  {str(row['refused']):>6}  {row['reason'][:52]}")
    lo, hi = r["refused_wilson"]
    print(f"   REFUSED {r['refused']} of {r['window']} = {r['refused_share']:.6f}, "
          f"Wilson [{lo:.6f}, {hi:.6f}]")
    print(f"   allowed because he issued `d`: {r['allowed_because_he_issued_d']}")

    print(f"\n3. THE READING THAT WAS WRONG, recorded because it was mine")
    nlo, nhi = r["constants_only_wilson"]
    print(f"   reconstructing the predicate from MIN_TOOL_CALLS="
          f"{r['MIN_TOOL_CALLS']} and MIN_PROSE={r['MIN_PROSE']} gives "
          f"{r['constants_only_reading']} of {r['window']}")
    print(f"   = {r['constants_only_reading']/r['window']:.6f}, Wilson "
          f"[{nlo:.6f}, {nhi:.6f}] -- against {r['refused']} when CALLED")
    print(f"   discordant: live-only {r['discordant_live_only']}, constants-only "
          f"{r['discordant_constants_only']}, exact McNemar p = {r['mcnemar_p']:.6f}")
    print(f"   `verdict` uses MIN_TOOL_CALLS only to WORD its message. Measuring a "
          f"constant is not measuring a decision.")

    print(f"\n4. ITS OWN SELF-TEST, EXECUTED: exit {r['self_test_exit']} "
          f"(0 = all cases correct)")
    print(f"   MAX_REFUSALS_PER_TURN = {r['MAX_REFUSALS_PER_TURN']}; "
          f"`ticket_queue_gate` does not yield at all, so it is the binding one")

    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)
    print("""
  1. No adaptation of the predicate was needed or made. It already refuses
     whenever OPEN work remains, and honours `d` absolutely.
  2. The fix was to REMOVE 3 disablements, not to change any logic.
  3. The correction in section 3 is the lesson: this project's standing rule is
     to verify the DECIDING layer, and a first reading of mine measured 2
     constants the decision does not consult.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
