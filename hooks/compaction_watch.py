#!/usr/bin/env python3
"""UserPromptSubmit hook: say LOUDLY when a compaction has happened and `rs` has not been run.

THE FAILURE THIS PREVENTS, and it is measured rather than hypothetical.

The founder runs this assistant as a remote session on a Mac Mini at home, driven from
wherever he happens to be. The remote interface gives NO indication that a compaction has
occurred. So he cannot know when to issue `rs`, and after a compaction the assistant is
working from a summary of the project rather than the project.

Measured in one session's transcript on 2026-09-04: SIX compactions, at 2026-08-26 00:19,
2026-08-28 03:50, 2026-08-30 17:06, 2026-08-31 21:45, 2026-09-01 13:16 and 2026-09-02
18:51 British Summer Time. Those 6 times were stated an hour early until 2026-10-01: the
transcript records UTC and they were copied out as though they were local, which is the
same fault `parse_transcript_ts` was added to stop. The UTC values are 2026-08-25 23:19,
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
import json
import subprocess, sys, time, pathlib, re, os
from datetime import datetime, timezone

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


def parse_transcript_ts(iso_ts):
    """A transcript timestamp as an AWARE datetime. Claude Code writes UTC ("...Z").

    THE DEFECT THIS EXISTS TO PREVENT, measured 2026-10-01 and confirmed to the
    second in mpmath. `time.mktime(time.strptime(ts[:19], ...))` reads a
    struct_time as LOCAL time, so the UTC stamp `2026-10-01T22:04:19.096Z` was
    taken as 22:04:19 BST, an hour before it happened. Two consequences, and
    neither is cosmetic:

      1. The age was inflated by exactly the UTC offset -- 3600 s under BST. A
         compaction 791 s old was announced as "73m ago".
      2. The notice printed the UTC wall clock with no zone label, directly
         beside `prompt_clock.py` printing LOCAL time with one. Two clocks an
         hour apart, in the same context window, and only one of them labelled.

    IT INVERTED AN ORDERING, which is the part that cost something. Asked
    whether a compaction fell before or after a save, the notice's "22:04" put
    it BEFORE a commit timestamped 22:58, when the truth was 23:04:19 BST and
    therefore AFTER it. The answer read off the instrument was the opposite of
    the answer in the record. The same hour also reached a delivered report,
    whose elapsed-time denominator was 1 hour too long and whose headline
    proportion was understated as a result.

    A stamp carrying an explicit offset is honoured. A naive one is taken as
    UTC, which is what Claude Code writes, and that assumption is stated here
    rather than left implicit.
    """
    s = (iso_ts or "").strip()
    if not s:
        return None
    if s.endswith(("Z", "z")):
        s = s[:-1] + "+00:00"
    d = None
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        try:
            d = datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d

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
        raw = f.read_text(encoding="utf-8").strip()
        if not raw:
            return False
        # COMPARE INSTANTS, NOT STRINGS. Both writers happen to emit UTC today
        # -- `cdsfl_recover.py` writes `datetime.now(timezone.utc).isoformat()`
        # and the transcript writes "...Z" -- so the old lexicographic compare
        # was correct, and verified so on 2026-10-01. It was also one edit away
        # from silently disarming this alarm: a marker written in LOCAL time is
        # lexicographically LARGER than the UTC stamp of the same instant, so a
        # restore that ran an hour BEFORE a compaction would read as after it.
        # That is the identical mixed-zone fault repaired 20 lines above, and
        # leaving its twin in the arming path is how the project keeps finding
        # the same defect twice.
        ran, comp = parse_transcript_ts(raw), parse_transcript_ts(iso_ts)
        if ran is not None and comp is not None:
            return ran >= comp
        return bool(raw) and raw[:19] >= (iso_ts or "")[:19]
    except (OSError, ValueError):
        return False

def _desktop_notify(when_iso, ago):
    """Fire a macOS notification ONCE per compaction, and never fell the hook.

    THE DEFECT THIS CLOSES, named by the founder on 2026-10-03: he had asked for
    a compaction alert in macOS notifications and reported it had never worked.
    Measured that day: **0 hooks emitted a desktop notification at all** -- no
    `osascript`, no `terminal-notifier`, nothing in the entire hooks directory.
    It had never been built, so it could never have fired.

    WHAT IS AND IS NOT REACHABLE. No hook runs AT compaction, so a genuine
    PRE-compaction warning cannot be delivered from here; the earliest moment
    the event is observable is the next UserPromptSubmit, which is this one.
    This is therefore a POST-compaction alert, and saying so is better than
    promising the thing the surface cannot do.

    ONCE PER COMPACTION, NOT ONCE PER TURN. The notice itself repeats every turn
    until `rs` is issued, by design. A notification that did the same would be
    42 banners over 10.69 hours -- the measured repeat count of the 2026-09-07
    compaction -- and would be muted within the hour, which is how an alarm
    stops being an alarm. The compaction timestamp is the key.
    """
    try:
        state = STATE / "desktop_notified"
        seen = set()
        if state.exists():
            seen = set(state.read_text().split("\n"))
        if when_iso in seen:
            return
        subprocess.run(
            ["osascript", "-e",
             'display notification "Context was compacted {} . Issue rs when convenient."'
             ' with title "Claude Code — CDSFL" subtitle "compaction detected"'.format(ago)],
            capture_output=True, timeout=10)
        seen.add(when_iso)
        state.write_text("\n".join(sorted(x for x in seen if x))[-8000:])
    except Exception:
        pass  # an alert must never break the hook that carries the notice


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

    # LOCAL TIME, AND LABELLED. The founder reads this beside a clock line in
    # local time; an unlabelled UTC stamp an hour away from it is worse than no
    # stamp. See parse_transcript_ts for what the unlabelled form cost.
    when = parse_transcript_ts(newest)
    if when is None:
        shown, ago = newest[:19].replace("T", " ") + " (UNPARSED)", "unknown"
    else:
        try:
            local = when.astimezone()
            shown = local.strftime("%Y-%m-%d %H:%M:%S %Z").strip()
            ago = human(time.time() - when.timestamp())
        except (OSError, OverflowError, ValueError):
            shown, ago = newest[:19].replace("T", " ") + " UTC", "unknown"
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
    _desktop_notify(str(newest), ago)
    msg = (f"[compaction] COMPACTION AT {shown} ({ago} ago) "
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


# GUARDED UNDER `__main__`, 2026-10-01. This ran at IMPORT time and then called
# `sys.exit(0)`, so the module could not be imported at all -- the wart its own
# comment above complains about ("importing that hook runs its main(), which
# reads a stdin this process has already consumed"). Claude Code invokes this
# file as a script, where `__name__` is `"__main__"`, so the runtime behaviour
# is byte-for-byte what it was; what changes is that `parse_transcript_ts` and
# `_recovery_ran_after` can now be CALLED by a test instead of being asserted
# about from their source text.
if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
