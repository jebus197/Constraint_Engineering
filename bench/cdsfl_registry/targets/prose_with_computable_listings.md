# Estimator Note: Dispersion and Interval Reporting in Run Summaries

A short technical note for review. It describes how a run summary reports the
spread of a per-round measurement and the interval on a proportion, and it
carries the two small listings that implement them.

## 1. Setup

A run produces one scalar per round. A summary reports the dispersion of those
scalars and, separately, a 95% interval on a proportion derived from counts of
findings. Both are quoted to a reader who will not re-derive them.

## 2. The claims under test

**Claim PL-01.** The dispersion helper below reports an **unbiased** estimate of
the population variance from a sample of rounds, so the figure it prints may be
quoted directly as the variance of the underlying process.

```python
def round_dispersion(values):
    """Unbiased sample variance of the per-round scalars."""
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    return sum((v - mean) ** 2 for v in values) / n
```

**Claim PL-02.** The interval helper below computes the Wilson score interval at
95%, and agrees with the standard implementation to within floating-point error,
so a proportion quoted with it needs no second tool.

```python
def wilson_interval(k, n, z=1.959963984540054):
    """Wilson score interval for k successes in n trials."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    centre = p + z ** 2 / n
    half = z * ((p * (1 - p) / n + z ** 2 / (4 * n ** 2)) ** 0.5)
    denominator = 1 + z ** 2 / n
    return ((centre - half) / denominator, (centre + half) / denominator)
```

**Claim PL-03.** Reporting dispersion alongside an interval is the right
presentation for this audience, because a reader who sees both is less likely to
over-read a single round's movement than one who sees only a central value.

## 3. What a reviewer is asked to do

Each claim is either computationally reducible or it is not, and the two kinds
should not be answered the same way. PL-01 and PL-02 are statements about the
listings beneath them and can be settled by executing those listings against a
reference. PL-03 is a statement about presentation and a reader's likely
inference; it carries no listing and no reference implementation, so it is not
settled by execution.
