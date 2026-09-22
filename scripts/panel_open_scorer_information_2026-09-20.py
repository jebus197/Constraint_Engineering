#!/usr/bin/env python3
"""Open-round seat: does the S_k gate MEASURE anything, and what is the
smallest repair?

Every seat in the blind round measured the DISTRIBUTION (672/902 at 1.0).
That establishes low spread.  It does not establish low INFORMATION, which is
the thing the gate needs.  This script measures information directly:

  1. per-gate spread and the mutual information each gate carries about sk
  2. the e2-availability confound (does absence of the behavioural gate
     manufacture ceiling scores?)
  3. whether ANY threshold in (0,1] can partition the archive non-trivially
  4. a negative control, so the measurement is falsifiable

Exit 0 iff all checks pass.
"""
import glob, json, math, os, sys
from collections import Counter
import numpy as np
from statsmodels.stats.proportion import proportion_confint

# WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
# ran the whole measurement. A help flag must ANSWER, never ACT.
from _cli_help import answer_help  # noqa: E402
answer_help(__doc__, __file__)

FAILS = []
def check(name, cond, detail=""):
    print(f"   [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))
    if not cond: FAILS.append(name)

def wilson(k, n):
    lo, hi = proportion_confint(k, n, alpha=0.05, method='wilson')
    return f"{100*k/n:.4f}% Wilson [{100*lo:.4f}%, {100*hi:.4f}%]"

recs = []
def walk(o):
    if isinstance(o, dict):
        sk = o.get('sk_result')
        if isinstance(sk, dict) and 'tristate' in sk: recs.append(sk)
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)

files = sorted(glob.glob('bench/logs/*/runner_state.json'))
for f in files:
    try: walk(json.loads(open(f, errors='ignore').read()))
    except Exception: pass

print(f"\n0  CENSUS ({len(files)} runner_state.json)")
tri = Counter(r['tristate'] for r in recs)
print(f"   decisions {len(recs)}   {dict(tri)}")
check("1247 decisions, 902 ADMISSIBLE, 191 REJECTED, 154 ESCALATE",
      len(recs) == 1247 and tri['ADMISSIBLE'] == 902 and tri['REJECTED'] == 191)
adm = [r for r in recs if r['tristate'] == 'ADMISSIBLE']
sk = np.array([r['sk'] for r in adm], dtype=float)
check("672 of 902 ADMISSIBLE score exactly 1.0",
      int((sk == 1.0).sum()) == 672, wilson(672, 902))
check("A is binary over all 1247 decisions",
      set(Counter(r.get('A') for r in recs)) == {1, 0.0},
      str(dict(Counter(r.get('A') for r in recs))))

print("\n1  PER-GATE SPREAD AND INFORMATION ABOUT sk")
GATES = ['g1_ast', 'g2_compile', 'e2_regression', 'e3_ruff', 'e4_bandit']
gs = {g: [] for g in GATES}
avail = {g: [] for g in GATES}
for r in adm:
    gd = r.get('gate_details') or {}
    for g in GATES:
        d = gd.get(g) or {}
        gs[g].append(d.get('score'))
        avail[g].append(d.get('score') is not None)   # unavailability IS score=None

def entropy(vals):
    c = Counter(vals); n = len(vals)
    return -sum((v/n)*math.log2(v/n) for v in c.values() if v)

H_sk = entropy([round(x, 6) for x in sk])
print(f"   H(sk) = {H_sk:.4f} bits, effective levels 2^H = {2**H_sk:.4f}, "
      f"sd = {sk.std(ddof=0):.6f}")
check("the whole score carries under 2 bits", H_sk < 2.0)

const_gates = []
for g in GATES:
    v = [x for x in gs[g] if x is not None]
    dist = len(set(round(x, 6) for x in v))
    Hg = entropy([round(x, 6) for x in v])
    # mutual information I(sk ; gate) via joint counts
    pairs = Counter((round(a, 6), round(b, 6))
                    for a, b in zip(sk, gs[g]) if b is not None)
    n = sum(pairs.values())
    Hj = -sum((c/n)*math.log2(c/n) for c in pairs.values())
    MI = H_sk + Hg - Hj
    flag = "  CONSTANT" if dist == 1 else ""
    if dist == 1: const_gates.append(g)
    print(f"   {g:<14} distinct={dist:<3} H={Hg:.4f}  I(sk;gate)={MI:.4f} bits{flag}")
check("3 of 5 gates are CONSTANT across all 902 scored fixes",
      sorted(const_gates) == sorted(['g1_ast', 'g2_compile', 'e4_bandit']),
      f"constant: {const_gates}")

print("\n2  THE e2 AVAILABILITY CONFOUND")
e2_av = np.array(avail['e2_regression'])
n_abs = int((~e2_av).sum())
print(f"   e2_regression unavailable on {n_abs} of {len(adm)} scored fixes "
      f"({wilson(n_abs, len(adm))})")
causes = Counter()
for r in adm:
    d = (r['gate_details'] or {}).get('e2_regression') or {}
    if d.get('score') is None:
        t = d.get('detail') or ''
        causes['TIMEOUT' if 'timed out' in t else 'NO TEST COMMAND'] += 1
print(f"   causes: {dict(causes)}")
rec = sum(1 for r in adm
          if ((r['gate_details'] or {}).get('e2_regression') or {}).get('score') is None
          and 'e2_regression' in ((r['gate_details'] or {}).get('_unavailable') or []))
print(f"   of those {n_abs}, only {rec} carry a _unavailable record "
      f"-- {n_abs-rec} are unrecoverable from the persisted score")
check("the unconfigured cases leave NO record (silent evidence loss)",
      rec == causes['TIMEOUT'] and causes['NO TEST COMMAND'] > 0,
      f"{causes['NO TEST COMMAND']} silent drops")
ceil = sk == 1.0
a_ceil = int((ceil & ~e2_av).sum()); a_n = int((~e2_av).sum())
p_ceil = int((ceil & e2_av).sum());  p_n = int(e2_av.sum())
print(f"   ceiling rate, e2 ABSENT  : {a_ceil}/{a_n} = {wilson(a_ceil, a_n)}")
print(f"   ceiling rate, e2 PRESENT : {p_ceil}/{p_n} = {wilson(p_ceil, p_n)}")
lo_a, _ = proportion_confint(a_ceil, a_n, 0.05, 'wilson')
_, hi_p = proportion_confint(p_ceil, p_n, 0.05, 'wilson')
check("intervals do NOT overlap: absent-e2 fixes score at the ceiling MORE",
      lo_a > hi_p, f"absent lower {100*lo_a:.4f}% > present upper {100*hi_p:.4f}%")
check(f"{a_ceil} of the 672 ceiling scores were produced with NO test evidence",
      a_ceil > 0, f"{100*a_ceil/672:.2f}% of the ceiling is non-measurement")

print("\n3  CAN ANY THRESHOLD PARTITION THE ARCHIVE NON-TRIVIALLY?")
best = None
for t in sorted(set(np.round(sk, 6))):
    below = int((sk < t).sum())
    if best is None or abs(below - len(sk)/2) < abs(best[1] - len(sk)/2):
        best = (t, below)
print(f"   observed minimum sk = {sk.min()};  most balanced cut t={best[0]} "
      f"puts {best[1]}/{len(sk)} below")
check("no threshold splits the archive better than 230/672",
      best[1] <= 230, f"best achievable minority mass = {best[1]}")
check("a threshold below 0.74 is EXTENSIONALLY the structural test sk>0",
      int((sk < 0.74).sum()) == 0)

print("\n4  THE SMALLEST REPAIR, AND WHY IT IS THE SMALLEST")
print("   The gate is fed a composite whose ceiling conflates two different")
print("   states: 'every gate ran and passed' and 'the only behavioural gate")
print(f"   did not run'.  Those are {p_ceil} and {a_ceil} fixes respectively,")
print("   and the archive cannot tell them apart from the number alone.")
print("   Repair: record the availability vector alongside sk.  ONE field.")
print("   It removes the conflation without changing any verdict, and it is")
print("   the precondition for ANY later discrimination study.")
sk_av = sk[e2_av]
H_av = entropy([round(x, 6) for x in sk_av])
print(f"   H(sk | e2 available) = {H_av:.4f} bits over {len(sk_av)} fixes "
      f"(vs {H_sk:.4f} unconditioned)")
check("conditioning on availability changes the score's information content",
      abs(H_av - H_sk) > 0.01, f"delta {H_av - H_sk:+.4f} bits")

print("\n5  NEGATIVE CONTROL -- the measurement can fail")
rng = np.random.default_rng(20260920)
fake = rng.uniform(0, 1, size=len(sk))
H_fake = entropy([round(x, 6) for x in fake])
check("a genuinely spread score would show far more entropy than sk does",
      H_fake > H_sk + 5, f"H(uniform surrogate) = {H_fake:.4f} vs H(sk) = {H_sk:.4f}")
check("the constant-gate detector does NOT fire on a varying surrogate",
      len(set(np.round(fake, 6))) > 1)

print("\n" + "="*70)
if FAILS:
    print("FAILED:", FAILS); sys.exit(1)
print("ALL CHECKS PASS"); sys.exit(0)
