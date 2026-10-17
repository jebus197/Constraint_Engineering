#!/usr/bin/env python3
"""Does the blocker test's hand-rolled predicate agree with the live counter?

HIS CORRECTION, 2026-10-16: *"The producer carries a hand written copy of the
counter's release conditions instead of calling the counter."* The producer was
repaired. The TEST that guards the same quantity was not: it still walks the
archive applying its own conditions, so it asserts on a set it derived itself.

WHY THAT CANNOT DETECT THE FAULT IT GUARDS. A test that re-derives the
predicate agrees with itself by construction. It cannot see a producer and a
consumer that disagree, because each is individually self-consistent -- the
recorded `execute-do-not-grep` shape, which has now found 4 defects in this
project and was found by reading in none of them.

THIS SCRIPT RUNS BOTH FORMS OVER THE SAME ARCHIVE AND COMPARES THEM, per
entry and not merely in total, because 2 sets of equal size can still differ.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as R  # noqa: E402

LOGS = REPO / "bench" / "logs"


def by_hand(ents: dict) -> tuple[int, set]:
    """The conditions the TEST applies itself, transcribed from its own body.

    CORRECTED 2026-10-17. A first version of this script guessed the conditions
    as unverified-and-severity-at-or-above-0.7 and reported 532 blockers
    against the counter's 167. THAT FIGURE IS WITHDRAWN: it measured a
    predicate the test does not use. The test's real conditions are a status of
    UNCONFIRMED, skipping an irreducible escalation that is not
    integrity-unobserved, and skipping an exhausted entry. The lesson is the
    one already recorded as `check-the-predicate-first`: a comparison is only
    as good as its weaker side, and here the weaker side was mine.
    """
    blocked, unservable = 0, set()
    for cid, e in ents.items():
        if not isinstance(e, dict) or e.get("status") != "UNCONFIRMED":
            continue
        if e.get("irreducible_escalation") and not e.get("integrity_unobserved"):
            continue
        if e.get("exhausted"):
            continue
        blocked += 1
        if not R._routing_would_admit(e):
            unservable.add(cid)
    return blocked, unservable


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    h_blocked = h_unserv = c_blocked = c_unserv = 0
    t_blocked = t_unserv = nested_blocked = nested_unserv = 0
    disagree_runs, entry_diffs = [], 0
    runs = 0
    runs_nested = 0
    for path in sorted(LOGS.rglob("runner_state.json")):
        # THE TEST DOES NOT RESTRICT TO TOP-LEVEL RUN STATES, and the producer
        # does. That difference alone changes the denominator, because 10 of
        # the 74 files found by rglob sit inside `sandbox_harvest/` and are
        # archived copies of what a SEAT saw. Both scopes are reported below so
        # the effect is visible rather than inferred.
        top_level = len(path.relative_to(LOGS).parts) == 2
        try:
            ents = (json.loads(path.read_text(errors="replace"))
                    .get("registry") or {}).get("entries") or {}
        except (OSError, ValueError):
            continue
        if not ents:
            continue
        runs += 1
        if not top_level:
            runs_nested += 1
        hb, hu = by_hand(ents)
        reg = R.FindingRegistry()
        reg.entries = ents
        try:
            cb = reg.unverified_critical_count()
            cu = set(reg.blockers_routing_cannot_serve())
        except Exception:                                 # noqa: BLE001
            continue
        h_blocked += hb; h_unserv += len(hu)
        if top_level:
            c_blocked += cb; c_unserv += len(cu)
            t_blocked += hb; t_unserv += len(hu)
        else:
            nested_blocked += hb; nested_unserv += len(hu)
        if not top_level:
            continue
        sym = (hu ^ cu)
        if hb != cb or sym:
            disagree_runs.append((path.relative_to(LOGS).parts[0], hb, cb,
                                  len(hu), len(cu), len(sym)))
            entry_diffs += len(sym)

    print(f"run states read (all nesting) ........ {runs}")
    print(f"  of which nested, e.g. sandbox copies  {runs_nested}")
    print()
    print("SAME SCOPE (top-level run states only), so only the predicate differs:")
    print(f"  blockers    hand-rolled vs counter .. {t_blocked} vs {c_blocked}")
    print(f"  unservable  hand-rolled vs counter .. {t_unserv} vs {c_unserv}")
    print()
    print("THE TEST'S OWN SCOPE, which also counts nested copies:")
    print(f"  blockers ............................. {h_blocked}")
    print(f"  unservable ........................... {h_unserv}")
    print(f"  contributed by nested copies ......... {nested_blocked} blockers, "
          f"{nested_unserv} unservable")
    print(f"runs where the 2 forms disagree ...... {len(disagree_runs)}")
    print(f"entries in the symmetric difference .. {entry_diffs}")

    if disagree_runs and not a.quiet:
        print("\nEVERY DISAGREEING RUN, so none hides behind the total:")
        print("  run                                        hand  cnt  hU  cU  sym")
        for r in disagree_runs:
            print(f"  {r[0][:42]:<42} {r[1]:>4} {r[2]:>4} {r[3]:>3} {r[4]:>3} {r[5]:>4}")

    if h_blocked == c_blocked and entry_diffs == 0:
        print("\nVERDICT: the 2 forms agree today. The test is still unsound,")
        print("because agreement today is not a property -- it holds until one")
        print("side changes, and nothing would report it.")
    else:
        print("\nVERDICT: THE 2 FORMS DISAGREE. The test asserts on a set it")
        print("derived itself, so it cannot see this. It must call the counter.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
