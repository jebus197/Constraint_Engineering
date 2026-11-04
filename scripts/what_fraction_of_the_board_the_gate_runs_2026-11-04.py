#!/usr/bin/env python3
"""What fraction of the test suite does the commit gate actually run?

WHY THIS EXISTS. On 2026-11-04 a note delivered to the founder stated that the
pre-commit gate "runs a full board, so every commit on the branch is a known-good
point by construction". That sentence was written to answer his question about
reverting to a last known good configuration, and it was wrong. The gate's own
output from the same night reports 2,476 passed, 8 failed and 11 skipped --
2,495 tests -- while the suite collects 15,368. The claim was corrected before
delivery and this script exists so the figure travels with its producer.

THE SCOPE IS DELIBERATE, NOT A DEFECT. `hooks/pre-commit` says so in its own
comments: the guard list is the guards written since 2026-10-29 plus earlier
additions, chosen for cost, because a full board takes about 10 minutes on the
founder's 8-core, 8-GiB machine and a separate entry already reports the gate
exceeding the cost limit written in its own header. So the honest statement is
that a commit here is a GATED point rather than a fully verified one.

THESE ARE CENSUSES, NOT SAMPLES. The totals are known exactly, so a confidence
interval does not apply and none is printed. Attaching one would be the false
rigour the note standard forbids.

Usage: python3 scripts/what_fraction_of_the_board_the_gate_runs_2026-11-04.py
"""
import argparse
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]


def gated_guard_files() -> list:
    """The guard list exactly as the shell parses it out of the hook."""
    t = (REPO / "hooks" / "pre-commit").read_text(encoding="utf-8")
    m = re.search(r'GUARDS="(.*?)"', t, re.S)
    if not m:
        return []
    return [l.strip() for l in m.group(1).splitlines() if l.strip()]


def all_guard_files() -> list:
    return sorted(p.name for p in (REPO / "bench" / "tests").glob("test_*.py"))


def collect(paths) -> int:
    """Ask pytest how many tests a path set holds. Collection only: nothing runs."""
    cmd = [sys.executable, "-m", "pytest", "-q", "--collect-only", *paths]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
    m = re.search(r"(\d+) tests? collected", r.stdout)
    return int(m.group(1)) if m else -1


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()

    gated, every = gated_guard_files(), all_guard_files()
    missing = [g for g in gated if not (REPO / g).exists()]

    n_gated_tests = collect(gated)
    n_all_tests = collect(["bench/tests/"])

    import sympy
    import mpmath
    mpmath.mp.dps = 30

    print("THE COMMIT GATE'S COVERAGE OF THE SUITE")
    print(f"  guard files in the gate : {len(gated)}")
    print(f"  guard files on disk     : {len(every)}")
    print(f"  outside the gate        : {len(every) - len(gated)}")
    if missing:
        print(f"  ★ gate names {len(missing)} file(s) that do not exist: {missing}")

    for k, n, label in ((len(gated), len(every), "guard files"),
                        (n_gated_tests, n_all_tests, "tests")):
        if k < 0 or n <= 0:
            print(f"  {label}: collection failed; figure NOT produced")
            continue
        exact = sympy.Rational(k, n)
        viamp = mpmath.mpf(k) / mpmath.mpf(n)
        agree = abs(float(exact) - float(viamp)) < 1e-15
        print(f"  {label:<12}{k} of {n} = {float(exact):.6f}  "
              f"(exact {exact}; mpmath agrees: {agree})")

    print("\n  No confidence interval is printed: both are censuses of a known")
    print("  total, not samples, so an interval would be false rigour.")
    print("\n  The scope is deliberate. hooks/pre-commit states it, and a full")
    print("  board costs about 10 minutes on an 8-core, 8-GiB machine. A commit")
    print("  here is a GATED point, not a fully verified one.")
    return 0 if n_gated_tests > 0 and n_all_tests > 0 and not missing else 1


if __name__ == "__main__":
    sys.exit(main())
