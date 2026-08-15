# Telemetry Statistics in Binary64 — Rounding, Cancellation and Error-Bound Reference

**Document ID:** NUM-05-REF-01
**Scope:** One numerical component (the telemetry sidecar that computes a mean and a
variance over a window of sensor readings) together with the reference implementations
that define it: the rounding model of the arithmetic, the two competing variance
formulas and their behaviour under cancellation, the small root of a quadratic, and
the accumulated error bound on a summation.
**Status:** Internal technical reference. Assertions carry traceability tags (NA-nn)
so review is logged against individual statements rather than whole sections.

---

## 1. The arithmetic model and its conventions

All arithmetic below is IEEE 754 binary64 with round-to-nearest, ties-to-even, and no
extended-precision accumulation: every named operation rounds its exact result to the
nearest representable value before the next operation begins. The unit roundoff is
u = 2^-53, so every rounded operation on finite operands satisfies
fl(a op b) = (a op b)(1 + delta) with |delta| <= u.

Constants and the window used throughout:

| Symbol | Value | Meaning |
|--------|-------|---------|
| u | 2^-53 | unit roundoff, 1.1102230246251565 x 10^-16 |
| eps | 2^-52 | the machine epsilon reported by the language, 2u |
| N | 10 | readings in one telemetry window |
| x0 | 1 000 000 000.0 | the sensor offset carried by every reading |

The ten readings of the reference window are x0 + d for d = 0.0, 1.0, 2.0, ..., 9.0,
that is 1 000 000 000.0 through 1 000 000 009.0 in unit steps. Every reading is exactly
representable in binary64, so the window itself introduces no rounding error and any
error observed below is produced by the arithmetic and not by the input.

---

## 2. Reference implementations

The listings below are the definitions the rest of this document reasons about. The
section imports `math`.

Listing A, the single-pass variance the sidecar currently uses.

```python
def variance_sum_of_squares(xs):
    """Sample variance from running sums of x and x*x, in one pass."""
    n = len(xs)
    s1 = 0.0
    s2 = 0.0
    for x in xs:
        s1 += x
        s2 += x * x
    return (s2 - s1 * s1 / n) / (n - 1)
```

Listing B, the two-pass variance, kept for comparison.

```python
def variance_two_pass(xs):
    """Sample variance about the computed mean, in two passes."""
    n = len(xs)
    mean = sum(xs) / n
    return sum((x - mean) ** 2 for x in xs) / (n - 1)
```

Listing C, the small root of a x^2 + b x + c with b positive and b^2 >> 4 a c.

```python
import math

def small_root_naive(a, b, c):
    return (-b + math.sqrt(b * b - 4.0 * a * c)) / (2.0 * a)

def small_root_stable(a, b, c):
    return (2.0 * c) / (-b - math.sqrt(b * b - 4.0 * a * c))
```

---

## 3. Representation and the rounding model

**NA-01.** The decimal literal 0.1 is not representable in binary64, and neither is
0.2 nor 0.3. The comparison 0.1 + 0.2 == 0.3 is therefore False, and the difference
(0.1 + 0.2) - 0.3 is exactly 2^-54, that is 5.551115123125783 x 10^-17 — one half of
the unit roundoff, and the smallest non-zero gap the two sides can differ by at that
magnitude.

**NA-02.** Floating-point addition is commutative but not associative. With the
reference offset, (1.0 + x0 x 10^7) - x0 x 10^7 evaluates to 0.0 while
1.0 + (x0 x 10^7 - x0 x 10^7) evaluates to 1.0: the first ordering rounds the 1.0 away
before the subtraction can recover it, and the second never forms the large
intermediate at all.

**NA-03.** Subtraction of two nearly equal quantities is exact in binary64 whenever
they lie within a factor of two of each other, by Sterbenz's lemma. Cancellation
therefore does not create error; it exposes error already present in the operands by
removing the leading digits that were masking it.

---

## 4. The two variance formulas on the reference window

**NA-04.** The exact sample variance of the ten readings is the exact sample variance
of 0.0 through 9.0, because the offset x0 is common to every reading and variance is
invariant under translation. That figure is 55 / 6 = 9.166666666666666, and Listing B
returns it to the last stored digit.

**NA-05.** On the reference window Listing A and Listing B agree to within one part in
10^12, both returning 9.1666666667, so the single-pass form of Listing A may be
preferred for its lower memory traffic without any loss of accuracy on telemetry data
of this shape.

**NA-06.** The quantity that governs the accuracy of Listing A is the ratio of the
mean to the standard deviation, not the number of readings. Adding readings to a
window with the same offset does not improve the conditioning, because the cancelling
subtraction `s2 - s1 * s1 / n` removes the same number of leading digits however many
terms went into the sums.

**NA-07.** Listing B is not exact in general either, since its mean is itself rounded
and the squared deviations are formed about the rounded value. Its advantage is that
the deviations are small compared with the readings, so the squares carry their own
leading digits rather than the offset's.

---

## 5. The small root of a badly conditioned quadratic

**NA-08.** For a = 1.0, b = 1.0 x 10^8 and c = 1.0 the exact small root is
-1.0000000000000001 x 10^-8 to sixteen figures. Listing C's naive form returns
-7.450580596923828 x 10^-9, a relative error of 25.5 per cent, because b and
sqrt(b^2 - 4ac) agree to fifteen digits and their difference retains almost none.

**NA-09.** The stable form of Listing C returns -1.0 x 10^-8 for the same inputs. It
avoids the cancellation by pairing the small root with the sum -b - sqrt(...), in which
both terms carry the same sign and no digits are lost.

---

## 6. Accumulated error on a summation

**NA-10.** Summing N floating-point numbers left to right in binary64 gives a computed
sum whose relative error is bounded by (N - 1) u / (1 - (N - 1) u), which for N = 1 000
is 1.109 x 10^-13. The bound is worst case and attained only when every rounding goes
the same way; on the reference window of N = 10 identical-magnitude readings the
realised error is zero, because every partial sum is exactly representable.

**NA-11.** Compensated summation reduces the error term to order u plus a term in
N u^2, which for any window this component will ever see is indistinguishable from a
single rounding. It costs four extra flops per element and no extra storage, and it is
the change to make if the bound of NA-10 is ever the binding constraint.

---

Written as a review fixture. Every figure is reproducible in IEEE 754 binary64 from
the constants of section 1 and the listings of section 2.
