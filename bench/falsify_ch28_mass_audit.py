"""
Falsifier for code-review finding CH-28 (exp48_chemistry target).

CLAIM UNDER TEST (CH-28, verbatim in the real target file):
    "The step-2 mass audit is run on every batch. If the total recorded output
     mass exceeds the total recorded input mass, then the audit has failed and
     conservation of mass has been violated ... the recorded output masses total
     45.02 g (26.85 g isolated product plus 18.17 g recovered filtrate solids),
     so the outputs do not exceed the inputs and no conservation violation is
     indicated; the 1.58 g difference, 3.4 per cent of the charge, sits within
     the 5 per cent handling-loss allowance."

FINDING: this audit logic ignores the liquid byproduct (acetic acid) and the
unreacted acetic anhydride, so a passing audit is not evidence of a closed mass
balance.

FALSIFIER STRATEGY (uses ONLY the target's own numbers + its own stoichiometry):
  * Route A is recorded in CH-07 as  C7H6O3 + C4H6O3 -> C9H8O4 + C2H4O2
    i.e. every mole of acetylsalicylic acid (aspirin) formed co-produces
    EXACTLY one mole of acetic acid (C2H4O2). This is a 1:1 hard constraint.
  * The audit's own "output ledger" is defined as two SOLID masses:
    isolated product + recovered filtrate SOLIDS. Acetic acid (bp 118 C) and
    acetic anhydride (bp 139 C) are liquids; neither is a filtrate solid, so
    neither can be inside the 45.02 g ledger.
  * From the isolated product mass alone (26.85 g aspirin, M=180.16), the 1:1
    stoichiometry forces a KNOWN mass of acetic acid to have been produced.
    If that forced-but-omitted mass exceeds the audit's entire claimed
    "handling loss" (1.58 g), the audit's conclusion is defective: it books a
    known reaction product as if it were never made.

The audit is a pure read of a static record, so there is no in-place mutation
to guard; nonetheless the parsed claim figures are SNAPSHOTTED up front, before
any independent computation, so the test compares against the record as written.

Exit non-zero / raise AssertionError  <=>  defect genuinely present.
Exit 0  <=>  defect absent.
"""

import re
import sys
from pathlib import Path

# --- 1. Import the REAL module and locate the REAL target via its own path ----
# Ensure the repo root (parent of the bench/ package) is importable regardless
# of the invoking cwd, then take the ABSOLUTE package import.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bench.cdsfl_registry.registry as reg  # real package, absolute import

TARGET = reg.REGISTRY_DIR / "targets" / "exp48_chemistry.md"
assert TARGET.exists(), f"real target missing: {TARGET}"
text = TARGET.read_text(encoding="utf-8")


def claim(tag: str) -> str:
    """Return the paragraph of a CH-nn claim straight from the real file."""
    m = re.search(rf"\*\*{re.escape(tag)}\.\*\*(.+?)(?:\n\n|\Z)", text, re.S)
    assert m, f"{tag} not found in real target"
    return " ".join(m.group(1).split())


ch28 = claim("CH-28")
ch07 = claim("CH-07")
ch12 = claim("CH-12")  # aspirin molar mass

# --- 2. SNAPSHOT the figures exactly as the record states them ---------------
def g(pattern: str, src: str) -> float:
    m = re.search(pattern, src)
    assert m, f"could not read {pattern!r}"
    return float(m.group(1))

snap = {
    "input_mass":       g(r"input mass was ([\d.]+) g", ch28),         # 46.60
    "output_total":     g(r"output masses total ([\d.]+) g", ch28),    # 45.02
    "isolated_product": g(r"([\d.]+) g isolated product", ch28),       # 26.85
    "filtrate_solids":  g(r"plus ([\d.]+) g recovered filtrate", ch28),# 18.17
    "claimed_shortfall":g(r"the ([\d.]+) g difference", ch28),         # 1.58
    "loss_allowance_pct": g(r"the (\d+) per cent handling-loss", ch28),# 5
    "M_aspirin":        g(r"is ([\d.]+) g/mol", ch12),                 # 180.16
}
print("SNAPSHOT of CH-28 record (from real target file):")
for k, v in snap.items():
    print(f"    {k:20s} = {v}")

# Confirm the audit's ledger and one-sidedness are as the finding describes.
assert abs((snap["isolated_product"] + snap["filtrate_solids"]) - snap["output_total"]) < 0.02, \
    "ledger identity broken -- re-read the claim"
one_sided = "exceeds" in ch28 and "audit has failed" in ch28
assert one_sided, "CH-28 no longer uses a one-sided 'output>input' failure rule"

# Confirm CH-07 really encodes the 1:1 aspirin:acetic-acid stoichiometry.
assert "C9H8O4 + C2H4O2" in ch07 and "coefficient sum is 4" in ch07, \
    "CH-07 stoichiometry changed -- re-derive"

# --- 3. Independent chemistry: acetic acid FORCED by the isolated product -----
# Molar mass of acetic acid C2H4O2 from standard atomic weights (IUPAC 2021).
M_C, M_H, M_O = 12.011, 1.008, 15.999
M_acetic_acid = 2 * M_C + 4 * M_H + 2 * M_O            # ~60.05 g/mol
print(f"\nM(acetic acid, C2H4O2) computed = {M_acetic_acid:.2f} g/mol")

mol_aspirin_isolated = snap["isolated_product"] / snap["M_aspirin"]
# 1:1 stoichiometry (CH-07): moles acetic acid >= moles aspirin isolated.
acetic_acid_forced = mol_aspirin_isolated * M_acetic_acid

print(f"moles aspirin isolated            = {mol_aspirin_isolated:.5f} mol")
print(f"acetic acid FORCED by CH-07 (1:1) = {acetic_acid_forced:.2f} g "
      f"(liquid, absent from the solids ledger)")

# What a correct closed-system ledger shows once this known product is included:
corrected_output = snap["output_total"] + acetic_acid_forced
print(f"\nAudit output ledger (as recorded) = {snap['output_total']:.2f} g")
print(f"+ forced acetic acid byproduct    = {acetic_acid_forced:.2f} g")
print(f"= corrected output (partial)      = {corrected_output:.2f} g "
      f"vs input {snap['input_mass']:.2f} g")

# --- 4. Verdict --------------------------------------------------------------
# Defect is present iff the omitted, stoichiometrically-forced acetic acid
# exceeds the entire "handling loss" the audit signed off on. If so, the audit
# has booked a known reaction product as never-produced and its "no violation"
# verdict is unsupported.
defect_present = acetic_acid_forced > snap["claimed_shortfall"]

# Secondary, independent symptom: adding the known byproduct pushes the true
# output ABOVE the input, which by CH-28's OWN rule ("output exceeds input ->
# audit failed") is a conservation violation the one-sided test cannot see,
# because the recorded (understated) output sits below input.
one_sided_blind = corrected_output > snap["input_mass"] >= snap["output_total"]

print("\n" + "=" * 68)
if defect_present:
    print("FALSIFIED: CH-28 mass audit is defective.")
    print(f"  The isolated 26.85 g of aspirin ALONE forces "
          f"{acetic_acid_forced:.2f} g of acetic acid")
    print(f"  (CH-07, 1:1), yet the audit's entire booked loss is only "
          f"{snap['claimed_shortfall']:.2f} g.")
    print(f"  A known liquid product {acetic_acid_forced/snap['claimed_shortfall']:.1f}x "
          f"larger than the 'handling loss' is omitted from the ledger.")
    if one_sided_blind:
        print(f"  Including it gives {corrected_output:.2f} g > "
              f"{snap['input_mass']:.2f} g input -> a violation under CH-28's own")
        print(f"  rule that the one-sided 'output>input' test is structurally blind to.")
    print("=" * 68)
    raise AssertionError(
        f"CH-28 audit omits {acetic_acid_forced:.2f} g acetic acid forced by its "
        f"own 1:1 stoichiometry; claimed loss only {snap['claimed_shortfall']:.2f} g."
    )
else:
    print("CLEAN: no omitted-byproduct defect detected in CH-28.")
    print("=" * 68)
    sys.exit(0)
