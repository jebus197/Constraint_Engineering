#!/usr/bin/env python3
"""How many commits landed for him today, and how many boards refused.

WHY THIS EXISTS. The closing report of 2026-11-08 claimed 7 commits landed and
2 boards refused. Both were TYPED rather than derived, and both were wrong: git
records 5 and the session's own board logs record 4 refusals. Getting a figure
about MY OWN activity wrong, in the document whose whole purpose is to be the
honest record, is the least excusable kind of error, and
`measured-rate-travels-with-its-script` is the rule it broke.

THE 2 HALVES ARE NOT EQUALLY REPRODUCIBLE, AND SAYING SO IS THE POINT.

  * THE COMMIT COUNT IS REPRODUCIBLE BY ANYONE: it comes from `git log` with a
    `--since` bound, so re-running this prints the same answer from the same
    repository.

  * THE BOARD OUTCOMES ARE SESSION-OBSERVED, not repo-derived. A refused commit
    leaves NO trace in the repository -- that is what a refusal means -- so the
    count comes from the exit codes this session captured in its own scratchpad.
    Those files are not versioned and will not exist for a later reader. The
    figure is therefore reported with that limit attached rather than presented
    as a measurement anyone can re-run, which is the distinction the earlier
    wrong figure elided.

Exit 0 always: this reports, it does not gate.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess

REPO = pathlib.Path(__file__).resolve().parent.parent
#: His message that opened this window, from the session clock.
SINCE = "2026-11-08 13:54"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since", default=SINCE)
    ap.add_argument("--boards", default=None,
                    help="directory holding this session's commit_board_*.log")
    a = ap.parse_args()

    print("=" * 74)
    print("1. COMMITS LANDED -- reproducible from the repository")
    print("=" * 74)
    r = subprocess.run(["git", "log", f"--since={a.since}",
                        "--format=%h\t%ad\t%s", "--date=format:%H:%M"],
                       cwd=REPO, capture_output=True, text=True)
    rows = [ln for ln in r.stdout.splitlines() if ln.strip()]
    for ln in rows:
        h, when, subj = ln.split("\t", 2)
        print(f"  {when}  {h}  {subj[:74]}")
    print(f"\n  commits since {a.since}: {len(rows)}")

    print("\n" + "=" * 74)
    print("2. BOARD OUTCOMES -- SESSION-OBSERVED, not reproducible from the repo")
    print("=" * 74)
    d = pathlib.Path(a.boards) if a.boards else None
    logs = sorted(d.glob("commit_board_*.log")) if d and d.is_dir() else []
    if not logs:
        print("  no board logs given or found. A refusal leaves no trace in the")
        print("  repository, so this half cannot be re-derived here. Pass")
        print("  --boards <dir> with the session's scratchpad to reproduce it.")
        return 0
    landed = refused = unknown = 0
    for f in logs:
        m = re.search(r"REAL_EXIT=(\d+)", f.read_text(errors="replace"))
        if m is None:
            unknown += 1
            verdict = "NO EXIT RECORDED"
        elif m.group(1) == "0":
            landed += 1
            verdict = "landed"
        else:
            refused += 1
            verdict = "REFUSED"
        print(f"  {f.name:26s} {verdict}")
    print(f"\n  captured board runs: {len(logs)} -- {landed} landed, "
          f"{refused} refused, {unknown} with no exit code recorded")
    print("  AND AT LEAST 1 FURTHER RUN IS NOT CAPTURED HERE: the first attempt")
    print("  of the window was piped into `tail`, so its exit code was the")
    print("  pipe's and its output was truncated. It refused, on 2 failures.")
    print("  So the honest statement is 9 runs, 5 landed and 4 refused, with")
    print("  8 of the 9 evidenced by a captured exit code.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
