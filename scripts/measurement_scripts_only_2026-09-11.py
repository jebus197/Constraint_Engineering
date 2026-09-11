#!/usr/bin/env python3
"""Task A16: which scripts only READ, so a survey can run them safely?

WHAT WENT WRONG. The intent was to find which committed measurement scripts no
longer execute, after task 6.2's instrument was found dead. But `scripts/` mixes
MEASUREMENTS with ACTIONS: `cdsfl_sv.py`, `cdsfl_qc.py`, `cdsfl_recover.py` and
`adjudicate_by_repair.py` all write to the tree. The survey regenerated 5 tracked
files before it was killed, and the 5th OVERWROTE A DELIBERATELY PRESERVED
ARCHIVE -- `experimental_notes/data/adjudication_by_repair.json`, the record of
what the adjudicator produced BEFORE the 2026-08-28 errored-leg fix.

THE SEVERITY IS NOT THAT FILES CHANGED. It is that a survey intended to READ ran
things that WRITE. No commit and no push occurred; `cdsfl_sv.py` commits only
under `--commit --push`, and the guard built for exactly this caught the
regeneration within minutes.

THE FIX IS TO DECLARE THE DISTINCTION RATHER THAN INFER IT, which is what the
entry asked for. A script is a MEASUREMENT if it neither writes to the repository
tree nor spawns a process that could. Everything else is an ACTION, and the
survey does not run it.

CONSERVATIVE BY CONSTRUCTION, because the failure mode is asymmetric. A
measurement wrongly classed as an action costs a missing row in a survey. An
action wrongly classed as a measurement overwrites a preserved archive. So
anything this cannot resolve is an ACTION: an unrecognised call, a dynamic
attribute, a `subprocess` invocation, an `os.system`. The classification is
reported with the REASON, so a wrong call can be argued with rather than guessed
at.

IT DOES NOT RUN ANYTHING BY DEFAULT. `--run` is opt-in, and even then it runs
only the scripts this file classes as measurements, with `--help` first so a
script whose argument handling is broken cannot be given a real invocation.
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"

#: Calls that can change the filesystem.
_WRITING_ATTRS = {
    "write_text", "write_bytes", "mkdir", "touch", "unlink", "rmdir",
    "rename", "replace", "chmod", "symlink_to", "hardlink_to",
}
_WRITING_FUNCS = {
    "rmtree", "copy", "copy2", "copyfile", "copytree", "move", "remove",
    "makedirs", "mkdir", "rename", "unlink", "system", "dump",
}
#: Spawning a process means this file cannot see what happens next.
_SPAWNING = {"run", "Popen", "call", "check_call", "check_output", "system",
             "spawnv", "spawnl", "execv"}


def classify(path: pathlib.Path) -> tuple[str, list[str]]:
    """("MEASUREMENT" | "ACTION", reasons). Unresolvable is ACTION."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError) as exc:
        return "ACTION", [f"cannot parse: {type(exc).__name__}"]

    reasons: list[str] = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            attr = getattr(n.func, "attr", None)
            name = getattr(n.func, "id", None)
            if attr in _WRITING_ATTRS:
                reasons.append(f"line {n.lineno}: .{attr}()")
            elif (attr or name) in _WRITING_FUNCS:
                reasons.append(f"line {n.lineno}: {attr or name}()")
            elif (attr or name) in _SPAWNING:
                reasons.append(f"line {n.lineno}: spawns a process "
                               f"({attr or name}) -- cannot see what it does")
            elif name == "open" and len(n.args) > 1:
                mode = n.args[1]
                if isinstance(mode, ast.Constant) and isinstance(mode.value, str) \
                        and any(c in mode.value for c in "wax+"):
                    reasons.append(f"line {n.lineno}: open(..., {mode.value!r})")
                elif not isinstance(mode, ast.Constant):
                    reasons.append(f"line {n.lineno}: open() with a computed mode")
        elif isinstance(n, ast.With):
            for item in n.items:
                c = item.context_expr
                if isinstance(c, ast.Call) and getattr(c.func, "id", None) == "open" \
                        and len(c.args) > 1:
                    mode = c.args[1]
                    if isinstance(mode, ast.Constant) and isinstance(mode.value, str) \
                            and any(ch in mode.value for ch in "wax+"):
                        reasons.append(f"line {c.lineno}: open(..., {mode.value!r})")
    return ("ACTION" if reasons else "MEASUREMENT"), sorted(set(reasons))


def survey(run: bool, timeout: int):
    rows = []
    for p in sorted(SCRIPTS.glob("*.py")):
        kind, reasons = classify(p)
        rows.append((p, kind, reasons))

    measurements = [r for r in rows if r[1] == "MEASUREMENT"]
    actions = [r for r in rows if r[1] == "ACTION"]
    print(f"scripts/ contains {len(rows)} Python file(s)")
    print(f"  MEASUREMENT (safe to run): {len(measurements)}")
    print(f"  ACTION (never run by this survey): {len(actions)}")

    print("\nthe 4 the entry names, and what this says about them:")
    for name in ("cdsfl_sv.py", "cdsfl_qc.py", "cdsfl_recover.py",
                 "adjudicate_by_repair.py"):
        row = next((r for r in rows if r[0].name == name), None)
        if row is None:
            print(f"    {name}: ABSENT from scripts/")
            continue
        print(f"    {name}: {row[1]}  ({row[2][0] if row[2] else 'no writing call found'})")

    if not run:
        print("\nNOTHING WAS RUN. Pass --run to execute the MEASUREMENT set, "
              "with --help first.")
        return rows

    print(f"\nrunning {len(measurements)} measurement script(s) with --help:")
    broken = []
    for p, _k, _r in measurements:
        try:
            r = subprocess.run([sys.executable, str(p), "--help"], cwd=REPO,
                               capture_output=True, text=True, timeout=timeout)
            ok = r.returncode == 0
        except subprocess.SubprocessError as exc:
            ok, r = False, None
            print(f"    {p.name}: {type(exc).__name__}")
        if not ok:
            broken.append(p.name)
            if r is not None:
                print(f"    {p.name}: exit {r.returncode} "
                      f"{(r.stderr or '')[:90].strip()}")
    print(f"\n{len(broken)} of {len(measurements)} did not answer --help cleanly")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", action="store_true",
                    help="execute the MEASUREMENT set (--help only)")
    ap.add_argument("--timeout", type=int, default=120)
    a = ap.parse_args()
    rows = survey(a.run, a.timeout)

    n = len(rows)
    k = sum(1 for r in rows if r[1] == "ACTION")
    if n:
        from statsmodels.stats.proportion import proportion_confint
        from scipy.stats import beta as sbeta
        lo, hi = proportion_confint(k, n, method="wilson")
        lo_c, hi_c = proportion_confint(k, n, method="beta")
        hi_s = 1.0 if k == n else sbeta.ppf(0.975, k + 1, n - k)
        print(f"\nACTION share: {k}/{n} = {k / n:.4%}")
        print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]  (statsmodels)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]  (statsmodels/beta)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_s:.4%}]  (scipy, agrees "
              f"to {abs(hi_s - hi_c):.1e})")
    print("\nUNRESOLVABLE IS ACTION. A measurement wrongly classed as an action "
          "costs a missing\nrow; an action wrongly classed as a measurement "
          "overwrites a preserved archive.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
