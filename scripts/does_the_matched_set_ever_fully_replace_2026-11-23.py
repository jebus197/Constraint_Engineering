#!/usr/bin/env python3
"""Does the cy gate's matched process set ever FULLY replace between polls?

DESTINATION `scripts/`. Written 2026-11-23.

WHY. The joint panel round of 2026-11-23 ended with the 2 seats disagreeing on
entry B209, the cy gate's anti-trap refusal counter. Driven, both scorers
reproduce and the disagreement turns out to be narrower than it looked: cc2's
scenario S3 and fable's scenario R1 are THE SAME SCENARIO -- the overlap key
failing when the observed process set is fully replaced between 2 consecutive
polls. The seats agree on the fact and differ on its WEIGHT. fable calls it
constructed and never observed; cc2 calls its consequence severe enough to
require a composed fix, and measured that composition at 5 of 6 against 4 of 6.

NEITHER SEAT MEASURED WHETHER THE SCENARIO IS REALISABLE. That is what this
does, and it is the only thing that can settle a disagreement about weight.

IT POLLS THE GATE'S OWN MATCHER, `_RUNNER_PATTERNS` via `pgrep -f`, rather than
re-implementing it, so the population measured is the population the gate sees.

WHAT IT CANNOT SETTLE, STATED UP FRONT: a short run is not a commit board. A
board lasts about 34 minutes against this probe's seconds, and other matched
processes may coexist with it. This measures what it measures.
"""
from __future__ import annotations
import argparse
import importlib.util
import pathlib
import subprocess
import sys
import time

#: z^2 at 95%, for the poll-pair diagnostic printed when no rate is identified.
Z2 = 1.959963984540054 ** 2

REPO = pathlib.Path(__file__).resolve().parents[1]
GATE = REPO / "hooks" / "cy_monitor_gate.py"


def gate_patterns() -> tuple[str, ...]:
    """Read the matcher FROM THE GATE, never typed here.

    A probe that spells its own patterns measures the probe. If the gate's
    patterns change, this must change with them or report nothing.
    """
    spec = importlib.util.spec_from_file_location("_cyg", GATE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_cyg"] = m
    spec.loader.exec_module(m)
    pats = getattr(m, "_RUNNER_PATTERNS", None)
    if not pats:
        raise RuntimeError(f"{GATE.name} exposes no _RUNNER_PATTERNS")
    return tuple(pats)


def observe(pats) -> set[int]:
    seen: set[int] = set()
    for p in pats:
        r = subprocess.run(["pgrep", "-f", p], capture_output=True, text=True)
        seen |= {int(x) for x in r.stdout.split() if x.strip().isdigit()}
    return seen


def classify(polls):
    """(full_replacements, identical, other, pairs_considered, opportunities).

    ★ `opportunities` ADDED 2026-11-23 (panel batch 12, seat fable), BECAUSE
    `pairs_considered` IS NOT A RISK SET AND THE INTERVAL BUILT ON IT IS NOT
    IDENTIFIED BY THE DATA.

    2 defects, both demonstrated by execution rather than argued:

    1. A FULL REPLACEMENT CANNOT OCCUR IN A PAIR WITH AN EMPTY SIDE, yet such
       pairs entered the denominator. `classify([{1}, set()] * 8)` returns 15
       pairs and 0 full replacements, giving a Wilson upper bound of 0.203883 --
       TIGHTER than the figure this script was written to report -- from a
       sequence in which the event was impossible in every single pair.

    2. THE BOUND IS A FUNCTION OF `--interval`, A FREE PARAMETER, NOT OF THE
       WORLD. At k=0 the Wilson upper bound is exactly z^2/(n + z^2) (derived
       with SymPy, confirmed on an independent kernel), so it falls monotonically
       as n rises. One unchanging pid polled over the same 106 s yields 14 pairs
       at 2.0 s -> 0.215311, and 1060 pairs at 0.1 s -> 0.003611, on IDENTICAL
       evidence. Measured, not hypothesised: a 20 s run at 1.0 s produced 19
       pairs and an upper bound of 0.168179 -- a TIGHTER bound from a FIFTH of
       the observation. An interval that narrows as you observe less is not
       measuring anything.

    `opportunities` counts consecutive pairs in which the matched set ACTUALLY
    CHANGED and both sides are non-empty: the occasions on which a full
    replacement was a possible outcome. With 0 opportunities no rate is
    identified at all, which is the honest reading of the observed data.

    RESIDUAL, STATED RATHER THAN HIDDEN: full/opportunities is still not fully
    interval-invariant, because slower polling aggregates several changes into
    one observed change and so makes a full replacement likelier per change. It
    is a denominator of events rather than of non-events, which is strictly
    better, not perfect.

    NOTHING IS REMOVED: every previously printed count is still printed.
    """
    full = same = other = pairs = opportunities = 0
    prev = None
    for s in polls:
        if prev is not None and (prev or s):
            pairs += 1
            if prev and s and prev != s:
                opportunities += 1
            if prev and s and not (prev & s):
                full += 1
            elif prev == s:
                same += 1
            else:
                other += 1
        prev = s
    return full, same, other, pairs, opportunities


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seconds", type=float, default=50.0,
                    help="how long to poll for (default 50)")
    ap.add_argument("--interval", type=float, default=2.0,
                    help="seconds between polls (default 2.0)")
    a = ap.parse_args(argv)

    pats = gate_patterns()
    print("=" * 74)
    print("DOES THE MATCHED PROCESS SET EVER FULLY REPLACE BETWEEN POLLS?")
    print("=" * 74)
    print(f"\n  patterns, read from {GATE.name}: {pats}")
    print(f"  polling for {a.seconds:.0f} s at {a.interval:.1f} s intervals\n")

    polls = []
    t0 = time.time()
    while time.time() - t0 < a.seconds:
        polls.append(observe(pats))
        time.sleep(a.interval)

    full, same, other, pairs, opportunities = classify(polls)
    sizes = sorted({len(s) for s in polls})
    print(f"  polls taken                                   : {len(polls)}")
    print(f"  pid-set sizes seen                            : {sizes}")
    print(f"  consecutive pairs considered                  : {pairs}")
    print(f"  FULL REPLACEMENTS (both non-empty, no overlap): {full}")
    print(f"  identical pairs                               : {same}")
    print(f"  partial / one side empty                      : {other}")
    print(f"  OPPORTUNITIES (set actually changed, both non-empty): {opportunities}")

    if pairs and not opportunities:
        #: ★ THE REFUSAL, ADDED 2026-11-23. A poll-pair interval is reported as
        #: a DIAGNOSTIC of the polling rate and explicitly NOT as a rate in the
        #: world, because 0 opportunities identifies no rate. The counts above
        #: are unchanged; only the claim attached to them is corrected.
        print(f"\n  full-replacement rate : UNIDENTIFIED.")
        print(f"  The matched set never changed in any of the {pairs} pairs, so a")
        print(f"  full replacement was never a possible outcome and there is no")
        print(f"  denominator. A Wilson interval on {pairs} poll-pairs would be")
        print(f"  z^2/(n+z^2) = {Z2 / (pairs + Z2):.6f}, which is a function of")
        print(f"  --interval and not of the world: poll the SAME unchanging run")
        print(f"  10x faster and it reads {Z2 / (10 * pairs + Z2):.6f} on identical evidence.")
        print(f"  NO BOUND IS REPORTED. Observe a real board, where the set churns.")
    elif pairs:
        from statsmodels.stats.proportion import proportion_confint
        import mpmath as mp
        mp.mp.dps = 40
        lo, hi = proportion_confint(full, opportunities, method="wilson")
        # route 2: the closed form, independent of statsmodels
        z = mp.mpf("1.959963984540054235524594430520551527955")
        n, k = mp.mpf(opportunities), mp.mpf(full)
        ph = k / n
        den = 1 + z**2 / n
        ctr = (ph + z**2 / (2 * n)) / den
        hw = (z / den) * mp.sqrt(ph * (1 - ph) / n + z**2 / (4 * n**2))
        d = max(abs(float(ctr - hw) - lo), abs(float(ctr + hw) - hi))
        print(f"\n  full-replacement rate : {full} of {opportunities} OPPORTUNITIES "
              f"= {full/opportunities:.6f}")
        print(f"  Wilson 95%            : [{lo:.6f}, {hi:.6f}]"
              f"   (mpmath closed form agrees to {d:.2e})")
        assert d < 1e-9, f"the 2 Wilson routes disagree by {d}"

    print("\n  WHAT THIS BEARS ON.")
    if opportunities and full == 0:
        print("    The scenario the 2 seats weigh differently -- cc2's S3 and")
        print("    fable's R1, which are the same scenario -- did NOT occur in")
        print("    any observed pair. That CORROBORATES fable's 'constructed,")
        print("    none observed' and is evidence for preferring the single fix.")
        print("\n    AND IT CUTS THE OTHER WAY TOO, WHICH IS WHY IT IS REPORTED")
        print("    RATHER THAN QUOTED SELECTIVELY: entry B209's own premise is")
        print("    that the key CHURNS because a board replaces its pytest child")
        print("    per guard file. A stable single pid across every pair is not")
        print("    what that premise predicts, so the premise needs re-measuring")
        print("    against a real board before B209's repair is chosen.")
    elif opportunities:
        print("    A full replacement WAS observed, which promotes the disputed")
        print("    scenario from constructed to demonstrated and strengthens the")
        print("    case for cc2's composed fix.")
    elif pairs:
        #: ★ SPLIT OUT 2026-11-23. This case -- processes matched, but the set
        #: never changed -- used to print "nothing matched", which was false,
        #: and used to be read as corroboration, which it cannot be.
        print("    Processes DID match, but the matched set never changed, so")
        print("    the disputed scenario was never PUT AT RISK of occurring.")
        print("    THIS CORROBORATES NEITHER SEAT. It does not support fable's")
        print("    'none observed', because a non-occurrence in 0 opportunities")
        print("    is not an observation; and it does not support cc2's weight")
        print("    either. It DOES cut against entry B209's own premise, which")
        print("    predicts the set churns as a board replaces its pytest child")
        print("    per guard file -- so that premise is the thing to re-measure,")
        print("    against a real board rather than a single pytest invocation.")
    else:
        print("    Nothing matched the gate's patterns while this ran, so the")
        print("    probe is UNINFORMATIVE -- run it while a suite or board runs.")

    print("\n  THE BOUND. A short probe is not a commit board: a board lasts")
    print("  about 34 minutes and may coexist with other matched processes.")
    print("  This settles the single-run case only.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__, takes_no_arguments=False)
    except ImportError:
        pass
    raise SystemExit(main())
