#!/usr/bin/env python3
"""R_n IS NOT A PROBABILITY, AND 3 SURFACES SAY IT IS.

FOUND BY A PANEL SEAT, EXTENDED BY FOLLOWING ITS CITATION.

The joint round of `the_period_reviewed_2026-11-04` reported that
`bench/directives/universal/cdsfl_operational.md` defines

    R_n = sum_k w_k . R_k(n)

and never says the w_k are normalised, while section 3 of the same file gates
on `R_k > 0.5`. A reader who carries R_n into that gate compares a
harm-weighted loss against a probability. The seat was right.

FOLLOWING ITS CITATION FOUND 2 MORE SURFACES CARRYING THE SAME CONFLATION,
AND ONE OF THEM RECORDS IT AS PROVED:

  1. docs/MATHEMATICAL_APPENDIX.md  attributes the range [0, pi_k] to R_n.
     [0, pi_k] is R_k's range under the appendix section 1 Moebius readout.
  2. experimental_notes/Mathematical_Model_Audit_2026-04-08.md records
     "R_n in [0, 1] for pi in [0,1), m in [0,1]" as PROVED by z3 unsat.
     The quantifier list is the tell: it names pi and m and never names w_k,
     so what was proved is a property of the PER-CLASS readout, relabelled
     as the weighted sum. The audit names no producer script, so the claim
     could not be re-run -- `measured-rate-travels-with-its-script`.
  3. The seat's own proposed wording inherited [0, pi_k] from surface 1,
     which is why this script checks the seat too rather than pasting it.

WHAT IS ACTUALLY TRUE, proved here rather than asserted:
  R_n in [0, sum_k w_k].  It equals [0, 1] exactly when sum_k w_k <= 1.
  Under the directive's own re-injection form R_k can exceed pi_k but
  never exceeds 1, so the directive's own "bounded in [0, 1]" is right
  about R_k and the appendix's "[0, pi_k]" is not right about either.

ANCHORS ARE DERIVED FROM THE FILES, NEVER HARDCODED AS LINE NUMBERS, so
this script keeps working when the files are edited above the claims.

Two routes for every mathematical claim (SymPy exact / mpmath numeric /
z3 for the quantified statements), per the 2026-04-21 cross-verification rule.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

DIRECTIVE = REPO / "bench/directives/universal/cdsfl_operational.md"
APPENDIX = REPO / "docs/MATHEMATICAL_APPENDIX.md"
AUDIT = REPO / "experimental_notes/Mathematical_Model_Audit_2026-04-08.md"

_WK_TOKEN = "\x00WK\x00"

_NORM = re.compile(
    r"(normalis|normaliz|convex\s+(combination|weight)"
    r"|(sum|\u03a3)[^.]{0,30}w_k\s*=\s*1"
    r"|w_k[^.]{0,30}(sum|add)[^.]{0,12}to\s*1"
    r"|weights[^.]{0,20}sum[^.]{0,12}to\s*1)", re.I)

# NEGATION GUARD. A sentence that DENIES normalisation is not a requirement
# for it. Needed because the scale note this script motivated says, in the
# subject file, "The w_k are NOT required to sum to 1" -- so without this the
# repair reads as the defect and the count went from 0 of 3 to 1 of 7 the
# moment the note landed. A detector must not match its own remedy.
_NEG = re.compile(
    r"\b(not|never|no|none|nothing|without|unnormalis|unnormaliz"
    r"|non-convex)\b", re.I)


def _strip_indices(line: str) -> str:
    """Drop LaTeX-ish index groups, in which `k=1` is a summation bound.

    `w_k` is protected first. Without that, the generic `_<char>` rule eats
    the subscript out of the very token being searched for, and every prose
    normalisation statement reads as absent.
    """
    line = line.replace("w_k", _WK_TOKEN)
    line = re.sub(r"[_^]\{[^}]*\}", " ", line)
    line = re.sub(r"[_^][A-Za-z0-9]\s*=\s*\d+", " ", line)
    return line.replace(_WK_TOKEN, "w_k")


def normalises(line: str) -> bool:
    """True when this line REQUIRES the weights to be normalised.

    THE NEGATION WINDOW IS THE ENCLOSING CLAUSE, FROM ITS START THROUGH THE
    END OF THE MATCH, and both halves were established by mutation rather
    than by design. A negation can sit BEFORE the match ("nothing in this
    file ... normalises the w_k") or INSIDE it ("the w_k are NOT required to
    sum to 1"), so a look-behind alone misses the second. And a flat
    character window picks up the negation of a NEIGHBOURING clause: the
    scale note's line reads "...may not be compared to.** The w_k are NOT
    required to sum to 1", and with a 60-character look-behind the inverted
    sentence still read as negated, so inverting the note was invisible to
    this script. Mutation 3 of
    `scripts/the_weighted_risk_mutations_2026-11-04.py` is that case.
    """
    if "w_k" not in line:
        return False
    stripped = _strip_indices(line)
    hit = _NORM.search(stripped)
    if not hit:
        return False
    cut = max(stripped.rfind(". ", 0, hit.start()),
              stripped.rfind(".**", 0, hit.start()),
              stripped.rfind("**", 0, hit.start()),
              stripped.rfind("; ", 0, hit.start()))
    window = stripped[(cut + 1) if cut != -1 else 0:hit.end()]
    return not _NEG.search(window)


# SENSITIVITY PINNED HERE, BOTH DIRECTIONS, AND EXECUTED ON EVERY RUN.
# The first version of this predicate matched `=\s*1` anywhere and so read
# the summation bound in `G_n = \u03a3_{k=1}^{K} w_k ...` as a normalisation
# requirement, reporting 1 of 13 where the truth is 0 of 13. A predicate
# whose only positive case lives in a docstring can be narrowed to nothing
# with every test still green, so the cases live in the code and run.
_CONTROLS = [
    ("> **G_n = \u03a3_{k=1}^{K} w_k \u00b7 [1 \u2212 ...]**", False,
     "braced summation bound, the measured false positive"),
    ("G_n = \u03a3_k=1 w_k \u00b7 x", False, "unbraced summation bound"),
    ("R_n = \u03a3_k w_k \u00b7 R_k(n)", False, "the definition, claiming neither way"),
    ("where w_k is the consequence weight for flaw class k.", False,
     "the directive's own gloss"),
    ("and what it may not be compared to.** The w_k are NOT required to "
     "sum to 1.", False,
     "NEGATED: the scale note this script motivated, the 2nd measured "
     "false positive"),
    ("The w_k are never normalised here.", False, "NEGATED: prose denial"),
    ("Weights are used without normalisation.", False, "NEGATED: without"),
    ("nothing in this file or in the operational directive normalises the "
     "w_k, so R_n is an expected-loss scale", False,
     "NEGATED: this script's OWN appendix correction, the 3rd measured "
     "false positive"),
    ("None of the w_k are normalised.", False, "NEGATED: none"),
    ("and what it may not be compared to.** The w_k are NOT required to "
     "sum to 1.", False,
     "the scale note's REAL line, negation inside the match"),
    ("and what it may not be compared to.** The w_k are required to "
     "sum to 1.", True,
     "the same line INVERTED -- must fire; a flat window missed this"),
    ("The weights are normalised, so \u03a3_k w_k = 1 by construction.", True,
     "explicit normalisation"),
    ("We require sum_k w_k = 1 throughout.", True, "sum form"),
    ("The w_k sum to 1.", True, "prose form"),
    ("Take the w_k as a convex combination over classes.", True, "convex phrasing"),
    ("w_k must add to 1.", True, "add-to form"),
]


def check_predicate() -> int:
    """Run the controls. Returns the number of failures; 0 is required."""
    bad = 0
    for text, expect, label in _CONTROLS:
        got = normalises(text)
        if got != expect:
            bad += 1
            print(f"    !! {got} expected {expect}  {label}")
    return bad



def _find(path: pathlib.Path, pattern: str) -> list[tuple[int, str]]:
    """Every (1-indexed line number, line) whose text matches `pattern`."""
    rx = re.compile(pattern)
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if rx.search(line):
            out.append((i, line))
    return out


def section_1_the_surfaces() -> dict:
    print("=" * 78)
    print("1. THE 3 SURFACES, LOCATED BY CONTENT")
    print("=" * 78)
    found = {}

    # The directive's definition of R_n, and its 0.5 gate on R_k.
    defn = _find(DIRECTIVE, r"R_n\s*=\s*Σ_k\s*w_k|R_n\s*=\s*sum_k\s*w_k")
    gate = _find(DIRECTIVE, r"R_k\s*>\s*0\.5")
    if not gate:
        # SILENCE IS NOT A PASS. If the threshold moves, a search for 0.5
        # finds nothing and this section prints nothing about the gate at
        # all, which reads identically to "the gate is fine".
        moved = _find(DIRECTIVE, r"R_k\s*>\s*0?\.[0-9]+")
        print(f"    !! the 0.5 gate was NOT found. "
              f"{len(moved)} R_k threshold(s) at another value: "
              f"{[l.strip()[:48] for _, l in moved] or 'none'}")
    print(f"\n  {DIRECTIVE.relative_to(REPO)}")
    for n, l in defn:
        print(f"    line {n:>4}  DEFINITION  {l.strip()[:96]}")
    for n, l in gate:
        print(f"    line {n:>4}  0.5 GATE    {l.strip()[:96]}")
    found["directive_defn"] = defn
    found["directive_gate"] = gate

    # Does the directive normalise the weights anywhere?
    wk = _find(DIRECTIVE, r"w_k")
    norm = [(n, l) for n, l in wk if normalises(l)]
    print(f"    w_k mentions: {len(wk)}; of those requiring normalisation: "
          f"{len(norm)}")
    found["directive_wk"] = len(wk)
    found["directive_norm"] = len(norm)

    # The appendix's range attribution, reported in EITHER state.
    #
    # A SEARCH FOR THE DEFECT ALONE GOES SILENT THE MOMENT THE DEFECT IS
    # FIXED, and silence is indistinguishable from "this file was never
    # checked". So both the defective wording and its correction are looked
    # for, and exactly 1 of them must be present.
    bad = _find(APPENDIX, r"R_n reports residual risk, whose range")
    good = _find(APPENDIX, r"per-class R_k reports residual risk, whose range")
    print(f"\n  {APPENDIX.relative_to(REPO)}")
    for n, l in bad:
        print(f"    line {n:>4}  RANGE       DEFECT PRESENT: attributes the "
              f"range to R_n")
    for n, l in good:
        print(f"    line {n:>4}  RANGE       CORRECTED: attributes the range "
              f"to the per-class R_k")
    if len(bad) + len(good) != 1:
        print(f"    !! {len(bad)} defective and {len(good)} corrected range "
              f"clause(s) found; expected exactly 1 of the 2. The appendix "
              f"wording moved and this check can no longer see its subject.")
    app = bad or good
    appwk = _find(APPENDIX, r"w_k")
    appnorm = [(n, l) for n, l in appwk if normalises(l)]
    print(f"    w_k mentions: {len(appwk)}; of those requiring normalisation: "
          f"{len(appnorm)}")
    found["appendix_range"] = app
    found["appendix_wk"] = len(appwk)
    found["appendix_norm"] = len(appnorm)

    # The audit's PROVED row, and whether it quantifies over w_k.
    aud = _find(AUDIT, r"R_n\s*∈\s*\[0, 1\]|R_n in \[0, 1\]")
    print(f"\n  {AUDIT.relative_to(REPO)}")
    for n, l in aud:
        print(f"    line {n:>4}  PROVED ROW  {l.strip()[:96]}")
        names_w = bool(re.search(r"w_k|weight", l))
        print(f"               quantifies over w_k: {names_w}  "
              f"<- False means it proved the PER-CLASS form")
        found["audit_names_w"] = names_w
    prod = _find(AUDIT, r"scripts/|\.py\b")
    print(f"    producer scripts named by the audit: {len(prod)}")
    found["audit_rows"] = aud
    found["audit_producers"] = len(prod)
    return found


def section_1b_the_cited_identity() -> bool:
    """The directive note CITES the appendix §4 L_n. Verify that it is there.

    A citation this script puts into a live directive must be checked against
    the cited file, or the note ships a reference nobody confirmed. Mutation 5
    of the companion harness renames the appendix definition; without this
    the rename was invisible.
    """
    print()
    print("=" * 78)
    print("1b. THE IDENTITY THE DIRECTIVE NOTE CITES, CHECKED IN THE APPENDIX")
    print("=" * 78)
    defn = _find(APPENDIX, r"L_n\s*=\s*Σ_k\s*s_k")
    red = _find(APPENDIX, r"When s_k = w_k.*L_n reduces to R_n")
    sev = _find(APPENDIX, r"\*\*s_k\*\*\s*=\s*expected harm")
    for label, hits in [("L_n = Σ_k s_k · R_{n,k}", defn),
                        ("the s_k = w_k reduction to R_n", red),
                        ("s_k defined as expected harm", sev)]:
        mark = "OK " if hits else "!! "
        where = f"line {hits[0][0]}" if hits else "NOT FOUND"
        print(f"  {mark}{label:<34} {where}")
    ok = bool(defn and red and sev)
    if not ok:
        print("  the directive note cites appendix §4 for this identity; "
              "the citation is no longer verifiable against the file.")
    return ok


def section_2_the_real_range() -> None:
    print()
    print("=" * 78)
    print("2. THE REAL RANGE OF R_n, PROVED ON 2 ROUTES")
    print("=" * 78)

    import sympy as sp
    import z3
    from mpmath import mp, mpf
    mp.dps = 40

    print("\n  ROUTE 1 - SymPy, the seat's witness exactly")
    w1, w2 = sp.Integer(3), sp.Integer(4)
    Rk = sp.Rational(1, 2)
    R_n = w1 * Rk + w2 * Rk
    print(f"    w = (3, 4), R_k = (1/2, 1/2)  ->  R_n = {R_n}")
    assert R_n == sp.Rational(7, 2), R_n
    print(f"    exact 7/2:                {R_n == sp.Rational(7, 2)}")
    print(f"    exceeds the 0.5 gate by:  {sp.nsimplify(R_n - sp.Rational(1, 2))}")

    print("\n  ROUTE 2 - mpmath, independent arithmetic")
    m = mpf(3) * mpf("0.5") + mpf(4) * mpf("0.5")
    delta = abs(mp.mpf(float(R_n)) - m)
    print(f"    R_n = {m};  disagreement with SymPy: {delta}")
    assert delta == 0, delta

    print("\n  ROUTE 3 - z3, the quantified statements the witness cannot settle")
    a, b, p, q = z3.Reals("w1 w2 R1 R2")
    Rn = a * p + b * q
    base = [p >= 0, p <= 1, q >= 0, q <= 1, a > 0, b > 0]

    checks = [
        ("R_n outside [0,1] when sum(w) <= 1",
         [a + b <= 1, z3.Or(Rn < 0, Rn > 1)], z3.unsat,
         "the audit's claim HOLDS under convex weights"),
        ("R_n > 1 when sum(w) > 1",
         [a + b > 1, Rn > 1], z3.sat,
         "the audit's claim FAILS without them"),
        ("R_n > sum(w_k)",
         [Rn > a + b], z3.unsat,
         "so [0, sum w_k] is the true range"),
        ("R_n < 0",
         [Rn < 0], z3.unsat,
         "lower bound 0 is safe"),
        ("R_n trips 0.5 while EVERY R_k passes 0.5",
         [Rn > z3.RealVal(1) / 2,
          p <= z3.RealVal(1) / 2, q <= z3.RealVal(1) / 2], z3.sat,
         "THE CATEGORY ERROR, as a theorem not a witness"),
    ]
    for label, extra, expect, why in checks:
        s = z3.Solver()
        s.add(base + extra)
        got = s.check()
        mark = "OK " if got == expect else "!! "
        print(f"    {mark}{label:<48} {str(got):>5}   {why}")
        assert got == expect, (label, got, expect)


def section_3_rk_vs_pik() -> None:
    print()
    print("=" * 78)
    print("3. AND [0, pi_k] IS NOT R_k'S RANGE UNDER THIS DIRECTIVE EITHER")
    print("=" * 78)

    import sympy as sp
    import z3

    pi, m, nb, nf, S = sp.symbols("pi m nu_b nu_f S_k", positive=True)
    R_base = pi * m / ((1 - pi) + pi * m)

    print("\n  SymPy - the appendix section 1 readout, with no re-injection")
    print(f"    R_base at m = 1: {sp.simplify(R_base.subs(m, 1))}"
          "   <- so [0, pi_k] IS right for this form")
    print(f"    R_base at m = 0: {sp.simplify(R_base.subs(m, 0))}")
    d = sp.simplify(sp.diff(R_base, m))
    print(f"    d/dm = {d}  (positive on 0 < pi < 1, so the max is at m = 1)")

    nu_eff = 1 - (1 - nb) * (1 - (1 - S) * nf)
    R_k = R_base * (1 - nu_eff) + nu_eff
    sub = {pi: sp.Rational(1, 10), m: 1, nb: sp.Rational(1, 5), nf: 0, S: 0}
    val = sp.nsimplify(R_k.subs(sub))
    print("\n    the directive's OWN form, R_k = R_base.(1-nu_eff) + nu_eff")
    print(f"    at pi=1/10, m=1, nu_b=1/5, nu_f=0, S_k=0:  R_k = {val}")
    print(f"    which EXCEEDS pi_k = 1/10 by {sp.nsimplify(val - sp.Rational(1, 10))}")
    assert val > sp.Rational(1, 10)

    print("\n  z3 - the general statement, under the directive's HARD CONSTRAINT")
    zp, zm, zb, zf, zs = z3.Reals("pi m nb nf S")
    zRbase = zp * zm / ((1 - zp) + zp * zm)
    znu = 1 - (1 - zb) * (1 - (1 - zs) * zf)
    zRk = zRbase * (1 - znu) + znu
    dom = [zp > 0, zp < 1, zm >= 0, zm <= 1, zb >= 0, zb <= 1,
           zf >= 0, zf <= 1, zs >= 0, zs <= 1, zb + zf <= 1]
    for label, extra, expect, why in [
        ("R_k > pi_k", [zRk > zp], z3.sat,
         "so [0, pi_k] is WRONG for the directive's form"),
        ("R_k > 1", [zRk > 1], z3.unsat,
         "but R_k IS still a probability, as the directive says"),
    ]:
        s = z3.Solver()
        s.add(dom + extra)
        got = s.check()
        mark = "OK " if got == expect else "!! "
        print(f"    {mark}{label:<12} {str(got):>5}   {why}")
        assert got == expect, (label, got, expect)


def main() -> int:
    bad = check_predicate()
    print(f"  predicate controls: {len(_CONTROLS)} run, {bad} failed")
    if bad:
        print("  REFUSING: the predicate that counts normalisation statements "
              "does not discriminate, so its count is not a count.")
        return 1
    found = section_1_the_surfaces()
    if len(found["appendix_range"]) != 1:
        print("\n  REFUSING: the appendix range clause could not be located "
              "in either state, so this script is no longer measuring it.")
        return 1
    cited_ok = section_1b_the_cited_identity()
    section_2_the_real_range()
    section_3_rk_vs_pik()

    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    print(f"""
  R_n is an expected-loss SCALE with range [0, sum_k w_k], not a probability.
  Surfaces carrying a probability claim about it: 2 in the repository
  (the appendix range line and the audit's PROVED row) plus the panel seat's
  own proposed wording, which inherited it from the first.

  Weights requiring normalisation: {found['directive_norm']} of
  {found['directive_wk']} w_k mentions in the directive and
  {found['appendix_norm']} of {found['appendix_wk']} in the appendix. Nothing
  normalises them, so nothing makes R_n a probability.

  The audit's row quantifies over w_k: {found.get('audit_names_w')}.
  Producer scripts the audit names: {found['audit_producers']}.

  The appendix §4 identity the directive note cites: {"VERIFIED" if cited_ok else "NOT VERIFIABLE"}.

  THE REPAIR IS A RANGE NOTE AT THE DEFINITION, NOT A CHANGE TO THE MATHS.
  The equation is correct; what is missing is the statement of what it
  returns. The 0.5 gate in section 3 reads the per-class R_k and is right
  to; only the carry-over of R_n into it is wrong.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
