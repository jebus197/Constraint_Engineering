#!/usr/bin/env python3
"""Is the frozen critical cut of 0.7 a severity measurement, or a constant with no scale behind it?

HIS QUESTION, 2026-11-11, which this script answers by measurement rather than by argument:
whether pinning an exact number on severity is "an entirely arbitrary and vacuous exercise"
once severity is accepted as a quantity each STEM domain already measures on its own scale,
and whether the harness and the models therefore "need to be told at what severity scale to
use and what the 'cut' should be, so that severity can be determined on a per domain basis".

4 things are measured, each on 2 independent tools:

  A. ROUTING. Where the harness gets a domain from, by AST over the live runner rather than
     by grep, and how many distinct domains the archive actually carries.
  B. DECLARATION. How many of the live domain configs declare a severity scale, and how many
     declare a cut.
  C. INVARIANCE. Whether `count(severity >= 0.7)` survives a strictly increasing re-scaling
     of the severity axis -- the admissible transformation of an ordinal scale -- and whether
     a cut named by a DISTINGUISHED ELEMENT survives it instead. z3 for the general claim,
     SymPy for the concrete transformation and its monotonicity.
  D. CONSEQUENCE. How many archived entries change CRITICAL status under a re-scaling that
     preserves the ORDER of every pair exactly.

Every proportion carries a Wilson and a Clopper-Pearson interval, each computed on 2 routes.
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
RUNNER = REPO / "bench" / "reference_runner_v3.py"
DOMAINS = REPO / "bench" / "cdsfl_registry" / "domains"
CUT = 0.7

INCLUDE_SEAT_COPIES = False


def _state_files():
    """DECLARED FRAME: byte-identical duplicates skipped, by file digest."""
    import hashlib

    seen = set()
    for fp in sorted(LOGS.glob("**/runner_state.json")):
        try:
            raw = fp.read_bytes()
        except OSError:
            continue
        if not INCLUDE_SEAT_COPIES:
            dg = hashlib.sha256(raw).hexdigest()
            if dg in seen:
                continue
            seen.add(dg)
        yield fp


def entries():
    for fp in _state_files():
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:  # noqa: BLE001
            continue
        reg = ((d or {}).get("registry") or {})
        for cid, e in (reg.get("entries") or {}).items():
            if isinstance(e, dict):
                yield fp, cid, e


# ---------------------------------------------------------------- intervals

def wilson_two_routes(k: int, n: int):
    """statsmodels, and the closed form in mpmath. Returns (lo, hi, max abs gap)."""
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp

    a_lo, a_hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    mp.mp.dps = 40
    z = mp.sqrt(2) * mp.erfinv(mp.mpf("0.95"))
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / d
    half = (z / d) * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    b_lo, b_hi = centre - half, centre + half
    gap = max(abs(mp.mpf(a_lo) - b_lo), abs(mp.mpf(a_hi) - b_hi))
    return float(a_lo), float(a_hi), float(gap)


def clopper_two_routes(k: int, n: int):
    """scipy beta quantiles, and an exact binomial tail bisection in mpmath."""
    from scipy.stats import beta
    import mpmath as mp

    a_lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    a_hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    mp.mp.dps = 30

    def tail_ge(p):  # P(X >= k)
        return mp.nsum(lambda i: mp.binomial(n, i) * p ** i * (1 - p) ** (n - i),
                       [k, n]) if 0 < p < 1 else (mp.mpf(1) if p >= 1 else mp.mpf(0))

    def tail_le(p):  # P(X <= k)
        return mp.nsum(lambda i: mp.binomial(n, i) * p ** i * (1 - p) ** (n - i),
                       [0, k]) if 0 < p < 1 else (mp.mpf(0) if p >= 1 else mp.mpf(1))

    b_lo = mp.mpf(0) if k == 0 else mp.findroot(lambda p: tail_ge(p) - mp.mpf("0.025"),
                                                mp.mpf(a_lo) if a_lo > 0 else mp.mpf("1e-9"))
    b_hi = mp.mpf(1) if k == n else mp.findroot(lambda p: tail_le(p) - mp.mpf("0.025"),
                                                mp.mpf(a_hi) if a_hi < 1 else mp.mpf(1) - mp.mpf("1e-9"))
    gap = max(abs(mp.mpf(a_lo) - b_lo), abs(mp.mpf(a_hi) - b_hi))
    return a_lo, a_hi, float(gap)


# ---------------------------------------------------------------- A. routing

def measure_routing():
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    args = []
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "add_argument" and n.args
                and isinstance(n.args[0], ast.Constant)
                and isinstance(n.args[0].value, str)
                and "domain" in n.args[0].value):
            kw = {k.arg: (k.value.value if isinstance(k.value, ast.Constant) else "<expr>")
                  for k in n.keywords}
            args.append((n.args[0].value, kw.get("default"), n.lineno))
    # Is there any function whose body derives a domain from the TASK text?
    classifiers = []
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and "domain" in n.name.lower() and (
                "classif" in n.name.lower() or "infer" in n.name.lower()
                or "detect" in n.name.lower() or "route" in n.name.lower()):
            classifiers.append((n.name, n.lineno))
    return args, classifiers


def measure_archive_domains():
    from collections import Counter

    seen = Counter()
    files = 0
    for fp in _state_files():
        files += 1
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:  # noqa: BLE001
            continue
        for key in ("domain", "task_domain"):
            v = (d or {}).get(key) or ((d or {}).get("config") or {}).get(key)
            if isinstance(v, str) and v:
                seen[v] += 1
                break
    return files, seen


# ------------------------------------------------------------ B. declaration

def measure_declarations():
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover
        import tomli as tomllib  # type: ignore

    SCALE_KEYS = {"severity_scale", "consequence_scale", "severity_levels",
                  "scale", "severity_cut", "critical_cut", "cut", "theta_crit"}
    rows = []
    for fp in sorted(DOMAINS.glob("*.toml")) + sorted((DOMAINS / "immune").glob("*.toml")):
        try:
            data = tomllib.loads(fp.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            data = {}
        keys = set()

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    keys.add(k)
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)

        walk(data)
        rows.append((fp.relative_to(REPO).as_posix(), sorted(keys & SCALE_KEYS)))
    return rows


# ------------------------------------------------------------- C. invariance

def prove_invariance():
    """z3: a fixed-VALUE cut is breakable; a DISTINGUISHED-ELEMENT cut is not."""
    import z3

    out = {}
    # (1) Fixed value cut. 2 severities, order preserved, yet the count changes.
    s1, s2, t1, t2, c = z3.Reals("s1 s2 t1 t2 c")
    solver = z3.Solver()
    solver.add(0 <= s1, s1 < s2, s2 <= 1, 0 <= t1, t1 < t2, t2 <= 1)  # phi strictly increasing
    solver.add(c == CUT)
    before = z3.If(s1 >= c, 1, 0) + z3.If(s2 >= c, 1, 0)
    after = z3.If(t1 >= c, 1, 0) + z3.If(t2 >= c, 1, 0)
    solver.add(before != after)
    out["fixed_cut_breakable"] = str(solver.check())
    #: ★ THE WITNESS IS RETURNED AS NUMBERS, NOT ONLY AS A STRING -- 2026-11-11.
    #: A guard that asserts only `sat` cannot tell WHICH constraint was solved:
    #: flipping `before != after` to `before == after` leaves the answer `sat`
    #: and inverts the claim, and the guard's own mutation harness caught
    #: exactly that (M1 green on the first run). Returning the model's values
    #: lets the guard check the PROPERTY -- order preserved, counts differ --
    #: rather than the solver's verdict about an unseen question.
    out["fixed_cut_witness"] = ""
    out["fixed_cut_values"] = {}
    if solver.check() == z3.sat:
        mdl = solver.model()
        out["fixed_cut_witness"] = str(mdl)

        def _f(sym):
            v = mdl.eval(sym, model_completion=True)
            return float(v.numerator_as_long()) / float(v.denominator_as_long())

        out["fixed_cut_values"] = {"s1": _f(s1), "s2": _f(s2),
                                   "t1": _f(t1), "t2": _f(t2), "c": _f(c)}

    # (2) Distinguished-element cut. The cut IS one of the severities and travels with phi.
    k = z3.Int("k")
    s1b, s2b, s3b, t1b, t2b, t3b = z3.Reals("s1b s2b s3b t1b t2b t3b")
    s2v = z3.Solver()
    s2v.add(s1b < s2b, s2b < s3b, t1b < t2b, t2b < t3b)       # order preserved exactly
    s2v.add(k >= 1, k <= 3)
    cut_before = z3.If(k == 1, s1b, z3.If(k == 2, s2b, s3b))
    cut_after = z3.If(k == 1, t1b, z3.If(k == 2, t2b, t3b))
    cnt_before = (z3.If(s1b >= cut_before, 1, 0) + z3.If(s2b >= cut_before, 1, 0)
                  + z3.If(s3b >= cut_before, 1, 0))
    cnt_after = (z3.If(t1b >= cut_after, 1, 0) + z3.If(t2b >= cut_after, 1, 0)
                 + z3.If(t3b >= cut_after, 1, 0))
    s2v.add(cnt_before != cnt_after)
    out["ranked_cut_breakable"] = str(s2v.check())   # expect unsat
    return out


def sympy_transformation(max_sev: float):
    """SymPy: the AFFINE map phi(x) = a*x is strictly increasing for a > 0 and is
    admissible on an interval or ratio scale, let alone an ordinal one. Solve for the
    `a` that puts the archive MAXIMUM just below the cut, so every CRITICAL call is
    destroyed by a transformation that preserves every pairwise order exactly."""
    import sympy as sp

    x, a = sp.symbols("x a", positive=True)
    phi = a * x
    deriv = sp.diff(phi, x)                     # = a
    strictly_increasing = sp.simplify(sp.Gt(deriv, 0))
    m = sp.Rational(str(max_sev))
    cut = sp.Rational(str(CUT))
    a_star = sp.solve(sp.Eq(a * m, cut), a)[0]  # a* = cut / max
    return {
        "derivative": str(deriv),
        "strictly_increasing": str(strictly_increasing),
        "a_star": float(a_star),
        "check_at_a_star": float(a_star * m),
    }


# ------------------------------------------------------------ D. consequence

def measure_consequence():
    """Re-scale with phi(x) = a*x, a = 0.999 * CUT / max. Strictly increasing, so EVERY
    pairwise order is preserved exactly; and it puts the archive maximum just below the
    cut, so every CRITICAL call vanishes. Counted on 2 independent routes."""
    import math

    import numpy as np

    sevs = []
    for fp, cid, e in entries():
        v = e.get("severity")
        if isinstance(v, (int, float)) and 0.0 <= float(v) <= 1.0:
            sevs.append(float(v))
    arr = np.asarray(sevs, dtype=float)
    n = int(arr.size)
    if n == 0:
        return {"n": 0}
    mx = float(arr.max())
    before_np = int((arr >= CUT).sum())
    before_py = sum(1 for v in sevs if v >= CUT)          # route 2: pure Python

    a = (0.999 * CUT / mx) if mx > 0 else 0.5
    phi = arr * a
    after_np = int((phi >= CUT).sum())
    after_py = sum(1 for v in sevs if v * a >= CUT)

    from scipy.stats import spearmanr
    rho = float(spearmanr(arr, phi).statistic)
    rng = np.random.default_rng(0)
    idx = rng.choice(n, size=min(n, 400), replace=False)
    s, t = arr[idx], phi[idx]
    pair_ok = bool(np.all(np.sign(s[:, None] - s[None, :]) == np.sign(t[:, None] - t[None, :])))

    return {"n": n, "max": mx, "a": a,
            "before": before_np, "before_route2": before_py,
            "after": after_np, "after_route2": after_py,
            "routes_agree": (before_np == before_py and after_np == after_py),
            "flipped": before_np - after_np,
            "spearman_rho": rho, "pairs_order_preserved": pair_ok}


def main(argv) -> int:
    #: ★ A `--help` MUST NEVER COST ANYTHING. This answers the flag and returns
    #: BEFORE the archive walk, because 15 of 17 runners once billed for a help
    #: request. Checked by `bench/tests/test_help_is_answered_2026-09-11.py`,
    #: which requires a usage line on stdout and no measurement behind it.
    if any(a in ("-h", "--help") for a in argv):
        print("usage: the_cut_is_a_domain_property_not_a_constant_2026-11-11.py [-h]")
        print(__doc__)
        return 0

    print("=" * 78)
    print("THE CUT IS A DOMAIN PROPERTY, NOT A CONSTANT — measured 2026-11-11")
    print("=" * 78)

    print("\nA. ROUTING — where does the harness get a domain from?")
    args, classifiers = measure_routing()
    for name, default, lineno in args:
        print(f"   {RUNNER.relative_to(REPO)}:{lineno}  {name}  default={default!r}")
    print(f"   command-line domain arguments: {len(args)}")
    print(f"   functions that CLASSIFY a domain from task content: {len(classifiers)}  {classifiers}")
    files, seen = measure_archive_domains()
    print(f"   archived runner_state.json files (de-duplicated by digest): {files}")
    print(f"   distinct domains recorded across them: {len(seen)}  {dict(seen)}")

    print("\nB. DECLARATION — which domain configs declare a severity scale or a cut?")
    rows = measure_declarations()
    with_scale = [r for r in rows if r[1]]
    print(f"   domain config files: {len(rows)}")
    print(f"   declaring any severity scale or cut key: {len(with_scale)}")
    if rows:
        k, n = len(with_scale), len(rows)
        wlo, whi, wgap = wilson_two_routes(k, n)
        clo, chi, cgap = clopper_two_routes(k, n)
        print(f"   {k} of {n} = {k/n:.6f}")
        print(f"     Wilson          [{wlo:.6f}, {whi:.6f}]   2 routes agree to {wgap:.3e}")
        print(f"     Clopper-Pearson [{clo:.6f}, {chi:.6f}]   2 routes agree to {cgap:.3e}")

    print("\nC. INVARIANCE — does a fixed-value cut survive a strictly increasing re-scaling?")
    z = prove_invariance()
    print(f"   z3, fixed cut at {CUT} can change the count while order is preserved: "
          f"{z['fixed_cut_breakable']}   (sat = NOT invariant)")
    print(f"      witness: {z['fixed_cut_witness']}")
    print(f"   z3, cut named by a DISTINGUISHED ELEMENT can change the count: "
          f"{z['ranked_cut_breakable']}   (unsat = invariant)")

    print("\nD. CONSEQUENCE — on the archive's own severities")
    d = measure_consequence()
    if d.get("n"):
        s = sympy_transformation(d["max"])
        print(f"   SymPy: phi(x) = a*x, derivative {s['derivative']}, "
              f"strictly increasing for a > 0: {s['strictly_increasing']}")
        print(f"   SymPy: a* = {CUT}/{d['max']} = {s['a_star']:.6f}, "
              f"and max*a* = {s['check_at_a_star']:.6f}")
        print(f"   archive severities in [0,1]: {d['n']}, maximum {d['max']:.6f}")
        print(f"   CRITICAL before re-scaling: {d['before']}")
        print(f"   CRITICAL after  re-scaling: {d['after']}   (a = {d['a']:.6f})")
        print(f"   2 counting routes (NumPy, pure Python) agree: {d['routes_agree']}  "
              f"before {d['before']}/{d['before_route2']}, after {d['after']}/{d['after_route2']}")
        print(f"   entries that FLIPPED while every pairwise order was preserved: {d['flipped']}")
        print(f"   Spearman rho between the 2 scales: {d['spearman_rho']:.10f}")
        print(f"   exhaustive pairwise sign check on a 400-sample: "
              f"order preserved = {d['pairs_order_preserved']}")
        if d["before"]:
            k, n = d["flipped"], d["before"]
            wlo, whi, wgap = wilson_two_routes(k, n)
            clo, chi, cgap = clopper_two_routes(k, n)
            print(f"   share of CRITICAL calls destroyed by a pure re-scaling: "
                  f"{k} of {n} = {k/n:.6f}")
            print(f"     Wilson          [{wlo:.6f}, {whi:.6f}]   2 routes agree to {wgap:.3e}")
            print(f"     Clopper-Pearson [{clo:.6f}, {chi:.6f}]   2 routes agree to {cgap:.3e}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
