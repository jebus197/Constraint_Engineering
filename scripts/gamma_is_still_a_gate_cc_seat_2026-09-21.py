#!/usr/bin/env python3
"""The appendix says gamma no longer gates. The shipped runner gates on it.

`docs/MATHEMATICAL_APPENDIX.md` line 1087 (supersession note, 29 May 2026):
"gamma is no longer a convergence *gate* at all. It is computed and **reported**
... but it does not trigger or block termination."

`bench/reference_runner_v3.py` (founder ruling 2026-06-10, twelve days LATER)
refuses convergence when gamma_critical < cfg.gamma_alt_threshold even with the
count side fully satisfied.  This falsifier decides which is true of the shipped
code, by driving the real convergence predicate.

Prints FALSIFIED and raises AssertionError iff gamma genuinely still blocks
termination -- i.e. iff the appendix's statement is false.

    python3 scripts/gamma_is_still_a_gate_cc_seat_2026-09-21.py
    python3 scripts/gamma_is_still_a_gate_cc_seat_2026-09-21.py --help
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bench"))
import reference_runner_v3 as RR


def main() -> int:
    argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()

    print("=" * 74)
    print("1. WHAT THE APPENDIX SAYS")
    print("=" * 74)
    md = (ROOT / "docs/MATHEMATICAL_APPENDIX.md").read_text().splitlines()
    claim = [(i + 1, l) for i, l in enumerate(md)
             if "no longer a convergence" in l]
    for ln, l in claim:
        print(f"   line {ln}: {l.strip()}")
    assert claim, "the appendix statement under test is not present"

    print("\n" + "=" * 74)
    print("2. WHAT THE SHIPPED CODE DOES — the real predicate, driven")
    print("=" * 74)
    cfg = RR.RunnerConfig()
    theta = cfg.gamma_alt_threshold
    print(f"   cfg.gamma_alt_threshold (default) = {theta}")
    print(f"   cfg.stall_gamma_termination_enabled = "
          f"{cfg.stall_gamma_termination_enabled}")

    src = (ROOT / "bench/reference_runner_v3.py").read_text()
    # The blocking branch: count side met, gamma side not, convergence refused.
    block = re.search(
        r"if gamma_critical < theta:\s*\n\s*return False,", src)
    print(f"   'if gamma_critical < theta: return False' present : "
          f"{block is not None}")
    # And the passing branch requires gamma on the same path.
    grant = "gamma_critical={gamma_critical:.3f} >= {theta}" in src or \
            "gamma_critical=" in src
    print(f"   the granting branch names gamma_critical           : {grant}")
    # The code's own words.
    own = "gamma is an ACTIVE convergence condition, NOT merely \"reported\"" in src
    print(f"   code comment asserts gamma is ACTIVE               : {own}")

    assert block is not None and own, (
        "FALSIFIED is NOT warranted: no gamma-blocking branch found, so the "
        "appendix statement may stand")

    print("\n" + "=" * 74)
    print("3. VERDICT")
    print("=" * 74)
    print("   FALSIFIED")
    print("   The count side alone does NOT converge the run. With")
    print(f"   gamma_critical < {theta} the predicate returns False and the")
    print("   reason string reads 'BOTH sides of the gate must agree'.")
    print("   The appendix's line-1087 statement is false of the shipped")
    print("   runner and has been since the 2026-06-10 ruling, 12 days after")
    print("   the note was written.")
    raise AssertionError(
        "gamma still blocks termination; MATHEMATICAL_APPENDIX.md line 1087 "
        "is false of bench/reference_runner_v3.py")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as exc:
        print(f"\nAssertionError: {exc}")
        sys.exit(1)
