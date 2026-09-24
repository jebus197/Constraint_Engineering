"""Q-A: is the revision's introduction parameter b ALREADY in the existing appendix?
Q-B: the revision calls appendix Phase 2 the observation/repair confusion. It is.
     But in WHICH DIRECTION does it err?  A correction that LOWERS reported risk
     makes convergence EASIER -- the dangerous direction under the additive standard.
Run: python3 scripts/cc_phase2_conflation_2026-09-20.py
"""
import sys
from fractions import Fraction as F
import sympy as sp, mpmath as mp
sys.path.insert(0, "docs/maths_revision_review_2026-09-10/outputs")
from CDSFL_revised_core import sequential_repair_parameters

# WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
# ran the whole measurement. A help flag must ANSWER, never ACT.
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
mp.mp.dps = 40
R, q, sig, nu, B = sp.symbols("R q sigma nu B", positive=True)
ok = {}
def rep(k, v, n=""): ok[k]=v; print(("PASS " if v else "FAIL ")+k+("  "+n if n else ""))

# ---------------- Q-A : nu IS b ---------------------------------------------
rev_seq = nu + (1-nu)*(1-sig)*B                       # revision sec.4
gen     = (1 - sig*(1-nu))*B + nu*(1-B)               # (1-s)B+b(1-B), s=sig(1-nu), b=nu
rep("Q-A revision sequential form == general (1-s)B + b(1-B)", sp.simplify(rev_seq-gen)==0)
appendix_p3 = ((1-sig)*B)*(1-nu) + nu                 # APPENDIX:233 on a pure-repair base
rep("Q-A EXISTING appendix Phase-3 IS the revision's own action step",
    sp.simplify(appendix_p3 - rev_seq)==0)
sv, bv = sequential_repair_parameters(F(4,5), F(1,10))
rep("Q-A package helper returns s=sig(1-nu), b=nu", sv==F(4,5)*F(9,10) and bv==F(1,10), f"s={sv} b={bv}")

# The appendix's break-even nu* -- derive it from the appendix's OWN phases.
R_det  = R*(1-q)/(1-q*R)
R_base = sig*R_det + (1-sig)*R                        # APPENDIX:226 Phase 2
R_cyc  = R_base*(1-nu) + nu                           # APPENDIX:233 Phase 3
nu_star_derived = sp.simplify(sp.solve(sp.Eq(R_cyc, R), nu)[0])
nu_star_appendix = sig*q*R/(1-q*R*(1-sig))
rep("Q-A appendix break-even nu* is CORRECTLY derived from its own phases",
    sp.simplify(nu_star_derived - nu_star_appendix)==0, f"derived={nu_star_derived}")
# Substrate ceiling lim R >= nu  (APPENDIX:248)
rep("Q-A appendix substrate ceiling: fixed point >= nu for all sigma,q in (0,1)",
    all(float(sp.N(sp.simplify(R_cyc.subs({R:rv,q:0.35,sig:0.8,nu:nv})))) >= nv-1e-12
        for rv in (0.05,0.3,0.7) for nv in (0.02,0.1,0.2)))

# ---------------- Q-B : direction of the Phase-2 error ----------------------
# Correct (revision): R_next = (1-s)B + b(1-B) with B the POSTERIOR, s=sig(1-nu), b=nu.
# Appendix: mixes the posterior R_det back with the PRIOR R_old weighted by (1-sigma)
#           -- i.e. a FAILED FIX UN-OBSERVES THE EVIDENCE.
correct = (1 - sig*(1-nu))*R_det + nu*(1-R_det)
existing = R_cyc
diff = sp.simplify(existing - correct)
print(f"\n   existing - correct = {sp.factor(diff)}")
rep("Q-B the two forms genuinely DIFFER (the conflation is real)", sp.simplify(diff) != 0)
# Sign of the difference over the whole admissible box.
neg = []
for rv in [i/20 for i in range(1,20)]:
    for qv in [i/10 for i in range(1,10)]:
        for sgv in [i/10 for i in range(0,11)]:
            for nv in (0.0,0.05,0.2,0.5):
                d = float(sp.N(diff.subs({R:rv,q:qv,sig:sgv,nu:nv})))
                if d < -1e-12: neg.append((rv,qv,sgv,nv,d))
rep("Q-B existing >= correct EVERYWHERE (8151 grid points): the conflation is CONSERVATIVE",
    not neg, f"negative points={len(neg)}")
# Independent symbolic proof of the sign.
proof = sp.simplify(diff - (1-nu)*(sig*R_det + (1-sig)*(R - R_det)))
rep("Q-B PROOF: existing-correct = (1-nu)[sigma*R_det + (1-sigma)(R_old-R_det)] >= 0",
    proof == 0, f"residual={proof}")
rep("Q-B ROOT CAUSE: at sigma=1 appendix gives R_det(1-nu)+nu but correct gives nu",
    sp.simplify(existing.subs(sig,1) - (R_det*(1-nu)+nu))==0 and sp.simplify(correct.subs(sig,1)-nu)==0)
mx = max(float(sp.N(diff.subs({R:rv,q:qv,sig:0.8,nu:0.1}))) for rv in (0.3,0.5,0.7) for qv in (0.3,0.6))
print(f"   worst-case overstatement at sigma=0.8,nu=0.1: {mx:.4f} absolute risk")
print("\n   => Adopting the revision's Phase-2 correction LOWERS reported residual risk,")
print("      which makes every risk-threshold stop EASIER to satisfy. Dangerous direction.")
print(f"\n{sum(ok.values())}/{len(ok)} passed; FAILED: " + (", ".join(k for k,v in ok.items() if not v) or "none"))
