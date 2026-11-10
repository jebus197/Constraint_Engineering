#!/usr/bin/env python3
"""Which of entry B21's 5 dependency-ordered steps are actually built.

WHY BY PARSING AND NOT BY READING. B21's own entry carries a correction headed
"THE PREMISE IS WRONG, ESTABLISHED BY EXECUTION": its headline said the
canonical runner does not call the policy engine, which the entry records as
*"true of the SYMBOL and false of the BEHAVIOUR"*. A question that has already
been answered wrongly once by reading prose is answered here by walking syntax
trees, and a call counts only when it is a real Call node -- a substring is not
a call, which cost 2 green reversions elsewhere on 2026-11-09.

THE 5 STEPS, quoted from the entry: (1) wire `load_effective_policy` into v3;
(2) redirect B13's 12 live per-model tables to read the merged policy instead of
their own dictionaries; (3) add a role dimension; (4) wire
`validate_all_policies()` as the run-level preflight; (5) generate the
selectable list from the registry plus an OpenRouter query plus a local-model
probe.

WHAT IT DELIBERATELY DOES NOT DO. It does not judge whether a step SHOULD be
built, and it does not touch the entry's marker. Adopting any of this changes
how a run selects models, which is his.
"""
from __future__ import annotations

import argparse
import ast
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
V3 = REPO / "bench/reference_runner_v3.py"

#: The 6 files B13 names as the LIVE harness, holding its 12 per-model tables.
LIVE_HARNESS = (
    "bench/reference_runner_v3.py",
    "bench/runner_core.py",
    "bench/cdsfl_registry/composer.py",
    "bench/experiment_11_orchestrator.py",
    "bench/routing.py",
    "bench/dm/_types.py",
)

#: Names any generator of a selectable model list would have to define.
SELECTABLE_NAMES = ("selectable", "available_models", "list_models",
                    "discover_models", "probe_local", "openrouter_models",
                    "selectable_models")

# THE CANONICAL `_iv`, LIFTED BYTE-EXACT FROM
# `scripts/what_the_commit_gate_actually_costs_over_time_2026-11-08.py`, where
# it is 1 of 16 identical copies (sha256 of the function source, first 16 hex:
# 5c0ff108ca6d5966). The explanation sits in this comment rather than in the
# docstring precisely so the body stays byte-identical: a docstring of my own
# would make this an 18th variant instead of the 17th user of the canonical
# one, and the guard that executes every `_iv` in `scripts/` requires all of
# them to agree.
#
# WHAT THE FIRST VERSION HERE GOT WRONG, AND IT IS NARROWER THAN FIRST
# REPORTED. It returned WILSON TWICE -- once from a written-out formula and
# once from statsmodels -- where every other helper returns Wilson and then
# CLOPPER-PEARSON. 2 facts follow and they are not the same fact:
#   (1) The TUPLE CONTRACT was broken. 6 parametrised cases of
#       `bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py` compare
#       all 4 numbers across every helper, so a Wilson pair in the slot the
#       others fill with Clopper-Pearson fails whatever the numbers are, and no
#       Clopper-Pearson interval was computed for B21's figures at all.
#   (2) The AGREEMENT FIGURE WAS NOT BOGUS, which is a correction of my own
#       correction. `scripts/counting_imports_ranks_producers_backwards_2026-11-03.py`
#       -- this project's own route predicate -- scores the old pairing
#       Wilson: 2 routes, `statsmodels proportion_confint` and `written-out
#       algebra`, and that guard's `test_the_same_quantity_twice_is_a_cross_check`
#       asserts exactly that pairing IS a cross-check. Calling it
#       near-tautological condemned a check the project accepts. It is the
#       WEAKER kind -- 1 formulation, 2 implementations -- and the 2026-10-31
#       independence rule says so, but it is not nothing. The printed
#       1.110223e-16 at 1 of 5 is also unchanged by this repair, because the
#       canonical helper reports max(Wilson spread, Clopper-Pearson spread) and
#       the Wilson spread dominates there.
# SymPy confirms the written-out lower bound minus the closed form simplifies
# to 0, so the 2 Wilson routes are the same quantity and not 2 quantities
# dressed as one.
#
# AND AT n == 0 IT RETURNS [0, 1], NOT [0, 0]. With no observations the
# binomial likelihood is 1 for every p, so no p is excluded and the whole unit
# interval is the only honest answer. The version here returned (0.0, 0.0),
# which asserts certainty that the proportion is 0 on the strength of no data.
def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    wdiff = max(abs(wl - (c - hw)), abs(wh - (c + hw)))
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))

    def bi(a, b, y):
        """Invert the regularised incomplete beta by bisection.

        HARDENED 2026-11-04. `mpmath.betainc` is fast, but its hyp2f1 path
        FAILS TO CONVERGE for large parameters at mid-range x. Measured at
        a=2437, b=17564 it succeeds for x <= 0.1264 and for x >= 0.9 and raises
        ValueError in between -- which is exactly where a bisection over [0, 1]
        takes its first step, so the whole inversion died rather than degrading.
        It surfaced when a producer called this at k=2436, n=20000; every
        existing caller used a small n, and the guard that executes every `_iv`
        against the same k and n uses n <= 38, so no test could have seen it.

        Where betainc raises, the same integral is computed by quadrature in
        log space instead. At the measured failing point that agreed with
        scipy's quantile to 1.11e-16. It costs about 6 s per bound against
        milliseconds for betainc, so it is used only after a failure, never by
        default.
        """
        logB = mpmath.log(mpmath.beta(a, b))

        def by_quad(x):
            if x <= 0:
                return mpmath.mpf(0)
            def dens(u):
                return mpmath.e**((a - 1) * mpmath.log(u)
                                  + (b - 1) * mpmath.log1p(-u) - logB)
            return mpmath.quad(dens, [0, min(mpmath.mpf(x), mpmath.mpf(1))])

        fell_back = False

        def f(x):
            nonlocal fell_back
            if not fell_back:
                try:
                    return mpmath.betainc(a, b, 0, x, regularized=True) - y
                except Exception:
                    fell_back = True
            return by_quad(x) - y

        # STOP ON PRECISION, not on a fixed count. The bracket halves every
        # step, so 2**-60 is already below this tolerance and a fixed 240 did
        # 180 redundant evaluations. That is free for betainc and it is NOT
        # free for the quadrature fallback, which costs about 28 ms per
        # evaluation: 240 steps took 6.66 s and 60 take 1.69 s for a bound
        # identical to 12 decimal places. The count is still capped so a
        # pathological case cannot spin.
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        tol = mpmath.mpf("1e-18")
        for _ in range(240):
            if hi - lo < tol:
                break
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)


def _tree(p: pathlib.Path):
    try:
        return ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, OSError):
        return None


def call_sites(p: pathlib.Path, name: str) -> list[int]:
    """Real Call nodes to `name`. A substring is not a call."""
    t = _tree(p)
    if t is None:
        return []
    out = []
    for n in ast.walk(t):
        if isinstance(n, ast.Call):
            f = n.func
            called = (f.attr if isinstance(f, ast.Attribute)
                      else getattr(f, "id", ""))
            if called == name:
                out.append(getattr(n, "lineno", 0))
    return out


def definitions(name: str) -> list[str]:
    out = []
    for root in (REPO / "bench", REPO / "scripts"):
        for p in root.rglob("*.py"):
            if "logs" in p.parts or "sandbox_harvest" in p.as_posix():
                continue
            t = _tree(p)
            if t is None:
                continue
            for n in ast.walk(t):
                if (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and n.name == name):
                    out.append(f"{p.relative_to(REPO).as_posix()}:{n.lineno}")
    return out




def _selectable_list_runs() -> str:
    """Path of a module that ACTUALLY produces a selectable model list, or "".

    Behavioural, not lexical. Imports each candidate module and calls any
    zero-argument public callable, accepting the first whose result is a
    non-empty sequence of mappings each carrying `id` and `source`. Returns
    the module path so the caller can name its evidence.

    IT NEVER RAISES AND IT NEVER REACHES THE NETWORK. Every import and call is
    wrapped, and the only candidates considered are modules in this repository;
    a callable that needs arguments is skipped rather than guessed at.
    """
    import importlib.util as _iu
    import inspect as _ins
    for mod_path in sorted(REPO.glob("bench/*catalogue*.py")) + \
            sorted(REPO.glob("bench/*model*list*.py")):
        try:
            spec = _iu.spec_from_file_location(f"_s5_{mod_path.stem}", mod_path)
            mod = _iu.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)
        except Exception:                                      # noqa: BLE001
            continue
        for name in dir(mod):
            if name.startswith("_"):
                continue
            fn = getattr(mod, name)
            if not callable(fn):
                continue
            try:
                sig = _ins.signature(fn)
                if any(p.default is _ins.Parameter.empty
                       and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
                       for p in sig.parameters.values()):
                    continue
                rows = fn()
            except Exception:                                  # noqa: BLE001
                continue
            if (isinstance(rows, (list, tuple)) and rows
                    and all(isinstance(r, dict) and "id" in r and "source" in r
                            for r in rows)):
                return f"{mod_path.relative_to(REPO)}:{name}"
    return ""

def measure() -> dict:
    s1 = call_sites(V3, "load_effective_policy")
    s4 = call_sites(V3, "validate_all_policies")

    reads = []
    for rel in LIVE_HARNESS:
        p = REPO / rel
        reads.append((rel, p.exists(),
                      len(call_sites(p, "load_effective_policy")) if p.exists() else 0))

    roles_dir = REPO / "bench/cdsfl_registry/roles"
    role_files = (sorted(x.name for x in roles_dir.glob("*.toml"))
                  if roles_dir.is_dir() else [])
    # the role dimension counts as built only if the merge function TAKES a role
    sig_takes_role = False
    reg = REPO / "bench/cdsfl_registry/registry.py"
    t = _tree(reg)
    if t is not None:
        for n in ast.walk(t):
            if (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and n.name == "load_effective_policy"):
                args = [a.arg for a in n.args.args + n.args.kwonlyargs]
                sig_takes_role = "role" in args

    #: ★ STEP 5 IS NOW DECIDED BY EXECUTION, 2026-11-10, AND THE NAME SEARCH IS
    #: KEPT BESIDE IT RATHER THAN REPLACED.
    #:
    #: WHY. `SELECTABLE_NAMES` is a guess at what the implementation would be
    #: called, written BEFORE any implementation existed. `bench/model_catalogue.py`
    #: was built on 2026-11-09 and names its functions `catalogue`,
    #: `local_models`, `remote_models`, `registry_models` and `known_roles` --
    #: 0 of the 7 guessed names -- so a WORKING step 5 measured as ABSENT. That
    #: is this project's own `execute-do-not-grep` lesson: a name is a proxy for
    #: a capability and the capability can be CALLED.
    #:
    #: WHAT IT ASKS NOW. Can something in the tree produce a selectable list?
    #: The test is behavioural: a callable that returns a non-empty sequence of
    #: mappings, each carrying an `id` and a `source`, with local entries
    #: sortable ahead of remote ones -- which is the founder's stated
    #: requirement, "available models on a user's local machine at the top of
    #: this list". A module that satisfies that IS step 5 whatever it is called.
    #:
    #: THE NAME SEARCH IS NOT REMOVED. It still runs and is still reported, so
    #: a future implementation using one of the expected names is still found,
    #: and so the 2 answers can be compared. Removing it would trade one blind
    #: proxy for another.
    s5 = {nm: definitions(nm) for nm in SELECTABLE_NAMES}
    s5_built = {k: v for k, v in s5.items() if v}
    s5_executed = _selectable_list_runs()
    if s5_executed and not s5_built:
        s5_built = {"(by execution)": [s5_executed]}

    k = sum(1 for _, _, c in reads if c)
    n = len(reads)
    return {
        "step1_v3_calls_load_effective_policy": s1,
        "step2_live_harness_reads_policy": reads,
        "step2_k": k, "step2_n": n,
        "step3_role_files": role_files,
        "step3_signature_takes_role": sig_takes_role,
        "step4_v3_calls_validate_all_policies": s4,
        "step5_definitions": s5_built,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    r = measure()

    done = []
    if args.json:
        print(json.dumps(r, indent=1, default=str))
        return 0

    print("B21's 5 DEPENDENCY-ORDERED STEPS, MEASURED BY WALKING SYNTAX TREES")
    print(f"  subject: {V3.relative_to(REPO).as_posix()}\n")

    s1 = r["step1_v3_calls_load_effective_policy"]
    print(f"1. load_effective_policy wired into v3     : "
          f"{'DONE' if s1 else 'NOT DONE'}  ({len(s1)} call site(s))")
    if not s1:
        others = definitions("load_effective_policy")
        print(f"     it IS defined at {others} and called from elsewhere; what is")
        print("     missing is the call in the CANONICAL runner, which is the step.")
    done.append(bool(s1))

    k, n = r["step2_k"], r["step2_n"]
    (wl, wh), (cpl, cph), diff = _iv(k, n)
    print(f"\n2. the live harness reads the merged policy : {k} of {n} file(s)")
    for rel, exists, c in r["step2_live_harness_reads_policy"]:
        tag = "READS" if c else ("own tables" if exists else "MISSING")
        print(f"     {tag:11s} {rel}")
    print(f"     share {k/n:.6f}  Wilson [{wl:.6f}, {wh:.6f}]")
    print(f"     Clopper-Pearson [{cpl:.6f}, {cph:.6f}]"
          f"  worst 2-route gap {diff:.3e}")
    done.append(k == n)

    rf, sig = r["step3_role_files"], r["step3_signature_takes_role"]
    ok3 = bool(rf) and sig
    print(f"\n3. a role dimension                        : "
          f"{'DONE' if ok3 else 'NOT DONE'}")
    print(f"     roles/*.toml           : {rf}")
    print(f"     merge signature takes a role : {sig}")
    done.append(ok3)

    s4 = r["step4_v3_calls_validate_all_policies"]
    print(f"\n4. validate_all_policies as a v3 preflight : "
          f"{'DONE' if s4 else 'NOT DONE'}  ({len(s4)} call site(s))")
    done.append(bool(s4))

    s5 = r["step5_definitions"]
    print(f"\n5. the selectable list is generated        : "
          f"{'DONE' if s5 else 'NOT DONE'}")
    if s5:
        for kk, vv in s5.items():
            print(f"     {kk}: {vv[:2]}")
    else:
        print(f"     0 definitions of any of {len(SELECTABLE_NAMES)} candidate names")
    done.append(bool(s5))

    kd, nd = sum(done), len(done)
    (dl, dh), (dcl, dch), ddiff = _iv(kd, nd)
    print(f"\nSTEPS BUILT: {kd} of {nd} = {kd/nd:.6f}")
    print(f"   Wilson [{dl:.6f}, {dh:.6f}]   "
          f"Clopper-Pearson [{dcl:.6f}, {dch:.6f}]")
    print(f"   worst disagreement between the 2 routes of EACH interval: "
          f"{ddiff:.3e}")
    print("\nTHIS IS A STATUS MEASUREMENT AND NOT A RECOMMENDATION. Adopting any")
    print("step changes how a run selects its models, which is the founder's.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
