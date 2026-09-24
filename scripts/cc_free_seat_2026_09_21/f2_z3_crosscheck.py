"""F2. z3 cross-check of every claim F1 made with SymPy. Independent tool, same claims.
Each claim is posed as: assert the NEGATION over the open unit cube; expect UNSAT."""
from z3 import Reals, Solver, And, Not, sat, unsat

# WIRED 2026-09-24 (CC1). Module-level work, so no main() to intercept `--help`.
import sys as _s, pathlib as _p
_s.path.insert(0, str(_p.Path(__file__).resolve().parents[1]))
from _cli_help import answer_help  # noqa: E402
# GUARDED 2026-09-24 (CC1). At MODULE level this read the HOST's argv:
# the operational-script probe imports via `python3 -c "..." <path>`, so
# sys.argv[1] was the script's own path and the guard refused it, exit 2.
# `__name__` is still "__main__" when the file is RUN, so `--help` answers
# exactly as before; on IMPORT it is skipped and argv is never inspected.
if __name__ == "__main__":
    answer_help(__doc__, __file__)
R, q, s, nu, z = Reals('R_old q sigma nu z')
cube = And(R > 0, R < 1, q > 0, q < 1, s >= 0, s <= 1, nu >= 0, nu <= 1)

R_det    = R*(1-q)/(1-q*R)
marginal = R*(1-q*s)                       # exact two-branch mixture
appendix = s*R_det + (1-s)*R               # appendix Phase 2
revision = (1-s*(1-nu))*R_det + nu*(1-R_det)

def check(name, prop):
    sol = Solver(); sol.add(cube); sol.add(Not(prop))
    r = sol.check()
    print(f"  {name:<58} {'UNSAT -> HOLDS' if r == unsat else 'SAT  -> FAILS ' + str(sol.model()) if r == sat else 'UNKNOWN'}")
    return r == unsat

ok = []
print("z3 over the OPEN unit cube (R_old,q in (0,1); sigma,nu in [0,1]):")
ok.append(check("C1 appendix Phase2 at sigma=0 equals R_old exactly",
                appendix == R if True else None) if False else
          check("C1 appendix Phase2 at sigma=0 equals R_old exactly",
                (s == 0) == ((s == 0), )[0] if False else
                __import__('z3').Implies(s == 0, appendix == R)))
ok.append(check("C2 exact two-branch mixture at sigma=0 equals R_old",
                __import__('z3').Implies(s == 0, marginal == R)))
ok.append(check("C3 revision at sigma=0 is STRICTLY BELOW R_old (nu=0)",
                __import__('z3').Implies(And(s == 0, nu == 0), revision < R)))
ok.append(check("C4 revision at sigma=1,nu=0 is exactly 0 (zero residual risk)",
                __import__('z3').Implies(And(s == 1, nu == 0), revision == 0)))
ok.append(check("C5 appendix NEVER understates risk vs exact marginal",
                appendix >= marginal))
ok.append(check("C6 appendix Phase2 stays in [0,1]",
                And(appendix >= 0, appendix <= 1)))
ok.append(check("C7 appendix Phase2 is monotone non-increasing in sigma",
                __import__('z3').Implies(True, R_det <= R)))
print(f"\n{sum(ok)}/{len(ok)} claims UNSAT-confirmed by z3.")
assert all(ok), "a z3 claim failed"
print("z3 AGREES WITH SymPy ON EVERY CLAIM.")
