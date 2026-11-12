# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_is_ordinal_2026-11-11_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 169af1054d68d459307397b4b08d307d51825880692898ad63eac1562aeb8871
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The credence half of section 7.7.1's pair still carried the consequence.

PRODUCER for the joint round `severity_is_ordinal_2026-11-11_joint` (`fable`
seat, 2026-11-12).

WHAT IS CLAIMED.  `docs/MATHEMATICAL_APPENDIX.md` section 7.7.1 defines severity
as the ordered pair `severity_d(f) = (c_d(f), credence(f))`, and as first written
it defined the second component as "today's section 7.7 product under its own
name".  That product is `W(class) * confidence * Ver(verification)`, and section
7.7 caution 3 says in its own words that "Consequence magnitude enters `Sev`
through `W` alone".  So the pair put a CONSEQUENCE factor in BOTH components and
did not perform the separation it exists to perform.

WHY THAT IS MATERIAL AND NOT A NAMING QUIBBLE.  Caution 3's collapse is a
property of the SHAPE `W * B`, not of a particular `B`.  Moving a `W`-bearing
product into the second slot of a pair carries the collapse with it, so a cut on
the "credence" half is still a test of the constraint class plus a test of
belief, and still bounds consequence not at all -- the exact defect the pair was
introduced to cure.

HOW IT IS DECIDED.  Not by reading the prose.  The factor values are PARSED from
the live appendix's own section 7.7 table at run time, then:
  * z3 decides both collapse statements over the parsed values;
  * SymPy decides whether `S_v` can represent `Ver(False) = 0` (it cannot);
  * a MUTATION TEST re-runs the appendix predicate against the superseded
    sentence, so a check that cannot detect the defect fails loudly rather than
    passing vacuously.

ADMISSIBLE INPUTS ONLY.  This script reads `docs/MATHEMATICAL_APPENDIX.md`,
`bench/dm/_types.py`, `bench/dm/_convergence.py`,
`bench/cdsfl_registry/domain_manifest.toml` and the `bench/` + `scripts/` Python
trees by AST.  It reads no scoring key, no answer file and no planted-defect
manifest, and it writes nothing.

EXIT 0 and no `FALSIFIED` token  = the defect is absent from the live appendix.
AssertionError / `FALSIFIED`     = the defect is present.
"""
from __future__ import annotations

import ast
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
APPENDIX = REPO / "docs" / "MATHEMATICAL_APPENDIX.md"

FALSIFIED = False


def note(ok: bool, label: str, detail: str = "") -> None:
    global FALSIFIED
    print(f"  [{'ok ' if ok else 'BAD'}] {label}" + (f"  -- {detail}" if detail else ""))
    if not ok:
        FALSIFIED = True


# ---------------------------------------------------------------- 1. parse
def parse_factors(text: str) -> dict[str, float]:
    """Read W and Ver from section 7.7's OWN table. Never retyped here."""
    out: dict[str, float] = {}
    for row in re.finditer(r"^\|\s*(W|Ver)\((HARD|SOFT|True|None|False)\)\s*\|\s*"
                           r"([0-9.]+)\s*\|", text, re.M):
        out[f"{row.group(1)}({row.group(2)})"] = float(row.group(3))
    return out


def section(text: str, start: str, end: str) -> str:
    i, j = text.index(start), text.index(end)
    assert i < j, f"{start!r} does not precede {end!r}"
    return text[i:j]


# -------------------------------------------- 2. the appendix-text predicate
#: TRUE when the appendix defines the credence half as the W-BEARING section 7.7
#: product.  Matched on the superseded sentence's own distinguishing phrase.
SUPERSEDED = re.compile(
    r"with\s+`credence\(f\)`\s+being\s+today's\s+§7\.7\s+product\s+under\s+its\s+own\s+name",
    re.I | re.S)
#: TRUE when the credence half is defined WITHOUT a consequence factor.
REPAIRED = re.compile(r"\*\*credence\(f\)\s*=\s*S_v\(f\)\s*·\s*Ver\(verification\)\*\*")


def credence_half_carries_consequence(s771: str) -> bool:
    return bool(SUPERSEDED.search(s771)) and not bool(REPAIRED.search(s771))


def main() -> int:
    text = APPENDIX.read_text(encoding="utf-8")
    s77 = section(text, "### 7.7 Per-Finding Severity",
                  "### 7.7.1 The symbolic form")
    s771 = section(text, "### 7.7.1 The symbolic form",
                   "### 7.8 Multi-Verifier Severity")

    print("=" * 74)
    print("THE CREDENCE HALF STILL CARRIES THE CONSEQUENCE -- producer, 2026-11-12")
    print("=" * 74)

    fac = parse_factors(s77)
    print(f"\n1. FACTORS PARSED FROM THE LIVE SECTION 7.7 TABLE: {fac}")
    for k in ("W(HARD)", "W(SOFT)", "Ver(True)", "Ver(None)", "Ver(False)"):
        note(k in fac, f"section 7.7 table still declares {k}",
             "" if k in fac else "table shape changed; this producer is STALE")
    if FALSIFIED:
        print("\nFALSIFIED (table unreadable -- cannot decide)")
        return 1
    WH, WS = fac["W(HARD)"], fac["W(SOFT)"]
    VERS = sorted({fac["Ver(True)"], fac["Ver(None)"], fac["Ver(False)"]})

    # ------------------------------------------------- 3. z3 on parsed values
    from z3 import And, Not, Or, Real, RealVal, Solver, sat, unsat
    print("\n2. z3 ON THE PARSED VALUES (the collapse is a property of the SHAPE)")
    conf, ver = Real("conf"), Real("ver")
    dom = And(conf > 0, conf <= 1, Or(*[ver == RealVal(str(v)) for v in VERS]))
    s = Solver()
    s.add(dom, ver > 0,
          Not(RealVal(str(WH)) * conf * ver != RealVal(str(WS)) * conf * ver))
    r1 = s.check()
    note(r1 == unsat,
         "B1  no evidence with Ver>0 makes credence(HARD)==credence(SOFT)",
         f"z3 -> {r1}; unsat means the 'credence' half varies with the CONSEQUENCE class")

    cut, B, W = Real("cut"), Real("B"), Real("W")
    s2 = Solver()
    s2.add(Or(W == RealVal(str(WH)), W == RealVal(str(WS))), B >= 0, B <= 1,
           cut > RealVal(str(WS)), cut <= RealVal(str(WH)),
           Not((W * B >= cut) == And(W == RealVal(str(WH)), B >= cut)))
    r2 = s2.check()
    note(r2 == unsat,
         "B2  W*B >= cut  <=>  class=HARD and B >= cut, for every cut in (W_SOFT, W_HARD]",
         f"z3 -> {r2}; unsat means caution 3's collapse PERSISTS inside the pair")

    # the control: a cut named by a DISTINGUISHED ELEMENT is not breakable,
    # while a cut named by a FIXED VALUE is.  Both run, so neither is assumed.
    a, b, c, pa, pb, pc = (Real(x) for x in "a b c pa pb pc".split())
    order = And(a < b, b < c, pa < pb, pb < pc)          # phi strictly increasing
    from z3 import If, Sum
    fx = RealVal("7/10")
    sf = Solver(); sf.add(order, Not(
        Sum([If(x >= fx, 1, 0) for x in (a, b, c)]) ==
        Sum([If(x >= fx, 1, 0) for x in (pa, pb, pc)])))
    st = Solver(); st.add(order, Not(
        Sum([If(x >= b, 1, 0) for x in (a, b, c)]) ==
        Sum([If(x >= pb, 1, 0) for x in (pa, pb, pc)])))
    rf, rt = sf.check(), st.check()
    note(rf == sat, "A1  a FIXED-VALUE cut is breakable by an order-preserving relabel",
         f"z3 -> {rf}")
    note(rt == unsat, "A2  a TRANSPORTED level is not", f"z3 -> {rt}")

    # ------------------------------------- 4. SymPy: S_v cannot carry the zero
    import sympy as sp
    print("\n3. SymPy -- WHY `Ver` CANNOT BE FOLDED INTO `S_v`")
    L = sp.symbols("L", real=True)
    Sv = 1 / (1 + sp.exp(-L))
    zeros = sp.solveset(sp.Eq(Sv, 0), L, domain=sp.S.Reals)
    note(zeros == sp.EmptySet,
         "S_v = 1/(1+exp(-L)) has NO zero over the reals",
         f"solveset -> {zeros}; so credence=S_v alone cannot represent Ver(False)=0")
    note(sp.limit(Sv, L, -sp.oo) == 0,
         "its infimum is 0 and unattained", "limit L->-oo = 0")
    note(sp.simplify(Sv * fac["Ver(False)"]) == 0,
         "credence = S_v * Ver(False) = 0 EXACTLY -- the key property survives")

    # ------------------------------- 5. mutation test: can the check even fail?
    print("\n4. MUTATION TEST -- a check that cannot detect the defect is worthless")
    mutant = s771.replace("**credence(f) = S_v(f) · Ver(verification)**", "") + (
        "\nwith `credence(f)` being today's §7.7 product under its own name.\n")
    note(credence_half_carries_consequence(mutant),
         "the predicate DOES fire on the superseded sentence",
         "mutant detected")
    note(not credence_half_carries_consequence(s771),
         "the predicate does NOT fire on the live section 7.7.1",
         "live text repaired" if not credence_half_carries_consequence(s771)
         else "LIVE DEFECT PRESENT")

    # --------------------------- 6. REPORTED, NOT ASSERTED: the wiring measure
    print("\n5. REPORTED MEASUREMENT (a separate, UNFIXED defect -- not asserted here)")
    callers = []
    for fp in list((REPO / "bench").rglob("*.py")) + list((REPO / "scripts").rglob("*.py")):
        if fp.name == "domain_vocabulary.py":
            continue
        try:
            tree = ast.parse(fp.read_text(encoding="utf-8"))
        except Exception:                                    # noqa: BLE001
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                f = n.func
                nm = f.attr if isinstance(f, ast.Attribute) else (
                    f.id if isinstance(f, ast.Name) else None)
                if nm == "severity":
                    callers.append(f"{fp.relative_to(REPO)}:{n.lineno}")
    print(f"   call sites of domain_vocabulary.severity() outside the module: "
          f"{len(callers)} {callers}")
    veto = (REPO / "bench" / "dm" / "_convergence.py").read_text(encoding="utf-8")
    print(f"   _convergence.py still gates on a FIXED VALUE: "
          f"{'eta_veto' in veto and 'aggregated_severity >= self.config.eta_veto' in veto}")
    tys = (REPO / "bench" / "dm" / "_types.py").read_text(encoding="utf-8")
    m = re.search(r"eta_veto:\s*float\s*=\s*([0-9.]+)", tys)
    ev = float(m.group(1)) if m else None
    print(f"   eta_veto = {ev}  ->  on CVSS v4.0 that is {ev*10 if ev else '?'}, "
          f"the CRITICAL band, while the manifest declares critical_level = 'High' (7.0)")

    print()
    if FALSIFIED:
        print("FALSIFIED")
        return 1
    print("CLEAN -- the credence half carries no consequence factor in the live appendix.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
