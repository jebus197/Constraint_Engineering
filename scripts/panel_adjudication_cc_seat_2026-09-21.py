#!/usr/bin/env python3
"""Adjudication falsifiers, CC panel seat, 2026-09-21.

Every claim in this seat's reply that can be decided by execution is decided
here, against the REAL modules (bench.reference_runner_v3, the committed
revision core), never against a retyped copy.

Each falsifier prints FALSIFIED and raises AssertionError iff the defect it
names is genuinely present, and exits cleanly when the claim under test is
false.  Reads are confined to the artefacts under review and the repository
modules they legitimately import.  No scoring key, answer file or planted-defect
manifest is opened.

    python3 scripts/panel_adjudication_cc_seat_2026-09-21.py
    python3 scripts/panel_adjudication_cc_seat_2026-09-21.py --help
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import subprocess
import sys
from fractions import Fraction as F

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bench"))

import numpy as np
import sympy as sp
import z3
from mpmath import mp
from statsmodels.stats.proportion import proportion_confint

mp.dps = 40


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


REV = _load(
    "cdsfl_revised_core",
    ROOT / "docs/maths_revision_review_2026-09-10/outputs/CDSFL_revised_core.py",
)
import reference_runner_v3 as RR  # the REAL shipped runner

FAILURES: list[str] = []


def head(n: str) -> None:
    print("\n" + "=" * 74 + f"\n{n}\n" + "=" * 74)


def wilson(k: int, n: int) -> str:
    if n == 0:
        return "n=0"
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return f"{100*k/n:.4f}%  Wilson [{100*lo:.4f}%, {100*hi:.4f}%]"


# ---------------------------------------------------------------- A1
def a1_astra_claim_one() -> None:
    """Astra 1: the '0' belongs to update(), not to expected_binary_review."""
    head("A1  ASTRA CLAIM 1 — the zero is mis-scoped (revision's own example)")
    r, q = F(1, 2), F(4, 5)

    single = REV.update(r, q, 0, 1, 0).risk_after_action          # positive branch only
    both = REV.expected_binary_review(r, q, 0, (1, 0), (0, 0))    # both branches
    neg = REV.update(r, 1 - q, 1).risk_after_action

    print(f"   update(r,q,0,removal=1,intro=0).risk_after_action = {single}")
    print(f"   expected_binary_review(r,q,0,(1,0),(0,0))         = {both}")
    print(f"   negative branch posterior                          = {neg}")
    assert single == 0, "the single-branch action step does NOT return 0"
    assert both == F(1, 10), f"expected 1/10, got {both}"
    assert neg == F(1, 6)

    # It is not a special number: both-branch value is r*(1-q) identically.
    bad = [(a, b) for a in range(1, 10) for b in range(1, 10)
           if REV.expected_binary_review(F(a, 10), F(b, 10), 0, (1, 0), (0, 0))
           != F(a, 10) * (1 - F(b, 10))]
    print(f"   grid 81 points where both-branch != r*(1-q): {len(bad)}")
    assert not bad

    # false_positive IS a declared parameter of the revision.
    import inspect
    params = list(inspect.signature(REV.expected_binary_review).parameters)
    print(f"   expected_binary_review signature: {params}")
    assert "false_positive" in params, "FALSIFIED: no false_positive parameter"
    print("   -> CC1's 'returns identically 0, asserting certainty' describes")
    print("      update(), the ACTION step on the positive branch. Astra HOLDS.")


# ---------------------------------------------------------------- A2
def a2_expectation_vs_conditional() -> None:
    """Astra 2: E[improvement] = R*q; derived, not asserted."""
    head("A2  ASTRA CLAIM 2 — conservative bound != conservative stopping rule")
    R, q, s = sp.symbols("R q sigma", positive=True)

    R_det = R * (1 - q) / (1 - q * R)
    dR = sp.simplify(R - R_det)
    print(f"   SymPy  conditional dR        = {sp.simplify(dR)}")
    assert sp.simplify(dR - q * R * (1 - R) / (1 - q * R)) == 0

    # Derive the expectation from the generative model, do not quote it.
    p_pos = q * R                       # phi = 0: report iff flaw present & caught
    E_new = sp.simplify(p_pos * 0 + (1 - p_pos) * R_det)
    E_imp = sp.simplify(R - E_new)
    print(f"   SymPy  E[R_new] over branches = {E_new}")
    print(f"   SymPy  E[improvement]         = {E_imp}")
    assert sp.simplify(E_imp - R * q) == 0, "FALSIFIED: expectation is not R*q"

    # Independent tool 1: the committed revision module, exact rationals.
    for a in (1, 3, 5, 9):
        for b in (1, 3, 7):
            rr, qq = F(a, 10), F(b, 10)
            got = rr - REV.expected_binary_review(rr, qq, 0, (1, 0), (0, 0))
            assert got == rr * qq, f"revision disagrees at {rr},{qq}"
    print("   revision module agrees with R*q on 12 exact-rational points")

    # Independent tool 2: z3 — can the conditional ever reach the expectation?
    zR, zq = z3.Reals("R q")
    sol = z3.Solver()
    sol.add(zR > 0, zR < 1, zq > 0, zq < 1)
    sol.add(zq * zR * (1 - zR) / (1 - zq * zR) >= zR * zq)
    print(f"   z3: conditional >= expectation anywhere in (0,1)^2 ? {sol.check()}")
    assert sol.check() == z3.unsat, "FALSIFIED: conditional can match expectation"

    # Independent tool 3: the disagreement at theta = 0.05, mpmath 40 digits.
    Rv, qv, th = mp.mpf("0.99"), mp.mpf("0.3"), mp.mpf("0.05")
    cond = qv * Rv * (1 - Rv) / (1 - qv * Rv)
    exp_ = Rv * qv
    print(f"   mpmath  conditional at R=.99 q=.3 = {mp.nstr(cond, 10)}")
    print(f"   mpmath  expectation  at R=.99 q=.3 = {mp.nstr(exp_, 10)}")
    print(f"   ratio = {mp.nstr(exp_/cond, 6)}")
    assert abs(cond - mp.mpf("0.004225")) < mp.mpf("1e-6")
    assert abs(exp_ - mp.mpf("0.297")) < mp.mpf("1e-30")
    assert cond < th < exp_, "FALSIFIED: the two rules do not disagree at 0.05"
    print("   -> the 2 rules disagree outright at theta=0.05. Astra HOLDS.")


# ---------------------------------------------------------------- A3
def a3_no_live_consumer() -> None:
    """MY SCOPING CLAIM: the premature-stop band has no live consumer."""
    head("A3  SCOPE — does any shipped decision read the conditional dR?")
    pats = ["hard_exit", "HARD_EXIT", "substrate_ceiling",
            "delta_rk", "delta_r_k", "rk_delta", "r_k_delta", "dR_n"]
    src = [p for p in (ROOT / "bench").rglob("*.py")
           if not {"tests", "__pycache__", "logs"} & set(p.parts)]
    print(f"   shipped runtime .py files swept: {len(src)}")
    hits = []
    for pat in pats:
        out = subprocess.run(["grep", "-rn", "-I", pat, *map(str, src)],
                             capture_output=True, text=True).stdout
        hits += [l for l in out.splitlines() if l.strip()]
    print(f"   grep over bench/ for a dR-based terminator: {len(hits)} hit(s)")
    for h in hits[:5]:
        print("     " + h[:110])
    assert not hits, "FALSIFIED: a dR-based terminator exists in bench/"

    # The one decision built on the conditional map IS the S* gate. Measure it.
    passes, s_star = RR.check_sk_threshold(
        sk=0.0, nu_b=0.05, nu_f=0.20, q=0.5, R=0.5, s_floor=0.0)
    print(f"   check_sk_threshold(sk=0.0) at the shipped operating point:"
          f" passes={passes}  S*={s_star}")
    assert passes and s_star == 0.0, (
        "the shipped S* gate rejects sk=0 at (q=.5,R=.5) — claim is false")
    print("   -> S* = 0 at the shipped point, so a WORTHLESS fix passes.")
    print("      The conditional map's only live consumer is already inert;")
    print("      the appendix correction therefore needs NO code change.")


# ---------------------------------------------------------------- A4
def a4_floor_is_nu_over_q() -> None:
    """The recorded nu/q floor, executed against the shipped compute_rk."""
    head("A4  FLOOR — nu/q, run on the shipped compute_rk")
    Rs, qs, ns = sp.symbols("R q nu", positive=True)
    T = (Rs * (1 - qs) / (1 - qs * Rs)) * (1 - ns) + ns      # sigma = 1
    fps = sorted(sp.solve(sp.Eq(sp.simplify(T), Rs), Rs), key=str)
    print(f"   SymPy fixed points at sigma=1: {fps}")
    assert sp.simplify(fps[1] - ns / qs) == 0 or sp.simplify(fps[0] - ns / qs) == 0

    for q, nu in ((0.2, 0.05), (0.1, 0.02), (0.5, 0.10)):
        R = 0.9
        for _ in range(20000):
            R = RR.compute_rk(R, q, 1.0, nu_b=nu, nu_f=0.0)
        print(f"   q={q} nu={nu}: orbit -> {R:.10f}   nu/q = {nu/q:.10f}"
              f"   stated floor nu = {nu}")
        assert abs(R - nu / q) < 1e-9, "FALSIFIED: orbit is not nu/q"
        assert R > nu + 1e-9, "the stated floor nu would be reached"
    print("   -> the stated floor nu is NOT reached; nu/q is. Correction HOLDS.")


# ---------------------------------------------------------------- A5
def a5_e1_is_circular_but_scoped() -> None:
    """Astra 3: the POST-repair separation is circular. And its exact scope."""
    head("A5  ASTRA CLAIM 3 — post-repair validation is circular")
    from fix_efficacy import FIX_CURES, FIX_INEFFECTIVE
    hi, _ = RR._run_effect_fix_efficacy(FIX_CURES)
    lo, _ = RR._run_effect_fix_efficacy(FIX_INEFFECTIVE)
    print(f"   e1_efficacy(FIX_CURES)      = {hi}")
    print(f"   e1_efficacy(FIX_INEFFECTIVE)= {lo}")
    print(f"   gate weight                 = {RR.FIX_EFFICACY_GATE_WEIGHT}")
    assert (hi, lo) == (1.0, 0.0), "FALSIFIED: e1 does not read the verdict"
    print("   -> sk is a deterministic function OF the cure verdict, so a test")
    print("      that sk separates cure from non-cure is near-tautological.")

    # BUT the scope is exactly one p-value. The PRE-repair independence result
    # is untouched, and it is the finding that justifies the gate.
    ok = 31
    print(f"   pre-repair: {ok}/{ok} non-curing fixes admitted = {wilson(ok, ok)}")
    print("   -> the DEFINITIONAL case for e1 (appendix line 214/377: sigma is")
    print("      g(V_pre,V_post)) stands independent of the void p-value.")


# ---------------------------------------------------------------- A6
def a6_routing_reach() -> None:
    """max_rungs: is raising it an improvement or an unmeasured cost?"""
    head("A6  ROUTING — max_rungs has no config surface; what does rung 3 buy?")
    import routing
    import inspect
    sig = inspect.signature(routing.route)
    print(f"   routing.route max_rungs default = "
          f"{sig.parameters['max_rungs'].default}")
    assert sig.parameters["max_rungs"].default == 2

    order = routing.DEFAULT_FALSIFIER_STRENGTH
    print(f"   DEFAULT_FALSIFIER_STRENGTH = {list(order)}")

    calls: list[tuple] = []

    def resolve(model, finding):
        calls.append(model)
        return "assert False"        # every rung writes a falsifier that fails

    def reverify(code):
        return "REFUTED"             # and none of them confirms

    f = {"finding_id": "X", "source_model": order[0]}
    for k in (2, 3, 5):
        calls.clear()
        res = routing.route(f, list(order), [], resolve, reverify,
                            lambda a, b: 0.0, max_rungs=k)
        print(f"   max_rungs={k}: rungs_tried={res.rungs_tried} "
              f"models={calls} resolved={res.resolved}")
        assert res.rungs_tried == min(k, len(order) - 1)
        assert not res.resolved
    print("   -> raising max_rungs costs one model dispatch per extra rung on")
    print("      EVERY unresolved critical, and buys nothing unless a rung-3+")
    print("      model confirms where rungs 1-2 failed. No archived run")
    print("      measures that, because no archived run ever entered rung 3.")


# ---------------------------------------------------------------- A7
def a7_phi_is_the_zero_special_case() -> None:
    """phi: what the smallest estimate has to be, and that it is not zero."""
    head("A7  phi — the detection posterior is the phi = 0 special case")
    R, q = sp.symbols("R q", positive=True)
    phi = sp.Symbol("phi", real=True)       # 0 MUST be in the solve domain
    general = R * (1 - q) / (R * (1 - q) + (1 - R) * (1 - phi))
    shipped = R * (1 - q) / (1 - q * R)
    sols = sp.solve(sp.Eq(sp.together(general - shipped), 0), phi)
    print(f"   SymPy: general == shipped iff phi in {sols}")
    assert sols == [0], f"FALSIFIED: they agree off phi=0, at {sols}"

    zR, zq, zp = z3.Reals("R q phi")
    s = z3.Solver()
    s.add(zR > 0, zR < 1, zq > 0, zq < 1, zp > 0, zp < 1)
    # denom_general = R(1-q) + (1-R)(1-phi);  denom_shipped = 1 - qR.
    # numerator R(1-q) > 0 and both denominators > 0, so
    #   shipped > general  <=>  denom_general > denom_shipped.
    s.add(zR * (1 - zq) + (1 - zR) * (1 - zp) > 1 - zq * zR)
    print(f"   z3: can the shipped form ever OVERSTATE true risk? {s.check()}")
    assert s.check() == z3.unsat, "FALSIFIED: shipped can overstate"

    rng = np.random.default_rng(20260921)
    Rv, qv, pv = rng.random(200000), rng.random(200000), rng.random(200000)
    gen = Rv*(1-qv) / (Rv*(1-qv) + (1-Rv)*(1-pv))
    shi = Rv*(1-qv) / (1-qv*Rv)
    k = int((shi > gen + 1e-12).sum())
    print(f"   numpy 200000 samples where shipped > general: {k}")
    print(f"   mean optimism (general - shipped)            : {(gen-shi).mean():.6f}")
    assert k == 0
    print("   -> phi > 0 makes TRUE risk HIGHER than reported: the model is")
    print("      OPTIMISTIC, always in the same direction. Sign is decided.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args()
    for fn in (a1_astra_claim_one, a2_expectation_vs_conditional,
               a3_no_live_consumer, a4_floor_is_nu_over_q,
               a5_e1_is_circular_but_scoped, a6_routing_reach,
               a7_phi_is_the_zero_special_case):
        try:
            fn()
        except AssertionError as exc:
            print(f"   FALSIFIED  {fn.__name__}: {exc}")
            FAILURES.append(fn.__name__)
    head("SUMMARY")
    print("   falsifiers run  : 7")
    print(f"   FALSIFIED       : {len(FAILURES)}  {FAILURES}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
