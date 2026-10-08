# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'rung_promotion_and_model_ids_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 143bedcf955b8e5734e355ac5c07e136f40f42d4267d768af83fa7faa625dba3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Falsifier for bench/promotion_gate.py. Imports the real module.

FAILS (AssertionError / prints FALSIFIED) iff the derived gate misses its
stated targets or the ladder dynamics contradict them. Exits cleanly iff the
gate does what bench/promotion_gate.py claims.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench.promotion_gate import (  # noqa: E402  -- the REAL target module
    ALPHA_TOP, BETA_TOTAL, DROP_DETECT, HOLD_SAFETY, P_BAD, P_DROP, P_GOOD,
    R_RUNGS, RungLadderState, derive_demotion_window, derive_promotion_gate)

from scipy.stats import binom
import numpy as np

fails = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FALSIFIED'}: {name} {detail}")
    if not cond:
        fails.append(name)


# ---- 1. the derived gate hits the per-campaign targets (closed form) ----
n_gate, k_gate = derive_promotion_gate()
q_good = float(binom.sf(k_gate - 1, n_gate, P_GOOD))
q_bad = float(binom.sf(k_gate - 1, n_gate, P_BAD))
top_good = q_good ** R_RUNGS
top_bad = q_bad ** R_RUNGS
print(f"derived gate: n={n_gate}, k={k_gate}; per-rung pass good={q_good:.6f} "
      f"bad={q_bad:.6f}; per-campaign top good={top_good:.6f} bad={top_bad:.2e}")
check("good model tops out >= 1-beta", top_good >= 1 - BETA_TOTAL,
      f"({top_good:.6f} vs {1-BETA_TOTAL})")
check("bad model tops out <= alpha", top_bad <= ALPHA_TOP,
      f"({top_bad:.2e} vs {ALPHA_TOP})")
# minimality: no smaller n admits any k meeting both targets
qg_req, qb_max = (1 - BETA_TOTAL) ** (1 / R_RUNGS), ALPHA_TOP ** (1 / R_RUNGS)
smaller_works = any(
    binom.sf(k - 1, n, P_GOOD) >= qg_req and binom.sf(k - 1, n, P_BAD) <= qb_max
    for n in range(1, n_gate) for k in range(1, n + 1))
check("n_gate is minimal", not smaller_works)
# the brief's (10, floor 0.50 -> 9/10) gate is dominated by this one for the
# good model AND for the bad model -- committed measurement for replacing it:
old_good = float(binom.sf(8, 10, P_GOOD)) ** R_RUNGS
old_bad = float(binom.sf(8, 10, P_BAD)) ** R_RUNGS
check("derived gate dominates 9/10-floor gate on good admission",
      top_good > old_good, f"({top_good:.4f} vs {old_good:.4f})")

# ---- 2. the derived demotion window hits its targets ----
w_dem, j_dem = derive_demotion_window()
healthy = float(binom.cdf(j_dem, w_dem, P_GOOD))
degraded = float(binom.cdf(j_dem, w_dem, P_DROP))
print(f"derived demotion: W={w_dem}, j={j_dem}; "
      f"P(demote|healthy)={healthy:.2e} P(demote|degraded)={degraded:.4f}")
check("healthy model survives window", healthy <= HOLD_SAFETY)
check("degraded model caught", degraded >= DROP_DETECT)

# ---- 3. simulate the full ladder: non-absorbing + ergodic occupancy ----
rng = np.random.default_rng(20261008)


def run(p, blocks=400):
    """Alternate: one gate block at the candidate rung, then W held attempts."""
    s = RungLadderState()
    occupancy = np.zeros(R_RUNGS + 1)
    for _ in range(blocks):
        for _ in range(n_gate):
            s.observe_gate(rng.random() < p, n_gate, k_gate, R_RUNGS)
        for _ in range(w_dem):
            s.observe_held(rng.random() < p, w_dem, j_dem)
        occupancy[s.rung] += 1
    return s, occupancy / occupancy.sum()


trials = 300
good_top_frac = np.mean([run(P_GOOD, blocks=40)[1][R_RUNGS] > 0 for _ in range(trials)])
check("good model reaches top despite early bad luck (non-absorbing)",
      good_top_frac >= 0.99, f"(reached in {good_top_frac:.3f} of {trials} runs)")

_, occ_bad = run(P_BAD, blocks=1000)
top_occ_bad = float(occ_bad[R_RUNGS - 1] + occ_bad[R_RUNGS])
print(f"  p={P_BAD} long-run occupancy by rung: {np.round(occ_bad, 3).tolist()}")
check("bad model's occupancy of top two rungs is bounded", top_occ_bad <= 0.05,
      f"(occupies top-2 {top_occ_bad:.4f} of blocks)")

# ---- 4. bidirectionality: a model that degrades 0.9 -> 0.4 descends ----
s = RungLadderState()
for _ in range(200):     # climb as a 0.9 model
    for _ in range(n_gate):
        s.observe_gate(rng.random() < P_GOOD, n_gate, k_gate, R_RUNGS)
rung_before = s.rung
for _ in range(50):      # degrade to 0.4; only held-rung work now
    for _ in range(w_dem):
        s.observe_held(rng.random() < P_DROP, w_dem, j_dem)
check("degraded model descends (bidirectional)",
      rung_before >= R_RUNGS - 1 and s.rung < rung_before,
      f"(rung {rung_before} -> {s.rung})")

print()
if fails:
    print("FALSIFIED:", fails)
    raise AssertionError(fails)
print("ALL CHECKS PASS -- the derived gate meets every stated target.")
