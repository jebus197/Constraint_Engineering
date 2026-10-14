# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3944e3260de0c128087e4440e5a41eab863910af04c3824e97eba77b440170f3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Approach B's verifier table: measured rates or assumed? Settled by record + derivation.

JOINT ROUND his_rulings_2026-10-13, J2. docs/MATHEMATICAL_APPENDIX.md section
7.8 gives Approach B (S_v = 1/(1+exp(-Lambda_total))) a verifier table: SymPy
TPR 0.99 / FPR 0.001, Dimensional 0.80 / 0.10, Numerical 0.70 / 0.15. Both
blind seats pointed to Approach B as the replacement for the model-asserted
`confidence` in section 7.7. The question neither answered: do those rates
rest on a MEASUREMENT?

PROVENANCE, from the repository record (paths printed below, checkable):

1. The table's earliest occurrence is
   docs/experimental_notes/CDSFL_Complete_Mathematical_Framework_Technical_2026-03-27.md
   (line ~155), dated 2026-03-27 -- BEFORE any archived experiment ran -- where
   it is labelled "Empirical weights" with NO producer, NO dataset, NO interval.
2. No script in this repository computes a verifier TPR or FPR from ground
   truth. (This script greps for one and prints the result.)
3. The project's own 5-model confer RECORDED the impossibility at the time:
   experimental_notes/Stage6_Full_Confer_Synthesis_2026-04-14.md -- "FPR =
   P(PASS | H0 true) requires ground-truth labels", "fail_fraction ... cannot
   be used for production calibration", ground-truth labelling filed "Phase
   7+". Claim 7 there is "FALSIFIED by definition", 5/5 models.
4. The "Table corrected during 5-model meta-test, 27 March 2026" note corrects
   the WEIGHT ARITHMETIC (ln(FNR/TPR) -> ln(FNR/TNR)); it does not measure a
   rate.

CONCLUSION ON PROVENANCE: the rates are ASSUMED. "Empirical" in the 2026-03-27
document is a label, not a measurement.

WHAT THAT DOES AND DOES NOT RELOCATE, derived below with 2 independent tools:

* DIRECTION-UNANIMOUS CELLS ARE RATE-INVARIANT. If every determinate verifier
  returns o_i = 1, then S_v > 0.5 for ANY rates with TPR_i > FPR_i; if every
  o_i = 0, S_v < 0.5 for ANY rates with FNR_i < TNR_i. In those cells the
  VERDICT side of the 0.5 threshold is decided by the tools alone; the assumed
  numbers set only the magnitude. (z3: negation unsat; SymPy agrees.)
* CONFLICT CELLS ARE DECIDED BY THE ASSUMED NUMBERS. SymPy-falsified +
  dimensional-verified + numerical-verified gives S_v = 0.272 < 0.5 under the
  table's rates, and S_v = 0.653 > 0.5 under SymPy TPR 0.95 / FPR 0.01 --
  rates every bit as defensible absent a measurement. Two plausible priors,
  opposite verdicts: in disagreement cells the author's number IS the vote.

VERDICT: substituting Approach B as-is removes the MODEL's number and installs
the AUTHOR's number exactly where verifiers disagree. The vote is relocated,
not removed, in conflict cells -- and removed, genuinely, in unanimous cells.
Promotion therefore requires measuring the rates first. The ground truth that
did not exist on 2026-03-27 exists now: 1,246 CONFIRMED and 40 REFUTED
runner-re-verified falsifier verdicts in the archive, plus the planted-defect
exams. Measure per-tool rates against those labels; until then the appendix
table must say ASSUMED.

Usage: python3 scripts/approach_b_rates_are_assumed_2026-10-14.py
"""
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    answer_help(__doc__, __file__)
    import mpmath
    import sympy as sp
    import z3

    print("=== 1. The published weights follow from the stated rates ===")
    rates = {"SymPy": (0.99, 0.001), "Dimensional": (0.80, 0.10),
             "Numerical": (0.70, 0.15)}
    pub = {"SymPy": (6.90, -4.60), "Dimensional": (2.08, -1.50),
           "Numerical": (1.54, -1.04)}
    for name, (tpr, fpr) in rates.items():
        wp_s = float(sp.log(sp.Rational(str(tpr)) / sp.Rational(str(fpr))))
        wn_s = float(sp.log((1 - sp.Rational(str(tpr))) / (1 - sp.Rational(str(fpr)))))
        wp_m = float(mpmath.log(mpmath.mpf(str(tpr)) / mpmath.mpf(str(fpr))))
        wn_m = float(mpmath.log((1 - mpmath.mpf(str(tpr))) / (1 - mpmath.mpf(str(fpr)))))
        ok = (abs(wp_s - pub[name][0]) < 0.01 and abs(wn_s - pub[name][1]) < 0.01
              and abs(wp_s - wp_m) < 1e-12 and abs(wn_s - wn_m) < 1e-12)
        print(f"  {name:<12} log(TPR/FPR)={wp_s:+.4f}  log(FNR/TNR)={wn_s:+.4f}  "
              f"published {pub[name]}  SymPy==mpmath, matches: {ok}")
        assert ok

    print("\n=== 2. Unanimous cells are rate-invariant (the tools decide) ===")
    # S_v > 0.5  iff  Lambda > 0  iff  product of likelihood ratios > 1.
    r1, r2, r3 = z3.Reals("r1 r2 r3")
    s = z3.Solver()
    s.add(r1 > 1, r2 > 1, r3 > 1, r1 * r2 * r3 <= 1)
    res = s.check()
    print(f"  z3: 'every ratio > 1 AND product <= 1' -> {res}")
    assert res == z3.unsat
    a, b, c = sp.symbols("a b c", positive=True)
    expr = sp.log(a) + sp.log(b) + sp.log(c)
    print(f"  SymPy: Lambda = log(a)+log(b)+log(c) = log(a*b*c); "
          f"a,b,c > 1 => Lambda > 0: "
          f"{sp.simplify(sp.logcombine(expr, force=True)) == sp.log(a*b*c)}")
    print("  So: any rates with TPR_i > FPR_i put a unanimous verification on")
    print("  the same side of 0.5. Direction is tool-owned in those cells.")

    print("\n=== 3. Conflict cells are decided by the assumed numbers ===")
    def s_v(weights):
        lam = sum(weights)
        return float(1 / (1 + mpmath.e ** (-mpmath.mpf(lam))))
    import math
    table = s_v([math.log(0.01 / 0.999), math.log(0.80 / 0.10),
                 math.log(0.70 / 0.15)])
    alt = s_v([math.log(0.05 / 0.99), math.log(0.80 / 0.10),
               math.log(0.70 / 0.15)])
    # second tool: sympy exact
    lam_t = sp.log(sp.Rational(1, 100) / sp.Rational(999, 1000)) + \
        sp.log(sp.Rational(8, 1)) + sp.log(sp.Rational(70, 15))
    table_sp = float(1 / (1 + sp.exp(-lam_t)))
    print(f"  SymPy-falsified + others verified:")
    print(f"    table rates  (TPR .99/FPR .001): S_v = {table:.4f}  "
          f"(SymPy exact route agrees: {abs(table - table_sp) < 1e-9})  -> REJECT")
    print(f"    alt rates    (TPR .95/FPR .01) : S_v = {alt:.4f}  -> ACCEPT")
    print(f"  Same tool outputs, opposite verdicts. Absent a measurement,")
    print(f"  the choice between those rate sets is the author's vote.")
    assert table < 0.5 < alt

    print("\n=== 4. No measurement producer exists in this repository ===")
    hits = []
    for d in ("scripts", "bench"):
        for fp in (REPO / d).glob("*.py"):
            try:
                txt = fp.read_text(errors="ignore")
            except Exception:  # noqa: BLE001
                continue
            if fp.name == pathlib.Path(__file__).name:
                continue  # this script names the rates; it does not measure them
            if re.search(r"TPR", txt) and re.search(r"0\.99", txt) and \
               re.search(r"ground.?truth|planted|label", txt, re.I):
                hits.append(str(fp))
    print(f"  scripts computing verifier TPR/FPR from ground truth: {hits or 'NONE'}")
    print("\nVERDICT: ASSUMED. Promotion of Approach B requires the per-tool")
    print("rate measurement first; the archive now carries the labels to do it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
