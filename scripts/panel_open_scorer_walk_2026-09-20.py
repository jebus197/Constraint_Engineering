#!/usr/bin/env python3
"""Independent open-round re-measurement of the scorer claims (Section 5)."""
import json, glob, math
from collections import Counter

# WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
# ran the whole measurement. A help flag must ANSWER, never ACT.
from _cli_help import answer_help  # noqa: E402
answer_help(__doc__, __file__)

def wilson(k, n):
    if n == 0: return (0.0, 0.0)
    z = 1.959963984540054; p = k / n
    d = 1 + z*z/n; ctr = p + z*z/(2*n)
    hw = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return ((ctr-hw)/d, (ctr+hw)/d)

tri = Counter(); A_vals = Counter(); sk_admiss = []; rej_sk = Counter()
gate_scores = {}; e2_absent_at_ceiling = 0; ceiling = 0
for f in sorted(glob.glob('bench/logs/*/runner_state.json')):
    try: data = json.load(open(f, errors='ignore'))
    except Exception: continue
    def walk(o):
        global e2_absent_at_ceiling, ceiling
        if isinstance(o, dict):
            sk = o.get('sk_result')
            if isinstance(sk, dict) and 'tristate' in sk:
                t = sk['tristate']; tri[t] += 1
                if 'A' in sk: A_vals[sk['A']] += 1
                if t == 'ADMISSIBLE':
                    sk_admiss.append(sk.get('sk'))
                    gs = sk.get('gate_scores') or {}
                    for gname, gv in (gs.items() if isinstance(gs, dict) else []):
                        gate_scores.setdefault(gname, Counter())[gv] += 1
                    if abs(sk.get('sk', 0) - 1.0) < 1e-12:
                        ceiling += 1
                        if isinstance(gs, dict) and 'e2_regression' not in gs:
                            e2_absent_at_ceiling += 1
                elif t == 'REJECTED':
                    rej_sk[sk.get('sk')] += 1
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(data)

n_adm = len(sk_admiss); ones = sum(1 for s in sk_admiss if abs(s-1.0) < 1e-12)
lo, hi = wilson(ones, n_adm)
print(f"tristate: {dict(tri)}")
print(f"A values across all decisions: {dict(A_vals)}")
print(f"ADMISSIBLE: {n_adm}; sk == 1.0: {ones} = {ones/n_adm:.4%}  Wilson [{lo:.4%}, {hi:.4%}]")
print(f"min admissible sk: {min(sk_admiss)}")
print(f"REJECTED sk values: {dict(rej_sk)}")
print(f"ceiling scores with e2_regression ABSENT: {e2_absent_at_ceiling} of {ceiling}")
for gname, ctr in sorted(gate_scores.items()):
    tot = sum(ctr.values())
    print(f"  gate {gname:14s} distinct={len(ctr):3d}  ==1.0 in {ctr.get(1.0,0)}/{tot}")
try:
    from statsmodels.stats.proportion import proportion_confint
    lo2, hi2 = proportion_confint(ones, n_adm, alpha=0.05, method='wilson')
    print(f"statsmodels Wilson agrees: {abs(lo-lo2)<1e-12 and abs(hi-hi2)<1e-12}")
except ImportError:
    print("statsmodels unavailable")
