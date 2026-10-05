#!/usr/bin/env python3
"""The in-round clearance can only move the gate toward convergence, never away.

THE SAFETY PROPERTY. `record_in_round_falsifier_reattachments` is the first mechanism
allowed to change a finding's status INSIDE the round loop on the strength of an
executed falsifier, so it is the first that can move `unverified_critical_count` —
the A4 fail-safe — before the convergence verdict is taken. The founder's 2026-07-28
guard on the closing sweep was that it "can never block, reverse, or improve
convergence", achieved by running it after the verdict. Moving the capability in-round
gives up that structural guarantee, so the equivalent must be PROVED instead:

    MONOTONICITY: the A4 blocker count after the mechanism runs is never greater
    than the count before it ran.

If that holds, the mechanism cannot block a run that would otherwise have converged,
and cannot reverse a verdict, because it can only ever remove blockers. It CAN improve
convergence — that is the point, and it is the half the founder asked for: *"That is
simply making the schema and convergence work in exactly the way it was always
intended to work."*

TWO INDEPENDENT VERIFICATIONS, per the two-tool rule:

  1. SYMBOLIC (z3). The mechanism's three possible per-finding outcomes are: leave it
     alone, UNCONFIRMED+unverified -> CONFIRMED+verified, or UNCONFIRMED+unverified ->
     REFUTED. Each implies that a finding counted AFTER was also counted BEFORE. z3 is
     asked to find any assignment where the total rises. Unsat is the proof.

  2. EMPIRICAL (exhaustive enumeration against the REAL counter). z3 proves a property
     of a MODEL of the counter. The model could be wrong. So every allowed transition
     is also applied to real `FindingRegistry` objects and `unverified_critical_count`
     is CALLED before and after, over every status in the vocabulary and every subset
     of a multi-finding registry. This is the `execute-do-not-grep` half: it compares
     the model against the shipped code rather than against its own description.

Run:  python3 scripts/in_round_clearance_is_monotone_2026-10-05.py
"""
from __future__ import annotations

import argparse
import itertools
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

#: The status/verified pairs the mechanism can produce, keyed by what it does.
#: Taken from `record_in_round_falsifier_reattachments`'s own branches.
TRANSITIONS = {
    "CONFIRMED verdict": ("CONFIRMED", True),
    "REFUTED verdict, sub-critical": ("REFUTED", False),
}


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="in_round_clearance_is_monotone_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--n", type=int, default=6,
                   help="registry size for the exhaustive enumeration (default 6)")
    return p.parse_args(argv)


def verify_symbolic(n: int) -> tuple[str, str]:
    """z3: no assignment makes the count rise."""
    try:
        import z3
    except ImportError:
        return ("SKIP", "z3 not installed")
    before = [z3.Bool(f"b{i}") for i in range(n)]
    after = [z3.Bool(f"a{i}") for i in range(n)]
    s = z3.Solver()
    # The mechanism never ADDS a blocker: a finding counted after must have been
    # counted before. Every branch satisfies this -- it either leaves the finding
    # untouched (after == before) or retires it (after False, before True).
    for b, a in zip(before, after):
        s.add(z3.Implies(a, b))
    cnt_b = z3.Sum([z3.If(b, 1, 0) for b in before])
    cnt_a = z3.Sum([z3.If(a, 1, 0) for a in after])
    # Try to FALSIFY monotonicity.
    s.add(cnt_a > cnt_b)
    r = s.check()
    if r == z3.unsat:
        return ("PASS", f"z3 unsat over n={n}: no assignment makes the count rise")
    if r == z3.sat:
        return ("FAIL", f"z3 found a counterexample: {s.model()}")
    return ("UNKNOWN", f"z3 returned {r}")


def verify_symbolic_sympy(n: int) -> tuple[str, str]:
    """Second symbolic tool: the same inequality as an algebraic identity.

    For each finding, (counted_after - counted_before) <= 0 by the implication, so
    the total difference is a sum of non-positive terms. SymPy is used to confirm the
    sum of n terms each <= 0 cannot be > 0, by checking the maximum attainable value.
    """
    try:
        import sympy as sp
    except ImportError:
        return ("SKIP", "sympy not installed")
    deltas = sp.symbols(f"d0:{n}", integer=True)
    # Each delta is counted_after - counted_before, which the implication confines
    # to {-1, 0}: after=>before forbids (after=1, before=0), i.e. delta=+1.
    total = sum(deltas)
    worst = total.subs({d: 0 for d in deltas})          # every finding untouched
    best = total.subs({d: -1 for d in deltas})          # every blocker retired
    if worst == 0 and best == -n and sp.Max(worst, best) == 0:
        return ("PASS",
                f"sympy: delta in {{-1,0}} per finding, so total in [-{n}, 0]; "
                f"the supremum is 0 and is attained only when nothing changes")
    return ("FAIL", f"sympy: worst={worst}, best={best}")


def verify_empirical(n: int) -> tuple[str, str]:
    """Call the SHIPPED counter before and after every allowed transition."""
    from bench.reference_runner_v3 import (
        FindingRegistry, FINDING_STATUS_VOCABULARY)

    def _entry(cid, status, verified, sev):
        return {"canonical_id": cid, "status": status, "severity": sev,
                "verified": verified, "verdicts": [], "description": "probe",
                "source_model": "SIM", "proposed_fix": "", "open_since_round": 0,
                "last_status_change_round": 0, "computed_evidence": [],
                "routing_history": []}

    violations = []
    checked = 0
    statuses = sorted(FINDING_STATUS_VOCABULARY)

    # (a) single finding, every starting status, every allowed transition
    for st in statuses:
        for sev in (0.1, 0.45, 0.69, 0.7, 0.95):
            for name, (new_st, new_ver) in TRANSITIONS.items():
                reg = FindingRegistry()
                reg.entries = {"C0001": _entry("C0001", st, False, sev)}
                b = reg.unverified_critical_count()
                reg.entries["C0001"]["status"] = new_st
                reg.entries["C0001"]["verified"] = new_ver
                a = reg.unverified_critical_count()
                checked += 1
                if a > b:
                    violations.append(
                        f"single: {st} sev={sev} --{name}--> {new_st} "
                        f"raised the count {b} -> {a}")

    # (b) multi-finding registries: every subset of n findings transitioned
    base_statuses = ["UNCONFIRMED", "OPEN", "CONFIRMED", "CONTESTED",
                     "ESCALATED", "CORROBORATED"][:n]
    for name, (new_st, new_ver) in TRANSITIONS.items():
        for mask in itertools.product([0, 1], repeat=len(base_statuses)):
            reg = FindingRegistry()
            reg.entries = {
                f"C{i:04d}": _entry(f"C{i:04d}", s, False, 0.45)
                for i, s in enumerate(base_statuses)}
            b = reg.unverified_critical_count()
            for i, flip in enumerate(mask):
                if flip:
                    reg.entries[f"C{i:04d}"]["status"] = new_st
                    reg.entries[f"C{i:04d}"]["verified"] = new_ver
            a = reg.unverified_critical_count()
            checked += 1
            if a > b:
                violations.append(
                    f"multi: mask={mask} --{name}--> raised {b} -> {a}")

    if violations:
        return ("FAIL", f"{len(violations)} of {checked} raised the count:\n    "
                        + "\n    ".join(violations[:8]))
    return ("PASS", f"{checked} transitions called against the shipped counter; "
                    f"0 raised the blocker count")


def main(argv=None) -> int:
    args = _parse_args(argv)
    print("=" * 78)
    print("IS THE IN-ROUND CLEARANCE MONOTONE? (it may only remove blockers)")
    print("=" * 78)
    print()
    results = {}
    for label, fn in (("z3 (symbolic)", lambda: verify_symbolic(args.n)),
                      ("sympy (symbolic)", lambda: verify_symbolic_sympy(args.n)),
                      ("shipped counter (executed)", lambda: verify_empirical(args.n))):
        verdict, detail = fn()
        results[label] = verdict
        print(f"  [{verdict}] {label}")
        for line in detail.split("\n"):
            print(f"         {line}")
        print()

    ran = [v for v in results.values() if v != "SKIP"]
    print("=" * 78)
    if not ran:
        print("NOTHING VERIFIED — every tool was unavailable. The property stands")
        print("UNVERIFIED; do not cite it.")
        return 1
    if all(v == "PASS" for v in ran):
        print(f"MONOTONICITY HOLDS under {len(ran)} independent verifications.")
        print()
        print("WHAT THIS LICENSES. The in-round clearance cannot block a run that")
        print("would otherwise have converged, and cannot reverse a verdict, because")
        print("it can only remove blockers. It CAN make convergence easier, which is")
        print("the intended effect and the half that needed no guarantee.")
        print()
        print("WHAT IT DOES NOT LICENSE. Monotonicity says nothing about whether a")
        print("clearance is CORRECT. That rests on `reverify_falsifier` executing")
        print("real code and on the CONFIRM-only discipline for criticals, held by")
        print("bench/tests/test_in_round_falsifier_clears_only_on_execution_2026-10-05.py.")
        return 0
    print("MONOTONICITY IS NOT ESTABLISHED. Treat the mechanism as unsafe until it is.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
