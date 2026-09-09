#!/usr/bin/env python3
"""UserPromptSubmit hook: say LOUDLY when a compaction has happened and `rs` has not been run.

THE FAILURE THIS PREVENTS, and it is measured rather than hypothetical.

The founder runs this assistant as a remote session on a Mac Mini at home, driven from
wherever he happens to be. The remote interface gives NO indication that a compaction has
occurred. So he cannot know when to issue `rs`, and after a compaction the assistant is
working from a summary of the project rather than the project.

Measured in one session's transcript on 2026-09-04: SIX compactions, at 2026-08-25 23:19,
2026-08-28 02:50, 2026-08-30 16:06, 2026-08-31 20:45, 2026-09-01 12:16 and 2026-09-02
17:51. The founder was aware of almost none of them. The last of the six preceded a night
in which four measurements in three hours were drawn from a narrow slice without checking
the population they claimed to describe -- a config scan of 4 files out of 44, a verdict
counted with a label the code never emits, and phrase occurrences inside model replies read
as gate events. Running `rs` corrected three conclusions that had already been delivered as
finished, one of them the headline of the previous night's report.

The remedy is not more care. It is knowing that the context is a summary.

HOW DETECTION WORKS. Claude Code writes the session transcript as JSONL and marks a
compaction with `"isCompactSummary": true` on a user entry. That is an exact, structural
marker -- not a heuristic over prose.

WHY IT IS CHEAP. The transcript reached 41 MB in this session, so re-reading it every turn
is not viable. This seeks to a stored byte offset and scans only what is new, so the cost
is proportional to one turn's output rather than to the session's history.

WHAT IT DOES. If the newest compaction is later than the last `rs` the founder acknowledged,
every prompt carries a notice until it is acknowledged. The notice names the time and how
long ago, so both parties see it -- the founder in the transcript, the assistant in context.

ACKNOWLEDGING. The hook clears itself when the founder's message contains `rs` as a
standalone token, which is the command that does the restoring. Nothing else clears it.

MUST ALWAYS EXIT 0. A hook that blocks a prompt is far worse than a missed notice.
"""
import json, sys, time, pathlib, re, os

STATE = pathlib.Path.home() / ".claude" / ".compaction_watch"
RS_TOKEN = re.compile(r"(?:^|[\s,;])rs(?:$|[\s,;.!])", re.I)


def human(sec):
    # NEGATIVE GUARD. A compaction cannot be in the future, but clock skew between
    # the writer of the transcript timestamp and this process can make it look that
    # way, and the naive form rendered "-35917s ago" -- caught by this hook's own
    # P-pass on 2026-09-04. A notice that reads as nonsense is a notice that gets
    # ignored, which is the failure the hook exists to prevent.
    if sec < 0:
        return "moments"
    s = int(sec)
    if s < 90:
        return f"{s}s"
    if s < 5400:
        return f"{s // 60}m"
    if s < 172800:
        return f"{s // 3600}h{(s % 3600) // 60:02d}m"
    return f"{s // 86400}d {(s % 86400) // 3600}h"


def find_transcript(session_id):
    if not session_id:
        return None
    root = pathlib.Path.home() / ".claude" / "projects"
    try:
        for p in root.glob(f"*/{session_id}.jsonl"):
            return p
    except Exception:
        pass
    return None


def _rs_was_issued(prompt: str) -> bool:
    """True only when `rs` is ISSUED as a command, not merely mentioned.

    An MC command line is short and made of short tokens. Prose is not. Checks
    the last 6 non-empty lines individually, so `rs` on its own final line after
    a paragraph still counts.
    """
    lines = [ln for ln in (prompt or "").strip().splitlines() if ln.strip()][-6:]
    for line in lines:
        toks = [t.strip().lower().rstrip(".!?,;") for t in re.split(r"[,\s]+", line.strip()) if t.strip()]
        if not toks or len(toks) > 14:
            continue
        if "rs" not in toks:
            continue
        # LOOSENED 2026-09-08, after the strict form rejected a real invocation.
        # Requiring EVERY token to be short rejected "a, d (Do the rs first.)"
        # for the 7-character "first.)" -- a genuine issuance, missed. Requiring
        # a SHORT LINE that is MOSTLY short tokens keeps the prose out ("so I can
        # run rs as needed..." is long and mostly long words) while admitting a
        # command with a parenthetical aside.
        short = sum(1 for t in toks if len(t) <= 3)
        if len(toks) <= 6 and short * 2 >= len(toks):
            return True
    return False


def _recovery_ran_after(iso_ts: str) -> bool:
    """Did an actual restore run since that compaction?

    THE SEMANTIC PATH, and the primary one. `scripts/cdsfl_recover.py --full`
    writes `~/.claude/.compaction_watch/last_recovery` when it completes, so the
    alarm can ask whether context was RESTORED rather than whether a token was
    TYPED. Both previous failures -- silenced by prose, then deaf to a real
    command -- came from inferring the event from text instead of recording it.
    """
    try:
        f = STATE / "last_recovery"
        if not f.is_file():
            return False
        ran = f.read_text(encoding="utf-8").strip()[:19]
        return bool(ran) and ran >= (iso_ts or "")[:19]
    except (OSError, ValueError):
        return False

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    sid = str(payload.get("session_id") or "").replace("/", "_")[:128]
    prompt = str(payload.get("prompt") or "")

    tpath = payload.get("transcript_path") or find_transcript(sid)
    if not tpath:
        return
    tpath = pathlib.Path(tpath)
    if not tpath.is_file():
        return

    STATE.mkdir(parents=True, exist_ok=True)
    sf = STATE / (sid or "default")
    st = {"offset": 0, "last_compaction": None, "acknowledged": None}
    try:
        if sf.exists():
            st.update(json.loads(sf.read_text()))
    except Exception:
        pass

    # A truncated or rotated transcript must not be scanned from a stale offset.
    try:
        size = tpath.stat().st_size
    except Exception:
        return
    if st.get("offset", 0) > size:
        st["offset"] = 0

    newest = st.get("last_compaction")
    try:
        with tpath.open("r", errors="ignore") as fh:
            fh.seek(st.get("offset", 0))
            for line in fh:
                if '"isCompactSummary"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("isCompactSummary") is True and d.get("type") == "user":
                    ts = d.get("timestamp")
                    if ts:
                        newest = ts
            st["offset"] = fh.tell()
    except Exception:
        pass
    st["last_compaction"] = newest

    # THE ALARM COULD BE DISARMED BY TALKING ABOUT IT (2026-09-08).
    #
    # `RS_TOKEN` matched "rs" anywhere in the prompt with only whitespace or
    # punctuation around it, so PROSE MENTIONING the command acknowledged the
    # compaction. Measured: the founder wrote "so I can run `rs` as needed" at
    # 00:53 while ASKING why the alarm had not reached him, and that sentence
    # silenced it. Asking about the alarm turned the alarm off, and the 14:15:01
    # compaction was marked acknowledged although `rs` was never run.
    #
    # Same shape as the other guards repaired this night: defeated by something
    # that merely RESEMBLES what it watches for.
    #
    # The rule now matches how MC commands are actually issued -- as a short line
    # of comma or space separated tokens ("rs", "a, d, rs"), never buried in a
    # sentence. This mirrors `commands_in()` in mc_commands.py, which returns []
    # for that same prose and ['a','d','rs'] for a real invocation, verified by
    # execution. It is reimplemented rather than imported because importing that
    # hook runs its main(), which reads a stdin this process has already consumed.
    if newest and (_recovery_ran_after(newest) or _rs_was_issued(prompt)):
        st["acknowledged"] = newest

    try:
        sf.write_text(json.dumps(st))
    except Exception:
        pass

    if not newest or st.get("acknowledged") == newest:
        return

    try:
        t = time.mktime(time.strptime(newest[:19], "%Y-%m-%dT%H:%M:%S"))
        ago = human(time.time() - t)
    except Exception:
        ago = "unknown"
    # ADDRESSED TO THE FOUNDER FIRST, 2026-09-08. This message used to speak only
    # to the assistant ("Say so, and run the restore"), and was emitted with
    # suppressOutput=True so it reached the assistant and NOBODY ELSE. Delivery to
    # the founder therefore depended on the assistant choosing to relay it, every
    # turn. Measured over the compaction of 2026-09-07 14:15:01: the notice fired
    # 42 times across 10.69 hours and was relayed once.
    #
    # An alarm routed through the party it is monitoring is not an independent
    # alarm. The founder is the one who issues `rs`, so the notice addresses him,
    # and the assistant's instruction follows rather than leads.
    msg = (f"[compaction] COMPACTION AT {newest[:19].replace('T', ' ')} ({ago} ago) "
           f"— `rs` HAS NOT BEEN RUN SINCE.\n"
           f"  GEORGE: issue `rs` when convenient. Until then the assistant is "
           f"working from a summary of the project rather than the project.\n"
           f"  ASSISTANT: say so in your reply, and restore before relying on "
           f"recalled state — the tracker, resources/RECOVERY.md, "
           f"scripts/cdsfl_recover.py --full.\n"
           f"  This repeats every turn until `rs` is issued, so it cannot scroll "
           f"out of view permanently.")
    # VISIBLE, NOT SUPPRESSED (founder ruling, 2026-09-08). See the note above.
    print(json.dumps({
        "suppressOutput": False,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": msg,
        },
    }))


try:
    main()
except Exception:
    pass
sys.exit(0)
