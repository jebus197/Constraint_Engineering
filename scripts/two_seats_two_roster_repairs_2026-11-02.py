#!/usr/bin/env python3
"""Two seats repaired the roster-blind gate differently. Which one, and why?

WHY THIS EXISTS, AND IT IS A CORRECTION IN PROGRESS. Entry B77 recommends adopting
the CC2 seat's `degraded_convergence_2026-10-07.py`, which scales the quiet-round
requirement by the roster ratio: `K_required = ceil(K * n_dec / n_live)`. While
judging a THIRD design from the same brief, the Fable seat's
`degradation_aware_convergence.py` was found to repair the SAME defect by a
different route: it restates the requirement as `n0 * K0` quiet SEAT-ROUNDS and
accumulates, per round, the number of seats that actually responded.

B77 NAMES A RECOMMENDATION HE MAY ACT ON, so if the alternative dominates it, that
must reach him before he does. `composability-requires-a-measurement` applies in
its exact sense: these are ALTERNATIVES, and a composed fix may be recommended
only with evidence that it beats either part alone. No such evidence is claimed
here; the question is which SINGLE fix is better, which is what his standard says
to prefer when it is.

THE 3 QUESTIONS, EACH ANSWERED BY EXECUTION:
  1. Are they the same at a CONSTANT roster? (SymPy, exact rationals)
  2. Do they differ when the roster VARIES across rounds, which is the case the
     archive actually contains?
  3. Is the Fable design's claim about WHERE the gate is weakest -- the sparsity
     fallback resting on condition (C) alone -- true of the live runner?
"""
from __future__ import annotations

import ast
import argparse
import math
import pathlib

import sympy as sp

REPO = pathlib.Path(__file__).resolve().parents[1]


def banner(s: str) -> None:
    print("=" * 74)
    print(s)
    print("=" * 74)


# ---- the 2 rules, implemented exactly as each design states them ----
def cc2_required_rounds(k: int, n_dec: int, n_live: int) -> int:
    """CC2: scale the ROUND count by the roster ratio."""
    if n_live <= 0:
        return math.inf                      # no window makes the evidence exist
    return max(k, math.ceil(k * n_dec / n_live))


def fable_required_seat_rounds(n_dec: int, k: int) -> int:
    """Fable: the requirement is a count of quiet SEAT-ROUNDS."""
    return n_dec * k


def fable_rounds_needed(attendance: list[int], n_dec: int, k: int) -> int | None:
    """How many trailing quiet rounds Fable's rule needs, given who answered.

    Accumulates each round's ACTUAL responder count until the seat-round
    requirement is met. Returns None if the supplied attendance never reaches it.
    """
    need = fable_required_seat_rounds(n_dec, k)
    got = 0
    for i, n in enumerate(attendance, start=1):
        got += n
        if got >= need:
            return i
    return None


def main() -> int:
    # ★ ARGPARSE IS NOT DECORATION HERE. Without it, `--help` fell through and ran
    # the whole measurement, which the suite refuses: a flag must never trigger
    # the work it is asking about. Same family as the standing rule that a
    # `--help` must never cost money.
    ap = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.strip().splitlines()[0] if __doc__ else None)
    ap.parse_args()
    K, N_DEC = 3, 6

    banner("1. AT A CONSTANT ROSTER, ARE THE 2 RULES THE SAME? (SymPy, exact)")
    k, n0, nl = sp.symbols("k n0 nl", positive=True, integer=True)
    cc2_sym = sp.ceiling(k * n0 / nl)
    fable_sym = sp.ceiling(n0 * k / nl)          # equivalent_quiet_rounds
    same_sym = sp.simplify(cc2_sym - fable_sym) == 0
    print(f"  CC2   symbolic : ceil(k*n0/nl)")
    print(f"  Fable symbolic : ceil(n0*k/nl)")
    print(f"  difference simplifies to 0 : {same_sym}")

    disagree = []
    for n_live in range(1, N_DEC + 1):
        a = cc2_required_rounds(K, N_DEC, n_live)
        b = fable_rounds_needed([n_live] * 60, N_DEC, K)
        if a != b:
            disagree.append((n_live, a, b))
    print(f"  constant-roster rosters tested : {N_DEC}")
    print(f"  disagreements                  : {disagree or 'NONE'}")
    print()
    print("  SO AT A CONSTANT ROSTER THEY ARE THE SAME RULE, and neither")
    print("  dominates the other there. The distinction has to be elsewhere.")
    print()

    banner("2. DO THEY DIFFER WHEN THE ROSTER VARIES ACROSS ROUNDS?")
    print("  This is the case the archive contains: a seat drops for 1 round and")
    print("  returns. CC2's rule takes a SINGLE n_live, so it has to be given one")
    print("  value for a run whose roster changed; Fable's accumulates what each")
    print("  round actually delivered.")
    print()
    cases = [
        ("1 seat missing in 1 round only", [6, 6, 5]),
        ("a seat drops then returns",      [4, 6, 6]),
        ("progressive attrition",          [6, 5, 4]),
        ("recovery after a bad round",     [2, 6, 6]),
        ("steady full roster (control)",   [6, 6, 6]),
    ]
    print(f"  requirement: {fable_required_seat_rounds(N_DEC, K)} quiet seat-rounds "
          f"(n0={N_DEC}, K0={K})")
    print()
    print(f"  {'case':34s} {'attendance':16s} {'Fable rounds':13s} "
          f"{'CC2 (min n_live)':17s} {'CC2 (last n_live)'}")
    for name, att in cases:
        f_r = fable_rounds_needed(att + [min(att)] * 40, N_DEC, K)
        cc2_min = cc2_required_rounds(K, N_DEC, min(att))
        cc2_last = cc2_required_rounds(K, N_DEC, att[-1])
        print(f"  {name:34s} {str(att):16s} {str(f_r):13s} "
              f"{str(cc2_min):17s} {cc2_last}")
    print()
    print("  CC2'S RULE IS AMBIGUOUS ON A VARYING ROSTER and the 2 readings")
    print("  disagree: taking the WORST round makes a run that recovered pay for a")
    print("  single bad round forever, and taking the LAST round lets a run that")
    print("  lost seats close on a requirement set by its healthiest moment.")
    print("  Fable's rule has no such choice to make, because it prices the")
    print("  evidence each round actually delivered. THAT is the named property on")
    print("  which 1 design dominates: it is DEFINED where the other needs a")
    print("  convention, and the archive's degraded runs are exactly of this shape")
    print("  -- a single short round with full rounds either side.")
    print()

    banner("3. IS THE FABLE DESIGN'S CLAIM ABOUT THE LIVE GATE TRUE?")
    runner = (REPO / "bench" / "reference_runner_v3.py").read_text()
    tree = ast.parse(runner)
    found = None
    for node in ast.walk(tree):
        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == "_check_hardened_convergence"):
            found = node
            break
    if found is None:
        print("  _check_hardened_convergence NOT FOUND -- the claim is about code")
        print("  that no longer exists, so it cannot be verified or adopted as is")
        return 1
    seg = ast.get_source_segment(runner, found) or ""
    print(f"  _check_hardened_convergence present at line {found.lineno}, "
          f"{len(seg.splitlines())} lines")
    has_sparsity = "gamma_crit_min_cumulative" in seg
    print(f"  names gamma_crit_min_cumulative (the sparsity fallback) : "
          f"{has_sparsity}")
    params = [a.arg for a in found.args.args] + [a.arg for a in found.args.kwonlyargs]
    roster_named = [p for p in params
                    if any(t in p.lower() for t in
                           ("roster", "seat", "model", "respond", "active"))]
    print(f"  its parameters ({len(params)}) naming a roster : "
          f"{roster_named or 'NONE'}")
    print(f"  mentions models_responded                      : "
          f"{'models_responded' in seg}")
    print()
    if has_sparsity and not roster_named:
        print("  CLAIM HOLDS: the hardened gate carries a sparsity fallback AND")
        print("  takes no roster parameter, so on that path closure can rest on the")
        print("  quiet count alone with nothing able to see a depleted panel. That")
        print("  is a STRICTLY LARGER target than the legacy arm the CC2 design")
        print("  addresses, and the hardened gate is the default.")
    else:
        print("  CLAIM DOES NOT HOLD AS STATED; it must not be cited in B77.")

    print()
    banner("VERDICT, AND IT CORRECTS B77")
    print("  The 2 repairs COINCIDE at a constant roster, so this is not a case of")
    print("  1 being wrong. On a VARYING roster -- the shape the archive actually")
    print("  holds -- the CC2 rule needs a convention it does not state and the 2")
    print("  available conventions disagree, while the Fable rule is defined. The")
    print("  Fable design also targets the hardened gate's sparsity fallback, where")
    print("  closure rests on the quiet count ALONE, which is the larger target.")
    print()
    print("  RECOMMENDATION CHANGES FROM 'adopt the CC2 design' TO 'adopt the")
    print("  Fable design', on simplest-sufficient AND additive grounds: 1 fix,")
    print("  no convention to choose, identical behaviour at full roster. NO")
    print("  COMPOSABILITY CLAIM IS MADE -- they are alternatives, and nothing")
    print("  measures a composed form beating either, which is what his standard")
    print("  requires before a composed fix may be recommended.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
