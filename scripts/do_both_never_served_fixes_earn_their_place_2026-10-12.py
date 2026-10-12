#!/usr/bin/env python3
"""Does cc2's never-served DOOR still fire once fable's SERVE has run?

THE QUESTION, AND WHY IT IS NOT RHETORICAL. The free panel of 2026-10-12 sent
two blind seats at the same defect -- a finding that nothing ever served blocks
convergence for ever -- and they returned two different mechanisms:

  fable  SERVES it: a never-served UNCONFIRMED entry is admitted into the
         existing routing ladder exactly once, so a TOOL can decide it.
  cc2    EXCLUDES it: after a minimum age, a never-served entry stops being
         counted as a blocker, with a paired named reader so that nothing is
         dropped from the count without being reported.

Each design passes its own falsifier and fails the other's (measured: 18/18 and
2 of 4, then 15 of 18 and 4/4). Composed, all 57 tests across both suites and
the two adjacent suites pass. But serving an entry WRITES `routing_history`,
and the absence of `routing_history` is one of the seven emptiness facts cc2's
door requires. So the composition raises a question the additive standard makes
mandatory: if the serve always runs first, the door matches nothing, and an
addition nothing reaches is not additive.

WHAT THIS SCRIPT MEASURES. It rehydrates the live registry of
`study_run1b_2026-10-03` (75 entries, the run whose 2 survivors C0066 and C0073
stopped it converging), runs the REAL `_apply_routing`, and then asks the REAL
reader `ladder_unserved_findings` what is left. Both code paths are executed,
not described: a source-text comparison cannot distinguish a door that fires
from one that merely looks like it would.

Usage: python3 scripts/do_both_never_served_fixes_earn_their_place_2026-10-12.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "bench"))

from _cli_help import answer_help  # noqa: E402

LIVE = os.path.join(REPO, "bench", "logs",
                    "study_run1b_2026-10-03_20261003T100439Z",
                    "runner_state.json")


def load():
    import reference_runner_v3 as R
    with open(LIVE) as fh:
        return R, R.FindingRegistry.from_dict(json.load(fh)["registry"])


def main() -> int:
    answer_help(__doc__, __file__)
    R, reg = load()
    n = len(reg.entries) if hasattr(reg, "entries") else len(reg._entries)
    print(f"live registry: {n} entries   "
          f"LADDER_UNSERVED_MIN_AGE_ROUNDS = {R.LADDER_UNSERVED_MIN_AGE_ROUNDS}")

    print("\nBEFORE any routing pass (the archived state):")
    for rnd in (None, 5, 6, 7, 8):
        a4 = reg.unverified_critical_count(rnd)
        excl = reg.ladder_unserved_findings(rnd)
        print(f"  round={str(rnd):>4}   A4={a4}   door excludes={excl}")

    # Run the REAL routing pass -- fable's serve lives inside it.
    R2, reg2 = load()
    served_err = None
    try:
        R2._apply_routing(reg2, 7, {}, cfg=None, repo_root=REPO)
    except Exception as exc:                      # noqa: BLE001
        served_err = f"{type(exc).__name__}: {exc}"

    print(f"\nAFTER the real _apply_routing at round 7"
          f"{' (raised ' + served_err + ')' if served_err else ''}:")
    for rnd in (None, 5, 6, 7, 8):
        a4 = reg2.unverified_critical_count(rnd)
        excl = reg2.ladder_unserved_findings(rnd)
        print(f"  round={str(rnd):>4}   A4={a4}   door excludes={excl}")

    pre = set(reg.ladder_unserved_findings(8))
    post = set(reg2.ladder_unserved_findings(8))
    print(f"\ndoor fires at round 8 BEFORE serve : {sorted(pre) or '[]'}")
    print(f"door fires at round 8 AFTER  serve : {sorted(post) or '[]'}")
    if pre and not post:
        print("\nVERDICT: the serve makes the door INERT on this registry. "
              "The door is only reachable where routing never runs.")
    elif pre and post:
        print("\nVERDICT: both fire. The serve did not reach these entries, "
              "so the door is still load-bearing.")
    else:
        print("\nVERDICT: the door does not fire on this registry at all.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
