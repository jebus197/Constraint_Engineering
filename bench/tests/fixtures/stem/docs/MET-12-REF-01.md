# Standardisation of Sodium Hydroxide against KHP — Stoichiometry and Uncertainty Reference

**Document ID:** MET-12-REF-01
**Scope:** One analytical procedure (the standardisation of a nominally 0.1 mol/L
sodium hydroxide titrant against dried potassium hydrogen phthalate) together with the
reference implementation that defines it: the stoichiometric relation, the resulting
concentration, the uncertainty budget and its combination, and a mass-balance check on
an unrelated reaction used to exercise the same unit algebra.
**Status:** Internal technical reference. Assertions carry traceability tags (CM-nn)
so review is logged against individual statements rather than whole sections.

---

## 1. The procedure and its constants

A weighed portion of dried potassium hydrogen phthalate (KHP, KHC8H4O4) is dissolved
in carbon-dioxide-free water and titrated with the sodium hydroxide solution to the
phenolphthalein end point. KHP is monoprotic in this titration, so one mole of KHP
consumes one mole of hydroxide, and the concentration follows from the weighed mass,
the molar mass and the delivered volume alone.

| Quantity | Value | Standard uncertainty | Source |
|----------|-------|----------------------|--------|
| m, mass of KHP | 0.5106 g | 0.0002 g | balance, calibration certificate |
| M, molar mass of KHP | 204.22 g/mol | 0.01 g/mol | IUPAC atomic weights |
| V, titre delivered | 24.87 mL | 0.03 mL | Class A burette, 50 mL |
| Purity of the KHP | 100.0 per cent | treated as exact | certified reference material |

Relative atomic masses used elsewhere in this document: C 12.011, H 1.008,
O 15.999.

---

## 2. Reference implementation

The listing below is the definition the rest of this document reasons about. It
imports `math` from the standard library and nothing else.

```python
import math

def khp_concentration(mass_g, molar_mass, titre_ml):
    """Concentration of the NaOH titrant, in mol/L, from a 1:1 standardisation."""
    moles = mass_g / molar_mass
    return moles / (titre_ml / 1000.0)

def relative_uncertainties(values_and_uncerts):
    """Relative standard uncertainty of each input quantity."""
    return [u / v for v, u in values_and_uncerts]

def combine_relative(rels):
    """Combine independent relative standard uncertainties."""
    return math.sqrt(sum(r * r for r in rels))
```

---

## 3. Stoichiometry and the point estimate

**CM-01.** KHP releases one acidic proton in this titration, from the carboxylic acid
group, while the second carboxyl remains as the potassium salt. The stoichiometric
factor is therefore 1:1 and the amount of hydroxide delivered equals the amount of
KHP weighed, with no factor of two anywhere in the calculation.

**CM-02.** The amount of KHP taken is n = m / M = 0.5106 / 204.22 = 2.5002 mmol.

**CM-03.** The concentration of the titrant is c = n / V = 2.5002 mmol / 24.87 mL =
0.10053 mol/L. Millimoles divided by millilitres gives moles per litre directly, since
the two thousandths cancel; that cancellation is why the expression can be written
either in base units or in the milli- prefixed ones without a conversion factor.

---

## 4. The uncertainty budget

**CM-04.** The relative standard uncertainties of the three inputs are
u(m)/m = 0.0002 / 0.5106 = 0.0392 per cent, u(M)/M = 0.01 / 204.22 = 0.0049 per cent,
and u(V)/V = 0.03 / 24.87 = 0.1206 per cent.

**CM-05.** The burette dominates the budget. Its relative uncertainty exceeds the
balance's by a factor of three and the molar mass's by a factor of twenty-five, and
because the terms enter as squares the burette accounts for more than nine tenths of
the combined variance. Improving the balance would move the result by almost nothing.

**CM-06.** Because c is a product of independent quantities raised to powers of plus
or minus one, the combined relative standard uncertainty is the root sum of squares of
the three relative components: u_c(c)/c = 0.165 per cent. The concentration is
therefore reported as c = 0.10053 +/- 0.00017 mol/L at k = 1.

**CM-07.** At the coverage factor k = 2, which is the level this laboratory reports,
the expanded uncertainty is twice the standard uncertainty and the interval is quoted
as approximately 95 per cent. The coverage factor multiplies the combined standard
uncertainty and does not re-enter the combination, so it cannot change which component
dominates.

---

## 5. A mass-balance cross-check on the unit algebra

The complete combustion of propane is used here only to exercise the same molar
arithmetic on a second reaction, where conservation of mass provides an independent
check that the bookkeeping is right.

C3H8 + 5 O2 -> 3 CO2 + 4 H2O

**CM-08.** The molar masses that follow from the atomic masses of section 1 are
44.097 g/mol for propane, 31.998 g/mol for dioxygen, 44.009 g/mol for carbon dioxide
and 18.015 g/mol for water.

**CM-09.** Burning 1.000 kg of propane consumes 22.677 mol x 5 = 113.386 mol of
dioxygen, that is 3.628 kg, and produces 2.994 kg of carbon dioxide and 1.634 kg of
water. The masses in, 1.000 + 3.628 = 4.628 kg, equal the masses out,
2.994 + 1.634 = 4.628 kg, to the precision quoted, as conservation of mass requires
of a balanced equation.

**CM-10.** The equation as written is balanced in every element: three carbons, eight
hydrogens and ten oxygens appear on each side, the ten oxygens on the right being six
from the three carbon dioxides and four from the four waters. An unbalanced equation
would fail the mass-balance check of CM-09 as well, so the two statements are not
independent.

---

Written as a review fixture. Every figure is recomputable from the table of section 1
and the listing of section 2.
