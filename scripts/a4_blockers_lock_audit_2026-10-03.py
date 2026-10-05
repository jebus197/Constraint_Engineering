#!/usr/bin/env python3
"""Which locks hold each A4 blocker shut, for a finished run.

The A4 fail-safe (unverified_critical_count, reference_runner_v3.py:2747) blocks
the zero-critical streak while any UNCONFIRMED critical is pending. The only
escape is the `exhausted` valve, which needs THREE conditions at once:

    status in EXHAUSTED_ELIGIBLE_STATUSES  and  severity >= 0.7
    and  age >= exhausted_round_threshold  and  len(verdicts) > 0

This prints, per blocking entry, which of those are open and which are shut, so
a proposed threshold change can be judged against the entries it would have to
free rather than against the mechanism in the abstract.
"""
import argparse, json, pathlib
import numpy as np
from statsmodels.stats.proportion import proportion_confint
import mpmath as mp

VALVE = ("OPEN", "CONTESTED", "REOPENED", "CORROBORATED", "WITHHELD", "UNCONFIRMED")
CRIT = 0.7

ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("--run", default=None)
ap.add_argument("--threshold", type=int, default=8)
ap.add_argument("--rounds", type=int, default=8)
a = ap.parse_args()

if getattr(a, "run", None) is None:
    ap.error("--run is required")

run = pathlib.Path(a.run)
d = json.loads((run / "runner_state.json").read_text(errors="replace"))
entries = (d.get("registry") or {}).get("entries") or {}
final_round = a.rounds - 1          # 0-based

blockers = {cid: e for cid, e in entries.items()
            if e.get("status") == "UNCONFIRMED" and e.get("severity", 0) >= CRIT}

print(f"run: {run.name}   entries: {len(entries)}   "
      f"final round_idx: {final_round}   threshold: {a.threshold}")
print(f"A4 blockers (UNCONFIRMED and severity >= {CRIT}): {len(blockers)}")
print()

would_free_now, would_free_at_7, shut_by_reviews = [], [], []
for cid, e in sorted(blockers.items()):
    lscr = e.get("last_status_change_round", 0)
    age = final_round - lscr
    nverd = len(e.get("verdicts", []) or [])
    l_status = e.get("status") in VALVE
    l_sev = e.get("severity", 0) >= CRIT
    l_age = age >= a.threshold
    l_rev = nverd > 0
    print(f"  {cid}  severity={e.get('severity'):.2f}  status={e.get('status')}")
    print(f"      last_status_change_round={lscr}  age at final round={age}")
    print(f"      verdicts={nverd}")
    print(f"      LOCKS -> status:{'OPEN' if l_status else 'SHUT'}  "
          f"severity:{'OPEN' if l_sev else 'SHUT'}  "
          f"age>={a.threshold}:{'OPEN' if l_age else 'SHUT'}  "
          f"has_reviews:{'OPEN' if l_rev else 'SHUT'}")
    freed = l_status and l_sev and l_age and l_rev
    freed_t7 = l_status and l_sev and (age >= final_round) and l_rev
    print(f"      valve fires as configured (T={a.threshold}): {freed}")
    print(f"      valve would fire at T={final_round}: {freed_t7}")
    print()
    if freed: would_free_now.append(cid)
    if freed_t7: would_free_at_7.append(cid)
    if not l_rev: shut_by_reviews.append(cid)

n = len(blockers)
print(f"SUMMARY over {n} blocker(s):")
print(f"  freed as configured (T={a.threshold}) : {len(would_free_now)} {would_free_now}")
print(f"  freed if T lowered to {final_round}        : {len(would_free_at_7)} {would_free_at_7}")
print(f"  still shut by has_reviews         : {len(shut_by_reviews)} {shut_by_reviews}")
print()

if n:
    k = len(shut_by_reviews)
    lo, hi = proportion_confint(k, n, method="wilson")
    # cross-check the interval in mpmath, as the project requires 2 tools
    mp.mp.dps = 30
    z = mp.mpf("1.959963984540054235309065817"); ph = mp.mpf(k)/n; nn = mp.mpf(n)
    c = (ph + z**2/(2*nn)) / (1 + z**2/nn)
    hw = (z/(1+z**2/nn)) * mp.sqrt(ph*(1-ph)/nn + z**2/(4*nn**2))
    assert abs(float(c-hw)-lo) < 1e-9 and abs(float(c+hw)-hi) < 1e-9, \
        "statsmodels and mpmath disagree on the Wilson interval"
    print(f"  shut by has_reviews: {k}/{n} = {100.0*k/n:.4f}%  "
          f"Wilson [{100*lo:.4f}%, {100*hi:.4f}%]  (statsmodels == mpmath)")

    ages = np.array([final_round - e.get("last_status_change_round", 0)
                     for e in blockers.values()])
    print(f"  ages (NumPy): min={ages.min()} max={ages.max()} "
          f"mean={ages.mean():.4f}")
    print(f"  threshold needed to free the OLDEST blocker: {ages.max()}")
