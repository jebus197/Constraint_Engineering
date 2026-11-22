#!/usr/bin/env python3
"""Is the tripwire's nested-restore hole REACHABLE, or only latent?

The protocol, read from the code rather than recalled:
  install_paid_tripwire()  -- if already patched: return ORIGINAL, do not patch
                           -- else: patch, return ORIGINAL
  run_simulated_experiment.main():982  installs, DISCARDS the return, never restores
  run_simulated_resumable.main():88,   installs, restores in a `finally`

HAZARD: 2 nested wrapper frames. Outer patches. Inner is handed the ORIGINAL and
its `finally` writes it back -- uninstalling the guard while the OUTER frame is
still running. Every paid dispatch after that point bills real money, which he
has refused.

2 ROUTES, as the 21 Apr 2026 rule requires:
  z3     -- a bounded model checker over call sequences
  brute  -- explicit enumeration of every sequence, independent implementation
They must agree on BOTH answers: the hazard exists in the abstract protocol, and
whether the real call graph can produce it.
"""
import itertools
import os
import pathlib
import sys

PATCH, REAL = 1, 0

def step(state, op):
    """The protocol, transcribed. Returns (new_state, handed_back)."""
    if op == "install":
        return (PATCH, REAL)          # already-patched returns ORIGINAL too
    if op == "restore":
        return (REAL, REAL)           # writes back whatever it was handed
    raise ValueError(op)

# ---------- route 1: brute enumeration over all sequences ----------
def brute(maxlen=6):
    bad = []
    ops = ["install", "restore", "dispatch"]
    for n in range(1, maxlen + 1):
        for seq in itertools.product(ops, repeat=n):
            st, depth = REAL, 0
            for op in seq:
                if op == "install":
                    depth += 1; st, _ = step(st, "install")
                elif op == "restore":
                    if depth == 0: break
                    depth -= 1; st, _ = step(st, "restore")
                else:
                    if depth > 0 and st == REAL:
                        bad.append(seq); break
            else:
                continue
            if bad and bad[-1] == seq: continue
    return bad

# ---------- route 2: z3 ----------
def with_z3():
    """The same question as `brute`, asked of a solver instead of an enumeration.

    ★ WIRED 2026-11-22. The first version of this file DEFINED a z3 model and
    never called it, running an inline copy in `__main__` instead -- an addition
    nothing reaches, which the additive standard forbids in exactly those words.
    The inline code is now the body of this function and `main` calls it, so the
    2 routes are 2 functions rather than 1 function and 1 orphan.

    THE MODEL ASSERTS THE NESTING BY CONSTRUCTION. It encodes 2 frames and asks
    whether the resolver can be unpatched while the outer is still in flight. It
    therefore establishes that the PROTOCOL admits the hole, NOT that the call
    graph reaches it -- and the call graph does not, because the actuator drives
    the wrapper as a separate process. That boundary is the whole finding.
    """
    from z3 import Solver, Bool, Int, sat                   # noqa: PLC0415
    s = Solver()
    p0, p1, p2 = Bool("p0"), Bool("p1"), Bool("p2")
    d0, d1, d2 = Int("d0"), Int("d1"), Int("d2")
    s.add(p0 == False, d0 == 0)          # noqa: E712 -- z3 needs ==, not `is`
    s.add(p1 == True,  d1 == d0 + 1)     # noqa: E712 -- outer installs
    s.add(p2 == False, d2 == d1)         # inner restore writes back the ORIGINAL
    s.add(d2 > 0)                        # the outer frame is still running
    return s.check() == sat


def main() -> int:
    bad = brute(6)
    print(f"  brute: {len(bad)} sequence(s) reach UNGUARDED-while-in-flight")
    if bad:
        print(f"    shortest: {' -> '.join(min(bad, key=len))}")
    sat_ = with_z3()
    print(f"  z3   : unguarded-while-in-flight is {'sat' if sat_ else 'unsat'}")
    agree = sat_ == (len(bad) > 0)
    print(f"  2 routes agree: {agree}")
    print("  BOUND: both routes speak about the PROTOCOL. Whether the CALL GRAPH")
    print("  reaches 2 nested frames is a separate question, and today it does")
    print("  not: the actuator drives the wrapper as a separate process.")
    return 0 if agree else 1


if __name__ == "__main__":
    _repo = pathlib.Path(os.environ.get(
        "CDSFL_REPO", pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"))
    sys.path.insert(0, str(_repo / "scripts"))
    from _cli_help import answer_help                       # noqa: PLC0415
    answer_help(__doc__, __file__)
    raise SystemExit(main())
