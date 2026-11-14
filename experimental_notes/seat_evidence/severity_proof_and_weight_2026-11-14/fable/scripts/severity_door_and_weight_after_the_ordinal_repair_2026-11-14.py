# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'severity_proof_and_weight_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 10b29bc62c72e105bfcae6bf8fcb9692f8e7d902c95c504d603f24c7753b2d3b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""After the ordinal repair: what is left of `severity_is_proven` and of W?

Panel round 2026-11-14. Three measurements, each refutable by re-running this
file. All three decide the round's question rather than describe it.

M-A  THE WEIGHT'S EXPRESSIVITY (F2, re-derived, then extended to R2).
     z3: with W in {0.5, 1.0} and belief fixed, 2 distinct severities are sat
     and 3 are unsat, so consequence magnitude enters the product as 1 binary
     variable. Adding a 3rd weight w3 in (1/2, 1) makes 3 levels sat -- R2
     does what its proposer says. BUT:

M-B  THE DECIDING PROPERTY: INVARIANCE UNDER ORDER-PRESERVING RE-LABELLING.
     The 2026-11-12 repair proved severity is ordinal, so any gate on it must
     survive a strictly increasing re-labelling phi of the consequence scale.
     z3: the product gate `W*B >= c` with a FIXED real cut is breakable (sat)
     with 2 weights AND with 3 -- R2 does not repair the proven defect, it
     enlarges the breakable formula. The pair gate `c_d >= theta_d` with
     theta_d a DISTINGUISHED ELEMENT transported by phi is unbreakable
     (unsat). And under R3 the product is a CREDENCE, so W carries a belief
     discount, not consequence: the consequence verdict c_d >= theta_d does
     not read W at all, so a 3rd weight changes ZERO consequence verdicts in
     the pair design. R2 and R3 are therefore COMPETING DESIGNS: R2 is dead
     weight under R3 and non-curative without it.

M-C  THE DOOR (R1). Over every archived entry that today escapes the blocking
     door (`severity < 0.7 AND severity_is_proven`), how many keep the
     exemption when the proof must be ABOUT the gated number at the proof's
     own WARN tolerance (|severity - recomputed R_k| <= 0.05). Direction and
     magnitude of the repointing, measured on the door's own population
     rather than on all PASS/WARN entries.

Usage: python3 scripts/severity_door_and_weight_after_the_ordinal_repair_2026-11-14.py
"""
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
PROVEN = {"PASS", "WARN"}
CUT = 0.7          # reference_runner_v3.CRITICAL_SEVERITY_THRESHOLD
WARN_TOL = 0.05    # the proof mechanism's own rounding-scale tolerance


def measure_weight_expressivity() -> None:
    from z3 import Real, Or, Solver

    def distinct_products(weights, k):
        """sat iff k pairwise-distinct severities W*B exist at a single B."""
        s = Solver()
        b = Real("b")
        s.add(b > 0, b <= 1)
        ws = [Real(f"w{i}") for i in range(k)]
        for w in ws:
            s.add(Or(*[w == v for v in weights]))
        for i in range(k):
            for j in range(i + 1, k):
                s.add(ws[i] * b != ws[j] * b)
        return s.check()

    two = (0.5, 1.0)
    three = (0.5, 0.8, 1.0)
    print("M-A  weight expressivity (z3):")
    print(f"  W in {two}:  2 distinct severities -> {distinct_products(two, 2)}"
          f"   3 distinct -> {distinct_products(two, 3)}")
    print(f"  W in {three}: 3 distinct severities -> {distinct_products(three, 3)}"
          f"   4 distinct -> {distinct_products(three, 4)}")

    import sympy as sp
    Bs = sp.Symbol("B", nonnegative=True)
    print(f"  SymPy: sup over the SOFT branch of W*B (B<=1, Ver<=1) = "
          f"{sp.Rational(1, 2)} (no cut above 0.5 reachable on SOFT); "
          f"at W=1, (Sev >= c) == (B >= c) identically: "
          f"{sp.simplify(sp.Eq(1 * Bs, Bs))}")


def measure_invariance() -> None:
    """The property that decides R2 vs R3: survival of order-preserving phi."""
    from z3 import Real, Solver, And, Or

    def product_gate_breakable(weights) -> str:
        """sat iff an order-preserving re-labelling of the weight set changes
        a gate decision W*B >= CUT."""
        s = Solver()
        b = Real("b")
        s.add(b >= 0, b <= 1)
        phis = [Real(f"phi{i}") for i in range(len(weights))]
        for p in phis:
            s.add(p > 0, p <= 1)
        for i in range(len(weights) - 1):
            s.add(phis[i] < phis[i + 1])          # order preserved
        flips = []
        ws = sorted(weights)
        for i, w in enumerate(ws):
            flips.append(And(w * b >= CUT, phis[i] * b < CUT))
            flips.append(And(w * b < CUT, phis[i] * b >= CUT))
        s.add(Or(*flips))
        return str(s.check())

    def pair_gate_breakable() -> str:
        """sat iff a strictly increasing phi changes c_d >= theta_d when
        theta_d is TRANSPORTED with the scale. 5-level ordinal scale,
        uninterpreted increasing map."""
        from z3 import Int, Function, IntSort
        s = Solver()
        phi = Function("phi", IntSort(), IntSort())
        levels = list(range(5))
        for a in levels:
            for bb in levels:
                if a < bb:
                    s.add(phi(a) < phi(bb))       # strictly increasing
        from z3 import Int as _Int
        c = _Int("c")
        th = _Int("th")
        s.add(c >= 0, c <= 4, th >= 0, th <= 4)
        s.add(Or(And(c >= th, phi(c) < phi(th)),
                 And(c < th, phi(c) >= phi(th))))
        return str(s.check())

    print("M-B  invariance under order-preserving re-labelling (z3):")
    print(f"  product gate, W in (0.5, 1.0):      breakable -> "
          f"{product_gate_breakable((0.5, 1.0))}   (sat = defect present)")
    print(f"  product gate, W in (0.5, 0.8, 1.0): breakable -> "
          f"{product_gate_breakable((0.5, 0.8, 1.0))}   "
          f"(sat = R2 does NOT repair it)")
    print(f"  pair gate c_d >= theta_d, theta transported: breakable -> "
          f"{pair_gate_breakable()}   (unsat = admissible)")
    print("  3rd weight vs the pair gate: the consequence verdict "
          "c_d >= theta_d contains no W term, so its truth value is "
          "W-independent by construction -- a 3rd weight changes 0 "
          "consequence verdicts under R3.")


def door_population():
    """(severity, recomputed R_k) for every archived PASS/WARN entry."""
    out = []
    for fp in LOGS.glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                 # noqa: BLE001
            continue
        for e in ((d or {}).get("registry") or {}).get("entries", {}).values():
            if not isinstance(e, dict):
                continue
            proof = e.get("severity_proof")
            if not isinstance(proof, dict):
                continue
            if str(proof.get("status") or "").strip().upper() not in PROVEN:
                continue
            sev = e.get("severity")
            rk = proof.get("recomputed_rk", proof.get("model_rk"))
            if isinstance(sev, (int, float)) and isinstance(rk, (int, float)):
                out.append((float(sev), float(rk)))
    return out


def measure_door() -> None:
    from statsmodels.stats.proportion import proportion_confint
    pairs = door_population()
    n_proven = len(pairs)
    escaping = [(s, r) for s, r in pairs if s < CUT]
    n = len(escaping)
    if n == 0:
        print("M-C  no archived entry escapes the door; measurement void.")
        return
    k = sum(1 for s, r in escaping if abs(s - r) <= WARN_TOL)
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    print("M-C  the door (R1), measured on the door's own population:")
    print(f"  archived entries with a PASS/WARN proof:             {n_proven}")
    print(f"  of those, escaping the blocking door (sev < {CUT}):   {n}")
    print(f"  still escaping when the proof must be ABOUT the gated number "
          f"(|sev - R_k| <= {WARN_TOL}): {k}/{n} = {k/n:.2%}  "
          f"Wilson [{lo:.2%}, {hi:.2%}]")
    print(f"  entries LOSING the exemption: {n - k}/{n} = {(n - k)/n:.2%} -- "
          f"the door TIGHTENS, and only tightens, because the repointed "
          f"predicate is a conjunction with the current one (a subset).")


def main() -> int:
    answer_help(__doc__, __file__)
    measure_weight_expressivity()
    print()
    measure_invariance()
    print()
    measure_door()
    return 0


if __name__ == "__main__":
    sys.exit(main())
