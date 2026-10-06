#!/usr/bin/env python3
"""Why the preflight check halts at the first failure, and in what order.

THE FOUNDER'S RULING, 2026-10-06: *"on a bios screen when 'booting up' it prints a
simple message against each check, which is just 'pass or fail'. If a test passes then
the next check fails, the system is halted, giving the user an opportunity to
investigate."*

Read as: checks run in sequence, each prints PASS, and the FIRST failure halts the
boot. It overrules the "reports, does not block" decision in the first version of
`preflight_health_check_2026-10-06.py`, and it exposes a defect in it that the
3-state GREEN/AMBER/RED scheme was hiding -- part 1 below.

3 questions, each answered by a tool rather than by argument:

  PART 1  Does a check that CRASHES currently let the boot proceed?  (executed)
  PART 2  Is the check order a valid topological order of their dependencies?  (z3)
  PART 3  What does halt-on-first cost in runs to clear k failures?  (SymPy + NumPy)

Run: python3 scripts/post_semantics_2026-10-06.py
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def part1_a_crashed_check_boots() -> bool:
    """A check that raises must not be survivable. Measured by CALLING main().

    `preflight_health_check_2026-10-06.py` maps any exception to AMBER, and AMBER
    does not set the exit code. So a check whose own code is broken reports a
    non-green row and still returns 0 -- the shape this project names as "a guard
    that cannot fail is not a guard".
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "pf", REPO / "scripts" / "preflight_health_check_2026-10-06.py")
    pf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pf)

    def _explodes():
        raise RuntimeError("this check's own code is broken")

    saved = list(pf.CHECKS)
    try:
        pf.CHECKS = [("a deliberately broken check", _explodes)]
        code = pf.main(["--quiet"])
    finally:
        pf.CHECKS = saved
    print(f"PART 1  a check that raises -> exit code {code}")
    print(f"        boot proceeds on a broken check: {code == 0}")
    return code == 0


#: check name -> the checks it depends on being sound first.
#: An edge A -> B means "B's result is meaningless unless A passed".
DEPENDENCIES = {
    "facilities armed explicitly": [],
    "severity test present": [],
    # The ladder is measured against the budget the LAUNCHER sets, so a launcher
    # whose facilities are unset makes the ladder measurement be about the wrong
    # configuration -- which is precisely the error the first version committed.
    "capability ladder climbs": ["facilities armed explicitly"],
    # Both of these call unverified_critical_count. If the severity test inside it
    # is absent or inert, they are reporting on a different function than the one
    # the run will use.
    "clearance is monotone": ["severity test present"],
    "blockers not labelled SETTLED": ["severity test present"],
}

#: The order the POST screen runs them in. Most fundamental first, BIOS fashion.
POST_ORDER = [
    "facilities armed explicitly",
    "severity test present",
    "clearance is monotone",
    "blockers not labelled SETTLED",
    "capability ladder climbs",
]


def part2_order_is_topological(order=None) -> bool:
    """z3: no check runs before something it depends on.

    Under halt-on-first the order is LOAD-BEARING in a way it was not before. If a
    dependency runs later than its dependent, the dependent's PASS was measured
    against an unestablished precondition, and the halt stops at the wrong row.
    """
    import z3
    order = list(order or POST_ORDER)
    pos = {name: z3.Int(f"pos_{i}") for i, name in enumerate(order)}
    s = z3.Solver()
    for i, name in enumerate(order):
        s.add(pos[name] == i)
    # Assert the ordering property; UNSAT means it is violated somewhere.
    for name, deps in DEPENDENCIES.items():
        for d in deps:
            s.add(pos[d] < pos[name])
    ok = s.check() == z3.sat
    print(f"PART 2  z3 on the POST order: {'sat -- topological' if ok else 'UNSAT -- a dependency runs too late'}")
    if not ok:
        print(f"        unsat core: {s.unsat_core()}")
    # Cross-check with a hand-rolled scan, so a z3 encoding slip cannot pass alone.
    idx = {n: i for i, n in enumerate(order)}
    manual = all(idx[d] < idx[n] for n, ds in DEPENDENCIES.items() for d in ds)
    print(f"        independent index scan agrees: {manual == ok}")
    assert manual == ok, "z3 and the index scan disagree about the same order"
    return ok


def part3_runs_to_clear_k() -> None:
    """How many runs does halt-on-first need to clear k independent failures?

    Exactly k, because each run reveals exactly 1. Trivial, and worth deriving
    because it is the whole justification for keeping a diagnostic mode that shows
    every failure: at k = 5 the halting screen costs 5 boot cycles to enumerate
    what 1 diagnostic run lists.
    """
    import sympy as sp
    import numpy as np

    k = sp.Symbol("k", positive=True, integer=True)
    halt_runs = k           # 1 failure revealed per run
    all_runs = sp.Integer(1)  # every failure listed in 1 run
    saved = sp.simplify(halt_runs - all_runs)
    print(f"PART 3  SymPy: runs under halt-on-first = {halt_runs}, "
          f"under --all = {all_runs}, difference = {saved}")

    # NumPy simulation against the same claim: walk a vector of failures, halting.
    rng = np.random.default_rng(20261006)
    agree = 0
    trials = 2000
    for _ in range(trials):
        n = int(rng.integers(1, 8))
        kk = int(rng.integers(1, n + 1))
        fails = np.zeros(n, dtype=bool)
        fails[rng.choice(n, size=kk, replace=False)] = True
        runs, remaining = 0, fails.copy()
        while remaining.any():
            first = int(np.argmax(remaining))   # halt here
            remaining[first] = False            # fix it, reboot
            runs += 1
        agree += (runs == kk)
    print(f"        NumPy simulation: {agree} of {trials} trials give runs == k")
    assert agree == trials, "the simulation contradicts the symbolic result"
    sub = int(halt_runs.subs(k, 5))
    print(f"        at k = 5: {sub} boot cycles against 1 diagnostic run")


def main() -> int:
    print("=" * 74)
    print("POST SEMANTICS -- evidence for halt-on-first and the check order")
    print("=" * 74)
    crashed_boots = part1_a_crashed_check_boots()
    print()
    topo = part2_order_is_topological()
    print()
    part3_runs_to_clear_k()
    print()
    print("=" * 74)
    print(f"a crashed check currently boots : {crashed_boots}   <- the defect")
    print(f"POST order is topological       : {topo}")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
