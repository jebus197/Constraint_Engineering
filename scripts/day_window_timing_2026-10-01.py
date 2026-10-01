#!/usr/bin/env python3
"""WHERE THE ELAPSED TIME OF 1 OCTOBER 2026 WENT, recomputed from the record.

WHY THIS SCRIPT EXISTS. `experimental_notes/Closing_Report_2026-10-01.md`
answered the founder's question "that took quite some time?" with a window
length and a suite share, and those figures had NO producing code -- the
arithmetic lived only as prose in the report, which `measured-rate-travels-with-its-script`
forbids. Worse, the window was WRONG, and wrong in a way only a script would
have caught.

THE DEFECT, and it is the same hour twice. The report opened "From the
compaction at 12:00 to this report is 6.8442 hours." The transcript records
that compaction as `2026-10-01T12:00:21.483Z` -- UTC -- which is 13:00:21
British Summer Time. The report read the UTC digits as local, so its
denominator was 3600 seconds too long and its headline proportion was
understated. The same mis-reading was live in `hooks/compaction_watch.py`,
which printed the UTC wall clock unlabelled beside a local-time clock line and
inflated every announced age by the UTC offset; that is repaired, and
`parse_transcript_ts` there carries the account.

WHAT IS MEASURED HERE VERSUS WHAT IS RECORDED. The compaction instant is READ
from the session transcript, so it cannot drift from the record. The 3 suite
durations are RECORDED CONSTANTS, taken from the pytest summary lines of the 3
completed full runs in that session; they are not recoverable from the
transcript after the fact, and that boundary is stated rather than hidden. The
2 deliberately abandoned part-runs are excluded, because a run stopped on
purpose is not a measurement of how long the suite takes.

NO CONFIDENCE INTERVAL IS REPORTED, DELIBERATELY. The suite share is an exact
ratio of 2 measured durations, not an estimate from a sample, so a Wilson or
any other sampling interval would be a category error. What IS reported is the
propagated timestamp granularity, which is the only uncertainty the quantity
actually has.

Run:  python3 scripts/day_window_timing_2026-10-01.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")
TRANSCRIPT = (pathlib.Path.home() / ".claude" / "projects"
              / "-Users-georgejackson-Developer-Projects"
              / "a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl")

# Pytest summary lines of the 3 COMPLETED full runs, 2026-10-01.
SUITE_RUNS_SECONDS = (2989.88, 3281.91, 3496.13)
# The instant the report's own window figure was computed at, local time.
WINDOW_END_LOCAL = "2026-10-01T18:51:00"
# What the report said before this script existed.
REPORT_WINDOW_HOURS = 6.8442
REPORT_SUITE_SHARE_PCT = 57.4208
# AND ITS NUMERATOR CANNOT BE RECONSTRUCTED EITHER, which is the second and
# larger fault. The report put suite time at 3.9300 h = 14148 s. The 3
# completed runs sum to 9767.92 s, leaving 4380 s to be explained by the 2
# part-runs the report itself describes as abandoned at 66% and 46%. Those
# fractions of a 2990-3496 s run give 3584 to 3920 s, short of 4380 s at
# either end of the range, so no accounting of the recorded runs reaches
# 3.9300 h. The figure is withdrawn rather than patched: a total that cannot
# be rebuilt from its parts is a claim about evidence, not evidence.
REPORT_SUITE_HOURS_WITHDRAWN = 3.9300


def newest_compaction(path: pathlib.Path) -> str | None:
    """The newest `isCompactSummary` timestamp at or before the window end."""
    newest = None
    if not path.is_file():
        return None
    with path.open("r", errors="ignore") as fh:
        for line in fh:
            if '"isCompactSummary"' not in line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("isCompactSummary") is True and d.get("type") == "user":
                ts = d.get("timestamp")
                if ts and ts[:10] == "2026-10-01" and ts < "2026-10-01T18:00:00Z":
                    if newest is None or ts > newest:
                        newest = ts
    return newest


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").strip().split("\n")[0])
    ap.add_argument("--transcript", default=str(TRANSCRIPT))
    args = ap.parse_args()

    ts = newest_compaction(pathlib.Path(args.transcript))
    if ts is None:
        print("THE COMPACTION INSTANT IS NOT AVAILABLE in this environment, so the "
              "window cannot be recomputed and no figure is reported.", file=sys.stderr)
        return 2

    utc = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    local = utc.astimezone(LONDON)
    end = dt.datetime.fromisoformat(WINDOW_END_LOCAL).replace(tzinfo=LONDON)

    window_h = (end - utc).total_seconds() / 3600
    suite_h = sum(SUITE_RUNS_SECONDS) / 3600
    share = suite_h / window_h * 100

    print("THE DAY'S WINDOW, 1 OCTOBER 2026")
    print("=" * 74)
    print(f"  compaction, as the transcript records it   {ts}  (UTC)")
    print(f"  compaction, local                          {local:%Y-%m-%d %H:%M:%S %Z}")
    print(f"  window end                                 {end:%Y-%m-%d %H:%M:%S %Z}")
    print(f"  window                                     {window_h:.4f} h")
    print(f"  suite time, {len(SUITE_RUNS_SECONDS)} completed runs           {suite_h:.4f} h")
    print(f"  suite share of the window                  {share:.4f} %")
    print()
    print(f"  the report stated                          {REPORT_WINDOW_HOURS:.4f} h, "
          f"{REPORT_SUITE_SHARE_PCT:.4f} %")
    drift = REPORT_WINDOW_HOURS - window_h
    print(f"  window overstated by                       {drift:.4f} h = {drift*3600:.1f} s")
    gap = REPORT_SUITE_HOURS_WITHDRAWN * 3600 - sum(SUITE_RUNS_SECONDS)
    print(f"  its suite total of {REPORT_SUITE_HOURS_WITHDRAWN:.4f} h leaves {gap:.0f} s "
          f"unaccounted by the {len(SUITE_RUNS_SECONDS)} recorded runs — WITHDRAWN")
    for frac in (0.66, 0.46):
        lo = frac * min(SUITE_RUNS_SECONDS)
        hi = frac * max(SUITE_RUNS_SECONDS)
        print(f"     a run abandoned at {frac:.0%} would contribute {lo:.0f}–{hi:.0f} s")

    # CROSS-VERIFICATION. The 21 April 2026 rule: at least 2 independent tools
    # on any computational claim. A single library agreeing with itself is not
    # a check.
    agree = []
    try:
        import numpy as np
        agree.append(("numpy", float(np.float64(suite_h) / np.float64(window_h) * 100)))
    except ImportError:
        pass
    try:
        import mpmath as mp
        mp.mp.dps = 30
        agree.append(("mpmath", float(mp.mpf(suite_h) / mp.mpf(window_h) * 100)))
    except ImportError:
        pass
    try:
        import sympy as sp
        agree.append(("sympy", float(sp.Float(suite_h, 20) / sp.Float(window_h, 20) * 100)))
    except ImportError:
        pass
    print()
    for name, val in agree:
        print(f"  share via {name:<8} {val:.6f} %")
    if len(agree) >= 2:
        spread = max(v for _n, v in agree) - min(v for _n, v in agree)
        print(f"  spread across {len(agree)} tools                      {spread:.2e} "
              f"percentage points")
    else:
        print("  ONLY 1 TOOL AVAILABLE — the cross-verification rule is NOT satisfied "
              "here and the figure is reported as unconfirmed.")

    try:
        from uncertainties import ufloat
        u = (ufloat(suite_h, len(SUITE_RUNS_SECONDS) / 3600)
             / ufloat(window_h, 2 / 3600) * 100)
        print(f"  propagated granularity                     {u:.4f} % "
              f"(1 s per endpoint; NOT a sampling interval)")
    except ImportError:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
