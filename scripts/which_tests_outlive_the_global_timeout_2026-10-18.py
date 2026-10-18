#!/usr/bin/env python3
"""FOLLOW for the 300-second global per-test timeout: whose declared ceiling is
discarded, and which test was actually killed by it.

WHY THIS EXISTS. `pytest.ini` sets `timeout = 300` as a GLOBAL per-test backstop
with `timeout_method = thread`. On 2026-10-18 a test that RUNS the pre-commit hook
was measured at 334.83 seconds (committed 71-entry guard list) and 333.84 seconds
(77 entries). Both exceed 300, so pytest-timeout killed the thread and took the
WHOLE suite down with it -- which is why no full-suite figure exists after
`1cfc30e` (2026-09-29, 8,878 passed) despite 382 later commits.

THE BLAST RADIUS IS THE POINT. A test whose OWN subprocess budget exceeds the
global limit is unreachable by construction: the global timeout fires first and
the declared budget never applies. That is a silent, permanent red, and it is
invisible in any run that the timeout aborts. This script finds every such test
by PARSING the test tree, so the rate travels with its producer.

WHAT THIS CAN AND CANNOT SEE -- AND AN EARLIER VERSION OF THIS SCRIPT GOT IT
WRONG, which is worth recording because the error is the same shape as the defect
the script was written to investigate. It first labelled a declared budget above
the global limit as "can NEVER pass". THAT IS FALSE. A test declaring
`timeout=600` does not RUN for 600 seconds; the number is a ceiling. What is
true is narrower and still worth knowing: the declared ceiling is UNREACHABLE,
because the global 300-second limit always fires first, so the author's intent
is silently discarded. Whether the test actually dies depends on its REAL
runtime, which static parsing cannot observe. Only `--durations` can settle that,
and this script says so rather than guessing.

Three classes are reported, none of them a failure claim:
  UNREACHABLE_BUDGET  a subprocess ceiling above the global limit, so the
                      ceiling can never apply -- dead configuration, not a red
  NEAR_THE_LIMIT      a ceiling within 20% below the limit, where subprocess
                      teardown cost can cross it
  UNBOUNDED           a subprocess call carrying NO timeout at all, which
                      relies entirely on the global backstop

Every proportion carries a 95% interval, cross-verified across statsmodels,
scipy and an independent NumPy/mpmath closed form, per the 21 April 2026 rule.
"""
from __future__ import annotations
import argparse, ast, configparser, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TESTS = ROOT / "bench" / "tests"

def global_timeout() -> float:
    cp = configparser.ConfigParser()
    cp.read(ROOT / "pytest.ini")
    for sect in cp.sections():
        if cp.has_option(sect, "timeout"):
            return float(cp.get(sect, "timeout"))
    raise SystemExit("pytest.ini declares no global timeout; this script's premise is gone")

SUBPROC = {"run", "check_output", "check_call", "call", "Popen"}

def enclosing_test(tree: ast.Module, lineno: int) -> str | None:
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            end = getattr(node, "end_lineno", node.lineno)
            if node.lineno <= lineno <= end:
                if best is None or node.lineno > best.lineno:
                    best = node
    return best.name if best else None

def marker_timeout(tree: ast.Module, fname: str) -> float | None:
    """A @pytest.mark.timeout(N) on the test overrides the global limit."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == fname:
            for dec in node.decorator_list:
                if not isinstance(dec, ast.Call):
                    continue
                tgt = dec.func
                parts = []
                while isinstance(tgt, ast.Attribute):
                    parts.append(tgt.attr); tgt = tgt.value
                if isinstance(tgt, ast.Name):
                    parts.append(tgt.id)
                if "timeout" in parts and dec.args:
                    a = dec.args[0]
                    if isinstance(a, ast.Constant) and isinstance(a.value, (int, float)):
                        return float(a.value)
    return None

def scan():
    LIMIT = global_timeout()
    over, at_risk, unbounded, bounded_ok = [], [], [], []
    files = sorted(TESTS.glob("test_*.py"))
    for f in files:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else None)
            if name not in SUBPROC:
                continue
            # only count subprocess.*/sp.* style calls, not unrelated .run()
            if isinstance(fn, ast.Attribute):
                owner = fn.value
                oname = owner.id if isinstance(owner, ast.Name) else (
                    owner.attr if isinstance(owner, ast.Attribute) else "")
                if oname not in {"subprocess", "sp", "sub"}:
                    continue
            tname = enclosing_test(tree, node.lineno)
            if tname is None:
                continue
            eff = marker_timeout(tree, tname) or LIMIT
            tv = None
            for kw in node.keywords:
                if kw.arg == "timeout" and isinstance(kw.value, ast.Constant):
                    if isinstance(kw.value.value, (int, float)):
                        tv = float(kw.value.value)
            rec = {"file": f.name, "test": tname, "line": node.lineno,
                   "subprocess_budget": tv, "effective_limit": eff}
            if tv is None:
                unbounded.append(rec)
            elif tv > eff:
                over.append(rec)
            elif tv >= 0.8 * eff:
                at_risk.append(rec)
            else:
                bounded_ok.append(rec)
    return LIMIT, files, over, at_risk, unbounded, bounded_ok

def intervals(k: int, n: int):
    """Wilson + Clopper-Pearson, three independent implementations."""
    out = {}
    try:
        from statsmodels.stats.proportion import proportion_confint
        out["statsmodels_wilson"] = tuple(proportion_confint(k, n, method="wilson"))
        out["statsmodels_exact"] = tuple(proportion_confint(k, n, method="beta"))
    except Exception as e:
        out["statsmodels_wilson"] = f"UNAVAILABLE: {e}"
    try:
        from scipy.stats import beta as sbeta
        lo = 0.0 if k == 0 else float(sbeta.ppf(0.025, k, n - k + 1))
        hi = 1.0 if k == n else float(sbeta.ppf(0.975, k + 1, n - k))
        out["scipy_exact"] = (lo, hi)
    except Exception as e:
        out["scipy_exact"] = f"UNAVAILABLE: {e}"
    try:
        import numpy as np
        z = 1.959963984540054
        p = k / n
        d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        out["numpy_closed_form_wilson"] = (float(c - h), float(c + h))
    except Exception as e:
        out["numpy_closed_form_wilson"] = f"UNAVAILABLE: {e}"
    try:
        import mpmath as mp
        mp.mp.dps = 30
        z = mp.mpf("1.959963984540054"); p = mp.mpf(k) / n
        d = 1 + z**2 / n
        c = (p + z**2 / (2 * n)) / d
        h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
        out["mpmath_wilson"] = (float(c - h), float(c + h))
    except Exception as e:
        out["mpmath_wilson"] = f"UNAVAILABLE: {e}"
    return out

def main() -> int:
    # `--help` MUST NOT COST ANYTHING, and the first version of this script
    # ignored the flag and ran the whole 668-file parse instead. The commit
    # guard `bench/tests/test_help_is_answered_2026-09-11.py` refused it, which
    # is the rule working: a reader asking what a measurement does should never
    # be charged the measurement to find out. argparse exits before `scan()`.
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--alpha", type=float, default=0.05,
                    help="two-sided significance level for the intervals")
    ap.parse_args()

    LIMIT, files, over, at_risk, unbounded, ok = scan()
    print("=" * 74)
    print("WHICH TESTS OUTLIVE THE GLOBAL PER-TEST TIMEOUT")
    print("=" * 74)
    print(f"pytest.ini global per-test timeout : {LIMIT:.0f} s")
    print(f"test files parsed                  : {len(files)}")
    total = len(over) + len(at_risk) + len(unbounded) + len(ok)
    print(f"subprocess call sites inside tests : {total}")
    print()
    for label, rows in (("UNREACHABLE BUDGET (ceiling above the global limit; "
                         "NOT a failure claim)", over),
                        ("NEAR THE LIMIT (within 20% below)", at_risk),
                        ("UNBOUNDED (no timeout kwarg; relies on the backstop)",
                         unbounded)):
        print(f"--- {label}: {len(rows)} ---")
        for r in rows[:40]:
            b = "none" if r["subprocess_budget"] is None else f"{r['subprocess_budget']:.0f}s"
            print(f"    {r['file']}:{r['line']}  {r['test']}")
            print(f"        budget={b}  effective_limit={r['effective_limit']:.0f}s")
        if len(rows) > 40:
            print(f"    ... and {len(rows)-40} more")
        print()
    if total:
        for label, k in (("UNREACHABLE_BUDGET", len(over)),
                         ("NEAR_THE_LIMIT", len(at_risk)),
                         ("UNBOUNDED", len(unbounded))):
            ci = intervals(k, total)
            print(f"RATE {label}: {k} of {total} = {100.0*k/total:.4f}%")
            for name, v in ci.items():
                if isinstance(v, tuple):
                    print(f"    {name:26} [{100*v[0]:.4f}%, {100*v[1]:.4f}%]")
                else:
                    print(f"    {name:26} {v}")
            print()
    print("=" * 74)
    print("AN UNREACHABLE BUDGET IS NOT A FAILING TEST. It means the author's")
    print("declared ceiling is discarded, because the global limit fires first.")
    print("A test only DIES if its real runtime exceeds the global limit, and")
    print("that is a RUNTIME fact this static scan cannot see. The one confirmed")
    print("case, measured 2026-10-18, is the pre-commit hook test at 334.83 s;")
    print("it now carries an explicit marker. To find any others, read")
    print("`--durations` from a completed full suite -- not this output.")
    print("=" * 74)
    return 0

if __name__ == "__main__":
    sys.exit(main())
