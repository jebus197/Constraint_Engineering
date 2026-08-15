# Slender Strut SS-114 — Buckling Capacity and Factor of Safety Reference

**Document ID:** STR-07-REF-01
**Scope:** One compression member (a hot-finished circular hollow strut used as the
diagonal brace of a walkway truss), together with the reference implementation that
defines how its capacity is computed: section properties, elastic critical load,
slenderness, factor of safety against the design action, and the sensitivity of
capacity to wall thickness.
**Status:** Internal technical reference. Assertions carry traceability tags (SM-nn)
so review is logged against individual statements rather than whole sections.

---

## 1. Purpose and conventions

The strut is a pinned-pinned member carrying axial compression only. Every capacity
statement below is a statement about the section constants of section 2 and the
reference implementation of section 3, and about no other. Lengths are millimetres,
forces newtons, stresses newtons per square millimetre (that is, megapascals).
Elastic capacity means the Euler elastic critical load; no allowance is made here for
material yielding, initial bow, or residual stress, and every figure is therefore an
upper bound on real capacity rather than a design resistance.

Design inputs used throughout:

| Symbol | Value | Meaning |
|--------|-------|---------|
| d_o | 114.3 mm | outside diameter of the hollow section |
| t | 6.0 mm | wall thickness |
| d_i | 102.3 mm | bore diameter, d_o - 2t |
| L | 3 600 mm | system length between pin centres |
| K | 1.0 | effective length factor, pinned at both ends |
| E | 200 000 MPa | Young's modulus of the steel |
| N_Ed | 180 000 N | design axial compression |
| rho | 7 850 kg/m^3 | density of the steel |

---

## 2. Section properties

**SM-01.** The bore of a hollow circular section is d_i = d_o - 2t = 114.3 - 12.0 =
102.3 mm. The wall is removed from both sides of the diameter, not one, so the
subtraction carries the factor of two.

**SM-02.** The second moment of area of an annulus is I = pi (d_o^4 - d_i^4) / 64.
With the constants above this evaluates to 3.0021 x 10^6 mm^4. The fourth-power
difference is taken before the division, not after, since (d_o - d_i)^4 is a
different quantity entirely and is smaller by three orders of magnitude here.

**SM-03.** The cross-sectional area is A = pi (d_o^2 - d_i^2) / 4 = 2 041.4 mm^2, and
the mass per metre is A rho = 16.03 kg/m. The area is the annulus area and not the
gross circle area of 10 261 mm^2, which would overstate the member by a factor of
five.

**SM-04.** The radius of gyration is r = sqrt(I / A) = 38.35 mm. It has the dimension
of length even though it is formed from a fourth-power quantity divided by a square
one, because the two length dimensions in the ratio leave length squared under the
root.

---

## 3. Reference implementation

The listing below is the definition the rest of this document reasons about, printed
in full so every capacity statement can be checked against the code it describes.
The module imports `math`.

```python
import math

def annulus_properties(d_o, t):
    """Return (I, A, r) for a circular hollow section, in mm^4, mm^2 and mm."""
    d_i = d_o - 2.0 * t
    I = math.pi * (d_o ** 4 - d_i ** 4) / 64.0
    A = math.pi * (d_o ** 2 - d_i ** 2) / 4.0
    return I, A, math.sqrt(I / A)

def euler_critical_load(E, I, L, K=1.0):
    """Elastic critical load of a prismatic strut, in newtons."""
    L_e = K * L
    return (math.pi ** 2) * E * I / (L_e ** 2)

def factor_of_safety(N_cr, N_Ed):
    return N_cr / N_Ed
```

---

## 4. Elastic critical load, slenderness and factor of safety

**SM-05.** The effective length is L_e = K L = 1.0 x 3 600 = 3 600 mm, and the elastic
critical load is N_cr = pi^2 E I / L_e^2 = 457.2 kN. Carrying the same computation
through a dimensional-analysis library, with E in gigapascals, I in mm^4 and L in
metres, returns a quantity whose base dimensions are mass times length divided by time
squared — that is, a force — confirming that the expression is dimensionally sound and
not merely numerically plausible.

**SM-06.** The slenderness is lambda = L_e / r = 3 600 / 38.35 = 93.88, a pure number.
The elastic critical stress may therefore be written either as N_cr / A or as
pi^2 E / lambda^2; both routes give 224.0 MPa, which is the arithmetic identity behind
the Euler curve rather than an independent check of it.

**SM-07.** Against the design action N_Ed = 180 kN the factor of safety on elastic
buckling is N_cr / N_Ed = 457.2 / 180 = 2.54. This is a factor against elastic
instability alone. It is not a factor against squashing, and for a steel of 355 MPa
yield the squash load of A f_y = 724.7 kN exceeds N_cr, so buckling and not yielding
governs this member.

**SM-08.** Thickening the wall from 6.0 mm to 8.0 mm raises the second moment of area
in proportion to the wall thickness, 8.0 / 6.0 = 1.333, so I rises to 4.0028 x 10^6
mm^4 and the elastic critical load to 609.7 kN. The gain in capacity is therefore
exactly proportional to the gain in mass, and thickening the wall buys nothing in
efficiency terms.

**SM-09.** Halving the system length while holding the section fixed quadruples the
elastic critical load, because L_e enters the expression squared and nothing else in
it depends on length. A 1 800 mm strut of the same section therefore reaches
1 829.0 kN, and its slenderness falls to 46.94.

---

## 5. Sensitivity table

Capacities below are elastic critical loads for the pinned-pinned member at
L = 3 600 mm, recomputed from section 3 for each wall thickness.

| t (mm) | d_i (mm) | I (x10^6 mm^4) | A (mm^2) | N_cr (kN) | mass (kg/m) |
|--------|----------|----------------|----------|-----------|-------------|
| 5.0 | 104.3 | 2.5692 | 1 716.9 | 391.3 | 13.48 |
| 6.0 | 102.3 | 3.0021 | 2 041.4 | 457.2 | 16.03 |
| 8.0 | 98.3 | 3.7949 | 2 671.6 | 578.0 | 20.97 |
| 10.0 | 94.3 | 4.4966 | 3 276.7 | 684.9 | 25.72 |

**SM-10.** The table shows capacity rising more slowly than the fourth power of any
single dimension and faster than mass: from t = 6.0 mm to t = 8.0 mm capacity rises
by a factor of 1.264 while mass rises by 1.308, so the thicker wall is very slightly
less efficient per kilogram, not more.

---

Written as a review fixture. Every figure is derivable from the constants of section 1
and the listing of section 3.
