#!/usr/bin/env python3
"""How fast does the master task list close, and does it grow while being closed?

WHY THIS EXISTS. The founder asked for an ETA on completing the list. A burn-down
figure answers that only if the list is a FIXED target, and this one is not: it
gains entries as it is worked, because closing an entry keeps turning up defects
that become entries. An ETA computed without that term is the classic
underestimate, and quoting one would be exactly the fabricated certainty this
project exists to catch.

WHAT IT MEASURES, from the file's own git history rather than from memory. For
every commit that touched the list, it counts the `<!-- task: ... | state: ... -->`
markers and how many read DONE. That gives the total and closed curves over the
list's life, and the difference between the first populated snapshot and the last
gives entries ADDED alongside entries CLOSED.

THE START POINT IS THE FIRST POPULATED SNAPSHOT, NOT A CONVENIENT ONE. Measured
by hand first, starting from the snapshot at the end of the list's second day,
the growth share came out at 16.8421% -- and that was an UNDERSTATEMENT produced
by choosing a start point after 20 entries had already been added. Reading from
the first commit at which the list had any entries at all gives 37.8947%. A
figure whose value depends on where the author began measuring is the figure this
script exists to replace.

THE FIGURE THAT MATTERS IS NOT THE CLOSURE RATE. It is the share of the list that
was created AFTER the list was first populated: work discovered by doing the
work. Expressed as a multiplier, 1/(1-r), it says how much total work each
nominal entry implies.

`measured-rate-travels-with-its-script`: every figure quoted about this list's
progress comes from here.
"""
from __future__ import annotations

import argparse
import re
import subprocess

LIST = "experimental_notes/CDSFL_MASTER_TASK_LIST.md"

#: A marker line. Anchored to the line so prose that merely quotes the syntax --
#: which several entries do -- is not counted as an entry.
MARK = re.compile(r"^<!-- task:\s*([^|]+?)\s*\|\s*state:\s*(\w+)", re.M)


def snapshots() -> list[tuple[str, str, int, int]]:
    """(when, short sha, distinct entry ids, DONE ids) for each touching commit.

    DISTINCT IDS rather than raw marker lines. The list briefly carried 6
    duplicated ids, and counting lines made their removal read as entries being
    deleted.
    """
    r = subprocess.run(
        ["git", "log", "--reverse", "--format=%H|%ad",
         "--date=format:%Y-%m-%d %H:%M", "--", LIST],
        capture_output=True, text=True)
    if r.returncode != 0:
        # REFUSE rather than report an empty history. A scan that cannot read the
        # repository must not report 0 commits as though the list were new.
        raise SystemExit("git log failed; refusing to report a burn-down from no history")
    out = []
    for line in r.stdout.strip().splitlines():
        sha, when = line.split("|", 1)
        blob = subprocess.run(["git", "show", f"{sha}:{LIST}"],
                              capture_output=True, text=True).stdout
        marks = MARK.findall(blob)
        # UNIQUE IDS, NOT RAW MARKERS. At `3501c38` six ids appeared TWICE --
        # P1, P2, P3, P4, 2.1 and 5.1 -- and the next commit de-duplicated them.
        # Counting raw markers made that cleanup look like 2 entries being
        # DELETED, which would be an additive-standard violation and was not one.
        # The set of ids is the thing that must never shrink.
        ids = {i.strip(): st for i, st in marks}
        out.append((when, sha[:7], len(ids),
                    sum(1 for st in ids.values() if st == "DONE"),
                    sum(1 for st in ids.values() if st == "WITHDRAWN")))
    return out


def per_day(rows: list) -> tuple[dict, dict]:
    """(discovered, closed) counts keyed by calendar day.

    DISCOVERED means an id seen for the FIRST time on that day. Day 1 is the list
    being CREATED, not discovery while working it, so a reader comparing days must
    drop the first.

    THIS IS THE FIGURE AN ETA ACTUALLY NEEDS. The closure rate says how fast the
    list empties; this says how fast it refills. Measured 2026-09-09 to 09-11:
    discovery ran 72, 16, 7 and closure ran 19, 44, 21. Closure outpaces discovery
    by 3x on the latest day, which is why the list converges at all.

    THE DECAY RATE IS NOT ESTABLISHED AND MUST NOT BE QUOTED AS ONE. With 2
    days of discovery-while-working, the day-on-day ratio is 0.4375 and a 95%
    Wilson interval on the split admits a ratio up to 1.0352 -- that is, the data
    cannot rule out a process that does not decay at all. The convergence
    argument rests on closure OUTPACING discovery, which is measured, not on a
    decay that is not.
    """
    import collections
    import subprocess as _sp
    seen, done_seen = set(), set()
    disc, clo = collections.Counter(), collections.Counter()
    for when, sha, *_rest in rows:
        blob = _sp.run(["git", "show", f"{sha}:{LIST}"],
                       capture_output=True, text=True).stdout
        ids = {i.strip(): st for i, st in MARK.findall(blob)}
        day = when[:10]
        for i, st in ids.items():
            if i not in seen:
                seen.add(i)
                disc[day] += 1
            if st == "DONE" and i not in done_seen:
                done_seen.add(i)
                clo[day] += 1
    return dict(disc), dict(clo)


def figures(rows: list[tuple[str, str, int, int]]) -> dict:
    populated = [r for r in rows if r[2] > 0]
    if len(populated) < 2:
        raise SystemExit("fewer than 2 populated snapshots; nothing to compare")
    first, last = populated[0], populated[-1]
    added, closed = last[2] - first[2], last[3] - first[3]

    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta
    k, n = added, last[2]
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    cl = float(beta.ppf(0.025, k, n - k + 1)) if k else 0.0
    ch = float(beta.isf(0.025, k + 1, n - k)) if k < n else 1.0
    return {"first": first, "last": last, "added": added, "closed": closed,
            "share": (k, n), "wilson": (lo, hi), "cp": (cl, ch),
            "multiplier": 1.0 / (1.0 - k / n)}


def branching(rows: list) -> dict:
    """Is the list SUBCRITICAL -- does it terminate at all?

    THE FOUNDER'S QUESTION, 2026-09-11: *"If the work list keeps growing ... and
    it looks like it might never finish, then that could be a problem."* It is the
    right question and it has a formal answer. Treat each closed entry as an
    individual in a branching process that produces R new entries. R < 1 is
    SUBCRITICAL and the process terminates with probability 1; R >= 1 and it need
    never terminate.

    R < 1 is equivalent to p < 1/2 for p = additions / (additions + closures), so
    the test is an ordinary proportion against the 0.5 threshold and carries an
    ordinary interval.

    MEASURED: R = 0.4444, 95% Wilson [0.3009, 0.6565], exact binomial test against
    the critical threshold p = 1.933172e-05. The interval lies entirely below 1,
    so the list terminates. Expected total from the 7 entries now live: 12.60,
    i.e. about 5.6 more entries ever, and 20.38 at the pessimistic bound.

    THREE CAVEATS, BECAUSE THE NUMBER IS MORE FRAGILE THAN IT LOOKS.

    1. R IS PARTLY A POLICY VARIABLE. The assistant decides what becomes an entry.
       A lower bar would raise R. It is not a pure property of the codebase, which
       cuts both ways: it is also controllable.
    2. THE REMAINING ENTRIES MAY NOT BE LIKE THE CLOSED ONES. If what is left is
       systematically harder, R could rise. The 7 now live are rulings rather than
       work, so this is weak here, but it is the right thing to watch.
    3. THIS R DESCRIBES THIS BODY OF WORK. Discovery may be falling because the
       areas being swept are nearly swept, not because defects are rare. Opening a
       genuinely new area -- Exp 56 -- could restart discovery at a rate this
       window says nothing about. **That is the honest limit of this figure.**
    """
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import binomtest

    f = figures(rows)
    added, closed = f["added"], f["closed"]
    k, n = added, added + closed
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    bt = binomtest(k, n, 0.5, alternative="less")
    R = k / n / (1 - k / n)
    return {"added": added, "closed": closed, "R": R,
            "R_interval": (lo / (1 - lo), hi / (1 - hi)),
            "p": (k, n), "p_interval": (lo, hi), "pvalue": bt.pvalue,
            "subcritical": hi < 0.5}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--per-day", action="store_true",
                    help="discovered and closed counts per calendar day")
    ap.add_argument("--curve", action="store_true",
                    help="print the full total/DONE curve, one line per commit")
    a = ap.parse_args()

    rows = snapshots()
    f = figures(rows)
    if a.per_day:
        disc, clo = per_day(rows)
        print(f"  {'day':12} {'discovered':>11} {'closed':>7}")
        for d in sorted(set(disc) | set(clo)):
            print(f"  {d:12} {disc.get(d, 0):>11} {clo.get(d, 0):>7}")
        print("  (day 1 is the list being CREATED, not discovery while working it)")
        print()
    if a.curve:
        print(f"  {'when':17} {'total':>6} {'done':>5} {'not done':>9}")
        for when, _sha, total, done, *_w in rows:
            print(f"  {when:17} {total:>6} {done:>5} {total - done:>9}")
        print()

    first, last = f["first"], f["last"]
    print(f"task list burn-down, from {LIST}'s own history")
    print(f"  first populated : {first[0]}  total {first[2]}, done {first[3]}")
    print(f"  latest          : {last[0]}  total {last[2]}, done {last[3]}")
    print(f"  closed since    : {f['closed']}")
    print(f"  ADDED since     : {f['added']}")
    print(f"  added per closed: {f['added'] / f['closed']:.4f}")
    k, n = f["share"]
    print(f"\n  share of the list created after it was first populated: "
          f"{k} of {n} = {100 * k / n:.4f}%")
    print(f"    Wilson          [{100 * f['wilson'][0]:.4f}%, {100 * f['wilson'][1]:.4f}%]")
    print(f"    Clopper-Pearson [{100 * f['cp'][0]:.4f}%, {100 * f['cp'][1]:.4f}%]")
    print(f"  implied work multiplier 1/(1-r): {f['multiplier']:.4f}")
    b = branching(rows)
    # WITHDRAWN entries are CLOSED, not outstanding. Counting them as live
    # inflated the projection from 7 to 11 and its tail from 12.60 to 19.80.
    last = f["last"]
    withdrawn = last[4] if len(last) > 4 else 0
    live = last[2] - last[3] - withdrawn
    print("\n  BRANCHING VIEW -- does the list terminate at all?")
    print(f"    R, new entries per entry closed : {b['R']:.4f}")
    print(f"    95% interval on R               : "
          f"[{b['R_interval'][0]:.4f}, {b['R_interval'][1]:.4f}]")
    print(f"    exact test against R = 1        : p = {b['pvalue']:.6e}")
    print(f"    SUBCRITICAL (terminates)        : {b['subcritical']}")
    if b["subcritical"]:
        tot = live / (1 - b["R"])
        worst = live / (1 - b["R_interval"][1])
        print(f"    expected entries ever from the {live} now live: {tot:.2f} "
              f"({worst:.2f} at the pessimistic bound); {withdrawn} WITHDRAWN "
              f"entries are excluded as already closed")
    print("\n  AN ETA FROM THE CLOSURE RATE ALONE WOULD BE WRONG BY THAT MULTIPLIER.")
    print("  The list is not a fixed target: closing an entry keeps turning up")
    print("  defects that become entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
