#!/usr/bin/env python3
"""Panel seat falsifiers for the maths-revision brief of 2026-09-20 (CC-seat).
Attacks CC1's Section 3 results and the brief's Q3 construction with SymPy +
mpmath + the REAL gate code. Read-only."""
from __future__ import annotations
import importlib.util, pathlib, random, sys
from fractions import Fraction as F
import mpmath as mp
import sympy as sp

# WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
# ran the whole measurement. A help flag must ANSWER, never ACT.
# Placed after the HEADER imports, not the last import: this file has a
# late import and the call landed after the work on the first attempt.
# `_cli_help` lives in scripts/. Locate it rather than assume a depth: the
# first version of this preamble inserted parents[1] (the repo ROOT) and so
# worked when the file was RUN (sys.path[0] is the script dir) and failed when
# it was IMPORTED, which is how 13 scripts stopped importing on 2026-09-24.
import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402
# GUARDED 2026-09-24 (CC1). At MODULE level this read the HOST's argv:
# the operational-script probe imports via `python3 -c "..." <path>`, so
# sys.argv[1] was the script's own path and the guard refused it, exit 2.
# `__name__` is still "__main__" when the file is RUN, so `--help` answers
# exactly as before; on IMPORT it is skipped and argv is never inspected.
if __name__ == "__main__":
    answer_help(__doc__, __file__)
REPO = pathlib.Path.cwd()
OUT = REPO / "docs" / "maths_revision_review_2026-09-10" / "outputs"

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

core = load("revised_core", OUT / "CDSFL_revised_core.py")
rr = load("rr", REPO / "bench" / "reference_runner_v3.py")
results = []

def check(label, ok, detail=""):
    results.append((label, ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" -- {detail}" if detail else ""))

z, s, b, d, R, p, q, sig, nu, B = sp.symbols("z s b d R p q sigma nu B", real=True)
fam = sp.solve(sp.Eq((1 - s) * z + b * (1 - z), d), b)[0]
check("3.1 family b(s) = (d - z + s z)/(1 - z)",
      sp.simplify(fam - (d - z + s * z) / (1 - z)) == 0)
pts = [(F(1, 10), F(11, 30)), (F(7, 10), F(17, 30)), (F(9, 10), F(19, 30))]
check("3.1 worked points z=1/4,d=1/2 exact",
      all((1 - sv) * F(1, 4) + bv * F(3, 4) == F(1, 2) for sv, bv in pts))

old = R * (1 - p) / (1 - p * R)
check("3.2 old form: p=0 -> R, p=1 -> 0, d/dp<0",
      sp.simplify(old.subs(p, 0) - R) == 0 and old.subs(p, 1) == 0
      and sp.simplify(sp.diff(old, p).subs({R: sp.Rational(1,2), p: sp.Rational(1,2)})) < 0)
act = (1 - s) * z + b * (1 - z)
check("3.2 action step reaches 0 and 1",
      act.subs({s: 1, b: 0}) == 0 and sp.simplify(act.subs({s: 0, b: 1}) - 1) == 0)
check("3.2 b=0 restores range [0,z]", sp.simplify(act.subs(b, 0) - (1 - s) * z) == 0)

ok = True; mp.mp.dps = 50; worst = mp.mpf(0)
for Rk in range(1, 20):
    for pk in range(0, 21):
        r0, pv = F(Rk, 20), F(pk, 20)
        got = core.update(r0, 1 - pv, 1).risk_after_action
        want = r0 * (1 - pv) / (1 - pv * r0)
        ok = ok and (got == want)
        gm = mp.mpf(Rk)/20*(1-mp.mpf(pk)/20)/(1-mp.mpf(pk)/20*mp.mpf(Rk)/20)
        worst = max(worst, abs(gm - mp.mpf(want.numerator)/want.denominator))
check("3.3 update(R,1-p,1) == R(1-p)/(1-pR), 399 exact pairs", ok,
      f"mpmath max delta={float(worst):.1e}")

fp = sp.solve(sp.Eq(R, (R * (1 - p) + b * (1 - R)) / (1 - p * R)), R)
check("3.4 fixed points are exactly {b/p, 1}",
      set(map(sp.simplify, fp)) == {b / p, sp.Integer(1)})
check("3.4 b/p values at p=0.35 exact",
      [F(2,100)/F(35,100), F(10,100)/F(35,100), F(20,100)/F(35,100)] ==
      [F(2,35), F(2,7), F(4,7)])
check("3.4 ATTACK: expected detection rate at R*=b/p is p*(b/p)=b, NOT 0",
      sp.simplify(p * (b / p) - b) == 0,
      "b=0.20 -> 1 detection per 5 rounds: observable, so 'decays to 0 in EVERY case' overreaches")

cfg = rr.RunnerConfig()
g1 = rr._estimate_gamma([5, 3, 1, 0, 0, 0])
c1, r1 = rr._check_gamma_alt_convergence(6, g1, [5,3,1,0,0,0], cfg, gamma_critical=g1, total_findings=9)
check("3.5 decayed-to-zero series converges", c1, f"gamma={g1:.3f}")
g2 = rr._estimate_gamma([5, 3, 2, 2, 2, 2])
c2, r2 = rr._check_gamma_alt_convergence(6, g2, [5,3,2,2,2,2], cfg, gamma_critical=g2, total_findings=16)
check("3.5 flat 2-criticals/round REFUSES", not c2, f"gamma={g2:.3f}")
c3, _ = rr._check_gamma_alt_convergence(6, 0.9, [5,3,1,0,0,1], cfg, gamma_critical=0.9, total_findings=10)
check("3.5 one new critical in last round REFUSES", not c3)
c4, r4 = rr._check_gamma_alt_convergence(6, 0.9, [5,3,1,0,0,0], cfg, gamma_critical=0.9,
                                         unresolved_critical=1, total_findings=9)
check("3.5 unresolved critical A4-BLOCKS", not c4, r4[:30])

random.seed(20260920)
p_inj, b_inj = 0.03, 0.10
n_runs, n_conv, high_resid, resid = 2000, 0, 0, []
for _ in range(n_runs):
    risk = 0.0
    hist = [5, 3, 1]
    for rnd in range(3, 12):
        risk = b_inj + (1 - b_inj) * risk
        det = 1 if random.random() < p_inj * risk else 0
        if det: risk *= 0.1
        hist.append(det)
        g = rr._estimate_gamma(hist)
        conv, _ = rr._check_gamma_alt_convergence(rnd + 1, g, hist, cfg, gamma_critical=g,
                                                  total_findings=sum(hist) + 4)
        if conv:
            n_conv += 1; resid.append(risk)
            if risk > 0.2: high_resid += 1
            break
import statsmodels.stats.proportion as smp

rate = high_resid / n_runs
lo, hi = smp.proportion_confint(high_resid, n_runs, method="wilson")
mean_resid = sum(resid)/len(resid) if resid else 0.0
check("Q3 blind-spot: gate converges with residual>20%", rate > 0.5,
      f"converged {n_conv}/{n_runs}; residual>20% at convergence {rate:.1%} "
      f"(Wilson {lo:.3f}-{hi:.3f}); mean residual {mean_resid:.1%}")

R_det = R * (1 - q) / (1 - q * R)
R_base = sig * R_det + (1 - sig) * R
R_k5 = R_base * (1 - nu) + nu
nu_star = sp.simplify(sp.solve(sp.Eq(R_k5, R), nu)[0])
check("Appendix nu* == exact break-even of its OWN recursion",
      sp.simplify(nu_star - sig * R * q / (1 - q * R * (1 - sig))) == 0)
rev_seq = nu + (1 - nu) * (1 - sig) * B
check("Revision seq form == (1-s)B+b(1-B) at s=sigma(1-nu), b=nu",
      sp.simplify((1 - sig * (1 - nu)) * B + nu * (1 - B) - rev_seq) == 0)
apx = R_k5.subs({R: sp.Rational(1,2), q: sp.Rational(4,5), sig: 1, nu: 0})
rev = rev_seq.subs({B: 1, sig: 1, nu: 0})
check("SEMANTIC SPLIT: confirmed flaw + perfect repair: appendix 1/6, revision 0",
      sp.simplify(apx - sp.Rational(1, 6)) == 0 and rev == 0)

for lbl, got, want in [
    ("4/13 positive f=0.2", core.update(F(1,10), F(4,5), F(1,5)).posterior_before_action, F(4,13)),
    ("1/6 negative clean", core.update(F(1,2), F(1,5), 1).posterior_before_action, F(1,6)),
    ("1/26 replication", core.update(F(1,6), F(1,5), 1).posterior_before_action, F(1,26))]:
    check(f"revision worked case {lbl}", got == want)
ex = core.expected_binary_review(F(1,2), F(4,5), 0, positive_action=(F(9,10), F(1,10)))
check("expected risk 0.14 (nu on positive branch only)", ex == F(7, 50))
ex2 = core.expected_binary_review(F(1,2), F(4,5), 0, positive_action=(F(9,10), F(1,10)),
                                  negative_action=(0, F(1,10)))
check("expected risk 0.19 (nu every branch)", ex2 == F(19, 100))
check("abstention counterexample: pass keeps prior 1/2",
      core.update(F(1,2), F(1,20), F(1,20)).posterior_before_action == F(1,2))

n_fail = sum(1 for _, k in results if not k)
print(f"\n{len(results)-n_fail}/{len(results)} checks passed" + ("" if not n_fail else f" -- {n_fail} FAILED"))
sys.exit(1 if n_fail else 0)
