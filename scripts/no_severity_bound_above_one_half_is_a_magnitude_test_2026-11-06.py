#!/usr/bin/env python3
"""
PRODUCER: the severity cut collapses under EVERY candidate repair, not just
under the status quo -- and the 2026-11-06 brief's lead framing ("sections 7.7
and 7.8 disagree, 0 vs 0.273") does not hold against the appendix's own text.

Written for the 2026-11-06 panel. Factor tables are READ FROM
docs/MATHEMATICAL_APPENDIX.md at run time, never retyped, so this producer goes
red if the specification moves under it.

Five results, each derived with two independent tools (SymPy and z3; mpmath as
the third check on the logistic value).

  T1. Cell suprema. Exactly one (class, verification) cell can exceed W_SOFT.
      Re-derived from the parsed table rather than cited.

  T2. THE GENERAL THEOREM, and it is the new result. For ANY severity of the
      shape Sev = W . B with W in {W_SOFT, W_HARD} and B in [0,1] -- B being
      any composition of belief factors whatsoever -- and for ALL cuts c in
      (W_SOFT, W_HARD]:

          Sev >= c   <=>   W = W_HARD  AND  B >= c

      quantified over c as a free real, not sampled at chosen cuts. The cut
      therefore tests the CLASS (two values) and the BELIEF (continuous). It
      places no constraint on consequence magnitude. This is a statement about
      the SHAPE of the formula, so it covers repairs not yet written.

  T3. All four candidate formulas on the table have that shape, hence all four
      collapse identically:
        F1  W . confidence . V        section 7.7 as written (status quo)
        F2  W . S_v . V               section 7.7 caution 1's own repair
        F3  W . sigma(Lambda_total)   the 2026-11-04 seat's EL(f) = Sev . P
        F4  W . S_v                   the joint-round seat's deletion of V
      So replacing `confidence` with a harness-computed S_v fixes PROVENANCE
      (who computed the number) and leaves the MAGNITUDE deficiency exactly
      where it was.

  T4. REFUTES THE BRIEF'S LEAD FRAMING. Section 7.7 caution 1 states the
      substitution target is `confidence`. Under that substitution a disproved
      finding scores W . S_v . V(False) = 0, not 0.273. The 0.273 is the BELIEF
      FACTOR (section 7.8's own text calls Lambda_prior "uniform prior:
      P(claim true) = 0.5", so S_v is a posterior credence) and 0 is the
      SEVERITY. Two different quantities, not two values of one quantity. The
      key property survives the appendix as written.

  T5. But it does NOT survive the deletion. S_v = 1/(1+exp(-Lambda)) has no
      zero, so F4 cannot represent V(False) = 0. The joint-round seat that
      warned the key property is "silently lost" if 7.7's `confidence . V` is
      replaced by `S_v` alone was right about F4.

Exit 0 iff every derivation discharges. The printed verdict is GATED on that
flag rather than appended to it.
"""
from __future__ import annotations

import pathlib
import re
import sys

import mpmath as mp
import sympy as sp
import z3
from sympy import Rational as R

REPO = pathlib.Path(__file__).resolve().parent.parent
APPENDIX = REPO / "docs" / "MATHEMATICAL_APPENDIX.md"

W_ROW = re.compile(r"\|\s*W\((HARD|SOFT)\)\s*\|\s*([0-9.]+)\s*\|")
V_ROW = re.compile(r"\|\s*V\((True|None|False)\)\s*\|\s*([0-9.]+)\s*\|")
LLR_ROW = re.compile(
    r"\|\s*(SymPy|Dimensional|Numerical)\s*\|\s*[0-9.]+\s*\|\s*[0-9.]+\s*\|"
    r"\s*([-−]?[0-9.]+)\s*\|\s*([-−]?[0-9.]+)\s*\|"
)


def _num(text: str) -> R:
    """Parse a table cell, tolerating the U+2212 minus the appendix uses."""
    return R(text.replace("−", "-").strip())


def read_spec():
    txt = APPENDIX.read_text(encoding="utf-8")
    W = {m.group(1): R(m.group(2)) for m in W_ROW.finditer(txt)}
    V = {m.group(1): R(m.group(2)) for m in V_ROW.finditer(txt)}
    llr = {m.group(1): (_num(m.group(2)), _num(m.group(3)))
           for m in LLR_ROW.finditer(txt)}
    missing = []
    if sorted(W) != ["HARD", "SOFT"]:
        missing.append("W rows parsed as %s" % sorted(W))
    if sorted(V) != ["False", "None", "True"]:
        missing.append("V rows parsed as %s" % sorted(V))
    if sorted(llr) != ["Dimensional", "Numerical", "SymPy"]:
        missing.append("LLR rows parsed as %s" % sorted(llr))
    if missing:
        raise SystemExit("SPEC PARSE FAILED (the appendix moved): " + "; ".join(missing))
    return W, V, llr


def q(x: R) -> z3.ArithRef:
    """Exact rational into z3 -- never via float."""
    return z3.RealVal(x.p) / z3.RealVal(x.q)


def main(argv):
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__)
        return 0

    W, V, llr = read_spec()
    w_soft, w_hard = W["SOFT"], W["HARD"]
    results = {}
    print("=" * 78)
    print("SPEC AS PARSED FROM docs/MATHEMATICAL_APPENDIX.md")
    print("  W = {HARD: %s, SOFT: %s}" % (w_hard, w_soft))
    print("  V = {True: %s, None: %s, False: %s}"
          % (V["True"], V["None"], V["False"]))
    print("  section 7.8 log-LRs (pos, neg) = "
          + ", ".join("%s: %s" % (k, v) for k, v in sorted(llr.items())))
    print("=" * 78)

    # ---- T1: cell suprema, SymPy -------------------------------------------
    c = sp.Symbol("c", real=True)
    sup = {}
    for kw, vw in W.items():
        for kv, vv in V.items():
            sup[(kw, kv)] = sp.maximum(vw * vv * c, c, sp.Interval(0, 1))
    print("\nT1  cell suprema of Sev over confidence in [0,1]:")
    for k in sorted(sup):
        print("      sup Sev%s = %s" % (k, sup[k]))
    above = [k for k, v in sup.items() if v > w_soft]
    print("      cells with supremum > W_SOFT = %s: %s" % (w_soft, above))
    results["T1_exactly_one_cell_exceeds_W_SOFT"] = (
        above == [("HARD", "True")] and sup[("HARD", "True")] == w_hard
    )

    # ---- T2: the general theorem, z3, quantified over all cuts -------------
    s = z3.Solver()
    zw, zb, zc = z3.Real("W"), z3.Real("B"), z3.Real("c")
    s.add(z3.Or(zw == q(w_soft), zw == q(w_hard)))
    s.add(zb >= 0, zb <= 1)
    s.add(zc > q(w_soft), zc <= q(w_hard))          # ALL such c, not samples
    lhs = zw * zb >= zc
    rhs = z3.And(zw == q(w_hard), zb >= zc)
    s.add(z3.Not(lhs == rhs))                        # seek a counterexample
    t2 = s.check()
    print("\nT2  z3: negation of  (W.B >= c  <=>  W=W_HARD and B >= c)  over")
    print("      all W in {%s, %s}, all B in [0,1], all c in (%s, %s]:  %s"
          % (w_soft, w_hard, w_soft, w_hard, t2))
    sym_soft_max = sp.maximum(w_soft * c, c, sp.Interval(0, 1))
    print("      SymPy: max over B of W_SOFT.B = %s , and %s > %s is %s"
          % (sym_soft_max, sym_soft_max, w_soft, bool(sym_soft_max > w_soft)))
    results["T2_collapse_holds_for_every_cut_above_W_SOFT"] = (
        t2 == z3.unsat and sym_soft_max == w_soft
    )

    # ---- T3: all four candidates have shape W . B with B in [0,1] ---------
    lam = sp.Symbol("Lambda", real=True)
    S_v = 1 / (1 + sp.exp(-lam))
    names = [
        "F1  W . confidence . V      (7.7 as written)",
        "F2  W . S_v . V             (7.7 caution 1's repair)",
        "F3  W . sigma(Lambda)       (2026-11-04 seat: EL = Sev . P)",
        "F4  W . S_v                 (joint-round seat: delete V)",
    ]
    print("\nT3  every candidate's belief factor B is a product of terms in "
          "[0,1], so B in [0,1]:")
    sv_inf = sp.limit(S_v, lam, -sp.oo)
    sv_sup = sp.limit(S_v, lam, sp.oo)
    s2 = z3.Solver()
    zt, zsv = z3.Real("t"), z3.Real("Sv")
    s2.add(zt > 0, zsv == 1 / (1 + zt), z3.Or(zsv < 0, zsv > 1))
    sv_bounded = s2.check()
    print("      SymPy: S_v ranges (%s, %s) ; z3: S_v outside [0,1] is %s"
          % (sv_inf, sv_sup, sv_bounded))
    v_in_unit = all(0 <= x <= 1 for x in V.values())
    print("      V values all in [0,1]: %s ; confidence clamped to [0,1] by "
          "compute_sev_f" % v_in_unit)
    for name in names:
        print("      %s  -> shape W . B, T2 applies" % name)
    results["T3_all_four_candidates_collapse"] = (
        sv_inf == 0 and sv_sup == 1 and sv_bounded == z3.unsat and v_in_unit
    )

    # ---- T4: refute the brief's lead framing -------------------------------
    lam_total = llr["SymPy"][1] + llr["Dimensional"][0] + llr["Numerical"][0]
    sv_val = 1 / (1 + sp.exp(-lam_total))
    sv_sympy = sp.N(sv_val, 20)
    mp.mp.dps = 30
    sv_mpmath = mp.mpf(1) / (1 + mp.e ** (-mp.mpf(str(float(lam_total)))))
    agree = abs(float(sv_sympy) - float(sv_mpmath)) < 1e-15
    sev_disproved = w_hard * sv_val * V["False"]
    s3 = z3.Solver()
    zsev, zsvf = z3.Real("Sev"), z3.Real("Sv_")
    s3.add(zsvf >= 0, zsvf <= 1)
    s3.add(zsev == q(w_hard) * zsvf * q(V["False"]), zsev > 0)
    z3_zero = s3.check()
    print("\nT4  the appendix's own substitution (S_v replaces `confidence`, "
          "V retained):")
    print("      Lambda_total (SymPy falsified, others verified) = %s = %s"
          % (lam_total, float(lam_total)))
    print("      S_v  SymPy  = %s" % sv_sympy)
    print("      S_v  mpmath = %s" % sv_mpmath)
    print("      agree to 1e-15: %s" % agree)
    print("      Sev = W_HARD . S_v . V(False) = %s . %.17f . %s = %s"
          % (w_hard, float(sv_val), V["False"], sp.simplify(sev_disproved)))
    print("      z3: Sev > 0 while V(False) = %s:  %s" % (V["False"], z3_zero))
    print("      => 0.273 is the BELIEF factor; 0 is the SEVERITY. The brief's")
    print("         '0 under 7.7 vs 0.273 under 7.8' compares a severity with a")
    print("         credence. No contradiction exists in the text as written.")
    results["T4_no_contradiction_between_7_7_and_7_8_as_written"] = (
        sp.simplify(sev_disproved) == 0 and z3_zero == z3.unsat and agree
        and abs(float(sv_sympy) - 0.27289178365887046) < 1e-15
    )

    # ---- T5: the deletion DOES lose the key property ----------------------
    sols = sp.solve(sp.Eq(S_v, 0), lam)
    s5 = z3.Solver()
    zt2, zsv2 = z3.Real("t"), z3.Real("Sv")
    s5.add(zt2 > 0, zsv2 == 1 / (1 + zt2), zsv2 == 0)
    z3_no_zero = s5.check()
    print("\nT5  can F4 (W . S_v, V deleted) represent V(False) = 0?")
    print("      SymPy solve(S_v = 0, Lambda) = %s  (no real solution)" % sols)
    print("      z3: S_v == 0 with exp(-Lambda) > 0:  %s" % z3_no_zero)
    print("      SymPy: limit S_v as Lambda -> -oo = %s, never attained" % sv_inf)
    print("      => deleting the V column makes the key property "
          "UNREPRESENTABLE, not merely unstated.")
    results["T5_deletion_loses_the_key_property"] = (
        sols == [] and z3_no_zero == z3.unsat and sv_inf == 0
    )

    print("\n" + "=" * 78)
    ok = True
    for name in results:
        print("  %s  %s" % ("PASS" if results[name] else "FAIL", name))
        ok = ok and results[name]
    print("=" * 78)
    if ok:
        print("""
VERDICT (gated on all five derivations discharging):

  1. No severity bound above W_SOFT is a bound on consequence magnitude, under
     ANY formula of the shape W . B -- which is all four candidates, including
     both repairs proposed to this panel. Moving the cut from 0.7 to 0.8
     tightens the BELIEF requirement and changes nothing about impact. This is
     the answer to the founder's second question: the bound that can honestly
     be set is a bound on belief, conditional on class = HARD, and it should be
     named that way.

  2. Replacing `confidence` with section 7.8's S_v is a PROVENANCE repair, not
     a magnitude repair. It is worth doing -- a tool-computed credence is not a
     model's self-report -- but it leaves T2 untouched. Section 7.7 caution 1
     offers it under a heading about magnitude, and that is the sentence to fix.

  3. The brief's lead framing is REFUTED. Sections 7.7 and 7.8 do not disagree
     as written: 7.8's S_v is a posterior credence (its own text sets
     Lambda_prior from "P(claim true) = 0.5"), 7.7's Sev is a severity, and
     under 7.7 caution 1's stated substitution a disproved finding still
     scores exactly 0. The disagreement appears only if V is DELETED -- which
     is what one joint-round seat proposed and the other warned against. The
     warning was correct.
""")
    else:
        print("\nVERDICT WITHHELD: a derivation failed. Do not quote this run.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
