#!/usr/bin/env python3
"""Recompute the G_n numerical illustration from the appendix's own formulas.

WHY THIS SCRIPT EXISTS
----------------------
`docs/MATHEMATICAL_APPENDIX.md` carries a worked example under the HIL detection
model. On 2026-09-05 a panel reviewer found it spliced from 2 inconsistent
computations, and the finding was confirmed here by SymPy and Wolfram agreeing
to 6 significant figures.

The table printed C_H = 0.698 where the appendix's own formulas give 0.921095,
and its combined rows were shifted by one position:

  printed against rho=0.3 : 0.851  ==  G_n at rho=0   computed with C_H=0.698
  printed against rho=0.6 : 0.748  ==  G_n at rho=0.3 computed with C_H=0.698

while the rho=0 row (0.961) used the CORRECT C_H=0.921095. So the first and last
rows were right and the 2 middle rows wrong, which is exactly why the table read
as internally plausible and survived review for months.

This script exists because of the standing project rule
`measured-rate-travels-with-its-script`: a number quoted in a document is a claim
about evidence unless the code that produced it is committed beside it. The
appendix cites this file by name.

Run:  python3 scripts/verify_appendix_numerical_illustration.py
Exit: 0 if the document's corrected values reproduce, 1 if they do not.
"""

from __future__ import annotations

import sys

import sympy as sp

# Parameters exactly as the appendix states them:
# "3 machine passes (p_M = 0.3, d_M = 0.7), 2 human passes
#  (E = 0.85, M = 0.9, alpha = 0.4, d_H = 0.9)"
E = sp.Rational(85, 100)
M = sp.Rational(9, 10)
ALPHA = sp.Rational(4, 10)
P_M = sp.Rational(3, 10)
D_M = sp.Rational(7, 10)
N_M = 3
D_H = sp.Rational(9, 10)
N_H = 2

# The values the corrected table prints.
EXPECTED = {
    "C_M": sp.Rational(507, 1000),
    "C_H": sp.Rational(921, 1000),
    "rho=0": sp.Rational(961, 1000),
    "rho=0.3": sp.Rational(825, 1000),
    "rho=0.6": sp.Rational(689, 1000),
    "rho=1.0": sp.Rational(507, 1000),
}

# What the OLD table printed, kept so the defect stays legible in the record.
SUPERSEDED = {"C_H": "0.698", "rho=0.3": "0.851", "rho=0.6": "0.748"}


def f_k(expertise, methodology, alpha):
    """f_k(E, M) = E * (alpha + (1 - alpha) * M)  -- appendix, HIL section."""
    return expertise * (alpha + (1 - alpha) * methodology)


def coverage(detection, per_pass, n_passes):
    """C = 1 - (1 - d * p)^n  -- one stream's coverage over n passes."""
    return 1 - (1 - detection * per_pass) ** n_passes


def G_n(c_machine, c_human, rho, weight=1):
    """G_n = w * [1 - (1 - C_M) * (1 - C_H * (1 - rho_MH))]."""
    return weight * (1 - (1 - c_machine) * (1 - c_human * (1 - rho)))


def main() -> int:
    p_H = f_k(E, M, ALPHA)
    c_m = coverage(D_M, P_M, N_M)
    c_h = coverage(D_H, p_H, N_H)

    print("Appendix numerical illustration, recomputed from the stated formulas")
    print("=" * 70)
    print(f"  f(E, M) = E*(alpha + (1-alpha)*M) = {p_H} = {float(p_H):.6f}")
    print(f"  C_M     = 1 - (1 - d_M*p_M)^n_M   = {float(c_m):.6f}")
    print(f"  C_H     = 1 - (1 - d_H*p_H)^n_H   = {float(c_h):.6f}")
    print()

    rows = [
        ("C_M", c_m),
        ("C_H", c_h),
        ("rho=0", G_n(c_m, c_h, 0)),
        ("rho=0.3", G_n(c_m, c_h, sp.Rational(3, 10))),
        ("rho=0.6", G_n(c_m, c_h, sp.Rational(6, 10))),
        ("rho=1.0", G_n(c_m, c_h, 1)),
    ]

    failures = []
    for name, value in rows:
        want = EXPECTED[name]
        # The table prints 3 decimal places, so compare at that resolution.
        got = sp.Rational(round(float(value) * 1000), 1000)
        ok = got == want
        mark = "ok " if ok else "FAIL"
        note = ""
        if name in SUPERSEDED:
            note = f"   (old table printed {SUPERSEDED[name]})"
        print(f"  [{mark}] {name:9s} computed {float(value):.6f} -> "
              f"{float(got):.3f}   document says {float(want):.3f}{note}")
        if not ok:
            failures.append((name, float(got), float(want)))

    print()
    print("The shift, demonstrated: recompute with the OLD table's C_H = 0.698")
    c_h_old = sp.Rational(698, 1000)
    for rho, printed_against in [(0, "rho=0.3 (0.851)"),
                                 (sp.Rational(3, 10), "rho=0.6 (0.748)")]:
        v = G_n(c_m, c_h_old, rho)
        print(f"    G_n(rho={float(rho):.1f}, C_H=0.698) = {float(v):.4f}"
              f"   <- what the old table printed against {printed_against}")

    if failures:
        print()
        print(f"MISMATCH in {len(failures)} row(s): {failures}")
        return 1
    print()
    print("All 6 rows reproduce the corrected table.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
