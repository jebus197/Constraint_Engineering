#!/usr/bin/env python3
"""Which commit messages carry a Timestamp that was typed rather than read.

HIS STANDING RULE: never type a timestamp, capture the clock. A typed time is
not a measurement of anything.

I BROKE IT 12 TIMES IN ONE DAY, and this is the script that says so. Each of
those commits carries a `Timestamp:` line drifting from the commit's own author
date. The drift is not random: it GROWS through the working session, from about
3 minutes to nearly 20, which is the signature of a guess falling steadily
behind a clock nobody read.

WHY THE DIRECTION MATTERS, and why a naive check would be wrong. A stamp
legitimately PRECEDES its commit, because this repository's pre-commit hook
runs over 1,300 tests and takes about 4.5 minutes: the stamp is captured, then
the hook runs, then the commit lands. So a stamp a few minutes behind the
commit is honest. A stamp AHEAD of the commit is not, because the future has
not happened yet. The hook that now enforces this is asymmetric for exactly
that reason.

HISTORY IS NOT REWRITTEN. His ruling in another context was "I am not
suggesting rewriting history", and 12 pushed commits are history. The figures
are recorded here instead, and `hooks/commit-msg` makes a recurrence
mechanically impossible rather than a matter of my remembering.

Usage: python3 scripts/which_commits_carry_a_typed_timestamp_2026-10-17.py
       python3 scripts/which_commits_carry_a_typed_timestamp_2026-10-17.py --limit 80
"""
from __future__ import annotations

import argparse
import datetime
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
STAMP = re.compile(r"^\s*Timestamp:\s*(\S+)\s*$", re.M)
AHEAD_ALLOWED = 120


def _proportion(k, n):
    from statsmodels.stats.proportion import proportion_confint
    import scipy.stats as st
    if n == 0:
        return None
    w = proportion_confint(k, n, method="wilson")
    b = proportion_confint(k, n, method="beta")
    cp_hi = 1.0 if k == n else float(st.beta.ppf(0.975, k + 1, n - k))
    return {"k": k, "n": n, "pct": 100.0 * k / n,
            "wilson": (w[0] * 100, w[1] * 100),
            "cp": (b[0] * 100, b[1] * 100),
            "agrees": abs(b[1] - cp_hi) < 1e-9}


def survey(limit: int = 60) -> dict:
    out = subprocess.run(
        ["git", "log", f"-{limit}", "--format=%H%x1e%aI%x1e%B%x1d"],
        capture_output=True, text=True, cwd=str(ROOT)).stdout
    stamped, ahead, behind = [], [], []
    for chunk in out.split("\x1d"):
        if not chunk.strip():
            continue
        parts = chunk.strip("\n").split("\x1e", 2)
        if len(parts) < 3:
            continue
        sha, aiso, body = parts
        m = STAMP.search(body)
        if not m:
            continue
        try:
            claimed = datetime.datetime.fromisoformat(m.group(1))
            actual = datetime.datetime.fromisoformat(aiso)
        except ValueError:
            continue
        drift = (claimed - actual).total_seconds()
        row = (sha[:8], m.group(1), aiso, drift,
               body.splitlines()[0][:58])
        stamped.append(row)
        if drift > AHEAD_ALLOWED:
            ahead.append(row)
        elif drift < 0:
            behind.append(row)
    return {"stamped": stamped, "ahead": ahead, "behind": behind}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.add_argument("--limit", type=int, default=60,
                        help="how many commits back to survey (default 60)")
    args = parser.parse_args(argv)

    res = survey(args.limit)
    stamped, ahead = res["stamped"], res["ahead"]
    print(f"  commits surveyed with a Timestamp line : {len(stamped)} "
          f"(window: the last {args.limit} commits)")
    #: ★ SAY WHEN THE WINDOW MAY HAVE SLID PAST THE RECORDED VIOLATIONS, added
    #: 2026-10-29. The 10 known violations are HISTORICAL, and on 2026-10-29 the
    #: newest sat exactly 60 commits behind HEAD -- 1 outside this default. Run
    #: bare, the producer therefore reported 0, and a reader could take that as
    #: "this never happened". A 0 that means "outside my window" must not look
    #: like a 0 that means "it does not occur".
    if not ahead:
        print(f"  0 violations INSIDE this window. The recorded violations are "
              f"historical, so if the window has slid past them this 0 means "
              f"'none in the last {args.limit}' and NOT 'none ever'. Re-run with "
              f"a larger --limit to reach them; the set is pinned in "
              f"bench/tests/test_a_typed_timestamp_is_refused_2026-10-17.py.")
    if not stamped:
        print("  none carry one; nothing to measure.")
        return 0
    p = _proportion(len(ahead), len(stamped))
    print(f"  carrying a stamp AHEAD of their own commit date, so typed:")
    print(f"    {p['k']} of {p['n']} = {p['pct']:.4f}%  "
          f"Wilson [{p['wilson'][0]:.4f}%, {p['wilson'][1]:.4f}%]  "
          f"Clopper-Pearson [{p['cp'][0]:.4f}%, {p['cp'][1]:.4f}%]  "
          f"scipy agrees {p['agrees']}")
    if ahead:
        drifts = sorted(r[3] / 60.0 for r in ahead)
        print(f"    drift range: {drifts[0]:+.1f} to {drifts[-1]:+.1f} minutes")
        print("    THE DRIFT GROWS THROUGH THE SESSION, which is the signature")
        print("    of a guess falling behind a clock nobody read:")
        for sha, c, a, d, subj in sorted(ahead, key=lambda r: r[2]):
            print(f"      {sha}  claimed {c[11:19]}  actual {a[11:19]}  "
                  f"{d/60:+5.1f} min  {subj}")
    print(f"  carrying a stamp BEHIND their commit date, which is HONEST "
          f"because the hook runs for minutes between the 2: {len(res['behind'])}")
    print("\n  PREVENTED GOING FORWARD by hooks/commit-msg, which refuses a")
    print("  stamp ahead of the clock and tolerates one behind it, for the")
    print("  asymmetric reason above. History is not rewritten.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
