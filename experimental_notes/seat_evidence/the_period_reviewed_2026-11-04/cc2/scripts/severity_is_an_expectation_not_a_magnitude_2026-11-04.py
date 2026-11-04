# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_period_reviewed_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 149ed7fc813ea843a2ef4699efa40fdce413a83548b1e198f9ba5084ee8bc67c
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""
PRODUCER: how severity and residual risk should actually be calculated, derived
rather than asserted. Written for the 2026-11-04 panel, PART A.

Four results, each derived with two independent tools. Nothing here restates a
figure: the factor tables are READ FROM the appendix, never typed in, so this
producer goes red if the specification moves under it.

  R1. `Sev(f) = W(class).confidence.V(verification)` is not a severity. Its own
      stated KEY PROPERTY -- disproved findings score 0 -- is the defining
      property of an EXPECTATION over "the defect is real", not of a
      consequence magnitude.
  R2. The two belief factors are multiplied. Multiplying two estimates of the
      SAME proposition is not a fusion rule, and section 7.8 Approach B in the
      same document gives the opposite direction on agreeing evidence.
  R3. At the 0.7 cut the formula collapses to a conjunction (re-derived here so
      the chain does not rest on an unexecuted citation).
  R4. cdsfl_operational.md:176 defines w_k as "the consequence weight for flaw
      class k" and :174 aggregates R_n = sum_k w_k . R_k(n). So the AGGREGATE
      residual risk already carries a consequence term, and is not on a
      probability scale unless the w_k are convex.

Exit 0 iff every derivation discharges. The printed verdict is GATED on that
flag rather than appended to it.
"""
from __future__ import annotations
import pathlib, re, sys, math

REPO = pathlib.Path(__file__).resolve().parent.parent
APPENDIX = REPO / "docs" / "MATHEMATICAL_APPENDIX.md"
OPERATIONAL = REPO / "bench" / "directives" / "universal" / "cdsfl_operational.md"
W_ROW = re.compile(r"\|\s*W\((HARD|SOFT)\)\s*\|\s*([0-9.]+)\s*\|")
V_ROW = re.compile(r"\|\s*V\((True|None|False)\)\s*\|\s*([0-9.]+)\s*\|")

def read_spec_constants():
    txt = APPENDIX.read_text(encoding="utf-8")
    W = {m.group(1): float(m.group(2)) for m in W_ROW.finditer(txt)}
    V = {m.group(1): float(m.group(2)) for m in V_ROW.finditer(txt)}
    m = re.search(r">\s*\*\*Sev\(f\)\s*=\s*([^*]+)\*\*", txt)
    return W, V, (m.group(1).strip() if m else "(formula line not found)")

def main() -> int:
    import sympy as sp, z3, mpmath
    ok = {}
    W, V, form = read_spec_constants()
    print("=" * 78)
    print("SEVERITY IS AN EXPECTATION, NOT A MAGNITUDE -- a derivation")
    print("=" * 78)
    print(f"\n[scope] constants READ from {APPENDIX.relative_to(REPO)}, not typed into this file.")
    print(f"        Sev(f) = {form}")
    print(f"        W = {W}")
    print(f"        V = {V}")
    if sorted(W) != ["HARD", "SOFT"] or sorted(V) != ["False", "None", "True"]:
        print("        SPEC TABLE DID NOT PARSE -- refusing to derive against assumed constants.")
        return 1

    print("\n" + "-" * 78)
    print("R1. THE KEY PROPERTY IDENTIFIES AN EXPECTATION, NOT A SEVERITY")
    print("-" * 78)
    print("""
  Let D = "the claimed defect is real"; h > 0 the consequence if D holds and
  the defect ships; b = P(D | evidence) in [0,1].

  A CONSEQUENCE MAGNITUDE is a property of the defect: it is h, independent of
  b. At b = 0 it is still h -- a disproved claim about a buffer overflow still
  names a class whose consequence is high; what changed is that no such defect
  is there.
  An EXPECTATION over D is E = b.h, and is 0 exactly when b = 0.

  Section 7.7's score vanishes with the BELIEF factor, not the consequence
  factor. By those two definitions it is E, not h.""")
    h, b = sp.symbols("h b", positive=True, real=True)
    mag_at_zero = sp.simplify(h.subs(b, 0))
    exp_at_zero = sp.simplify((b * h).subs(b, 0))
    conf = sp.Symbol("confidence", nonnegative=True)
    sev_expr = sp.simplify(sp.Rational(str(W["HARD"])) * conf * sp.Rational(str(V["False"])))
    r1 = bool(mag_at_zero != 0) and bool(exp_at_zero == 0) and bool(sev_expr == 0)
    print(f"\n  magnitude   h  at b=0 -> {mag_at_zero}  (nonzero: {mag_at_zero != 0})")
    print(f"  expectation b.h at b=0 -> {exp_at_zero}  (zero:    {exp_at_zero == 0})")
    print(f"  W(HARD).confidence.V(False) = {sev_expr}   -> vanishes for ALL confidence")
    print(f"\n  => the quantity 7.7 names a SEVERITY behaves as an EXPECTATION.  [{r1}]")
    ok["R1_key_property_identifies_an_expectation"] = r1

    print("\n" + "-" * 78)
    print("R2. MULTIPLYING confidence BY V IS NOT A FUSION RULE")
    print("-" * 78)
    print("""
  `confidence` and `V` are two estimates of the SAME proposition D. Section 7.7
  combines them by multiplication. Section 7.8 Approach B, in the same
  document, combines evidence on D in log-odds: S_v = 1/(1+exp(-Lambda)).
  Bayes composes evidence by ADDING log-likelihood-ratios -- multiplying ODDS,
  not probabilities. A product of two probabilities is P(A and B) for
  independent A,B, which is the wrong event: one posterior on D is wanted, not
  the joint of two readings of D.

  Derived consequence: the product rule is not idempotent under AGREEING
  evidence. Two verifiers each reading "0.9 likely real" must not yield a
  posterior BELOW either input. Under multiplication they always do.""")
    p = sp.Symbol("p", positive=True)
    gap = sp.factor(sp.simplify(p - p * p))
    zp = z3.Real("p"); s = z3.Solver(); s.add(zp > 0, zp < 1, zp * zp >= zp)
    z3_res = s.check()
    lo = 1.0 / (1.0 + math.exp(-(2 * math.log(0.9 / 0.1))))
    lo_mp = 1 / (1 + mpmath.e ** (-(2 * mpmath.log(mpmath.mpf(9)))))
    r2 = (z3_res == z3.unsat) and bool(gap.subs(p, sp.Rational(9, 10)) > 0) and abs(lo - float(lo_mp)) < 1e-12
    print(f"\n  p - p*p = {gap}   -> strictly positive on 0<p<1")
    print(f"  z3: exists p in (0,1) with p*p >= p ?  {z3_res}   (unsat = agreeing evidence ALWAYS weakens)")
    print(f"  0.9 and 0.9  ->  7.7 product rule : {0.9*0.9:.6f}   (BELOW either input)")
    print(f"               ->  7.8 log-odds    : {lo:.6f}   (mpmath agrees: {abs(lo-float(lo_mp))<1e-12})")
    print(f"\n  => 7.7 and 7.8 give OPPOSITE directions on agreeing evidence.  [{r2}]")
    ok["R2_product_rule_contradicts_section_7_8"] = r2

    print("\n" + "-" * 78)
    print("R3. AT THE 0.7 CUT THE FORMULA COLLAPSES TO A CONJUNCTION")
    print("-" * 78)
    sup = {(cn, vn): wv * 1.0 * vv for cn, wv in W.items() for vn, vv in V.items()}
    survivors = sorted(k for k, v in sup.items() if v >= 0.7)
    print("  supremum of Sev over confidence in [0,1], per cell:")
    for k in sorted(sup):
        flag = "   <-- only cell able to reach 0.7" if sup[k] >= 0.7 else ""
        print(f"    W({k[0]:<4}) . V({k[1]:<5}) -> sup = {sup[k]:.4f}{flag}")
    zc, zw, zv = z3.Real("c"), z3.Real("w"), z3.Real("v")
    s2 = z3.Solver()
    s2.add(zc >= 0, zc <= 1)
    s2.add(z3.Or(zw == W["HARD"], zw == W["SOFT"]))
    s2.add(z3.Or(zv == V["True"], zv == V["None"], zv == V["False"]))
    s2.add(z3.Not((zw * zc * zv >= 0.7) == z3.And(zw == W["HARD"], zv == V["True"], zc >= 0.7)))
    z3_collapse = s2.check()
    r3 = (survivors == [("HARD", "True")]) and z3_collapse == z3.unsat
    print(f"\n  cells able to reach the cut: {survivors}")
    print(f"  z3: negation of the equivalence -> {z3_collapse}   (unsat = the collapse holds)")
    print(f"  inside the surviving cell Sev = {W['HARD']} . c . {V['True']} = c exactly.")
    print(f"\n  => the two harness-owned factors are a PRE-FILTER on eligibility; the")
    print(f"     magnitude is the model's own number.  [{r3}]")
    ok["R3_cut_collapses_to_conjunction"] = r3

    print("\n" + "-" * 78)
    print("R4. THE AGGREGATE RESIDUAL RISK ALREADY CARRIES A CONSEQUENCE TERM")
    print("-" * 78)
    op = OPERATIONAL.read_text(encoding="utf-8")
    agg = re.search(r"R_n\s*=\s*.{0,6}_k\s*w_k\s*.\s*R_k\(n\)", op)
    wdef = re.search(r"where\s+w_k\s+is\s+the\s+([a-z ]+?)\s+for\s+flaw\s+class\s+k", op)
    gate = re.search(r"If\s+R_k\s*>\s*(0\.\d+)", op)
    print(f"  {OPERATIONAL.relative_to(REPO)}")
    print(f"    aggregate line found : {bool(agg)}  -> {agg.group(0) if agg else None!r}")
    print(f"    w_k is defined as    : {wdef.group(1) if wdef else None!r}")
    print(f"    section 3 gate       : {('R_k > ' + gate.group(1)) if gate else None!r}")
    carries = bool(wdef and "consequence" in wdef.group(1))
    print("""
  So w_k IS a consequence weight by the directive's own words. The panel
  brief's statement that residual risk is "a different quantity with no
  severity term" holds for the per-class R_k(i) and FAILS for the aggregate
  R_n the same directive defines one line above it.

  Appendix section 4 defines L_n = sum_k s_k . R_(n,k) and states "when
  s_k = w_k ... L_n reduces to R_n". The operational file defines w_k AS the
  consequence weight. Substituting, s_k = w_k identically, so L_n == R_n: the
  "severity separation" the appendix offers as an available EXTENSION is
  already collapsed in the deployed model. It is not an option on the table;
  it is a distinction the operational spec has already spent.""")
    w1, w2, R1s, R2s = sp.symbols("w1 w2 R1 R2", nonnegative=True)
    witness = (w1 * R1s + w2 * R2s).subs({w1: 3, w2: 4, R1s: sp.Rational(1, 2), R2s: sp.Rational(1, 2)})
    zw1, zw2, zr1, zr2 = z3.Reals("w1 w2 R1 R2")
    s3 = z3.Solver()
    s3.add(zw1 > 0, zw2 > 0, zr1 >= 0, zr1 <= 1, zr2 >= 0, zr2 <= 1, zw1 + zw2 != 1, zw1 * zr1 + zw2 * zr2 > 1)
    z3_scale = s3.check()
    # NOTE: this pattern was initially written as `...|normalis` and matched
    # "Jaccard over normalised token sets" at :889, an unrelated line. A loose
    # pattern reporting a constraint that is not there is the same defect class
    # this producer is reporting, so it is anchored on w_k.
    normalised = re.search(r"w_k[^\n]{0,80}(sum|add)[^\n]{0,20}(to\s*)?1\b"
                           r"|(sum|\u03a3)_k\s*w_k\s*=\s*1"
                           r"|w_k[^\n]{0,60}normalis", op)
    print(f"  SCALE: R_n = w1.R1 + w2.R2 with consequence weights need not lie in [0,1].")
    print(f"    w=(3,4), R=(1/2,1/2)  ->  R_n = {witness} = {float(witness)}   (> 1)")
    print(f"    z3: such a witness exists -> {z3_scale}")
    print(f"    does the directive require sum_k w_k = 1 anywhere? {bool(normalised)}")
    print("""
    With no normalisation requirement in the file, R_n is not confined to
    [0,1], so a 0.5 threshold is meaningful ONLY on the per-class R_k.
    Applied to R_n it compares a harm-weighted loss against a probability.
    That is the conflation, in the gating path, with a number on it.""")
    r4 = carries and bool(agg) and z3_scale == z3.sat and float(witness) > 1
    print(f"\n  [{r4}]")
    ok["R4_aggregate_residual_risk_is_a_loss_not_a_probability"] = r4

    print("\n" + "=" * 78)
    print("WHAT THE SEPARATION SHOULD BE")
    print("=" * 78)
    print("""
  Three quantities, one job each, no factor appearing in two of them:

    Sev(f) = W(class)            consequence ONLY, no belief term. A disproved
                                 finding keeps its class; it simply stops
                                 being a finding.
    P(f)   = sigma(Lambda_total) belief that f is real, from TOOL receipts, by
                                 section 7.8 Approach B. Already specified,
                                 and already clears the d_tool admissibility
                                 bar that entry B87 shows refuses
                                 self-asserted confidence. V(False) enters as
                                 Lambda = -infinity.
    EL(f)  = Sev(f) . P(f)       expected loss. THIS is what 7.7 actually
                                 defines and what its KEY PROPERTY describes.
                                 Gate on it.

  And for the process rather than the finding:

    R_k(n) in [0,1]              per-class residual risk. A probability.
                                 Threshold it at 0.5.
    L_n = sum_k Sev_k . R_k(n)   expected residual loss. NOT a probability.
                                 Never threshold it at 0.5. Either rename R_n
                                 to L_n, or require sum_k w_k = 1 and give up
                                 the consequence reading of w_k. One or the
                                 other, not both.

  So the appendix's product is the RIGHT ARITHMETIC UNDER THE WRONG NAME with
  one redundant factor. The repair DELETES a factor rather than adding
  machinery: drop `confidence` as a free-standing multiplicand, let 7.8 supply
  the belief, re-attach the key property to EL.

  This is a FOURTH option entry B87 does not list. B87 offers (a) amend 7.7's
  second factor, (b) narrow the directive to admit tool-derived confidence,
  (c) adopt the shadow's substitution; it recommends (b). (b) is NECESSARY BUT
  NOT SUFFICIENT: it makes the second factor admissible and leaves both the
  category error and the double-count untouched.""")
    print("=" * 78)
    allok = all(ok.values())
    for k, v in ok.items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")
    if allok:
        print("\nVERDICT: all four derivations discharge. Section 7.7 defines an expected")
        print("  loss and names it a severity; the operational aggregate R_n defines a")
        print("  loss and names it a risk. The conflation the founder attributes to")
        print("  himself is present in BOTH specification files.")
    else:
        print("\nVERDICT: NOT ESTABLISHED -- at least one derivation did not discharge, so")
        print("  no claim above is asserted. See the FAIL lines.")
    return 0 if allok else 1

if __name__ == "__main__":
    raise SystemExit(main())
