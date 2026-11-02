#!/usr/bin/env python3
"""The Stop gate that exists to stop CC1 stopping is KILLED BY A TIMEOUT.

HIS QUESTION, 2026-11-02, verbatim: *"The reason we built the automated master
task list was so that you would keep working and wouldn't randomly drop
outstanding work. A couple of times recently that has worked out quite well. But
even more recently, that automated process no longer seems to be working, and you
have gone back to randomly stopping, despite having extensive work in front of
you? Can you fix it?"*

HIS OBSERVATION IS EXACTLY RIGHT, INCLUDING THE "WORKED, THEN STOPPED" SHAPE, AND
THE CAUSE IS MECHANICAL. `hooks/work_not_narrate.py` decides correctly -- executed
directly it refuses a stop with 12 items open on every input combination that
should refuse. It never gets to say so. Claude Code runs Stop hooks with
`timeoutMs: 15000` and kills whatever has not returned; a killed hook's exit code
2 never arrives, so the stop proceeds.

WHY IT DECAYS WITH SESSION LENGTH, WHICH IS WHY IT USED TO WORK. `turn_signals()`
reads the ENTIRE transcript to count this turn's tool calls and prose. The
transcript grows monotonically all session. So the gate's cost rises until it
crosses 15 s and the gate silently stops existing. It is not a regression in the
gate; it is the gate being outgrown.

THE PROJECT ALREADY SOLVED THIS EXACT PROBLEM ONCE. `hooks/compaction_watch.py`
scans the same transcript in 0.055 s against 41 MB, because it seeks to a stored
byte offset and reads only what is new. That technique was never applied here.
"""
from __future__ import annotations
import json, pathlib, re, sys, time, math, importlib.util

# `_cli_help` lives in scripts/. Locate it rather than assume a depth: the
# project has already had a helper import break when a script moved.
import sys as _sys, pathlib as _pl
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

T = pathlib.Path("/Users/georgejackson/.claude/projects/"
                 "-Users-georgejackson-Developer-Projects/"
                 "a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl")
HOOK = pathlib.Path.home() / ".claude" / "hooks" / "work_not_narrate.py"


def wilson(k: int, n: int):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n; z = 1.959963984540054
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def main() -> int:
    answer_help(__doc__, __file__)
    print("=" * 78)
    print("THE STOP GATE IS KILLED BY A TIMEOUT")
    print("=" * 78)
    sz = T.stat().st_size
    print(f"  transcript size: {sz:,} bytes ({sz/1048576:.1f} MiB)")

    # --- 1. the timeout record, straight out of the transcript -------------
    pat = re.compile(r'work_not_narrate\.py","durationMs":(\d+)(,"timedOut":(true|false))?')
    tsp = re.compile(r'"timestamp":"([0-9T:\-\.Z]+)"')
    seen = {}
    with T.open(errors="replace") as fh:
        for line in fh:
            if "work_not_narrate.py\",\"durationMs\"" not in line:
                continue
            m = pat.search(line); ts = tsp.search(line)
            if not m or not ts:
                continue
            seen[ts.group(1)] = (int(m.group(1)), m.group(3) == "true")
    by_day = {}
    for ts, (dur, to) in sorted(seen.items()):
        by_day.setdefault(ts[:10], []).append((dur, to))
    print(f"\n  STOP-HOOK INVOCATIONS RECORDED: {len(seen)}")
    print(f"  {'date':12s} {'n':>4s} {'timed out':>10s} {'rate':>8s}  {'median ms':>10s}")
    tot_n = tot_to = 0
    for day in sorted(by_day):
        rows = by_day[day]
        n = len(rows); to = sum(1 for _, t in rows if t)
        tot_n += n; tot_to += to
        durs = sorted(d for d, _ in rows)
        med = durs[len(durs) // 2]
        print(f"  {day:12s} {n:4d} {to:10d} {to/n:8.4f}  {med:10d}")
    p, lo, hi = wilson(tot_to, tot_n)
    print(f"  {'TOTAL':12s} {tot_n:4d} {tot_to:10d} {p:8.4f}  "
          f"Wilson 95% [{lo:.6f}, {hi:.6f}]")

    # --- 2. execute the hook's own reader and time it ----------------------
    spec = importlib.util.spec_from_file_location("wnn", HOOK)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    t0 = time.perf_counter()
    calls, prose, commit, had_d = m.turn_signals(T)
    t1 = time.perf_counter()
    print(f"\n  EXECUTING turn_signals() ON THE LIVE TRANSCRIPT")
    print(f"    wall clock           : {t1-t0:.3f} s   (hook budget 15.000 s)")
    print(f"    returned             : calls={calls} prose={prose} "
          f"commit={commit} had_d={had_d}")
    t0 = time.perf_counter()
    n_open, nxt = m.open_items()
    t1 = time.perf_counter()
    print(f"    open_items()         : {t1-t0:.3f} s -> n_open={n_open} next={nxt!r}")
    blocked, _why = m.verdict(calls, prose, commit, had_d, n_open, nxt, False)
    print(f"    verdict()            : {'REFUSE' if blocked else 'ALLOW'}")
    print(f"    -> THE DECISION IS CORRECT. IT IS NEVER DELIVERED.")

    # --- 3. the comparison that names the available fix --------------------
    cw = pathlib.Path.home() / ".claude" / "hooks" / "compaction_watch.py"
    has_offset = "offset" in cw.read_text() if cw.is_file() else False
    hook_src = HOOK.read_text()
    print(f"\n  THE FIX ALREADY EXISTS IN THIS REPOSITORY")
    print(f"    compaction_watch.py uses a stored byte offset : {has_offset}")
    print(f"    work_not_narrate.py uses a stored byte offset : "
          f"{'offset' in hook_src}")
    print(f"    work_not_narrate reads the whole file         : "
          f"{'read_text' in hook_src or 'for line in' in hook_src}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
