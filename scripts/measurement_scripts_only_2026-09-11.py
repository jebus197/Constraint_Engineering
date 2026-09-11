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
    # `truncate` empties a file and was absent (panel round 12, fable).
    "truncate",
}
_WRITING_FUNCS = {
    "rmtree", "copy", "copy2", "copyfile", "copytree", "move", "remove",
    "makedirs", "mkdir", "rename", "unlink", "system", "dump",
}
#: Spawning a process means this file cannot see what happens next.
_SPAWNING = {"run", "Popen", "call", "check_call", "check_output", "system",
             "spawnv", "spawnl", "execv"}


def _open_is_a_write(call: ast.Call) -> str:
    """A reason string if this `open` call can write, else "".

    THE MODE IS AT A DIFFERENT INDEX IN EVERY FORM -- `open(p, "w")`,
    `Path(p).open("w")`, `io.open(p, "w")`, `open(p, mode="w")` -- so every
    argument is a candidate rather than a chosen one. An argument that is not a
    string constant cannot be resolved, and unresolvable is a WRITE here,
    because the failure this classifier prevents is asymmetric.
    """
    # THE RECEIVER CARRIES THE PATH IN THE METHOD FORM, so the mode is argument
    # 0 there and argument 1 for the builtin. Getting this wrong let
    # `Path("x").open("w")` through: its single argument looked like the PATH.
    is_method = isinstance(call.func, ast.Attribute)
    positional = list(call.args) if is_method else list(call.args)[1:]
    keyword = [kw.value for kw in call.keywords if kw.arg in ("mode", "flags")]
    candidates = positional + keyword
    if not candidates:
        return ""                       # `open(p)` with no mode reads
    for arg in candidates:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            if any(c in arg.value for c in "wax+"):
                return f"open(..., {arg.value!r})"
        elif not isinstance(arg, ast.Constant):
            return "open() with a mode this scan cannot resolve"
    return ""


def _imported_writers(tree: ast.AST) -> dict:
    """{local name: "module.func"} for imported functions that WRITE.

    THE HOLE THIS CLOSES, found 2026-09-11 by the cc2 seat in panel round 12:
    `scripts/cdsfl_seal_logs.py` came back MEASUREMENT, and its default
    invocation SEALS LOG DIRECTORIES -- it writes through `save_json`, imported
    from `bench.verification_chain`. The classifier resolved calls inside one
    file and could not see across an import boundary, so a write delegated to a
    helper was invisible. That is the same resolve-versus-match shape as task
    A17, at module scope.

    ONE LEVEL DEEP, DELIBERATELY. A full call graph is a different program and
    would be slower and less legible; one level catches the direct delegation
    that actually occurs. Anything this cannot resolve stays an ACTION for the
    reason the whole classifier is conservative: an ACTION misread as a
    measurement is what overwrote a preserved archive.
    """
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        rel = node.module.replace(".", "/") + ".py"
        mod = REPO / rel
        if not mod.is_file():
            continue
        try:
            mtree = ast.parse(mod.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError):
            continue
        defs = {n.name: n for n in mtree.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.ClassDef))}

        def _writes(scope) -> str:
            for sub in ast.walk(scope):
                if isinstance(sub, ast.Call):
                    a = getattr(sub.func, "attr", None)
                    i = getattr(sub.func, "id", None)
                    if a in _WRITING_ATTRS or (a or i) in _WRITING_FUNCS \
                            or (a or i) in _SPAWNING:
                        return f"{a or i}()"
            return ""

        for alias in node.names:
            target = defs.get(alias.name)
            if target is None:
                continue
            if isinstance(target, ast.ClassDef):
                # AN IMPORTED CLASS WHOSE METHODS WRITE. `cdsfl_seal_logs.py`
                # imports `VerificationChain` and calls `chain.save_json(...)`,
                # and `save_json` is a METHOD -- invisible to a scan that looks
                # only at module-level functions. Each writing method is
                # registered under its own name, so a call to it here is caught
                # without assuming every method of the class writes.
                for meth in target.body:
                    if isinstance(meth, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                            and _writes(meth):
                        out[meth.name] = (f"{node.module}.{alias.name}."
                                          f"{meth.name}")
                continue
            why = _writes(target)
            if why:
                out[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return out


def classify(path: pathlib.Path) -> tuple[str, list[str]]:
    """("MEASUREMENT" | "ACTION", reasons). Unresolvable is ACTION."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError) as exc:
        return "ACTION", [f"cannot parse: {type(exc).__name__}"]

    reasons: list[str] = []
    writers = _imported_writers(tree)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            _called = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
            if _called in writers:
                reasons.append(f"line {n.lineno}: {_called}() writes, via "
                               f"{writers[_called]}")
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
            elif (attr or name) == "open":
                # EVERY `open`, BUILTIN OR METHOD. Found 2026-09-11 by the fable
                # seat in panel round 12: this handled only the builtin with a
                # positional second argument, so `Path("x").open("w")`,
                # `io.open("x","w")`, `os.open(...)` and `open("x", mode="w")`
                # all came back MEASUREMENT -- the asymmetric direction this
                # classifier exists to prevent, since an ACTION misread as a
                # measurement is what overwrote a preserved archive.
                #
                # The mode sits at a different index for each form, so EVERY
                # argument is treated as a mode candidate, and anything that
                # cannot be resolved is an ACTION. The cost is the cheap
                # direction: a read-only `open("w_file.txt")` would be flagged,
                # losing a survey row rather than a file.
                verdict = _open_is_a_write(n)
                if verdict:
                    reasons.append(f"line {n.lineno}: {verdict}")
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
            # EXIT 0 IS NOT AN ANSWER, and reading it as one hid 30 scripts.
            #
            # Measured 2026-09-11: of the 53 scripts this survey classed as
            # measurements, 30 exited 0 with no usage line at all -- 56.6038%,
            # Wilson [43.2654%, 69.0496%]. They have no argument parser, so
            # `--help` was ignored, the whole measurement ran, and a successful
            # run was counted as a clean answer to a question never asked. 2 of
            # them showed up only in a fresh clone, where the work they silently
            # did happened to fail, and those 2 were part of what made task A2's
            # "a fresh clone is green" untrue.
            #
            # The predicate lives in scripts/_cli_help.py so this file and
            # scripts/help_is_answered_2026-09-11.py cannot drift apart.
            sys.path.insert(0, str(REPO / "scripts"))
            from _cli_help import usage_line_present
            ok = (r.returncode == 0
                  and usage_line_present((r.stdout or "") + (r.stderr or "")))
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
