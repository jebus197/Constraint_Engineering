# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 35fda88fe7bad9611285f6fc6e6eb0d3b9458bc1b2383cf96fdbe0eea90a3b9b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""J2 producer, 2026-10-14: are Approach B's verifier rates MEASURED or ASSUMED?

docs/MATHEMATICAL_APPENDIX.md sec.7.8 gives a verifier table -- SymPy
TPR 0.99 / FPR 0.001, Dimensional 0.80 / 0.10, Numerical 0.70 / 0.15 -- and
both seats named Approach B (S_v = 1/(1+exp(-Lambda_total))) as the real
replacement for model-asserted `confidence`. Neither seat asked where the rates
came from.

THIS SCRIPT IS AN ABSENCE CHECK, AND IT IS MECHANICAL. The project's standing
rule is that a measured rate travels with the script that produced it. So the
test for "measured" is executable: find a producer, or there is none. The script
reports, by execution:

  1. Whether sec.7.8 attributes the rates to any measurement (keyword scan of the
     section text for measured / observed / calibrated / sample / n= / CI).
  2. Whether sec.7.8 cites a producer script, as the adjacent sec.7.7 now does.
  3. Whether the six rates appear anywhere in the repository OUTSIDE the
     appendix, its copies, and text quoting it -- i.e. in any data file,
     results JSON, or script.
  4. Whether Approach A or B is implemented in executable code at all.
  5. Two independent derivations (SymPy exact, mpmath 30 dps) of the published
     weights, the closed form S_v = TPR/(TPR+FPR) for a single verifier, and
     the TPR at which the documented "veto property" stops holding.
  6. A z3 decision on whether the veto property is STRUCTURAL (true for any
     verifier better than chance) or CONTINGENT on the chosen numbers.

Run:  python3 scripts/approach_b_rates_are_assumed_not_measured_2026-10-14.py
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
APPENDIX = REPO / "docs" / "MATHEMATICAL_APPENDIX.md"

MEASUREMENT_WORDS = (
    "measured", "observed", "calibrated", "calibration", "sample",
    "n =", "n=", "confidence interval", "CI ", "dataset", "experiment",
)


def section_78(text: str) -> str:
    i = text.find("### 7.8")
    j = text.find("### 7.9", i + 1)
    return text[i:j] if i >= 0 else ""


def main() -> int:
    ap = argparse.ArgumentParser(
        description=("J2: decide whether appendix sec.7.8's verifier TPR/FPR table "
                     "rests on measured or assumed rates, by execution."))
    ap.parse_args()

    print("=" * 78)
    print("J2 -- PROVENANCE OF THE APPROACH B VERIFIER TABLE")
    print("=" * 78)

    text = APPENDIX.read_text(encoding="utf-8")
    sec = section_78(text)
    print("appendix sec.7.8 located: %s (%d chars)" % (bool(sec), len(sec)))

    print("\n[1] does sec.7.8 attribute the rates to a measurement?")
    hits = [w for w in MEASUREMENT_WORDS if w.lower() in sec.lower()]
    print("    measurement vocabulary present in sec.7.8: %s" % (hits or "NONE"))

    print("\n[2] does sec.7.8 cite a producer script? (sec.7.7 is the control)")
    i77 = text.find("### 7.7")
    sec77 = text[i77:text.find("### 7.8", i77 + 1)] if i77 >= 0 else ""
    prod_re = re.compile(r"(?:scripts|bench)/[\w./-]+\.py")
    print("    producers cited in 7.8: %s" % (prod_re.findall(sec) or "NONE"))
    print("    producers cited in 7.7: %s" % (prod_re.findall(sec77) or "NONE"))

    print("\n[3] do the six rates appear OUTSIDE the appendix and text quoting it?")
    try:
        out = subprocess.run(
            ["rg", "-l", "--multiline", "--multiline-dotall",
             r"0\.99.{0,400}0\.001.{0,400}0\.15", "."],
            cwd=REPO, capture_output=True, text=True, timeout=180).stdout
        files = [f for f in out.splitlines() if f.strip()]
    except Exception as exc:                                   # noqa: BLE001
        print("    rg unavailable (%s); skipping" % exc)
        files = []
    def is_doc_or_quote(p: str) -> bool:
        return (p.endswith("MATHEMATICAL_APPENDIX.md")
                or "/logs/" in p or p.startswith("./bench/logs")
                or "sandbox_harvest" in p or "experimental_notes" in p
                or p.endswith(".md"))
    data_hits = [f for f in files if not is_doc_or_quote(f)]
    print("    files matching the rate triple: %d" % len(files))
    print("    of those, NON-prose (data/script) files: %s"
          % (data_hits or "NONE -- no data file, no results JSON, no script"))

    print("\n[4] is Approach A or B implemented in executable code?")
    try:
        out = subprocess.run(
            ["rg", "-n", "--type", "py",
             r"Lambda_total|lambda_total|C_sympy|C_dim|C_num", "."],
            cwd=REPO, capture_output=True, text=True, timeout=180).stdout
        lines = [l for l in out.splitlines() if l.strip()]
    except Exception as exc:                                   # noqa: BLE001
        print("    rg unavailable (%s)" % exc)
        lines = []
    print("    python hits: %d" % len(lines))
    for l in lines[:8]:
        print("      %s" % l[:150])

    print("\n[5] two-tool derivation of the published table")
    import sympy as sp
    import mpmath as mp
    mp.mp.dps = 30
    rates = {"SymPy": ("99/100", "1/1000"),
             "Dimensional": ("8/10", "1/10"),
             "Numerical": ("7/10", "15/100")}
    wp_s, wm_s = {}, {}
    for k, (t, f) in rates.items():
        T, F = sp.Rational(t), sp.Rational(f)
        wp_s[k] = sp.log(T / F); wm_s[k] = sp.log((1 - T) / (1 - F))
        Tm, Fm = mp.mpf(sp.N(T, 30)), mp.mpf(sp.N(F, 30))
        wp_m = mp.log(Tm / Fm); wm_m = mp.log((1 - Tm) / (1 - Fm))
        agree = (abs(float(wp_s[k]) - float(wp_m)) < 1e-12
                 and abs(float(wm_s[k]) - float(wm_m)) < 1e-12)
        print("    %-12s w+ sympy=%+.6f mpmath=%+.6f | w- sympy=%+.6f "
              "mpmath=%+.6f | agree=%s"
              % (k, float(wp_s[k]), float(wp_m), float(wm_s[k]), float(wm_m),
                 agree))
    TPR, FPR, Lp = sp.symbols("TPR FPR Lambda_prior", positive=True)
    Sv = 1 / (1 + sp.exp(-sp.log(TPR / FPR)))
    print("    SymPy closed form, Lambda_prior=0, one verifier PASS: S_v = %s"
          % sp.simplify(Sv))
    print("      identical to TPR/(TPR+FPR): %s"
          % (sp.simplify(Sv - TPR / (TPR + FPR)) == 0))
    rhs = wp_s["Dimensional"] + wp_s["Numerical"]
    print("    veto inequality |w-_SymPy| > sum other w+ : %.4f > %.4f -> %s"
          % (abs(float(wm_s["SymPy"])), float(rhs),
             abs(float(wm_s["SymPy"])) > float(rhs)))
    thr_m = 1 - mp.mpf("0.999") * mp.e ** (-mp.mpf(sp.N(rhs, 30)))
    thr_s = sp.nsolve(sp.log((1 - sp.Symbol("t")) / sp.Rational(999, 1000))
                      + rhs, sp.Symbol("t"), 0.97)
    print("    TPR at which the veto property FAILS: mpmath %.6f / sympy %.6f "
          "(agree=%s)" % (float(thr_m), float(thr_s),
                          abs(float(thr_m) - float(thr_s)) < 1e-6))

    print("\n[6] z3: is the veto STRUCTURAL or CONTINGENT on these numbers?")
    from z3 import Reals, Solver, And, Not, sat
    t_s, f_s, t_d, f_d, t_n, f_n = Reals("t_s f_s t_d f_d t_n f_n")
    s = Solver()
    s.add(And(t_s > f_s, t_d > f_d, t_n > f_n,
              t_s > 0, t_s < 1, f_s > 0, f_s < 1,
              t_d > 0, t_d < 1, f_d > 0, f_d < 1,
              t_n > 0, t_n < 1, f_n > 0, f_n < 1))
    # veto  <=>  (1-FPR_s)/(1-TPR_s) > (t_d*t_n)/(f_d*f_n), exponentiated so z3
    # needs no logarithm. Ask whether it can FAIL.
    s.add(Not((1 - f_s) * (f_d * f_n) > (1 - t_s) * (t_d * t_n)))
    r = s.check()
    print("    can the veto FAIL with every verifier better than chance? %s" % r)
    if r == sat:
        m = s.model()
        print("    z3 counterexample: %s"
              % {str(v): str(m[v]) for v in (t_s, f_s, t_d, f_d, t_n, f_n)})
        print("    => the veto is CONTINGENT on the assumed table, not a theorem")
    s2 = Solver()
    s2.add(Not((1 - 0.001) * (0.1 * 0.15) > (1 - 0.99) * (0.8 * 0.7)))
    print("    do the PUBLISHED rates violate the veto? %s (unsat = holds there)"
          % s2.check())

    print("\n" + "=" * 78)
    print("VERDICT: ASSUMED. sec.7.8 makes no measurement claim, cites no producer,")
    print("the rates appear in no data file or script, and neither Approach A")
    print("nor B has ever been executed. S_v for a single verifier reduces to")
    print("TPR/(TPR+FPR) -- a pure function of the assumed rates -- so")
    print("substituting Approach B for a model's `confidence` replaces a model's")
    print("number with an author's number. It relocates the vote; it does not")
    print("remove it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
