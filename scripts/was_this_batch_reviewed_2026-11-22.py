#!/usr/bin/env python3
"""Did a free panel see this batch before it was committed?

HIS INSTRUCTION, 2026-11-21, given in the same breath as the autonomy handover
and called equally important: *"after every meaningful batch of work, you should
always run your fixes by a free panel to check them, the check any fixes they
suggest before implementing them."* (*"the check"* is a typo for *"then check"*;
the correction is unambiguous and is recorded in THE_STANDING_GOAL.md.)

WHY A DETECTOR AND NOT A RESOLUTION TO REMEMBER. This project's own record on
rules that depend on remembering is explicit: *"The failure was never the absence
of a rule or a checker; it was never running the checker."* An instruction that
lives only in prose is an instruction nothing reaches, and `additive-standard`'s
symmetric form rules that out -- 11 confirmed defects here were additions that
did nothing. So the question is asked mechanically, at the one moment it can be
answered: a commit is the unit of a batch under his 2026-11-10 ruling, so the
pre-commit pre-flight is where "was this batch reviewed" has a definite meaning.

IT REPORTS. IT DOES NOT REFUSE. A false refusal at a commit gate costs about 27
minutes of his 8-core machine per occurrence and would make the rule the first
thing a future session switches off; this project has already recorded a case
where a false positive is why a rule went unenforced. The report is modelled on
the guard-gap pre-flight added the same night, which prints one line and exits 0
whatever it finds. If the report is measured to be ignored, THAT is the evidence
for escalating to a refusal -- not an assumption now.

WHAT COUNTS AS A ROUND. A panel round writes one directory under bench/logs/.
A round is COMPLETE when `completion_barrier.json` exists, which is the marker
this project already learned to wait for rather than inferring completion from
seat files appearing. A round is USEFUL when at least 1 seat returned ok with a
non-empty response: a round where every seat failed is a round that checked
nothing, and reporting it as review would be the fail-safe-recorded-as-fact
error this project has already made once.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
BARRIER = "completion_barrier.json"

#: Seat identifiers from the dispatch table in .claude/CLAUDE.md. A file named
#: for one of these is a seat's reply; every other json in a round directory is
#: harness bookkeeping (topology, sandbox manifest, attribution) and must not be
#: counted as a review.
SEATS = ("cc2", "cx", "ge", "cgpt", "ds", "fable")


def head_time():
    """Committer time of HEAD, or None in a repository with no commits."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct"], cwd=REPO,
            capture_output=True, text=True, timeout=30)
    except Exception:                      # noqa: BLE001 -- report, never raise
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def seats_in(d: pathlib.Path):
    """(ok_seats, failed_seats) for one round directory."""
    ok, bad = [], []
    for name in SEATS:
        f = d / f"{name}.json"
        if not f.is_file():
            continue
        try:
            rec = json.loads(f.read_text())
        except Exception:                  # noqa: BLE001
            bad.append(name)
            continue
        if rec.get("ok") and str(rec.get("response") or "").strip():
            ok.append(name)
        else:
            bad.append(name)
    return ok, bad


def rounds_since(epoch):
    """Complete rounds whose barrier landed after `epoch`. Newest first."""
    found = []
    if not LOGS.is_dir():
        return found
    for d in LOGS.iterdir():
        if not d.is_dir():
            continue
        barrier = d / BARRIER
        if not barrier.is_file():
            continue
        try:
            mt = barrier.stat().st_mtime
        except OSError:
            continue
        if epoch is not None and mt <= epoch:
            continue
        ok, bad = seats_in(d)
        found.append({"dir": d.name, "mtime": mt, "ok": ok, "failed": bad})
    found.sort(key=lambda r: r["mtime"], reverse=True)
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quiet", action="store_true",
                    help="one line, for the pre-commit pre-flight")
    ap.add_argument("--since", default=None,
                    help="ISO timestamp to measure from; default is HEAD's time")
    args = ap.parse_args(argv)

    if args.since:
        try:
            epoch = datetime.datetime.fromisoformat(args.since).timestamp()
        except ValueError:
            print(f"unparseable --since: {args.since!r}", file=sys.stderr)
            return 2
    else:
        epoch = head_time()

    rounds = rounds_since(epoch)
    useful = [r for r in rounds if r["ok"]]

    if args.quiet:
        when = ("since HEAD" if not args.since else f"since {args.since}")
        if useful:
            seats = sorted({s for r in useful for s in r["ok"]})
            print(f"panel: {len(useful)} reviewed round(s) {when} "
                  f"— seats {', '.join(seats)} — latest {useful[0]['dir']}")
        elif rounds:
            print(f"panel: {len(rounds)} round(s) {when} but 0 seat replies — "
                  "NOT a review; his instruction is that every batch is checked")
        else:
            print(f"panel: 0 panel rounds {when} — his standing instruction is "
                  "that every meaningful batch is put to a free panel first")
        return 0

    stamp = ("(no commits)" if epoch is None else
             datetime.datetime.fromtimestamp(epoch).isoformat(timespec="seconds"))
    print(f"Measuring panel rounds completed since {stamp}\n")
    if not rounds:
        print("  0 complete rounds.")
    for r in rounds:
        t = datetime.datetime.fromtimestamp(r["mtime"]).isoformat(timespec="seconds")
        mark = "REVIEWED" if r["ok"] else "NO SEAT REPLY"
        print(f"  {mark:14s} {r['dir']}")
        print(f"                 barrier {t}")
        print(f"                 ok: {', '.join(r['ok']) or 'none'}"
              + (f"   failed: {', '.join(r['failed'])}" if r["failed"] else ""))
    print(f"\n{len(useful)} of {len(rounds)} complete round(s) carried at least "
          "1 seat reply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
