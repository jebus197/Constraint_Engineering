# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'panel_b12_20261123T170728Z', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: fef0033e85eb1355744dfa93b3f1f1b3951454dbe24732891c050db324a310a3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Is the full-replacement denominator a RISK SET, or just the polling rate?

DESTINATION `scripts/`. Written 2026-11-23, panel batch 12, Q2, seat fable.

THE DEFECT THIS FALSIFIES, in `classify` of
`scripts/does_the_matched_set_ever_fully_replace_2026-11-23.py`. The reported
denominator was `pairs_considered`: every consecutive pair of polls with at
least one non-empty side. 2 consequences, both demonstrated by running it:

  1. A PAIR WITH AN EMPTY SIDE CANNOT CONTAIN A FULL REPLACEMENT, because the
     definition requires both sides non-empty. Such pairs still entered the
     denominator, so a sequence in which the event was IMPOSSIBLE throughout
     yielded a tight bound: `[{1}, set()] * 8` gives 15 pairs, 0 events, Wilson
     upper 0.203883 -- tighter than the 0.215311 the script reported.

  2. AT k=0 THE WILSON UPPER BOUND IS EXACTLY z^2/(n + z^2), which is strictly
     decreasing in n. Since n is the number of POLLS, the bound is set by
     `--interval`, a free parameter, not by the world. The same unchanging
     single pid over the same 106 s reads 0.215311 at 2.0 s spacing and
     0.003611 at 0.1 s spacing.

THE FIX UNDER TEST. `classify` now also returns `opportunities`: pairs in which
the matched set ACTUALLY CHANGED with both sides non-empty -- the occasions on
which a full replacement was a possible outcome. With 0 opportunities the script
reports UNIDENTIFIED and prints no bound.

WHAT THIS ASSERTS, importing the REAL module and never a retyped copy:
  A. `classify` exposes an opportunity count at all.
  B. A sequence with an empty side in every pair yields 0 opportunities.
  C. An unchanging set yields 0 opportunities however many polls are taken, so
     the count does NOT move with the polling rate.
  D. A genuine full replacement IS counted as an opportunity -- anti-vacuity,
     so the fix cannot pass by reporting 0 for everything.
  E. The closed form z^2/(n+z^2) that makes defect 2 true is itself correct.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PROBE = REPO / "scripts" / "does_the_matched_set_ever_fully_replace_2026-11-23.py"
Z2 = 1.959963984540054 ** 2


def main() -> int:
    spec = importlib.util.spec_from_file_location("_probe", PROBE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    bad = []

    got = m.classify([{1}] * 15)
    print(f"  A/C unchanging set, 15 polls        -> classify = {got}")
    if len(got) < 5:
        bad.append("classify exposes no opportunity count: the denominator is "
                   "still the poll count, which is set by --interval")
        print("FALSIFIED")
        raise AssertionError("\n  ".join(bad))

    if got[4] != 0:
        bad.append(f"an unchanging set reported {got[4]} opportunities; a set "
                   f"that never changed never put the event at risk")

    faster = m.classify([{1}] * 150)
    print(f"  C   same set, 10x the polls         -> classify = {faster}")
    if faster[4] != got[4]:
        bad.append(f"the opportunity count moved from {got[4]} to {faster[4]} "
                   f"when only the polling rate changed, so it is still an "
                   f"artefact of --interval")
    if faster[3] <= got[3]:
        bad.append("the poll-pair count did NOT grow with the polling rate, so "
                   "this falsifier is not exercising the defect it claims")

    empty = m.classify([{1}, set()] * 8)
    print(f"  B   alternating matched/empty       -> classify = {empty}")
    if empty[4] != 0:
        bad.append(f"pairs with an empty side contributed {empty[4]} "
                   f"opportunities, though a full replacement is impossible "
                   f"in such a pair by definition")

    real = m.classify([{1}, {2}])
    print(f"  D   a genuine full replacement      -> classify = {real}")
    if real[0] != 1:
        bad.append("a genuine full replacement was not counted as an event")
    if real[4] != 1:
        bad.append("a genuine full replacement was not counted as an "
                   "opportunity, so the fix reports 0 for everything and is "
                   "vacuous")

    for n, expect in ((14, 0.215311), (1060, 0.003611)):
        bound = Z2 / (n + Z2)
        print(f"  E   z^2/(n+z^2) at n={n:<5}          -> {bound:.6f} "
              f"(expected {expect})")
        if abs(bound - expect) > 5e-7:
            bad.append(f"the closed form disagrees with the reported bound at "
                       f"n={n}: {bound:.6f} vs {expect}")

    if bad:
        print("FALSIFIED")
        raise AssertionError(
            "the full-replacement denominator is not a risk set:\n  "
            + "\n  ".join(bad))
    print("\n  the denominator counts OPPORTUNITIES, is invariant to the polling "
          "rate,\n  and still counts a real replacement. Upheld in both directions.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__)
    except ImportError:
        pass
    raise SystemExit(main())
