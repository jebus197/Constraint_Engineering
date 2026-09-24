"""F7. A CONSTANT GATE AT WEIGHT 2.0 PUTS A HARD FLOOR UNDER sigma.

scripts/scorer_discrimination_2026-09-20.py measures e4_bandit at ZERO VARIANCE
across 902 decisions (distinct values 1, min=max=1.0) and g2_compile likewise.
A gate that is a constant at weight 2.0 in a renormalised weighted ARITHMETIC
mean cannot lower E — it can only hold it up.

CLAIM: with e4 pinned at 1.0, sk (hence sigma) has a positive lower bound BY
CONSTRUCTION, so compute_rk can never be told "this fix resolved nothing",
however the fix performs. FALSIFIED if the floor is 0.
"""
import sys, itertools, numpy as np
from z3 import Reals, Solver, And, sat, unsat
sys.path.insert(0, ".")
from bench.reference_runner_v3 import FIX_EFFICACY_GATE_WEIGHT as W1, compute_rk

# WIRED 2026-09-24 (CC1). Module-level work, so no main() to intercept `--help`.
import sys as _s, pathlib as _p
_s.path.insert(0, str(_p.Path(__file__).resolve().parents[1]))
from _cli_help import answer_help  # noqa: E402
answer_help(__doc__, __file__)

W = {"e1": W1, "e2": 2.0, "e3": 1.0, "e4": 2.0}

def E(sc): 
    t = sum(W[g] for g in sc); return sum((W[g]/t)*v for g, v in sc.items())

print("A. FLOOR BEFORE TODAY'S REPAIR (e1 absent), e4 pinned at 1.0")
print(f"   worst case e2=e3=0, e4=1 : E = {E({'e2':0.0,'e3':0.0,'e4':1.0}):.6f}")
print("B. FLOOR AFTER TODAY'S REPAIR (e1 present and ZERO), e4 pinned at 1.0")
after = E({'e1':0.0,'e2':0.0,'e3':0.0,'e4':1.0})
print(f"   worst case e1=e2=e3=0, e4=1 : E = {after:.6f}")
print(f"   -> the repair LOWERED the floor 0.400000 -> {after:.6f}. A REAL GAIN.")
print(f"   -> but the floor is still {after:.6f} > 0, NOT zero.")

print("\nC. z3: with e4 == 1 and all gates available, can E reach 0?")
e1,e2,e3,e4 = Reals('e1 e2 e3 e4')
sol = Solver()
sol.add(And(*[And(g>=0,g<=1) for g in (e1,e2,e3,e4)]), e4 == 1)
Eexpr = (W['e1']*e1+W['e2']*e2+W['e3']*e3+W['e4']*e4)/sum(W.values())
sol.add(Eexpr < after - 1e-9)
r = sol.check()
print(f"   E < {after:.6f} ?  {r}  -> {'FLOOR PROVED' if r==unsat else 'floor breakable'}")
assert r == unsat

print("\nD. WHAT THAT FLOOR DOES TO THE RECURSION")
R_old, q = 0.5, 0.4
r_floor = compute_rk(R_old, q, after, nu_b=0.0, nu_f=0.0)
r_true  = compute_rk(R_old, q, 0.0,   nu_b=0.0, nu_f=0.0)
print(f"   R_old={R_old} q={q}: sigma forced >= {after:.6f} -> R_k <= {r_floor:.6f}")
print(f"   the honest sigma=0 answer would be R_k = {r_true:.6f}")
print(f"   risk understated by at least {r_true-r_floor:.6f} on EVERY cycle where")
print( "   a constant gate is available, no matter how badly the fix performs.")

print("\nE. THE FLOOR IS REMOVED BY e4 VARYING, NOT BY RE-WEIGHTING e1")
sol2 = Solver(); sol2.add(And(*[And(g>=0,g<=1) for g in (e1,e2,e3,e4)]))
sol2.add(Eexpr <= 1e-9); print(f"   with e4 FREE, E ~ 0 reachable? {sol2.check()}")
assert after > 0.0
print(f"\nFALSIFIED: sigma floor = {after:.6f} > 0 by construction.")
