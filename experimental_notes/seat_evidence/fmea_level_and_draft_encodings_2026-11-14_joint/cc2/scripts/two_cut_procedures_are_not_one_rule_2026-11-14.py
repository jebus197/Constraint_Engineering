# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fmea_level_and_draft_encodings_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c9c3f982a34c6e02bdfda1ccefb12f5734a06b617015dc9b43ca381d3c9c7661
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Are the 2 Q1 cut-procedures the same rule in different words? z3 says no.

`cc2`   step 3: cut = LOWEST band that AT LEAST ONE material category REACHES.
                qualifying predicate:  B INTERSECT M  !=  empty      (overlap)
`fable` step  : cut = LOWEST landmark whose published definition ENTAILS the
                project's materiality definition.
                qualifying predicate:  B SUBSET OF M                 (entailment)

For non-empty B, (B subset M) implies (B intersect M non-empty), so fable's
predicate is STRICTLY STRONGER and fable's cut is >= cc2's cut. They coincide
only when the lowest OVERLAPPING band happens to be wholly contained in M.
A band that PARTIALLY overlaps materiality separates them.
"""
from z3 import Bool, Solver, Implies, And, Or, Not, sat, unsat

# A standard with 4 bands; each band holds 2 defect kinds (a, b).
# mat[band][kind] = "a defect of this kind in this band is MATERIAL".
BANDS = range(4)
mat = {(b, k): Bool(f"mat_{b}_{k}") for b in BANDS for k in ("a", "b")}

def overlap(b):   # cc2: some defect in b is material
    return Or(mat[(b, "a")], mat[(b, "b")])

def entails(b):   # fable: EVERY defect in b is material
    return And(mat[(b, "a")], mat[(b, "b")])

def lowest(pred):
    """Symbolic 'lowest qualifying band' as a disjunction per candidate."""
    return [And(pred(b), *[Not(pred(j)) for j in range(b)]) for b in BANDS]

s = Solver()
# Monotone materiality: if a kind is material at band b it is material above b.
for k in ("a", "b"):
    for b in range(3):
        s.add(Implies(mat[(b, k)], mat[(b + 1, k)]))

cc2_lo, fab_lo = lowest(overlap), lowest(entails)
# Ask for a standard where cc2's cut is band 1 and fable's is band 2.
s.push()
s.add(cc2_lo[1], fab_lo[2])
r = s.check()
print("CLAIM 1  'the 2 predicates can pick DIFFERENT cuts' :", r,
      "  <-- sat = THEY ARE 2 RULES, NOT 1" if r == sat else "")
if r == sat:
    m = s.model()
    print("  witness standard (band: kind a material?, kind b material?)")
    for b in BANDS:
        print(f"    band {b}: a={m[mat[(b,'a')]]}, b={m[mat[(b,'b')]]}")
    print("  cc2 (overlap)   cut -> band 1")
    print("  fable (entail)  cut -> band 2   DISAGREEMENT = 1 band")
s.pop()

# And prove the ordering is not accidental: fable's cut can never be BELOW cc2's.
s.push()
viol = Or(*[And(fab_lo[i], cc2_lo[j]) for i in BANDS for j in BANDS if i < j])
s.add(viol)
r2 = s.check()
print("CLAIM 2  'fable cut can sit BELOW cc2 cut'          :", r2,
      "  <-- unsat = fable's rule is STRICTLY the looser-cutting one"
      if r2 == unsat else "")
assert r == sat, "the two procedures could not be separated"
assert r2 == unsat, "the ordering between the procedures is not what was derived"
print("\nDERIVED: the 2 procedures are NOT the same rule. fable's cut >= cc2's")
print("cut always, with equality only when the lowest overlapping band is")
print("wholly material. A partially-material band separates them.")
