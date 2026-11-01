#!/usr/bin/env python3
"""PROOF: a first-anchored evidence window is unsatisfiable after the first edit.

B63 observes that the FFAFP Stop gate's FOLLOW signal cannot be satisfied once a
turn has made its first mutation, while P-PASS can always be satisfied by one
further call. This script PROVES that rather than observing it, on 2 tools, so
the finding does not rest on a sequence of refusals that happened to be seen.

THE 2 PREDICATES, verbatim from `~/.claude/hooks/ffafp_audit.py`:

    FOLLOW  (:889)  scan_text = " ".join(t for i, t in scans if i < first)
    P-PASS  (:851)  verified_after = last is not None and any(i > last ...)

`first` is the index of the turn's FIRST mutation and `last` of its LAST. An
agent that has already made an edit can only act at indices >= first. So the
question is whether each predicate admits any index in that reachable set.

WHY THIS MATTERS AND WHY IT IS NOT AN ARGUMENT FOR LOOSENING ANYTHING. Before an
edit is exactly when a trace is worth something, so the FOLLOW rule is right
about a normal turn. What the proof shows is that the signal carries no
information about the REST of a long turn: a refusal after the first edit cannot
distinguish "never traced" from "traced 26 times, none of them before edit 1".
That is a reason to anchor per-mutation -- crediting a scan that precedes the
mutation IT relates to -- which is how P-PASS already behaves with `last`.
"""
from __future__ import annotations

import argparse


def prove() -> dict:
    import z3
    import sympy as sp

    i, first, last, n = z3.Ints("i first last n")

    reachable = [first >= 0, last >= first, i >= first]

    s = z3.Solver()
    s.add(*reachable, i < first)                 # FOLLOW's requirement
    follow = s.check()

    t = z3.Solver()
    t.add(*reachable, i > last)                  # P-PASS's requirement
    ppass = t.check()

    u = z3.Solver()
    u.add(last >= 0, n == last + 1, z3.Not(n > last))
    always = u.check()                           # unsat => one more call suffices

    k = sp.Symbol("k", integer=True, nonnegative=True)
    f = sp.Symbol("first", integer=True, nonnegative=True)
    l = sp.Symbol("last", integer=True, nonnegative=True)
    later = f + k
    sympy_follow = sp.simplify(later < f)        # expect False for all k >= 0
    witness = sp.simplify(l - f + 1)             # k that satisfies later > last

    return {
        "z3_follow": str(follow),
        "z3_ppass": str(ppass),
        "z3_one_more_call_always_exceeds_last": str(always),
        "sympy_follow_after_first_edit": str(sympy_follow),
        "sympy_ppass_witness_k": str(witness),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    r = prove()

    if args.json:
        import json
        print(json.dumps(r, indent=2))
        return 0

    print(__doc__)
    print("=" * 78)
    print(f"  z3  FOLLOW reachable after the first edit : {r['z3_follow']}"
          "   (unsat = impossible)")
    print(f"  z3  P-PASS reachable after the first edit : {r['z3_ppass']}"
          "     (sat = always possible)")
    print(f"  z3  'one further call fails i > last'     : "
          f"{r['z3_one_more_call_always_exceeds_last']}"
          "   (unsat = one call always suffices)")
    print(f"  SymPy  later_index < first, for k >= 0    : "
          f"{r['sympy_follow_after_first_edit']}")
    print(f"  SymPy  k witnessing later_index > last    : "
          f"{r['sympy_ppass_witness_k']}")
    print()
    ok = (r["z3_follow"] == "unsat" and r["z3_ppass"] == "sat"
          and r["sympy_follow_after_first_edit"] == "False")
    if ok:
        print("BOTH TOOLS AGREE. A first-anchored window admits nothing an agent")
        print("  can still do; a last-anchored window is always reachable by one")
        print("  further call. The asymmetry is STRUCTURAL, not a matter of")
        print("  diligence, and no behaviour on the agent's part can clear it.")
        return 0
    print("THE PROOF DID NOT REPRODUCE. Do not quote B63's claim until it does.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
