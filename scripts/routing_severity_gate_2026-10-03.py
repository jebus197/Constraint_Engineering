#!/usr/bin/env python3
"""Does routing serve only criticals while A4 counts every severity?

`_apply_routing` (bench/reference_runner_v3.py:6899) skips any entry below
CRITICAL_SEVERITY_THRESHOLD. `unverified_critical_count` (:2747) has had NO
severity gate since founder ruling 23 (2026-09-06). If both hold, a finding
below 0.7 can never be served a falsifier, can never be released by the
`exhausted` valve (which also gates at 0.7), and is counted against A4 for the
life of the run.

This measures the association on a FINISHED run's registry rather than reading
the source: routed (has a routing_history) against severity >= 0.7.
"""
import argparse, json, pathlib
import numpy as np
from scipy import stats as sps
from statsmodels.stats.proportion import proportion_confint
from statsmodels.stats.contingency_tables import Table2x2
import mpmath as mp

CRIT = 0.7
ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("--state", default=None)
a = ap.parse_args()

if getattr(a, "state", None) is None:
    ap.error("--state is required")

d = json.loads(pathlib.Path(a.state).read_text(errors="replace"))
entries = (d.get("registry") or {}).get("entries") or {}

rows = []
for cid, e in entries.items():
    sev = float(e.get("severity") or 0.0)
    rh = e.get("routing_history")
    routed = bool(rh)
    rows.append((cid, sev, sev >= CRIT, routed))

crit_routed = sum(1 for _, _, c, r in rows if c and r)
crit_unrouted = sum(1 for _, _, c, r in rows if c and not r)
sub_routed = sum(1 for _, _, c, r in rows if not c and r)
sub_unrouted = sum(1 for _, _, c, r in rows if not c and not r)

print(f"entries: {len(rows)}")
print()
print("                      routed   not routed")
print(f"  severity >= {CRIT}      {crit_routed:5d}   {crit_unrouted:9d}")
print(f"  severity <  {CRIT}      {sub_routed:5d}   {sub_unrouted:9d}")
print()

# Fisher exact, two tools
table = [[crit_routed, crit_unrouted], [sub_routed, sub_unrouted]]
odds_sp, p_sp = sps.fisher_exact(table)
print(f"  scipy Fisher exact : p = {p_sp:.6e}  OR = {odds_sp}")
try:
    t2 = Table2x2(np.array(table) + 0.5)   # Haldane correction for a zero cell
    print(f"  statsmodels Table2x2 (Haldane-corrected) OR = "
          f"{t2.oddsratio:.6f}, 95% CI {tuple(round(x,6) for x in t2.oddsratio_confint())}")
except Exception as exc:
    print(f"  statsmodels Table2x2 unavailable: {exc}")

# the decisive proportion: of SUB-critical entries, how many were ever routed?
n_sub = sub_routed + sub_unrouted
if n_sub:
    lo, hi = proportion_confint(sub_routed, n_sub, method="wilson")
    mp.mp.dps = 30
    z = mp.mpf("1.959963984540054235309065817"); ph = mp.mpf(sub_routed)/n_sub; nn = mp.mpf(n_sub)
    c = (ph + z**2/(2*nn))/(1 + z**2/nn)
    hw = (z/(1+z**2/nn))*mp.sqrt(ph*(1-ph)/nn + z**2/(4*nn**2))
    assert abs(float(c-hw)-lo) < 1e-9 and abs(float(c+hw)-hi) < 1e-9, \
        "statsmodels and mpmath disagree on Wilson"
    print()
    print(f"  SUB-CRITICAL entries ever routed: {sub_routed}/{n_sub} = "
          f"{100.0*sub_routed/n_sub:.4f}%  Wilson [{100*lo:.4f}%, {100*hi:.4f}%]"
          f"  (statsmodels == mpmath)")

# and the A4 blockers specifically
print()
print("  THE A4 BLOCKERS (UNCONFIRMED, no resolved falsifier):")
for cid, e in sorted(entries.items()):
    if e.get("status") != "UNCONFIRMED":
        continue
    sev = float(e.get("severity") or 0.0)
    rh = e.get("routing_history")
    print(f"    {cid}  sev={sev:.2f}  {'>=0.7' if sev>=CRIT else '< 0.7'}  "
          f"routing_history={'present len '+str(len(rh)) if rh else 'ABSENT'}")
