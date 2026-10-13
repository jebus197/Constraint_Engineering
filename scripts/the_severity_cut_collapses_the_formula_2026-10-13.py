#!/usr/bin/env python3
"""At a 0.7 cut, Sev(f) = W.confidence.V collapses to a conjunction. Derived.

FREE PANEL, 2026-10-13, ITEM 1. Answers the 2 questions the brief left open, by
derivation rather than judgement.

THE PROPOSAL UNDER ATTACK: collect `confidence` and a HARD/SOFT class from the
model, have the harness compute Sev(f) = W(class) . confidence . V(verification)
per docs/MATHEMATICAL_APPENDIX.md section 7.7, keep the cut at
CRITICAL_SEVERITY_THRESHOLD = 0.7, and require the model to PROVE its own
arithmetic the way `_validate_rk_computation` re-derives R_k. The claim attached:
"2 of the 3 factors become harness-owned, and the one the model supplies is
multiplied by a factor the harness can set to zero", therefore "the opposite of
a vote".

RESULT 1 -- THE CUT IS UNREACHABLE IN 5 OF THE 6 CELLS. W in {1.0, 0.5}, V in
{1.0, 0.5, 0.0}, confidence the only continuous factor, bounded in [0,1].
Suprema over confidence: (HARD,True) 1; (HARD,None) 1/2; (HARD,False) 0;
(SOFT,True) 1/2; (SOFT,None) 1/4; (SOFT,False) 0. So at a 0.7 cut

    Sev(f) >= 0.7   IS   HARD  AND  CONFIRMED  AND  confidence >= 0.7

as an identity over the whole domain: z3 returns unsat for the negation of the
equivalence, and SymPy agrees cell by cell. Both run below.

RESULT 2 -- INSIDE THE SURVIVING CELL, Sev IS THE ASSERTED NUMBER. On W=1, V=1
the product reduces to `confidence` identically (d Sev/d confidence = 1; z3
finds no 2 distinct confidences with equal severity, so the map is injective).
The 2 harness-owned factors are a CONJUNCTIVE PRE-FILTER on eligibility and
place no constraint on magnitude. ANSWER TO HIS SECOND QUESTION: multiplying by
harness-owned factors makes it a QUIETER vote, not a different kind of thing --
the same vote over a smaller population. "Opposite of a vote" overstates by
exactly one factor, and it is the factor the appendix leaves model-asserted.

RESULT 3 -- WHAT THE 25-POINT MOVEMENT IS NOT EVIDENCE OF. Every entry that
crosses downward does so because V < 1, NECESSARILY: sev >= 0.7 with sev.V < 0.7
forces V < 1. So the movement measures one quantity -- how many findings the
live gate calls critical that no tool has verified -- and carries no information
about whether 0.7 is well calibrated. The cut must move if and only if one wants
an UNVERIFIED finding to be able to be critical, which is the opposite of this
project's founding principle. Keeping 0.7 is that principle written as a number;
the 25 points are its intended consequence, not an artefact.

RESULT 4 -- THE DEFAULT RULE INVERTS, AND THE PROPOSAL INHERITS IT SILENTLY.
The brief calls HARD/SOFT "existing project vocabulary". That vocabulary carries
a default: cdsfl_core.txt section 1, `class(c) = HARD if c is ambiguous`,
conservative where written. In section 7.7 it inverts -- Sev(HARD) > Sev(SOFT)
strictly for every confidence > 0 (z3: unsat for the negation) -- so
ambiguous -> HARD INFLATES severity. In the severity context the conservative
default is SOFT.

RESULT 5 -- THE PROOF STEP REPRODUCES A DEFECT ALREADY MEASURED HERE.
`scripts/severity_proof_gaming_2026-10-12.py` establishes that
`_validate_rk_computation` recomputes R_k from the model's OWN STATED inputs
with nothing cross-checking those inputs against any registry fact, so an
invented-but-consistent block PASSES. A "proof of W . confidence" has the same
shape and is weaker still, being one multiplication. Re-deriving a model's
arithmetic from the model's own premises checks arithmetic, not truth.

WHAT TO DO INSTEAD, and it is already in the appendix. The factor that must stop
being model-asserted is `confidence`, and section 7.8 Approach B supplies a
harness-owned replacement computed from verifier outcomes,
S_v = 1 / (1 + exp(-Lambda_total)), listed in the appendix's own status table as
"Ready for implementation". Sev(f) = W . S_v . V contains no model-asserted
number and is the form that earns the phrase. Note also that the V half of the
brief's proposal is ALREADY BUILT and tested:
`FindingRegistry.severity_spec_shadow` (bench/reference_runner_v3.py:3119),
wired into round telemetry at :10010, with an anti-dead-code assertion in
bench/tests/test_the_severity_specification_shadow_2026-10-12.py.

Usage: python3 scripts/the_severity_cut_collapses_the_formula_2026-10-13.py
"""
import collections
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
CUT = 0.7
VERIFIED = {"CONFIRMED"}
DISPROVED = {"REFUTED"}
CLASS_FIELDS = ("constraint_class", "hard_soft", "severity_class", "class")


def entries():
    for fp in LOGS.glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                 # noqa: BLE001
            continue
        for cid, e in (((d or {}).get("registry") or {}).get("entries") or {}).items():
            if isinstance(e, dict):
                yield fp, cid, e


def v_factor(entry: dict) -> float:
    v = str(entry.get("falsifier_verdict") or "").strip().upper()
    return 1.0 if v in VERIFIED else (0.0 if v in DISPROVED else 0.5)


def derive_with_sympy():
    import sympy as sp
    c = sp.Symbol("c", nonnegative=True)
    cut = sp.Rational(7, 10)
    Ws = {"HARD": sp.Integer(1), "SOFT": sp.Rational(1, 2)}
    Vs = {"True": sp.Integer(1), "None": sp.Rational(1, 2), "False": sp.Integer(0)}
    cells = {}
    for wn, wv in Ws.items():
        for vn, vv in Vs.items():
            sup = sp.simplify(wv * vv)
            need = sp.solve(sp.Eq(wv * c * vv, cut), c)
            cells[(wn, vn)] = {"sup": sup, "reaches": bool(sup >= cut),
                               "need": (need[0] if need else None),
                               "feasible": bool(need and 0 <= need[0] <= 1)}
    return {"cells": cells, "reduced": sp.simplify(Ws["HARD"] * c * Vs["True"]),
            "deriv": sp.diff(Ws["HARD"] * c * Vs["True"], c)}


def derive_with_z3():
    from z3 import Solver, Real, Reals, RealVal, Or, And, Not, unsat
    cut = RealVal(7) / 10
    W, c, V, S = Reals("W c V S")
    base = [Or(W == 1, W == RealVal(1) / 2),
            Or(V == 1, V == RealVal(1) / 2, V == 0),
            c >= 0, c <= 1, S == W * c * V]
    out = {}
    s = Solver(); s.add(base); s.add(V != 1, S >= cut)
    out["unverified_can_be_critical"] = (s.check() != unsat)
    s = Solver(); s.add(base); s.add(W == RealVal(1) / 2, S >= cut)
    out["soft_can_be_critical"] = (s.check() != unsat)
    s = Solver(); s.add(base); s.add(Not((S >= cut) == And(W == 1, V == 1, c >= cut)))
    out["cut_is_the_conjunction"] = (s.check() == unsat)
    c1, c2 = Reals("c1 c2")
    s = Solver(); s.add(c1 >= 0, c1 <= 1, c2 >= 0, c2 <= 1, c1 != c2,
                        RealVal(1) * c1 * RealVal(1) == RealVal(1) * c2 * RealVal(1))
    out["sev_injective_in_confidence"] = (s.check() == unsat)
    cc = Real("cc"); s = Solver(); s.add(cc > 0, cc <= 1)
    s.add(Not(RealVal(1) * cc * RealVal(1) > (RealVal(1) / 2) * cc * RealVal(1)))
    out["hard_strictly_exceeds_soft"] = (s.check() == unsat)
    return out


def ci(k: int, n: int):
    if n == 0:
        return None
    from statsmodels.stats.proportion import proportion_confint
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    cl, ch = proportion_confint(k, n, alpha=0.05, method="beta")
    import mpmath as mp
    mp.mp.dps = 50
    z = mp.mpf("1.959963984540054235524594430520551527955899076163")
    p = mp.mpf(k) / mp.mpf(n); nn = mp.mpf(n)
    den = 1 + z ** 2 / nn
    centre = (p + z ** 2 / (2 * nn)) / den
    half = (z / den) * mp.sqrt(p * (1 - p) / nn + z ** 2 / (4 * nn ** 2))
    mpl, mph = float(centre - half), float(centre + half)
    return {"p": k / n, "wilson": (wl, wh), "cp": (cl, ch),
            "agree": abs(mpl - wl) < 1e-9 and abs(mph - wh) < 1e-9}


def main() -> int:
    answer_help(__doc__, __file__)
    print("=" * 78)
    print("PART 1 -- DERIVATION (SymPy, then z3 independently)")
    print("=" * 78)
    d = derive_with_sympy()
    print("\nSymPy, supremum of Sev over confidence in [0,1], per section-7.7 cell:")
    for (wn, vn), r in d["cells"].items():
        tag = "REACHES 0.7" if r["reaches"] else "cannot reach 0.7"
        need = r["need"]
        ns = ("confidence required = %s%s" % (need, "" if r["feasible"] else "  INFEASIBLE (>1)")
              if need is not None else "product identically 0")
        print(f"  W={wn:5s} V={vn:5s}  sup = {str(r['sup']):4s}  {tag:17s}  {ns}")
    print(f"\n  on the surviving cell (HARD, CONFIRMED): Sev = {d['reduced']}"
          f"    d Sev/d confidence = {d['deriv']}")
    z = derive_with_z3()
    print("\nz3, same claims, independently, over the reals:")
    print(f"  a non-CONFIRMED finding can be critical          : "
          f"{z['unverified_can_be_critical']}   (False = unsat = impossible)")
    print(f"  a SOFT finding can be critical                   : "
          f"{z['soft_can_be_critical']}   (False = unsat = impossible)")
    print(f"  'Sev>=0.7' IS 'HARD and CONFIRMED and conf>=0.7' : "
          f"{z['cut_is_the_conjunction']}   (True = negation unsat = identity)")
    print(f"  Sev injective in confidence on that cell         : "
          f"{z['sev_injective_in_confidence']}   (True = Sev IS the asserted number)")
    print(f"  Sev(HARD) > Sev(SOFT) for every confidence > 0   : "
          f"{z['hard_strictly_exceeds_soft']}   (True = ambiguous->HARD inflates)")
    sympy_agrees = all(not r["reaches"] for (wn, vn), r in d["cells"].items()
                       if not (wn == "HARD" and vn == "True"))
    print(f"\n  SymPy and z3 agree on every cell: "
          f"{sympy_agrees and not z['unverified_can_be_critical'] and not z['soft_can_be_critical']}")

    print()
    print("=" * 78)
    print("PART 2 -- THE ARCHIVE, AND WHAT THE MOVEMENT ACTUALLY MEASURES")
    print("=" * 78)
    by_v = collections.Counter()
    n = crit_asserted = crit_spec = crossed = crossed_nonconf = 0
    conf_present = class_present = 0
    for _fp, _cid, e in entries():
        sev = e.get("severity")
        if not isinstance(sev, (int, float)):
            continue
        n += 1
        v = v_factor(e)
        by_v[v] += 1
        if e.get("confidence") is not None:
            conf_present += 1
        if any(str(e.get(f) or "").strip().upper() in {"HARD", "SOFT"} for f in CLASS_FIELDS):
            class_present += 1
        shadow = float(sev) * v
        if float(sev) >= CUT:
            crit_asserted += 1
            if shadow < CUT:
                crossed += 1
                if v < 1.0:
                    crossed_nonconf += 1
        if shadow >= CUT:
            crit_spec += 1
    if n == 0:
        print("\n  no archived entries with a numeric severity in this clone")
        return 3

    print(f"\n  archived entries with a numeric severity : {n}")
    print(f"    carrying a `confidence` field          : {conf_present}")
    print(f"    carrying a HARD/SOFT class             : {class_present}")
    print("\n  section-7.7 V, from the harness's own falsifier verdict:")
    for v, lab in ((1.0, "V=1.0 CONFIRMED"), (0.5, "V=0.5 not assessed"),
                   (0.0, "V=0.0 REFUTED")):
        k = by_v.get(v, 0)
        print(f"    {lab:22s} {k:5d}   {100.0 * k / n:7.4f}%")
    print("\n  critical population, asserted float vs the V factor applied:")
    for lab, k in (("asserted severity >= 0.7", crit_asserted),
                   ("severity . V       >= 0.7", crit_spec),
                   ("crossed downward", crossed)):
        s = ci(k, n)
        print(f"    {lab:26s} {k:5d}/{n} = {100 * s['p']:7.4f}%"
              f"   Wilson [{100 * s['wilson'][0]:7.4f}%, {100 * s['wilson'][1]:7.4f}%]"
              f"  CP [{100 * s['cp'][0]:7.4f}%, {100 * s['cp'][1]:7.4f}%]"
              f"  mpmath agrees: {s['agree']}")
    print(f"\n  of the {crossed} crossing downward, how many have V < 1 : "
          f"{crossed_nonconf} ({100.0 * crossed_nonconf / max(crossed, 1):.4f}%)")
    print("  THIS IS A TAUTOLOGY, NOT A FINDING, and that is the point.")
    print(f"\n  upper bound on the FULL section-7.7 critical set over the uncollected W:")
    print(f"    W=HARD everywhere (most generous) : {crit_spec}")
    print(f"    so the full-formula count lies in [0, {crit_spec}]; W can only REDUCE it.")
    print("    Collecting the class cannot restore any entry V already removed.")

    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    print("""
  1. At the 0.7 cut, section 7.7 does not re-rank findings. It PARTITIONS them
     by the harness's falsifier verdict and applies the model's own number
     inside the CONFIRMED block. Derived, 2 tools agreeing.
  2. "Opposite of a vote" holds for ELIGIBILITY and fails for MAGNITUDE.
  3. The cut does not need to move to make the formula right -- only if an
     unverified finding should be able to be critical.
  4. Section 1's `ambiguous -> HARD` default inflates severity here. In this
     context the conservative default is SOFT.
  5. The remaining model-asserted factor is `confidence`; section 7.8
     Approach B already specifies the harness-owned replacement.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
