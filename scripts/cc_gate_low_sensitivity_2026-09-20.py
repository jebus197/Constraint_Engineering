"""Q3: does the two-sided gate close the R* = b/(p+b) hole, or only appear to?

The gate's condition (a) counts NOVEL CRITICAL FINDINGS -- i.e. DETECTED defects.
The residual risk depends on UNDETECTED introduced defects.  If a repair injects a
defect class the SAME review is LESS sensitive to, the injected defect does not
surface as a critical, the zero-critical streak accrues, and the gate CONVERGES
while risk is at equilibrium.  Constructed and executed against the REAL gate.

Run: python3 scripts/cc_gate_low_sensitivity_2026-09-20.py
"""
import sys, random
from pathlib import Path
import sympy as sp, mpmath as mp
sys.path.insert(0, str(Path("bench").resolve()))
import reference_runner_v3 as rr

mp.mp.dps = 40
gate = rr._check_gamma_alt_convergence
cfg = rr.RunnerConfig()
K = cfg.gamma_alt_consecutive_zero_crit
E = cfg.gamma_alt_earliest_round
print(f"REAL gate config: window K={K}, earliest_round={E}")

def call(hist, **kw):
    kw.setdefault("gamma", 0.001)          # FLAT gamma
    return gate(max(E, len(hist)-1), kw.pop("gamma"), hist, cfg, **kw)

# --- Control: reproduce the brief's 3.5 claims against the real function -------
print("\n[CONTROL] reproducing PANEL_BRIEF 3.5 against the real gate")
c1 = call([0]*K);                      print(f"  flat gamma, 0 new criticals : {c1[0]}  {c1[1][:70]}")
c2 = call([2]*K);                      print(f"  flat gamma, 2/round         : {c2[0]}  {c2[1][:70]}")
c3 = call([0]*(K-1)+[1]);              print(f"  1 new critical in last round: {c3[0]}  {c3[1][:70]}")
c4 = call([0]*K, unresolved_critical=1);print(f"  unresolved critical (A4)    : {c4[0]}  {c4[1][:70]}")

# --- THE CONSTRUCTED CASE -----------------------------------------------------
# Repairs inject at rate b.  Original defect class detected at sensitivity p.
# INJECTED class detected at p' < p.  Each round the panel reports as NOVEL
# CRITICAL only what it DETECTS.  Simulate the observable series the gate sees.
print("\n[CONSTRUCTED] repair injects a class the review is LESS sensitive to")
p, p_inj, b = 0.35, 0.05, 0.10
Rstar_same = b/(p+b)            # if injected class detected at p
Rstar_low  = b/(p_inj+b)        # if injected class detected at p'
print(f"  p={p} p'={p_inj} b={b}")
print(f"  equilibrium residual if injected class seen at p : {Rstar_same:.2%}")
print(f"  equilibrium residual if injected class seen at p': {Rstar_low:.2%}")

rng = random.Random(20260920)
TRIALS = 200000
conv = 0
for _ in range(TRIALS):
    hist = []
    for _r in range(K):
        injected = 1 if rng.random() < b else 0          # a repair damaged a clean region
        detected = 1 if (injected and rng.random() < p_inj) else 0
        hist.append(detected)
    if gate(max(E, K-1), 0.001, hist, cfg)[0]:
        conv += 1
emp = conv/TRIALS
theo = float((1 - b*p_inj)**K)
# Wilson 95% interval on the proportion
import statsmodels.stats.proportion as smp
lo, hi = smp.proportion_confint(conv, TRIALS, alpha=0.05, method="wilson")
print(f"  gate CONVERGES in {conv}/{TRIALS} = {emp:.4%}  Wilson95=[{lo:.4%}, {hi:.4%}]")
print(f"  closed form (1-b*p')^K = {theo:.4%}   inside interval: {lo <= theo <= hi}")
assert lo <= theo <= hi, "closed form outside Wilson interval"

# Contrast: same b, but injected class detected at the SAME sensitivity p.
conv2 = 0
for _ in range(TRIALS):
    hist = []
    for _r in range(K):
        injected = 1 if rng.random() < b else 0
        hist.append(1 if (injected and rng.random() < p) else 0)
    if gate(max(E, K-1), 0.001, hist, cfg)[0]:
        conv2 += 1
lo2, hi2 = smp.proportion_confint(conv2, TRIALS, alpha=0.05, method="wilson")
print(f"  [contrast p'=p] gate converges {conv2/TRIALS:.4%} Wilson95=[{lo2:.4%},{hi2:.4%}]"
      f"  closed form={(1-b*p)**K:.4%}")

print("\n[VERDICT]")
print(f"  With a LOW-sensitivity injected class the gate certifies convergence "
      f"{emp:.2%} of the time while equilibrium residual risk is {Rstar_low:.2%}.")
print(f"  The gate does NOT close the hole: it closes it only to the extent the "
      f"SAME review detects the injected class.  Blind spot scales as (1-b*p')^K.")
print(f"  Gate detection power against injection = 1-(1-b*p')^K = {1-theo:.3%}")
