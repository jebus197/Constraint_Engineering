#!/usr/bin/env python3
"""How often does a SECOND sv follow a first closely enough to be refused for memory?

WHY THIS EXISTS. `scripts/cdsfl_sv.py`'s `memory-updated` check measures "has any
memory file been modified since the PREVIOUS sv commit".  Its baseline is
`_previous_sv_commit`, i.e. the newest commit whose subject starts with `sv:`.

That is correct for the FIRST sv of a session.  It is a blind spot for the SECOND:
when the first sv commits, pushes, and then FAILS a postcondition (typically the
RECOVERY SESSION STATE block, which sv deliberately will not write), the remedy is
to write that block and re-run sv.  The session's memory already exists -- it was
written for the first sv -- but it now predates the first sv commit, so the check
refuses the follow-up for lacking memory it has.

This script measures how often that shape arises, from git history alone.  Memory
mtimes live outside the repository and cannot be backfilled, so the measurable
quantity is the INTERVAL between consecutive sv commits: a gap short enough to be
the same working session is an occasion on which the blind spot could fire.

It decides nothing.  It reports a rate so the fix can be argued from evidence.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SESSION_GAP = timedelta(hours=6)   # a gap under this is plausibly one session

# The `memory-updated` check did not always exist.  It entered scripts/cdsfl_sv.py in
# ddd6e4c3 on 2026-08-06, so a close pair BEFORE that date is not exposure at all --
# the check could not have refused a save it was not yet part of.  Measuring without
# this cutoff overstates the rate: 117 of 209 pairs fall inside 6 hours across all
# history, but most of them predate the check.  Derived, not assumed:
#     git log --all --format='%h %cI %s' -S'memory-updated' -- scripts/cdsfl_sv.py | tail -1
CHECK_BORN = datetime.fromisoformat("2026-08-06T01:43:49+01:00")
CHECK_BORN_SHA = "ddd6e4c3"


def sv_commits(root: Path) -> list[tuple[str, datetime, str]]:
    out = subprocess.run(
        ["git", "log", "--all", "--grep=^sv:", "--format=%h%x1f%cI%x1f%s"],
        cwd=root, capture_output=True, text=True, check=True,
    ).stdout
    rows = []
    for line in out.splitlines():
        if not line.strip():
            continue
        sha, when, subject = line.split("\x1f", 2)
        rows.append((sha, datetime.fromisoformat(when), subject))
    rows.sort(key=lambda r: r[1])
    return rows


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    try:
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
        return (float(lo), float(hi))
    except Exception:
        z, p = 1.959963984540054, k / n
        d = 1 + z * z / n
        c = p + z * z / (2 * n)
        h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
        return (max(0.0, (c - h) / d), min(1.0, (c + h) / d))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--gap-hours", type=float, default=SESSION_GAP.total_seconds() / 3600)
    args = ap.parse_args()
    root = Path(args.root).resolve()
    gap = timedelta(hours=args.gap_hours)

    rows = sv_commits(root)
    if len(rows) < 2:
        print(f"only {len(rows)} sv commit(s) in history -- nothing to pair")
        return 0

    all_pairs = list(zip(rows, rows[1:]))
    # Only a pair whose SECOND commit postdates the check's birth is exposure.
    pairs = [(a, b) for a, b in all_pairs if b[1] >= CHECK_BORN]
    close = [(a, b) for a, b in pairs if (b[1] - a[1]) <= gap]
    quick = [(a, b) for a, b in close if (b[1] - a[1]) <= timedelta(minutes=15)]
    n, k = len(pairs), len(close)
    lo, hi = wilson(k, n)
    qlo, qhi = wilson(len(quick), n)

    print(f"sv commits in history:            {len(rows)}")
    print(f"consecutive pairs, all history:   {len(all_pairs)}")
    print(f"  of those, AFTER the check was born ({CHECK_BORN_SHA}, "
          f"{CHECK_BORN:%Y-%m-%d}): {n}")
    print(f"pairs within {args.gap_hours:g} h (one session): {k}  "
          f"{100.0 * k / n:.4f}%  Wilson [{100 * lo:.4f}%, {100 * hi:.4f}%]")
    print(f"pairs within 15 min (a follow-up fixing a postcondition, tonight's shape): "
          f"{len(quick)}  {100.0 * len(quick) / n:.4f}%  "
          f"Wilson [{100 * qlo:.4f}%, {100 * qhi:.4f}%]")
    print()
    print("THE SUB-15-MINUTE PAIRS -- the follow-up shape specifically:")
    for a, b in quick:
        mins = (b[1] - a[1]).total_seconds() / 60.0
        print(f"  {a[0]} -> {b[0]}  {mins:8.1f} min   {b[2][:58]}")
    print()
    print("THE CLOSE PAIRS -- each is an occasion the memory baseline could refuse a follow-up:")
    for a, b in close[-12:]:
        mins = (b[1] - a[1]).total_seconds() / 60.0
        print(f"  {a[0]} -> {b[0]}  {mins:8.1f} min   {b[2][:58]}")
    if len(close) > 12:
        print(f"  ... and {len(close) - 12} earlier")
    print()
    print("WHAT THIS DOES NOT SHOW. A close pair means the blind spot COULD fire, not that")
    print("it did: whether memory was written between the two is not recorded in git. The")
    print("rate bounds the exposure; it does not count refusals.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
