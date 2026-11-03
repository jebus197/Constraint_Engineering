#!/usr/bin/env python3
"""Revert the second route to the superlative and require its guard to go red.

A FIX I HAVE NOT TRIED TO BREAK IS A HYPOTHESIS. The subject is the second,
independent route added to `scripts/c0001_provenance_does_not_reconcile_2026-11-03.py`
on 2026-11-03: where the primary counts registry entries at or above a severity
threshold constant of 1.0 and asks whether that count is 0, the secondary takes
the run's actual MAXIMUM severity and compares. Both are reported, with their
agreement, so a disagreement cannot hide.

WHY THE MUTATIONS HAVE TO BE CHOSEN CAREFULLY HERE. On the live archive the 2
routes AGREE in 4 of 4 candidate runs, so a mutation that merely breaks the
secondary's accuracy may leave every live verdict unchanged. The guard therefore
tests `_max_severity` directly against planted registries, and the mutations
below target that function and the reporting that reaches the output.

4 MUTATIONS, EACH UNDOING A DIFFERENT PROPERTY:
  M1  `_max_severity` returns None always   -> the secondary computes nothing
  M2  it returns the MINIMUM instead        -> the wrong extremum
  M3  a None severity is coerced to 0.0     -> a floor beneath the maximum
  M4  the route-B line is not printed       -> the secondary exists but is mute

M3 IS THE ONE THAT NEARLY ESCAPED. The guard's first version asserted that a
registry of `{None, 0.4}` yields 0.4, which coercion ALSO satisfies, because 0.0
can never be the maximum of a set containing a positive number. That assertion
was vacuous and was replaced by the single-entry case, where skipping returns
None and coercing returns 0.0. If M3 does not go red, the vacuity is back.

M4 IS THE ADDITIVE-STANDARD CHECK. A second route that is computed and never
reported is an addition nothing reaches, which the standard rejects in its
symmetric form.

THE SUBJECT IS RESTORED BY HASH, NOT BY HOPE, per
`feedback_a_harness_must_restore_what_it_found_2026-11-01`: the original bytes
are held in memory, written back in a `finally`, and the sha256 compared before
the exit code is decided.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "scripts" / "c0001_provenance_does_not_reconcile_2026-11-03.py"
GUARD = (REPO / "bench" / "tests"
         / "test_the_superlative_has_two_routes_2026-11-03.py")

BODY = '''    sevs = [float(v["severity"]) for v in ents.values()
            if isinstance(v, dict) and v.get("severity") is not None]
    return max(sevs) if sevs else None'''

ROUTE_B_PRINT = '''        print(f"     route B, C0001 {c1sev} against max {mx} : {route_b}")'''

MUTATIONS = [
    ("M1 the secondary computes nothing",
     "the second route's existence as a computation",
     BODY,
     '    return None  # MUTANT: the secondary computes nothing'),
    ("M2 it returns the minimum, not the maximum",
     "the choice of extremum, which is the whole content of the route",
     BODY,
     '    sevs = [float(v["severity"]) for v in ents.values()\n'
     '            if isinstance(v, dict) and v.get("severity") is not None]\n'
     '    return min(sevs) if sevs else None  # MUTANT'),
    ("M3 a None severity is coerced to 0.0",
     "the skip-versus-coerce boundary the first guard version could not see",
     BODY,
     '    sevs = [float(v.get("severity") or 0.0) for v in ents.values()\n'
     '            if isinstance(v, dict)]  # MUTANT\n'
     '    return max(sevs) if sevs else None'),
    ("M4 the route-B line is never printed",
     "the reporting, without which the route is an unreached addition",
     ROUTE_B_PRINT,
     '        pass  # MUTANT: the second route is computed and never reported'),
]


def _run_guard() -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO), timeout=600,
    )
    lines = [ln for ln in (r.stdout + r.stderr).strip().splitlines() if ln.strip()]
    return r.returncode == 0, (lines[-1] if lines else "")


def main() -> int:
    argparse.ArgumentParser(
        description=("Revert the second route to the superlative and require "
                     "its guard to go red.")).parse_args()

    original = SUBJECT.read_bytes()
    h0 = hashlib.sha256(original).hexdigest()
    results: list[tuple[str, bool, str]] = []
    try:
        green, tail = _run_guard()
        results.append(("the UNMUTATED producer passes the guard", green, tail))
        if not green:
            print("  The guard fails on the unmutated producer; mutating it")
            print(f"  would prove nothing. {tail}")
            return 1
        text = original.decode()
        for name, reverts, find, repl in MUTATIONS:
            n = text.count(find)
            if n != 1:
                results.append((f"{name} [NOT APPLIED]", False,
                                f"its anchor occurs {n} times, not 1"))
                continue
            SUBJECT.write_text(text.replace(find, repl, 1), encoding="utf-8")
            red, tail = _run_guard()
            SUBJECT.write_bytes(original)
            results.append((name, not red,
                            tail if not red else
                            f"GAP: the guard stayed GREEN, so it does not hold "
                            f"{reverts}."))
    finally:
        SUBJECT.write_bytes(original)

    h1 = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()
    restored = h0 == h1
    print("=" * 76)
    print("DOES THE GUARD NOTICE THE SECOND ROUTE BEING UNDONE?")
    print("=" * 76)
    for name, ok, tail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {tail[:150]}")
    n_ok = sum(1 for _n, ok, _t in results if ok)
    print()
    print(f"  producer restored byte-for-byte : {restored}")
    print(f"    sha256 {h0[:16]} -> {h1[:16]}")
    print(f"  {n_ok} of {len(results)} propert(ies) hold")
    if not restored:
        print("  THE PRODUCER WAS NOT RESTORED. Fix that before anything else.")
    return 0 if (n_ok == len(results) == len(MUTATIONS) + 1 and restored) else 1


if __name__ == "__main__":
    raise SystemExit(main())
