#!/usr/bin/env python3
"""Characterise WHEN the reviewed file was rewritten during the 2026-09-08 Exp 45 run.

Input: bench/logs/target_mutation_watch_2026-09-08/target_state_transitions.log,
written by the 15-second poll loop that ran as background task bx051kc0l from
07:14 to 16:40 BST on 2026-09-08. Each line records a blob hash for
bench/dm/_memory.py that the poller had not seen before.

The question this answers: were the rewrites spread evenly across the run (many
seats each editing as they went), or concentrated in a burst (one seat editing
repeatedly)? Even spread and burst have different remedies, so the shape matters.

Two tools per claim, per the 21 Apr 2026 cross-verification rule.
"""
import re, datetime as dt
from pathlib import Path

import numpy as np
from scipy import stats as sps
from statsmodels.stats.proportion import proportion_confint
import mpmath as mp

LOG = Path("bench/logs/target_mutation_watch_2026-09-08/target_state_transitions.log")
ts, sizes = [], []
for line in LOG.read_text().splitlines():
    m = re.match(r"NEW target state (\d+) at (\d\d:\d\d:\d\d): blob (\w+), (\d+) bytes", line)
    if m:
        h, mi, s = (int(x) for x in m.group(2).split(":"))
        ts.append(h * 3600 + mi * 60 + s)
        sizes.append(int(m.group(4)))

t = np.array(ts, dtype=float)
n = len(t)
span = t[-1] - t[0]
gaps = np.diff(t)
print(f"distinct target states logged     : {n}")
print(f"first / last                      : {dt.timedelta(seconds=int(t[0]))} -> {dt.timedelta(seconds=int(t[-1]))}")
print(f"window                            : {span:.0f} s ({span/60:.1f} min)")
print(f"gaps (s)                          : {', '.join(str(int(g)) for g in gaps)}")
print(f"median gap / max gap              : {np.median(gaps):.0f} s / {gaps.max():.0f} s")

# --- Clustering test 1: KS of arrival positions against Uniform over the window.
u = (t[1:-1] - t[0]) / span                      # interior points; endpoints are fixed by construction
ks = sps.kstest(u, "uniform")
print(f"\n[scipy]  KS vs uniform arrivals   : D={ks.statistic:.4f}, p={ks.pvalue:.4g}  (n={len(u)} interior)")

# --- Cross-check with an independent statistic: coefficient of variation of gaps.
# Poisson (memoryless) arrivals give CV = 1; bursts give CV > 1. Null band by Monte Carlo.
cv = gaps.std(ddof=1) / gaps.mean()
rng = np.random.default_rng(20260908)
sim = rng.random((200_000, n - 2))
sim.sort(axis=1)
edges = np.concatenate([np.zeros((200_000, 1)), sim, np.ones((200_000, 1))], axis=1)
g = np.diff(edges, axis=1) * span
cv_null = g.std(axis=1, ddof=1) / g.mean(axis=1)
p_cv = (cv_null >= cv).mean()
print(f"[numpy]  gap CV                   : {cv:.4f}   (uniform-null mean {cv_null.mean():.4f}), MC p={p_cv:.4g}")

# --- The burst: how many states landed in the first 10 minutes?
burst_win = 600.0
k = int(((t - t[0]) <= burst_win).sum())
print(f"\nstates within {burst_win:.0f}s of the first  : {k} of {n}")
lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
lo_c, hi_c = proportion_confint(k, n, alpha=0.05, method="beta")   # Clopper-Pearson
print(f"[statsmodels] Wilson 95%          : {k/n:.4f}  [{lo_w:.4f}, {hi_w:.4f}]")
print(f"[statsmodels] Clopper-Pearson 95% : {k/n:.4f}  [{lo_c:.4f}, {hi_c:.4f}]")

# mpmath closed-form Wilson, independent of statsmodels' implementation.
mp.mp.dps = 30
z = mp.mpf(str(sps.norm.ppf(0.975)))
p_hat, N = mp.mpf(k) / n, mp.mpf(n)
centre = (p_hat + z**2 / (2 * N)) / (1 + z**2 / N)
half = (z / (1 + z**2 / N)) * mp.sqrt(p_hat * (1 - p_hat) / N + z**2 / (4 * N**2))
print(f"[mpmath]      Wilson 95% (closed) : [{float(centre-half):.4f}, {float(centre+half):.4f}]")

# Probability of >=k of n uniform points landing in a 600s slice of the window, if spread evenly.
q = mp.mpf(burst_win) / mp.mpf(span)
tail = mp.nsum(lambda i: mp.binomial(n, i) * q**i * (1 - q)**(n - i), [k, n])
print(f"[mpmath]      P(>={k} of {n} in that slice | uniform) = {float(tail):.4g}")
print(f"[scipy ]      same via binom.sf        = {sps.binom.sf(k-1, n, float(q)):.4g}")

print(f"\nbytes vs HEAD, min/max            : {min(sizes)} / {max(sizes)}")
