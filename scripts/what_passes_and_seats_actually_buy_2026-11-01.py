#!/usr/bin/env python3
"""What additional PASSES and additional SEATS actually buy, derived.

HIS QUESTIONS, 2026-11-01, annotating the closing report:
  "how is that calculation then done, and how much does adding additional
  passes (and also additional seats) reduce the risk that any given answer
  to a problem might be wrong[?] In other words, what value does adding
  additional passes and additional seats bring in terms of increasing our
  confidence in an outcome? [...] But how do we know how low, low should be,
  before we accept an outcome as valid? Does not the mathematics of
  probability give us a potential insight into this? Can it be measured from
  our historical data? Surely whether a run is simulated, or real, should
  have no impact on this measurement either?"

This script answers the parts that are DERIVABLE from the model already in
docs/MATHEMATICAL_APPENDIX.md, and names the parts that are not.

The forms are taken from the appendix, not invented here:
  line 189  R_k(i) = R_k(i-1)(1 - q) / (1 - q R_k(i-1)),  R_k(0) = pi_k
  line 195  R_k     = pi_k m_k / ((1 - pi_k) + pi_k m_k),  m_k = PROD_i(1 - d_i p_ik)
  line 313  R_k(i) = R_base (1 - nu) + nu        [Phase 3 re-injection]
  line 329  composite fixed points {1, nu/q} at sigma = 1; nu/q attracts

Every claim is cross-verified on 2 independent tools, per the 21 Apr 2026 rule.
"""
from __future__ import annotations

import argparse
import sys

import sympy as sp
import mpmath as mp
import z3

mp.mp.dps = 40


def _parse_args() -> None:
    """A `--help` must never run the measurement. 15 of 17 runners once BILLED a
    live dispatch on an unrecognised argument; this script costs no money but the
    rule is the rule, and an unguarded `--help` here becomes offender N+1."""
    ap = argparse.ArgumentParser(
        prog="what_passes_and_seats_actually_buy_2026-11-01.py",
        description="Derive what extra PASSES and extra SEATS buy, from the "
                    "appendix's own residual-risk forms. Takes no arguments; "
                    "prints the derivation and exits non-zero if any check fails.")
    ap.parse_args()


_parse_args()

R, q, nu, u, O = sp.symbols("R q nu u O", positive=True)
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'OK ' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


# ---------------------------------------------------------------- 1. the odds law
print("\n1. THE RECURSION IS EXACTLY GEOMETRIC DECAY OF THE ODDS")
update = R * (1 - q) / (1 - q * R)
odds = lambda x: x / (1 - x)
lhs = sp.simplify(odds(update))
rhs = sp.simplify(odds(R) * (1 - q))
check("SymPy: odds(R') == odds(R)*(1-q)", sp.simplify(lhs - rhs) == 0,
      f"odds(R') = {sp.simplify(lhs)}")

# z3: no counterexample on the open unit square
zR, zq = z3.Reals("R q")
z_update = zR * (1 - zq) / (1 - zq * zR)
s = z3.Solver()
s.add(zR > 0, zR < 1, zq > 0, zq < 1)
s.add(z3.Not(z_update / (1 - z_update) == (zR / (1 - zR)) * (1 - zq)))
check("z3: unsat for any violation of the odds law", s.check() == z3.unsat, str(s.check()))

# ------------------------------------------------- 2. closed form for pass count
print("\n2. PASSES TO REACH A TARGET -- CLOSED FORM, NO RUN REQUIRED")
n_sym = sp.symbols("n", positive=True)
O0, Ot = sp.symbols("O_0 O_t", positive=True)
n_closed = sp.log(Ot / O0) / sp.log(1 - q)
print(f"   n = {n_closed}")


def passes_needed(r0: float, rt: float, qq: float) -> float:
    o0, ot = r0 / (1 - r0), rt / (1 - rt)
    return float(mp.log(ot / o0) / mp.log(1 - qq))


for r0, rt, qq in [(0.50, 0.05, 0.30), (0.50, 0.01, 0.30), (0.90, 0.05, 0.20)]:
    n_mp = passes_needed(r0, rt, qq)
    # independent check: iterate the recursion n_mp times with NumPy-free mpmath
    r = mp.mpf(r0)
    for _ in range(int(mp.ceil(n_mp))):
        r = r * (1 - qq) / (1 - qq * r)
    n_sympy = float(sp.N(n_closed.subs({O0: r0 / (1 - r0), Ot: rt / (1 - rt), q: qq})))
    check(f"   R {r0}->{rt} at q={qq}: n = {n_mp:.6f}",
          abs(n_mp - n_sympy) < 1e-12 and r <= rt + 1e-12,
          f"after ceil(n) passes R = {float(r):.8f} <= {rt}")

# ------------------------------------- 3. SEATS AND PASSES ARE NOT INTERCHANGEABLE
print("\n3. AT EQUAL SEAT-EVALUATION COST, SEATS BEAT PASSES WHENEVER nu > 0")
print("   2 seats in 1 pass vs 1 seat in each of 2 passes: identical miss product,")
print("   but the 2-pass arm pays the re-injection event TWICE.")
phase3 = lambda x: x * (1 - nu) + nu
one_pass_two_seats = phase3(R * (1 - (1 - (1 - u) ** 2)) / (1 - (1 - (1 - u) ** 2) * R))
step = lambda x: phase3(x * (1 - u) / (1 - u * x))
two_passes_one_seat = step(step(R))
diff = sp.simplify(sp.together(two_passes_one_seat - one_pass_two_seats))
print(f"   2-pass minus 1-pass = {sp.factor(sp.simplify(diff))}")
check("SymPy: the difference vanishes identically at nu = 0",
      sp.simplify(diff.subs(nu, 0)) == 0)

zu, znu = z3.Reals("u nu")
zph = lambda x: x * (1 - znu) + znu
z_two = zph(zph(zR * (1 - zu) / (1 - zu * zR)) * (1 - zu) / (1 - zu * zph(zR * (1 - zu) / (1 - zu * zR))))
qq2 = 1 - (1 - zu) ** 2
z_one = zph(zR * (1 - qq2) / (1 - qq2 * zR))
s2 = z3.Solver()
s2.add(zR > 0, zR < 1, zu > 0, zu < 1, znu > 0, znu < 1)
s2.add(z_two < z_one)          # can 2 passes ever BEAT 1 pass with 2 seats?
check("z3: unsat -- 2 passes never beat 2 seats in 1 pass (nu > 0)",
      s2.check() == z3.unsat, str(s2.check()))

for rv, uv, nuv in [(0.5, 0.2, 0.05), (0.9, 0.3, 0.10), (0.3, 0.15, 0.02)]:
    sub = {R: rv, u: uv, nu: nuv}
    a = float(sp.N(one_pass_two_seats.subs(sub)))
    b = float(sp.N(two_passes_one_seat.subs(sub)))
    print(f"   R={rv} u={uv} nu={nuv}: 1 pass/2 seats = {a:.8f}   2 passes/1 seat = {b:.8f}"
          f"   penalty = {b - a:.8f}")

# --------------------------------------------------------------- 4. the hard floor
print("\n4. THE FLOOR IS nu/q AND IT IS UNREACHABLE-BELOW AT ANY PASS COUNT")
composite = sp.simplify(phase3(R * (1 - q) / (1 - q * R)))
fps = sp.solve(sp.Eq(composite, R), R)
check("SymPy: fixed points are exactly {1, nu/q}",
      set(sp.simplify(f) for f in fps) == {sp.Integer(1), nu / q}, f"{[sp.simplify(f) for f in fps]}")
gp = sp.simplify(sp.diff(composite, R).subs(R, nu / q))
print(f"   g'(nu/q) = {gp}")
# mpmath: iterate from above and from below, confirm convergence to nu/q
for qv, nuv in [(0.30, 0.05), (0.20, 0.05), (0.50, 0.01)]:
    floor = nuv / qv
    r = mp.mpf("0.999")
    for _ in range(4000):
        r = (r * (1 - qv) / (1 - qv * r)) * (1 - nuv) + nuv
    check(f"   mpmath: q={qv} nu={nuv} converges to nu/q = {floor:.10f}",
          abs(r - floor) < mp.mpf("1e-12"), f"limit = {float(r):.12f}")
s3 = z3.Solver()
s3.add(zR > 0, zR < 1, zq > 0, zq < 1, znu > 0, znu < 1, znu < zq)
s3.add(zR > znu / zq)
s3.add((zR * (1 - zq) / (1 - zq * zR)) * (1 - znu) + znu < znu / zq)
check("z3: unsat -- one pass from above the floor never lands below it",
      s3.check() == z3.unsat, str(s3.check()))

# ------------------------------------------- 5. HOW LOW IS LOW ENOUGH, and when it is IMPOSSIBLE
print("\n5. 'HOW LOW SHOULD LOW BE' IS NOT A CONSTANT -- IT IS A LOSS BUDGET")
Lstar, sev = sp.symbols("L_star s", positive=True)
r_accept = Lstar / sev
print(f"   single class, appendix L_n = sum_k w_k s_k R_k  =>  accept while R <= {r_accept}")
print("   FEASIBILITY TEST, which is the part a gate can actually run:")
print("   a target R_target is reachable at SOME pass count iff nu/q < R_target.")
cases = [(0.30, 0.05, 0.10), (0.20, 0.05, 0.10), (0.30, 0.05, 0.15),
         (0.30, 0.05, 0.20), (0.30, 0.01, 0.10), (0.60, 0.05, 0.10)]
reach = [nuv / qv < tgt for qv, nuv, tgt in cases]
check("the feasibility test DISCRIMINATES (both verdicts occur)",
      any(reach) and not all(reach),
      f"{sum(reach)} reachable of {len(cases)}")
for qv, nuv, tgt in cases:
    floor = nuv / qv
    feasible = floor < tgt
    n = passes_needed(0.5, tgt, qv) if feasible else float("inf")
    print(f"   q={qv} nu={nuv} target={tgt}: floor={floor:.6f} "
          f"{'REACHABLE in %.3f passes from R=0.5' % n if feasible else 'UNREACHABLE at any pass count'}")

print("\n6. WHAT IS *NOT* DERIVABLE, AND THEREFORE WHAT A REAL RUN IS FOR")
print("   q = eta*d*p, sigma and nu are PER-SEAT, PER-CLASS empirical rates.")
print("   Everything above is arithmetic ON those rates and is substrate-independent:")
print("   it holds identically for simulated and real seats. What a simulated run")
print("   cannot supply is the VALUE of d_i for a real model. It can supply, and in")
print("   this project already has supplied, the SHAPE and SPREAD of the severity")
print("   statistic and the DECISIONS two candidate forms disagree on.")

print("\n" + "=" * 70)
print("FAILURES:", len(FAILURES))
for f in FAILURES:
    print("  -", f)
raise SystemExit(1 if FAILURES else 0)
