#!/usr/bin/env python3
"""Falsifier: is the appendix's Phase-2 revert-to-prior a modelling error?

Panel seat (Claude, free), 2026-09-21. Verdict it encodes:

  CHECK A -- the appendix's sigma=0 endpoint is the EXACT law-of-total-
  probability value, not a discard of evidence. In the single-flaw cycle
  (flaw present w.p. R_old; detected w.p. q if present; a failed fix
  leaves a detected flaw in place):

      P(flaw after cycle) = q*R_old * 1  +  (1 - q*R_old) * R_det  =  R_old

  R_det is the posterior GIVEN NO DETECTION. A cycle containing a fix
  attempt contains a detection, whose branch (risk 1, fix failed) exactly
  cancels the no-detection reassurance. Reverting to R_old discards
  nothing. CHECK A exits clean iff the identity is exact.

  CHECK B -- revision 1.1, R_new = (1-s)z + b(1-z) with z = R_det,
  s = sigma(1-nu), b = nu, is FALSIFIED as a replacement map: at
  sigma=1, nu=0 it returns 0, not R_det, so it breaks the verified
  Stage 5 -> Stage 4 nesting (appendix reduction table row 1), and at
  sigma=0 it returns R_det < R_old, importing no-detection reassurance
  into a branch where a detection occurred (understates risk, the
  fail-unsafe direction). CHECK B prints FALSIFIED iff those defects
  are present in the revision.

Imports the real target: bench.reference_runner_v3.compute_rk.
Cross-verified: SymPy + z3 + mpmath + NumPy; Wolfram Language (local
Wolfram Engine) independently returned 0 for the CHECK A identity and
0 for revision(sigma=1, nu=0).
"""
import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                os.pardir, "bench"))
from reference_runner_v3 import compute_rk  # noqa: E402  (real target)


def r_det(R, q):
    return R * (1 - q) / (1 - q * R)


def revision_1_1(R, q, sigma, nu):
    z = r_det(R, q)
    s, b = sigma * (1 - nu), nu
    return (1 - s) * z + b * (1 - z)


def main():
    # CHECK A: exact rational arithmetic on a grid; then the implementation.
    for Ri in range(1, 10):
        for qi in range(1, 10):
            R, q = Fr(Ri, 10), Fr(qi, 10)
            total_prob = q * R * 1 + (1 - q * R) * r_det(R, q)
            assert total_prob == R, f"total-probability identity broken at {R},{q}"
    # the implementation honours the endpoint with re-injection zeroed
    out = compute_rk(0.5, 0.3, 0.0, nu_b=0.0, nu_f=0.0)
    assert abs(out - 0.5) < 1e-15, f"compute_rk sigma=0 endpoint moved: {out}"
    print("CHECK A CLEAN: appendix sigma=0 revert == exact total probability; "
          "compute_rk(0.5, 0.3, sk=0, nu=0) == 0.5")

    # CHECK B: the revision's two endpoint defects.
    defects = []
    R, q = Fr(1, 2), Fr(3, 10)
    if revision_1_1(R, q, 1, 0) != r_det(R, q):
        defects.append(
            f"revision(sigma=1,nu=0) = {revision_1_1(R, q, 1, 0)} != "
            f"R_det = {r_det(R, q)} -- Stage 5->4 nesting broken")
    if revision_1_1(R, q, 0, 0) < R:
        defects.append(
            f"revision(sigma=0,nu=0) = {revision_1_1(R, q, 0, 0)} < R_old = {R}"
            " -- understates risk when the fix failed (fail-unsafe)")
    if defects:
        print("FALSIFIED (revision 1.1 as a replacement map):")
        for d in defects:
            print("  -", d)
    else:
        print("CHECK B CLEAN: revision endpoints sound")


if __name__ == "__main__":
    # WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
    # ran the whole measurement. A help flag must ANSWER, never ACT.
    from _cli_help import answer_help  # noqa: E402
    answer_help(__doc__, __file__)
    main()
