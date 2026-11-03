#!/usr/bin/env python3
"""Would a simulated experiment test the fixes made since he last spoke?

HIS AIM, 2026-11-03, verbatim: *"A wider aim of these experiments should be to
test all fixes/additional features you have produced since I first interacted
with you yesterday morning too."* This answers whether a simulated run CAN do
that, before a run is authorised on the assumption that it does.

THE ANSWER IS NO FOR MOST OF IT, and the split matters because the 2 halves need
different instruments. A simulated run exercises the modules it imports or
spawns. The commit board exercises the guards and the producers. Most of the
work of 2026-11-02 and 2026-11-03 is the second kind.

REACHABILITY HAS 2 ROUTES AND THE FIRST VERSION OF THIS MEASUREMENT KNEW ONLY 1.
An import closure from `bench/tools/run_simulated_experiment.py` gives 68
modules. It MISSED every component the runner launches as a subprocess -- and
`scripts/cy_watchdog_2026-10-02.py` is exactly that, spawned rather than
imported, which made the subject of this session's own watchdog repair look
unreachable. Adding the spawn route takes the closure to 76. A reachability
measurement that knows only about imports understates it.

AND THE DYNAMIC-REFERENCE CHECK WAS RUN AND IS REPORTED, because "not imported"
is not the same as "never referenced". Of the modules the static closure misses,
the only one referenced anywhere inside the closure is `bench/model_admission.py`
-- and the reference is INSIDE A COMMENT, not a call. So the static verdict
survives its own falsification rather than being asserted.

WHAT THIS DOES NOT CLAIM. Reachability is necessary for a run to exercise a
change, not sufficient: a module on the import path may hold a branch no run
takes. So the figure is an UPPER BOUND on what a run could test, and the honest
reading is that a run tests at most this much, not that it tests this much.
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import re
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[1]
ENTRY = REPO / "bench" / "tools" / "run_simulated_experiment.py"
SKIP = ("/.git/", "sandbox", "/logs/", "__pycache__", "/.scratch/")


def _local_imports(path: pathlib.Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(errors="replace"))
    except Exception:                                        # noqa: BLE001
        return set()
    names: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            names |= {a.name.split(".")[-1] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            names.add(n.module.split(".")[-1])
            names |= {a.name for a in n.names}
    return names


def _index() -> dict[str, pathlib.Path]:
    out: dict[str, pathlib.Path] = {}
    for p in REPO.rglob("*.py"):
        if any(x in str(p) for x in SKIP):
            continue
        out.setdefault(p.stem, p.resolve())
    return out


def _closure(entries, index) -> set[pathlib.Path]:
    seen: set[pathlib.Path] = set()
    frontier = list(entries)
    while frontier:
        cur = frontier.pop()
        if cur in seen:
            continue
        seen.add(cur)
        for nm in _local_imports(cur):
            t = index.get(nm)
            if t and t not in seen:
                frontier.append(t)
    return seen


#: A `.py` literal counts as a SPAWN only within this many characters of a
#: subprocess launch. Prose mentions a script far more often than code runs one.
_SPAWN_WINDOW = 400

_LAUNCH = re.compile(r"subprocess\.(?:run|Popen|call|check_call|check_output)"
                     r"|sys\.executable|os\.exec|spawn")


def _spawned(modules, index) -> set[pathlib.Path]:
    """Scripts the closure LAUNCHES, not scripts it merely names.

    THE ROUTE THE FIRST VERSION MISSED, AND THE FALSE POSITIVE THE SECOND ONE
    HAD. The runner launches the watchdog with `subprocess.Popen([sys.executable,
    str(script), ...])`, so the script's name appears only as a string literal
    and an import-only closure cannot see it. But matching EVERY `.py` literal
    then counts prose: `scripts/which_fix_is_better_2026-10-24.py` appears in
    `reference_runner_v3.py` only inside `evidence_required` documentation
    strings, and was being reported as spawned.

    So a literal counts only when a launch construct sits within
    `_SPAWN_WINDOW` characters of it. That is a PROXIMITY heuristic and is
    stated as one: it can still miss a launch assembled far from its literal,
    and it errs toward UNDER-counting, which is the safe direction for a figure
    used as an upper bound.
    """
    names: set[str] = set()
    for p in modules:
        try:
            t = p.read_text(errors="replace")
        except OSError:
            continue
        for m in re.finditer(r'["\']([A-Za-z0-9_/.-]+\.py)["\']', t):
            lo = max(0, m.start() - _SPAWN_WINDOW)
            hi = min(len(t), m.end() + _SPAWN_WINDOW)
            if _LAUNCH.search(t[lo:hi]):
                names.add(pathlib.Path(m.group(1)).stem)
    return {index[n] for n in names if n in index}


def _rel(paths) -> set[str]:
    out = set()
    for p in paths:
        try:
            out.add(str(p.relative_to(REPO)))
        except ValueError:
            pass
    return out


def _changed(since: str) -> list[str]:
    r = subprocess.run(["git", "log", f"--since={since}", "--name-only",
                        "--format="], capture_output=True, text=True,
                       cwd=str(REPO))
    return sorted({c for c in r.stdout.split()
                   if c.endswith(".py") and not c.startswith("bench/logs/")
                   and "sandbox" not in c})


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, on 2 independent implementations EACH.

    ★ WILSON HAD ONLY 1 ROUTE UNTIL 2026-11-03 and the gap was invisible
    because the function imported 3 libraries. Clopper-Pearson was genuinely
    cross-checked -- scipy.beta against an mpmath bisection -- while Wilson came
    from statsmodels alone, so the reported `|diff|` spoke for one of the 2
    quantities and said nothing about the other. That is exactly the defect
    B97 names: 2 library names buying 0 cross-checks for the quantity that
    needed one.

    THE REPAIR IS A PROPAGATION, NOT AN INVENTION. The written-out Wilson below
    is the implementation already proven in
    `scripts/a_models_own_verified_flag_closes_it_2026-11-03.py`, where SymPy
    simplifies it minus the canonical closed form to 0 on both bounds. The
    returned difference is now the MAXIMUM over both quantities, so neither can
    hide behind the other.
    """
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import math
    import mpmath
    mpmath.mp.dps = 40

    def bi(a, b, y):
        def f(x):
            return mpmath.betainc(a, b, 0, x, regularized=True) - y
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        for _ in range(240):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
        return float((lo + hi) / 2)

    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    # SECOND WILSON, written out, so a library disagreement cannot pass.
    z = stats.norm.ppf(0.975)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    wdiff = max(abs(wl - (centre - half)), abs(wh - (centre + half)))
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))
    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=("Measure what a simulated run could exercise of the "
                     "changes made in a window."))
    ap.add_argument("--since", default="2026-11-02 00:00",
                    help="git --since for the change window")
    args = ap.parse_args()

    index = _index()
    imported = _closure([ENTRY.resolve()], index)
    spawned = _spawned(imported, index)
    full = _closure(list(imported) + list(spawned), index)
    imp_r, full_r = _rel(imported), _rel(full)

    print("=" * 78)
    print("WHAT WOULD A SIMULATED RUN ACTUALLY TEST?")
    print("=" * 78)
    print(f"  window: --since {args.since!r}")
    print(f"  route 1, imports only           : {len(imp_r)} module(s)")
    print(f"  route 1 + route 2, with spawns  : {len(full_r)} module(s)  "
          f"(+{len(full_r) - len(imp_r)})")
    print("  the spawn route is what reaches the watchdog, which the runner")
    print("  launches as a subprocess rather than importing.")

    changed = _changed(args.since)
    tests = [c for c in changed if c.startswith("bench/tests/")]
    scripts = [c for c in changed if c.startswith("scripts/")]
    product = [c for c in changed
               if not c.startswith("bench/tests/") and not c.startswith("scripts/")]
    hooks = [c for c in product if c.startswith("hooks/")]

    print(f"\n  python files changed in the window : {len(changed)}")
    print(f"    guard tests  : {len(tests):4d}  exercised by the COMMIT BOARD")
    print(f"    scripts      : {len(scripts):4d}  run directly; the board's "
          f"reachability ratchet covers the dated ones")
    print(f"    product      : {len(product):4d}  the only kind a run can exercise")

    print("\n  PRODUCT MODULES, one line each:")
    for c in sorted(product):
        if c in full_r:
            tag = "REACHED"
        elif c in hooks:
            tag = "a session hook: fires on commits and stops, never on a run"
        else:
            tag = "not reached"
        print(f"    {'[R]' if c in full_r else '[ ]'} {c:44s} {tag}")

    k, n = sum(1 for c in product if c in full_r), len(product)
    (wl, wh), (cl, ch), d = _iv(k, n)
    print(f"\n  REACHABLE BY A SIMULATED RUN: {k} of {n}, {k / n if n else 0:.6f}")
    print(f"    Wilson 95%          [{wl:.6f}, {wh:.6f}]")
    print(f"    Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]   (2-route |diff| {d:.1e})")

    print("\n  THE DYNAMIC-REFERENCE FALSIFICATION, run rather than assumed:")
    missed = [c for c in product if c not in full_r]
    any_ref = 0
    for c in missed:
        stem = pathlib.Path(c).stem
        refs = []
        for p in full:
            try:
                t = p.read_text(errors="replace")
            except OSError:
                continue
            for m in re.finditer(rf"[^\n]*{re.escape(stem)}[^\n]*", t):
                refs.append((p.name, " ".join(m.group(0).split())))
        if refs:
            any_ref += 1
            nm, ctx = refs[0]
            commented = ctx.lstrip().startswith("#")
            print(f"    {stem}: {len(refs)} reference(s); first in {nm}, "
                  f"{'INSIDE A COMMENT' if commented else 'in code'}")
        else:
            print(f"    {stem}: 0 references anywhere in the closure")
    print(f"    modules with any reference: {any_ref} of {len(missed)}")

    print("\n  SO THE 2 HALVES NEED DIFFERENT INSTRUMENTS, which is the point:")
    print("  a simulated run can exercise the product modules it imports or")
    print("  spawns, and nothing else. The guards and the producers are the")
    print("  commit board's job, and the board already runs them on every")
    print("  commit. An experiment authorised to 'test all the fixes' would")
    print("  test a minority of them.")
    print("\n  AND REACHABILITY IS AN UPPER BOUND, NOT A MEASURE OF COVERAGE:")
    print("  a module on the path may hold a branch no run takes. This says a")
    print("  run tests AT MOST this much.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
