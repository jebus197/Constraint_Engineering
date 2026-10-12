#!/usr/bin/env python3
"""Stop hook: refuse to end a turn when work has accumulated well past the usual save rhythm.

HIS RULING, 2026-10-11: *"with sv also ran at every significant milestone, that would be a
significant advancement in our working practices. So if you can implement these features
mechanically somehow, I would suggest that you do this too."*

WHY A GATE AND NOT AN AUTOMATIC `sv`. The restore is read-only, so running it unasked is safe
and `compaction_watch.py` now does exactly that. `sv` is not: it writes state files, commits and
PUSHES. Running it automatically would push half-finished work the moment a turn ended, and the
founder's standing rule reserves pushing to his agreement. So the MECHANISM here is refusal, not
execution -- the same shape as `ffafp_stop_gate.py`, which cannot be forgotten because it fires
on the way out.

THE THRESHOLD IS DERIVED, NOT SHIPPED. He objected to a constant of 10 for the round cap on
exactly this ground: a number that is an average of THIS project's behaviour becomes arbitrary
the moment anything changes. Measured over the last 600 commits on 2026-10-11: 42 `sv` saves,
median gap 2 commits, 75th percentile 10.8, 90th 22.9, and a worst case of 267 commits with no
save at all. A fixed threshold of 3 would have fired on 19 of 42 cycles, 0.4524, Wilson
[0.3122, 0.6005] -- it would interrupt normal rhythm rather than catch the tail. So the gate
recomputes the 75th percentile from the repository's own history every time it runs, and fires
only when the current gap is worse than 3 save cycles in 4 historically were.

IT REFUSES AT MOST ONCE PER TURN, like the FFAFP gate, so it can be acknowledged and passed.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
STATE = pathlib.Path.home() / ".claude" / ".sv_milestone"
LOOKBACK = 600
FLOOR = 4          # never nag below this, whatever the history says
CEILING = 40       # never let a pathological history disarm the gate entirely


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=str(REPO), capture_output=True,
                              text=True, timeout=60).stdout
    except Exception:
        return ""


def _gaps_and_current() -> tuple[list[int], int]:
    """Commits between consecutive `sv:` saves, and how many have landed since the last one."""
    lines = [l for l in _git("log", f"-n{LOOKBACK}", "--pretty=%s").splitlines()]
    gaps, run, current, seen_first = [], 0, 0, False
    for msg in lines:                      # newest first
        if msg.lower().startswith("sv:"):
            if not seen_first:
                current, seen_first = run, True
            else:
                gaps.append(run)
            run = 0
        else:
            run += 1
    if not seen_first:
        current = run
    return gaps, current


def _threshold(gaps: list[int]) -> int:
    if not gaps:
        return FLOOR
    s = sorted(gaps)
    # 75th percentile, nearest-rank. No numpy: a hook must not need the science stack.
    idx = max(0, min(len(s) - 1, int(round(0.75 * (len(s) - 1)))))
    return max(FLOOR, min(CEILING, s[idx]))


def main() -> int:
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    if not (REPO / ".git").exists():
        return 0
    STATE.mkdir(parents=True, exist_ok=True)

    gaps, current = _gaps_and_current()
    thr = _threshold(gaps)
    if current <= thr:
        return 0

    head = _git("rev-parse", "--short", "HEAD").strip()
    marker = STATE / "last_refusal"
    try:
        if marker.is_file() and marker.read_text(encoding="utf-8").strip() == head:
            return 0          # already refused at this HEAD; do not loop
    except OSError:
        pass
    try:
        marker.write_text(head, encoding="utf-8")
    except OSError:
        pass

    dirty = len([l for l in _git("status", "--porcelain").splitlines() if l.strip()])
    sys.stderr.write(
        f"[sv-gate] {current} commits since the last `sv:` save, against a threshold of {thr} "
        f"derived from this repository's own history (median gap "
        f"{sorted(gaps)[len(gaps)//2] if gaps else 'n/a'}, 75th percentile {thr}, worst recorded "
        f"{max(gaps) if gaps else 'n/a'}).\n"
        f"  HIS RULING, 2026-10-11: \"sv also ran at every significant milestone ... implement "
        f"these features mechanically\".\n"
        f"  Working tree: {dirty} uncommitted path(s).\n"
        f"  RUN IT NOW: python3 scripts/cdsfl_sv.py --commit --push -m \"sv: <what landed>\"\n"
        f"  It is NOT run automatically because sv PUSHES, and pushing half-finished work on "
        f"every turn end is worse than the gap it would close.\n"
        f"  If a save is genuinely not owed yet, say so in one line and continue -- this "
        f"refuses at most once per HEAD.\n")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
