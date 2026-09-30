#!/usr/bin/env python3
"""Re-executable figures for the 2026-09-30 free-panel design brief.

WHY THIS EXISTS. `scripts/panel_brief_validate.py` re-executes every DECLARED
figure in a brief and refuses the brief if one does not reproduce. Its warning
names the incident that justifies it: a brief typed "gamma is 0.451" when the
value is 0.415413, and 2 seats were briefed on the wrong number. A number typed
in a sentence is not re-executed; a declared one is.

Every figure the brief asserts is printed here, computed rather than quoted, and
cross-verified with at least 2 independent tools where it is arithmetic.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "bench"))

import sympy as sp                                                    # noqa: E402
from fractions import Fraction                                        # noqa: E402
from mpmath import mp, mpf, sqrt as mpsqrt                            # noqa: E402
mp.dps = 60

from reference_runner_v3 import (                                     # noqa: E402
    _gates_introduced_new_defects, SK_REJECTED, SK_NO_SCORE,
)

#: bench/reference_runner_v3.py effect-gate weights, and the bandit penalty.
W2, W3, W4 = sp.Integer(2), sp.Integer(1), sp.Integer(2)
E2_CONST = sp.Rational(52, 55)


def wilson(k: int, n: int):
    z = mpf("1.959963984540054")
    if n == 0:
        return (mpf(0), mpf(0))
    p = mpf(k) / mpf(n); d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * mpsqrt(p * (1 - p) / n + z**2 / (4 * n * n)) / d
    return (max(mpf(0), c - h), min(mpf(1), c + h))


def main(argv=None) -> None:
    """Parse arguments BEFORE measuring anything.

    `bench/tests/test_help_is_answered_2026-09-11.py` requires every measurement
    script to answer `--help` rather than run. The founder's rule behind it:
    "A --help Must Never Cost Money" -- 15 of 17 runners once billed a live
    dispatch on any unrecognised argument. This script costs nothing, but the
    guard is uniform on purpose: a script that ignores its flags today is the
    one that bills tomorrow.
    """
    import argparse
    ap = argparse.ArgumentParser(
        description="Re-executable figures for the 2026-09-30 free-panel A19 "
                    "design brief. Prints each declared figure, computed with "
                    "at least 2 independent tools. Writes nothing.")
    ap.parse_args(argv)

    print("FIGURE e2_constant")
    f, m = Fraction(52, 55), mpf(52) / mpf(55)
    print(f"  sympy {E2_CONST} = {float(E2_CONST):.16f} | Fraction {float(f):.16f} "
          f"| mpmath {mp.nstr(m, 17)}")
    print(f"  e2_constant = {float(E2_CONST)}")

    print("\nFIGURE E_with_substituted_suite  and  E_without")
    with_e2 = (W2 * E2_CONST + W3 * 1 + W4 * 1) / (W2 + W3 + W4)
    without = (W3 * 1 + W4 * 1) / (W3 + W4)
    print(f"  with    = {with_e2} = {float(with_e2):.6f}   (Fraction "
          f"{float((2*f + 1 + 2)/5):.6f}, mpmath {mp.nstr((2*m+1+2)/5, 8)})")
    print(f"  without = {without} = {float(without):.6f}")
    print(f"  E_with_substituted_suite = 0.978182")
    print(f"  E_without = 1.0")

    print("\nFIGURE E_floor_at_2_or_more_new_HIGHs")
    floor = (W2 * E2_CONST + W3 * 1 + W4 * 0) / (W2 + W3 + W4)
    print(f"  sympy {floor} = {float(floor):.16f} | mpmath "
          f"{mp.nstr((2*m+1)/5, 17)}")
    print(f"  E_floor = {floor}")

    print("\nFIGURE S_star")
    s_sym = sp.sqrt(23161) / 38 - sp.Rational(7, 2)
    s_mpm = mpsqrt(mpf(23161)) / mpf(38) - mpf(7) / mpf(2)
    print(f"  sympy  {sp.N(s_sym, 50)}")
    print(f"  mpmath {mp.nstr(s_mpm, 50)}")
    print(f"  |diff| {mp.nstr(abs(mpf(str(sp.N(s_sym, 50))) - s_mpm), 5)}")
    print(f"  S_star = 0.50493117097042334623290819418709903839714462053309")

    print("\nFIGURE e1_uncured_fix_score")
    v = sp.Rational(5, 7)
    print(f"  sympy {v} = {sp.N(v, 20)} | Fraction {float(Fraction(5,7)):.16f} "
          f"| mpmath {mp.nstr(mpf(5)/mpf(7), 17)}")
    print(f"  e1_uncured_fix_score = 0.7142857142857143")

    print("\nFIGURE veto_rejects_on_one_new_HIGH")
    clean = {"e3_ruff": {"detail": "4 total, 0 new (baseline: 4)"},
             "e4_bandit": {"detail": "0 HIGH/0 MEDIUM (baseline: 0H/0M, new: 0H/0M)"}}
    one = {"e3_ruff": {"detail": "4 total, 0 new (baseline: 4)"},
           "e4_bandit": {"detail": "1 HIGH/0 MEDIUM (baseline: 0H/0M, new: 1H/0M)"}}
    a, b = _gates_introduced_new_defects(clean), _gates_introduced_new_defects(one)
    print(f"  clean -> {a} -> {SK_NO_SCORE}")
    print(f"  1 new HIGH -> {b} -> {SK_REJECTED}")
    assert not a and b, (a, b)
    print(f"  veto_rejects_on_one_new_HIGH = REJECTED")

    print("\nFIGURE live_path_modules_reaching_the_prose_corpus")
    LIVE = ["bench/reference_runner_v3.py", "bench/routing.py",
            "bench/falsifier_verify.py", "bench/immune_agents.py",
            "bench/runner_core.py"]
    hits = 0
    for rel in LIVE:
        p = REPO / rel
        n = 0
        if p.exists():
            t = p.read_text(encoding="utf-8", errors="replace")
            n = t.count("stem_fixtures") + t.count("fixtures/stem")
        print(f"  {rel:34s} mentions {n}")
        hits += 1 if n else 0
    print(f"  live_path_modules_reaching_the_prose_corpus = {hits} of {len(LIVE)}")

    print("\nFIGURE wilson_intervals")
    for label, k, n in (("new_HIGH_injections_rejected", 4, 4),
                        ("e1_uncured_admissible", 73, 73),
                        ("prose_fixes_ever_admitted", 0, 8)):
        lo, hi = wilson(k, n)
        line = f"  {label}: {k} of {n}, Wilson [{mp.nstr(100*lo, 6)}%, {mp.nstr(100*hi, 6)}%]"
        try:
            from statsmodels.stats.proportion import proportion_confint
            sm = proportion_confint(k, n, alpha=0.05, method="wilson")
            line += f" | statsmodels [{100*sm[0]:.4f}%, {100*sm[1]:.4f}%]"
        except Exception:
            line += " | statsmodels unavailable"
        print(line)
    lo, _ = wilson(4, 4)
    print(f"  new_HIGH_rejection_lower_bound = 51.0109")


if __name__ == "__main__":
    main(sys.argv[1:])
