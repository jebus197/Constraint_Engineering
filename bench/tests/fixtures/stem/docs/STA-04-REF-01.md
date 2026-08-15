# Batch Acceptance Statistics for Yield Strength — Method Reference

**Document ID:** STA-04-REF-01
**Scope:** One acceptance procedure (the twenty-five-specimen tensile check applied to
each incoming plate batch), together with the reference implementation that defines
it: the point estimate, the dispersion estimate and its bias, the interval estimate,
and the sample size required to reach a stated precision.
**Status:** Internal technical reference. Assertions carry traceability tags (ST-nn)
so review is logged against individual statements rather than whole sections.

---

## 1. The measurement and its conventions

Twenty-five specimens are drawn from each batch and pulled to yield. The twenty-five
readings are treated as independent draws from a single normal population whose mean
and variance are both unknown; that assumption is what licenses everything below, and
where a statement depends on it the dependence is named. All strengths are megapascals.

Every interval quoted is a two-sided interval at the 95 per cent nominal level. The
level is a property of the procedure across repeated batches, not of any one interval
already computed, and section 4 states that distinction as a claim rather than leaving
it to the reader.

The twenty-five readings for batch 2026-114, printed in full so every figure below is
recomputable:

| # | MPa | # | MPa | # | MPa | # | MPa | # | MPa |
|---|-----|---|-----|---|-----|---|-----|---|-----|
| 1 | 352.1 | 6 | 358.6 | 11 | 357.2 | 16 | 359.9 | 21 | 346.2 |
| 2 | 347.8 | 7 | 344.9 | 12 | 348.4 | 17 | 354.3 | 22 | 360.7 |
| 3 | 361.4 | 8 | 366.3 | 13 | 362.0 | 18 | 347.1 | 23 | 352.9 |
| 4 | 355.0 | 9 | 353.7 | 14 | 351.6 | 19 | 363.5 | 24 | 349.8 |
| 5 | 349.2 | 10 | 350.5 | 15 | 345.7 | 20 | 356.8 | 25 | 358.1 |

---

## 2. Reference implementation

The listing below is the definition the rest of this document reasons about. It
imports `math` and `statistics` from the standard library.

```python
import math
import statistics

def batch_summary(xs):
    """Return (n, mean, sample_sd) for a batch of readings."""
    n = len(xs)
    mean = statistics.fmean(xs)
    sample_sd = statistics.stdev(xs)          # divides by n - 1
    return n, mean, sample_sd

def mean_ci(xs, crit=1.96):
    """Two-sided 95% confidence interval for the population mean."""
    n, mean, sd = batch_summary(xs)
    half = crit * sd / math.sqrt(n)
    return mean - half, mean + half

def required_n(sigma, half_width, crit=1.96):
    """Smallest n reaching the stated half-width at the stated critical value."""
    return math.ceil((crit * sigma / half_width) ** 2)
```

---

## 3. Point estimates and the bias of the dispersion estimate

**ST-01.** For batch 2026-114 the sample mean is 354.148 MPa and the sample standard
deviation, taken with the divisor n - 1, is 6.0901 MPa. The corresponding standard
error of the mean is 6.0901 / sqrt(25) = 1.2180 MPa.

**ST-02.** Dividing the sum of squared deviations by n rather than n - 1 gives
5.9671 MPa on the same readings, a figure 2.0 per cent smaller. The two differ because
the deviations are taken about the sample mean, which is itself fitted to the data and
therefore sits closer to the readings than the population mean does.

**ST-03.** The estimator that divides by n is biased low by exactly the factor
(n - 1) / n in the variance: its expectation is ((n - 1) / n) sigma^2, which at n = 25
is 0.96 sigma^2. Dividing by n - 1 removes that factor exactly, which is why the
n - 1 form is the unbiased one and why the correction matters most at small n and
vanishes as n grows.

**ST-04.** Unbiasedness of the variance estimator does not carry over to the standard
deviation, because the square root is a concave function and Jensen's inequality
makes E[s] strictly less than sigma whenever s has non-zero variance. The n - 1
divisor therefore yields an unbiased variance and a slightly biased standard
deviation, and the document quotes s as an estimate rather than as an unbiased one.

---

## 4. The interval estimate

**ST-05.** With n = 25 the sample is large enough that the normal critical value
1.96 may be used in place of the Student t value, so the half-width of the 95 per cent
confidence interval for the mean is 1.96 x 1.2180 = 2.387 MPa and the interval is
[351.761, 356.535] MPa. This is the interval the reference implementation of section 2
returns, and it is the interval quoted on the batch certificate.

**ST-06.** The 95 per cent level attaches to the procedure, not to the realised
interval. Over many batches, 95 per cent of the intervals so constructed contain the
true batch mean; the interval already computed for batch 2026-114 either contains it
or does not, and no probability statement about that particular interval follows from
the construction.

**ST-07.** The interval narrows only as the square root of the sample size, so
quartering the half-width demands sixteen times the specimens. That is a property of
the standard error and not of the critical value, and it holds whichever critical
value is used.

---

## 5. Sample size

**ST-08.** Taking sigma = 6.0 MPa as a planning value from historical batches, the
sample size needed for a 95 per cent half-width of 1.5 MPa is (1.96 x 6.0 / 1.5)^2 =
61.46, rounded up to 62 specimens. The rounding is always upward, since 61 specimens
would leave the half-width above the target.

**ST-09.** Relaxing the target half-width from 1.5 MPa to 2.0 MPa cuts the requirement
to (1.96 x 6.0 / 2.0)^2 = 34.57, that is 35 specimens — a reduction of 43.5 per cent in
testing for a 33 per cent loss of precision, which is the usual shape of the trade
under an inverse-square law.

**ST-10.** The planning figure sigma = 6.0 MPa is itself an estimate, so the sample
sizes above are conditional on it. Using the batch's own s = 6.0901 MPa instead raises
the 1.5 MPa requirement from 62 to 64 specimens; the requirement scales as sigma
squared, so a 1.5 per cent error in the planning value moves the answer by about 3 per
cent.

---

Written as a review fixture. Every figure is recomputable from the twenty-five
readings of section 1 and the listing of section 2.
