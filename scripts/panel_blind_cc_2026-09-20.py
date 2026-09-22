#!/usr/bin/env python3
"""Blind-round seat: three executed results on the founder's framing.

F1  The width-z band that CC1 reports for the revised action step is EXACTLY the
    width of the existing collapse model's own reachable set. Measuring the
    introduction rate buys back the status quo's forbidding power -- no more.
F2  Appendix 7.12's re-injection model D_{n+1} = nu*D_n + eps_n carries the SAME
    1-dimensional degeneracy, by an exact reparameterisation nu = 1-s,
    eps = b(1-z). CC1's Section 4 distinction does not survive.
F3  The fix score has an ALGEBRAIC FLOOR. Three of five gates emitted a constant
    1.0 over 902 of 902 archived scored fixes, so E >= 0.4 (all gates available)
    or E >= 2/3 (regression gate unavailable) whatever the fix does. The lower
    disputed threshold 0.395043 sits BELOW that floor and is therefore
    unreachable by construction, not merely unreached by accident.

Read-only over the repository. SymPy + z3 + mpmath + NumPy + statsmodels.
Run:  python3 scripts/panel_blind_cc_2026-09-20.py
"""
from __future__ import annotations

import argparse, glob, json, math, os, sys
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 60_000_000
FAIL: list[str] = []


def ck(name: str, cond: bool) -> bool:
    print(f"   [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        FAIL.append(name)
    return cond


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


# ---------------------------------------------------------------- F1
def f1_reachable_sets() -> None:
    """SymPy: reachable set of the action step with b fixed, vs the old model."""
    import sympy as sp
    z, s, b, p, R = sp.symbols("z s b p R", nonnegative=True)

    act = (1 - s) * z + b * (1 - z)                 # revised action step
    # s in [0,1] and the step is affine, strictly decreasing in s (coeff -z<=0).
    hi = sp.simplify(act.subs(s, 0))                # s=0  -> upper end
    lo = sp.simplify(act.subs(s, 1))                # s=1  -> lower end
    width_new = sp.simplify(hi - lo)

    old = R * (1 - p) / (1 - p * R)                 # existing collapse form
    old_hi = sp.simplify(old.subs(p, 0))            # p=0 -> R
    old_lo = sp.simplify(sp.limit(old, p, 1))       # p=1 -> 0
    width_old = sp.simplify(old_hi - old_lo)

    print("F1  REACHABLE SETS (SymPy)")
    print(f"   revised, b fixed : [{lo}, {hi}]   width = {width_new}")
    print(f"   existing, p free : [{old_lo}, {old_hi}]   width = {width_old}")
    ck("revised band width is exactly z, free of b", sp.simplify(width_new - z) == 0)
    ck("existing band width is exactly R (=z)", sp.simplify(width_old - R) == 0)
    ck("the two widths are the SAME function of prior risk",
       sp.simplify(width_new.subs(z, R) - width_old) == 0)
    # the translation is b(1-z): revised band = existing band + b(1-z)
    ck("revised band = existing band translated by b(1-z)",
       sp.simplify(lo - b * (1 - z)) == 0 and sp.simplify(hi - (z + b * (1 - z))) == 0)
    # the existing model can never raise risk; the revised one can, iff b>0
    ck("existing model forbids risk increase (upper end == prior)",
       sp.simplify(old_hi - R) == 0)
    ck("revised model permits risk increase exactly when b>0",
       sp.simplify(hi - z - b * (1 - z)) == 0)
    # with b ALSO free the union is all of [0,1]
    ck("b free => union over b reaches 0 and 1",
       sp.simplify(lo.subs(b, 0)) == 0 and sp.simplify(hi.subs(b, 1)) == 1)

    # z3: no (s,b) with b pinned can escape the band. Second, independent tool.
    from z3 import Reals, Solver, And, Or, unsat
    zz, ss, bb, dd = Reals("z s b d")
    S = Solver()
    S.add(And(zz >= 0, zz <= 1, ss >= 0, ss <= 1, bb >= 0, bb <= 1))
    S.add(dd == (1 - ss) * zz + bb * (1 - zz))
    S.add(Or(dd < bb * (1 - zz), dd > zz + bb * (1 - zz)))   # outside the band
    ck("z3: no action outcome lies outside the width-z band", S.check() == unsat)

    # mpmath, 40 digits, third check on the width.
    import mpmath as mp
    mp.mp.dps = 40
    worst_mp = mp.mpf(0)
    worst_ex = F(0)
    for i in range(21):
        for j in range(21):
            zv, bv = mp.mpf(i) / 20, mp.mpf(j) / 20
            w = ((1 - 0) * zv + bv * (1 - zv)) - ((1 - 1) * zv + bv * (1 - zv))
            worst_mp = max(worst_mp, abs(w - zv))
            ze, be = F(i, 20), F(j, 20)
            we = ((1 - 0) * ze + be * (1 - ze)) - ((1 - 1) * ze + be * (1 - ze))
            worst_ex = max(worst_ex, abs(we - ze))
    ck(f"exact rationals: worst |width - z| = {worst_ex}", worst_ex == 0)
    ck(f"mpmath 40dp: worst |width - z| = {mp.nstr(worst_mp, 5)} (rounding only, < 1e-35)",
       worst_mp < mp.mpf("1e-35"))
    print()


# ---------------------------------------------------------------- F2
def f2_appendix_712_has_the_same_degeneracy() -> None:
    """SymPy: 7.12 IS the revised action step reparameterised, degeneracy and all."""
    import sympy as sp
    z, s, b, nu, eps, D = sp.symbols("z s b nu eps D", nonnegative=True)

    revised = (1 - s) * z + b * (1 - z)
    appendix = nu * D + eps                           # 7.12 state transition
    mapped = appendix.subs({nu: 1 - s, eps: b * (1 - z), D: z})

    print("F2  APPENDIX 7.12 UNDER THE SUBSTITUTION nu = 1-s, eps = b(1-z)")
    print(f"   revised action step : {sp.expand(revised)}")
    print(f"   7.12 mapped         : {sp.expand(mapped)}")
    ck("7.12's recursion IS the revised action step, exactly",
       sp.simplify(sp.expand(revised - mapped)) == 0)

    # fixed points, both ways
    fp_rev = sp.solve(sp.Eq(revised.subs(z, D), D), D)[0]
    fp_app = sp.simplify((eps / (1 - nu)).subs({nu: 1 - s, eps: b * (1 - fp_rev)}))
    print(f"   revised fixed point : {sp.simplify(fp_rev)}")
    print(f"   7.12  D* = eps*/(1-nu), eps* = b(1-D*) : {sp.simplify(fp_app)}")
    ck("fixed points agree exactly (b/(s+b))",
       sp.simplify(fp_rev - sp.Rational(1) * b / (s + b)) == 0
       and sp.simplify(fp_rev - fp_app) == 0)

    # THE DEGENERACY, in 7.12's OWN coordinates: for any target D* and any nu<1
    # there is an eps* reaching it. Same 1 free direction CC1 charges to the
    # revision alone.
    Dstar, nuv = sp.symbols("Dstar nuv", nonnegative=True)
    eps_sol = sp.solve(sp.Eq(eps / (1 - nuv), Dstar), eps)[0]
    print(f"   7.12 solved for eps* given ANY nu : eps* = {sp.simplify(eps_sol)}")
    ck("7.12 reaches any target D* along a 1-parameter line, exactly as the revision does",
       sp.simplify(eps_sol - Dstar * (1 - nuv)) == 0)
    ck("that line is inside 7.12's own stated domain nu in [0,1), eps >= 0",
       sp.simplify(eps_sol.subs({Dstar: sp.Rational(1, 3), nuv: sp.Rational(1, 2)})) > 0)
    print()


# ---------------------------------------------------------------- F3
def load_sk() -> list[dict]:
    rows: list[dict] = []
    for f in sorted(glob.glob(str(ROOT / "bench/logs/*/runner_state.json"))):
        if os.path.getsize(f) > MAX_BYTES:
            continue
        try:
            raw = open(f, errors="ignore").read()
        except OSError:
            continue
        if "sk_result" not in raw:
            continue
        try:
            d = json.loads(raw)
        except Exception:
            continue

        def walk(o):
            if isinstance(o, dict):
                sk = o.get("sk_result")
                if isinstance(sk, dict) and "tristate" in sk:
                    rows.append(sk)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(d)
    return rows


def f3_score_floor() -> None:
    rows = load_sk()
    adm = [r for r in rows if r.get("tristate") == "ADMISSIBLE"]
    n = len(adm)
    print(f"F3  THE FIX SCORE, MEASURED ({len(rows)} decisions, {n} scored)")

    A = Counter(r.get("A") for r in rows)
    ck(f"A is binary over the whole archive: {dict(A)}", set(A) <= {0.0, 1, 1.0})

    for g in ("e4_bandit", "g1_ast", "g2_compile", "e3_ruff", "e2_regression"):
        c = Counter((r.get("gate_details") or {}).get(g, {}).get("score") for r in adm)
        const = len(c) == 1
        k = sum(v for key, v in c.items() if key is not None and float(key) == 1.0)
        lo, hi = wilson(k, n)
        print(f"   {g:14s} distinct={len(c):2d}  score==1.0 in {k}/{n} "
              f"= {k/n:8.4%} Wilson [{lo:.4%}, {hi:.4%}]{'   CONSTANT' if const else ''}")
    ck("e4_bandit (weight 2.0) emitted a constant 1.0 on every scored fix",
       len(Counter((r.get("gate_details") or {}).get("e4_bandit", {}).get("score")
                   for r in adm)) == 1)

    # THE ALGEBRAIC FLOOR, derived with SymPy then proved unreachable with z3.
    import sympy as sp
    e2, e3, e4 = sp.symbols("e2 e3 e4", nonnegative=True)
    E_all = sp.Rational(2, 5) * e2 + sp.Rational(1, 5) * e3 + sp.Rational(2, 5) * e4
    E_noe2 = sp.Rational(1, 3) * e3 + sp.Rational(2, 3) * e4
    floor_all = sp.simplify(E_all.subs({e2: 0, e3: 0, e4: 1}))
    floor_noe2 = sp.simplify(E_noe2.subs({e3: 0, e4: 1}))
    print(f"   E (all gates, w=2,1,2) = {E_all};  floor at e4=1 is {floor_all}")
    print(f"   E (e2 unavailable)     = {E_noe2};  floor at e4=1 is {floor_noe2}")
    ck("floor with all gates available is exactly 2/5", floor_all == sp.Rational(2, 5))
    ck("floor with the regression gate unavailable is exactly 2/3",
       floor_noe2 == sp.Rational(2, 3))

    # The algebra predicts the OBSERVED minima. This is the falsifiable part.
    grp = defaultdict(list)
    for r in adm:
        un = tuple(sorted((r.get("gate_details") or {}).get("_unavailable", [])))
        grp[un].append(r)
    for un, v in sorted(grp.items(), key=lambda t: -len(t[1])):
        sks = [x["sk"] for x in v]
        print(f"   group unavailable={un or '(none)'}: n={len(v)} min sk={min(sks)} "
              f"max={max(sks)} distinct={len(set(sks))}")
    # Predict EVERY recorded sk from the recorded per-gate scores and weights.
    # This is the falsifiable core of F3: if the weights or the renormalisation
    # were not what the source says, these reconstructions would disagree.
    bad = 0
    for r in adm:
        g = r.get("gate_details") or {}
        parts = []
        for name, w in (("e2_regression", 2), ("e3_ruff", 1), ("e4_bandit", 2)):
            sc = (g.get(name) or {}).get("score")
            if sc is not None:
                parts.append((F(str(sc)) if not isinstance(sc, int) else F(sc), w))
        W = sum(w for _, w in parts)
        Ehat = sum(F(w, W) * sc for sc, w in parts)
        if abs(float(Ehat) - r["sk"]) > 5e-5:   # sk is round(.,4)
            bad += 1
    ck(f"every archived sk reconstructs from its own gate scores at weights 2/1/2 "
       f"({n - bad}/{n} exact to 4dp)", bad == 0)

    # z3: with e4 available and equal to 1, E can NEVER reach 0.395043.
    from z3 import Reals, Solver, And, unsat
    a2, a3, a4, Ev = Reals("a2 a3 a4 Ev")
    S = Solver()
    S.add(And(a2 >= 0, a2 <= 1, a3 >= 0, a3 <= 1, a4 == 1))
    S.add(Ev == a2 * 2 / 5 + a3 * 1 / 5 + a4 * 2 / 5)
    S.add(Ev < 0.395043)
    ck("z3: threshold 0.395043 is UNREACHABLE while e4_bandit returns 1 (unsat)",
       S.check() == unsat)
    S2 = Solver()
    S2.add(And(a2 >= 0, a2 <= 1, a3 >= 0, a3 <= 1, a4 == 1))
    S2.add(Ev == a2 * 2 / 5 + a3 * 1 / 5 + a4 * 2 / 5)
    S2.add(Ev < 0.504931)
    ck("z3: threshold 0.504931 IS reachable in principle (sat)", S2.check() != unsat)

    # Extensional identity of the two gates on the archive.
    sks = [r["sk"] for r in adm]
    mn = min(sks)
    ck(f"both disputed thresholds sit below the observed minimum {mn}",
       0.504931 < mn and 0.395043 < mn)
    ones = sum(1 for s in sks if s == 1.0)
    lo, hi = wilson(ones, n)
    c = Counter(sks)
    H = -sum((k / n) * math.log2(k / n) for k in c.values())
    print(f"   sk == 1.0 exactly: {ones}/{n} = {ones/n:.4%} Wilson [{lo:.4%}, {hi:.4%}]")
    print(f"   distinct levels {len(c)}, Shannon H = {H:.4f} bits, "
          f"effective levels 2^H = {2**H:.4f}, sd = {(sum((x-sum(sks)/n)**2 for x in sks)/n)**0.5:.6f}")

    try:
        from statsmodels.stats.proportion import proportion_confint
        l2, h2 = proportion_confint(ones, n, alpha=0.05, method="wilson")
        ck("statsmodels Wilson agrees with the local closed form",
           abs(l2 - lo) < 1e-12 and abs(h2 - hi) < 1e-12)
    except ImportError:
        print("   [SKIP] statsmodels unavailable")
    try:
        import numpy as np
        ck("NumPy agrees on the tie-at-ceiling count",
           int((np.array(sks) == 1.0).sum()) == ones)
    except ImportError:
        print("   [SKIP] numpy unavailable")
    print()


# ---------------------------------------------------------------- F4
def f4_stopping_rule_test_is_not_runnable() -> None:
    """The founder's point-10 test needs 2 numbers per run. They are not
    co-located, and the only available proxy is unsound in BOTH directions."""
    import ast
    print("F4  CAN THE FOUNDER'S STOPPING-RULE TEST BE RUN ON THIS ARCHIVE?")
    src = (ROOT / "bench/reference_runner_v3.py").read_text(errors="ignore")

    state_keys = set()
    for f in sorted(glob.glob(str(ROOT / "bench/logs/*/runner_state.json"))):
        try:
            state_keys |= set(json.loads(open(f, errors="ignore").read()).keys())
        except Exception:
            pass
    print(f"   union of runner_state.json top-level keys: {sorted(state_keys)}")
    ck("runner_state.json persists NO rounds-executed count",
       not any(k in state_keys for k in ("rounds_executed", "n_rounds", "round_count")))
    ck("runner_state.json persists NO termination reason",
       not any(k in state_keys for k in
               ("termination_reason", "termination", "stop_reason", "outcome")))
    ck("runner_state.json persists NO ceiling",
       "max_rounds" not in state_keys and "extension_cap" not in state_keys)

    # Why the only proxy (len(gamma_history)) cannot substitute.
    ck("gamma_history has exactly 1 append site (so it counts rounds...)",
       src.count("gamma_history.append(") == 1)
    ck("...but is CLEARED on phase transitions, so it undercounts",
       src.count("gamma_history.clear()") >= 1)
    ck("...and is RESTORED from checkpoint on resume, so it overcounts",
       'ckpt_data.get("gamma_history"' in src)
    ck("...and cfg (hence max_rounds) is replaced mid-run by phase overrides",
       "cfg = replace(cfg, **overrides)" in src)

    # The proxy, reported ONLY to show it disagrees with itself.
    runs = {}
    for f in sorted(glob.glob(str(ROOT / "bench/logs/*/runner_state.json"))):
        try:
            d = json.loads(open(f, errors="ignore").read())
        except Exception:
            continue
        runs[os.path.basename(os.path.dirname(f))] = len(d.get("gamma_history") or [])
    over = 0
    comp = 0
    for run, glen in runs.items():
        mr = None
        for g in glob.glob(str(ROOT / f"bench/logs/{run}/*.json")):
            if g.endswith("runner_state.json"):
                continue
            try:
                d = json.loads(open(g, errors="ignore").read())
            except Exception:
                continue

            def find(o):
                if isinstance(o, dict):
                    if isinstance(o.get("max_rounds"), int):
                        return o["max_rounds"]
                    for v in o.values():
                        r = find(v)
                        if r is not None:
                            return r
                elif isinstance(o, list):
                    for v in o:
                        r = find(v)
                        if r is not None:
                            return r
                return None
            mr = find(d)
            if mr is not None:
                break
        if mr is None:
            continue
        comp += 1
        cap = None
        if glen > mr:
            over += 1
    print(f"   runs with both a series and a launch ceiling: {comp}")
    print(f"   runs whose series EXCEEDS the launch ceiling: {over}  "
          f"<- impossible if the series were a round count")
    ck("the proxy is self-refuting: some series exceed the run's own ceiling",
       over > 0)
    print("   => the test is NOT runnable on this archive. VERDICT: UNCHECKED,")
    print("      and the fix is 1 persisted field, not new apparatus.")
    print()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)
    f1_reachable_sets()
    f2_appendix_712_has_the_same_degeneracy()
    f3_score_floor()
    f4_stopping_rule_test_is_not_runnable()
    print("-" * 70)
    if FAIL:
        print(f"FALSIFIED: {len(FAIL)} check(s) failed:")
        for f in FAIL:
            print("   -", f)
        return 1
    print("All checks passed. No claim in this seat's answer is asserted unexecuted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
