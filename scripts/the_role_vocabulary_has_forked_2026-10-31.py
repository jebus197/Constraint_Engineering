#!/usr/bin/env python3
"""PRODUCER: the structural role vocabulary HAS forked in live code, 2026-10-31.

FOUND BY TESTING THE SEAT-WRITTEN FIXES, which is what the founder's ruling
requires before anything folds back: *"Any fixes emerging from these briefs
should be tested with a, f, sy, before folding back into the runners and to the
project at large."*

WHAT THE TESTING FOUND, AND IT INVERTS MY FIRST READING. Run from the
preservation directory, 2 of the 4 seat tests failed their own ANTI-VACUITY
control -- the check each seat wrote to prove its scanner was not blind. Run at
the depth the seats intended (`bench/tests/`, where `parents[2]` is the repo
root rather than the seat's own folder), BOTH controls pass and both tests fail
on their SUBSTANTIVE assertion instead. The tests are correct and the live tree
carries the defect. My first run was measuring the path, not the code.

THE DEFECT. `bench/experiment_11_orchestrator.py:59` declares
`Role = Literal["collator", "player_manager", "participant"]` and `:77` makes
`role: Role` a required field. Python does not enforce a Literal at runtime, so
live code constructs values outside it and nothing objects.

WHY IT MATTERS WHILE CHANGING NO BEHAVIOUR TODAY. Every live consumer tests
only against `"collator"` (`mc.role != "collator"`), and every undeclared
spelling is `!= "collator"` exactly as `"participant"` is, so the predicates
cannot tell them apart -- cc2's "1 bit with 4 spellings". But `get_by_role`
compares for EQUALITY, so a seat the simulated runner builds as `"player"`,
intending a participant, is INVISIBLE to the declared selector. That is latent
only because `get_by_role` currently has 0 callers. A future caller inherits a
silent exclusion.

THIS SCRIPT ASSERTS NOTHING ABOUT WHICH VOCABULARY IS RIGHT. B21's open
question -- whether the structural enum and the founder's functional words are
1 dimension or 2 -- is his, and is not reducible to a measurement. What is
measured here is narrower and is a fact either way: the declared set and the
constructed set do not match.
"""
from __future__ import annotations

import ast
import pathlib
import subprocess
import sys
import typing

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import mpmath as mp  # noqa: E402
from statsmodels.stats.proportion import proportion_confint  # noqa: E402

FAILURES: list[str] = []


def _check(label: str, cond: bool, detail: str = "") -> None:
    if not cond:
        FAILURES.append(f"{label}: {detail}")


def wilson(k: int, n: int) -> tuple[float, float]:
    lo_sm, hi_sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    lo_mp, hi_mp = float((c - h) / d), float((c + h) / d)
    _check("wilson cross-check", abs(lo_sm - lo_mp) < 1e-9 and abs(hi_sm - hi_mp) < 1e-9,
           f"statsmodels ({lo_sm},{hi_sm}) vs mpmath ({lo_mp},{hi_mp})")
    return float(lo_sm), float(hi_sm)


def _live_files() -> list[pathlib.Path]:
    """Live product Python under bench/, excluding logs (sandbox harvests hold
    COPIES, so counting them multiplies one site by the number of runs) and
    tests."""
    return [p for p in sorted((REPO / "bench").rglob("*.py"))
            if "logs" not in p.parts and "tests" not in p.parts]


def scan(paths, handle_ifexp: bool):
    """Quoted `role=` values on a `ModelConfig(...)` call.

    `handle_ifexp` reproduces the ONE difference between the 2 seats'
    scanners, so the difference is measured rather than described. cc2
    accepted only `ast.Constant`; fable also walked both arms of an
    `ast.IfExp`, and its docstring says so deliberately.
    """
    hits = []
    for p in paths:
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else (
                fn.attr if isinstance(fn, ast.Attribute) else "")
            if name != "ModelConfig":
                continue
            for kw in node.keywords:
                if kw.arg != "role":
                    continue
                vals = []
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    vals = [kw.value.value]
                elif handle_ifexp and isinstance(kw.value, ast.IfExp):
                    for arm in (kw.value.body, kw.value.orelse):
                        if isinstance(arm, ast.Constant) and isinstance(arm.value, str):
                            vals.append(arm.value)
                for v in vals:
                    # A PLANTED PROBE FILE LIVES OUTSIDE THE REPO, so
                    # relative_to raises. cc2's scanner handled this and the
                    # first version of mine did not, which failed its own
                    # anti-vacuity controls.
                    try:
                        shown = p.relative_to(REPO).as_posix()
                    except ValueError:
                        shown = p.name
                    hits.append((shown, node.lineno, v))
    return hits


def main() -> int:
    from bench.experiment_11_orchestrator import ExperimentConfig, ModelConfig, Role

    declared = set(typing.get_args(Role))
    files = _live_files()

    print("=" * 72)
    print("M1. THE DECLARED SET AGAINST THE CONSTRUCTED SET")
    print("=" * 72)
    print(f"declared Role Literal : {sorted(declared)}")
    fable_hits = scan(files, handle_ifexp=True)
    cc2_hits = scan(files, handle_ifexp=False)
    constructed = {v for _, _, v in fable_hits}
    print(f"constructed in live code: {sorted(constructed)}")
    undeclared = sorted(constructed - declared)
    unconstructed = sorted(declared - constructed)
    print(f"UNDECLARED but constructed: {undeclared}")
    print(f"declared but NEVER constructed: {unconstructed}")
    _check("the fork exists", bool(undeclared),
           "no undeclared value found -- the finding would be withdrawn")

    print()
    print("=" * 72)
    print("M2. THE SITES, AND THE 2 SEATS' SCANNERS DISAGREE")
    print("=" * 72)
    stray_f = [h for h in fable_hits if h[2] not in declared]
    stray_c = [h for h in cc2_hits if h[2] not in declared]
    print(f"undeclared sites, fable's scanner (handles a conditional): {len(stray_f)}")
    for f, ln, v in stray_f:
        print(f"   {f}:{ln}  role={v!r}")
    print(f"undeclared sites, cc2's scanner (ast.Constant only):      {len(stray_c)}")
    for f, ln, v in stray_c:
        print(f"   {f}:{ln}  role={v!r}")
    missed = [h for h in stray_f if h not in stray_c]
    print()
    print(f"sites fable sees and cc2 cannot: {len(missed)}")
    for f, ln, v in missed:
        print(f"   {f}:{ln}  role={v!r}  <-- a conditional expression, not a constant")
    print()
    print("NEITHER SCANNER IS WRONG. cc2's is AST-strict and will not match a")
    print("non-constant; fable's walks both arms of a conditional and says so in")
    print("its own docstring. For a fold-back the conditional form must be")
    print("handled, because the site it reaches is the SIMULATED RUNNER.")
    _check("the scanners differ as described", bool(missed),
           "cc2 and fable agree, so the IfExp distinction is untested here")

    print()
    print("=" * 72)
    print("M3. HOW MANY SITES THE PROJECT'S OWN TYPE CHECKER ALREADY CATCHES")
    print("=" * 72)
    by_file = sorted({f for f, _, _ in stray_f})
    caught = 0
    for f in by_file:
        proc = subprocess.run(
            [sys.executable, "-m", "mypy", f, "--ignore-missing-imports",
             "--no-error-summary", "--no-pretty"],
            cwd=REPO, capture_output=True, text=True)
        lines = [ln for ln in (proc.stdout or "").splitlines()
                 if 'Argument "role"' in ln and "incompatible type" in ln]
        n_here = len([h for h in stray_f if h[0] == f])
        print(f"   {f}: {len(lines)} mypy arg-type error(s) against "
              f"{n_here} undeclared site(s)")
        caught += len(lines)
    lo, hi = wilson(caught, len(stray_f))
    print()
    print(f"mypy flags {caught} of {len(stray_f)} undeclared sites  "
          f"Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print()
    print("THE 2 MISSES HAVE 2 DIFFERENT CAUSES, AND I GOT BOTH WRONG BEFORE")
    print("TESTING THEM. The first version of this section said the misses were")
    print("`the conditional-expression form`, which is true of 1 of the 2.")
    print()
    print("  MISS 1, run_simulated_experiment.py:637 -- a CONDITIONAL")
    print("  expression. mypy widens `'a' if c else 'b'` to `str`, which is")
    print("  assignable to the Literal's union, so no error. Confirmed below.")
    print()
    print("  MISS 2, gemini_tool_switch_test.py:70 -- NOT the conditional. That")
    print("  site is a plain constant. The file imports with a BARE module name")
    print("  (`from experiment_11_orchestrator import ModelConfig`), and under")
    print("  `--ignore-missing-imports` mypy cannot resolve it, so ModelConfig")
    print("  becomes `Any` and the constructor is never checked. mypy then")
    print("  reports `Success: no issues found in 1 source file`.")
    print()
    print("  PROVEN BY MINIMAL PROBE, not inferred: with the bare import")
    print("  `reveal_type(ModelConfig)` gives `Any`; with `bench.`-prefixed")
    print("  import it gives the full signature including")
    print("  `role: Literal['collator'] | Literal['player_manager'] |")
    print("  Literal['participant']`, and the same bad role then raises")
    print("  `error: Argument \"role\" ... incompatible type`.")
    print()
    print("  AN EARLIER ATTEMPT TO TEST THIS WITH MYPYPATH=bench SHOWED NOTHING")
    print("  AND WAS NOT EVIDENCE: it introduced a package-layout error and mypy")
    print("  printed `errors prevented further checking`, so the target file was")
    print("  never analysed. A tool run that aborted has measured nothing --")
    print("  the same rule this project applies to a failed Wolfram call.")

    print()
    print("=" * 72)
    print("M4. THE CONCRETE FAILURE PATH, EXECUTED")
    print("=" * 72)
    cfg = ExperimentConfig(models=[
        ModelConfig(label="mgr", model_id="s", api="sim",
                    role="player_manager", system_prompt_path=None),
        ModelConfig(label="as_the_runner_builds_it", model_id="s", api="sim",
                    role="player", system_prompt_path=None),
        ModelConfig(label="spelled_as_declared", model_id="s", api="sim",
                    role="participant", system_prompt_path=None),
    ])
    got = [m.label for m in cfg.get_by_role("participant")]
    print(f"get_by_role('participant') returns: {got}")
    _check("the exclusion is real", "as_the_runner_builds_it" not in got,
           "the undeclared spelling WAS returned, so there is no exclusion")
    print("A seat the simulated runner intends as a participant is not returned")
    print("by the declared selector. Latent: `get_by_role` has 0 callers today.")

    print()
    print("=" * 72)
    print("M5. ADJUDICATION OF THE 4 SEAT-WRITTEN TESTS")
    print("=" * 72)
    rows = [
        ("cc2  test_the_role_axis_carries_demotion", "GREEN",
         "4 passed against the live tree; safe to fold as-is"),
        ("cc2  test_the_role_literal_is_enforced", "NOT FOLDABLE",
         "imports ROLE_ALIASES, which cc2 added to its SANDBOX copy of "
         "experiment_11_orchestrator.py and which preservation did NOT keep; "
         "it is a test for a proposed fix, not for the tree"),
        ("cc2  ..._cannot_fork_silently", "CORRECT, RED",
         "catches the live defect at 3 sites; red until the defect is fixed"),
        ("fable ..._cannot_fork_silently", "CORRECT, RED",
         "catches it at 4 sites, including the conditional cc2 cannot see"),
    ]
    for name, verdict, why in rows:
        print(f"   {verdict:<13} {name}")
        print(f"   {'':<13} {why}")
    print()
    print("AND A COLLISION THAT BLOCKS A NAIVE FOLD-BACK: the 2 seats wrote")
    print("DIFFERENT files under the SAME NAME, so copying both into")
    print("bench/tests/ would have one silently overwrite the other.")

    print()
    print("=" * 72)
    print("M6. THE WIDER DEFECT: `mypy_check` REPORTS OK ON FILES IT CANNOT TYPE")
    print("=" * 72)
    # Generalised from MISS 2. This is not about roles at all.
    PROJECT_MODULES = {q.stem for q in (REPO / "bench").glob("*.py")}
    bare, pkg = set(), set()
    for q in files:
        try:
            tree = ast.parse(q.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, OSError):
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and n.module:
                root = n.module.split(".")[0]
                if root == "bench":
                    pkg.add(q)
                elif root in PROJECT_MODULES:
                    bare.add(q)
    total = len(bare | pkg)
    lo2, hi2 = wilson(len(bare), total)
    print(f"live bench/ files importing a project module: {total}")
    print(f"  with a BARE module name: {len(bare)}  "
          f"Wilson 95% [{lo2:.6f}, {hi2:.6f}]")
    print(f"  with the bench.* package form: {len(pkg - bare)}")
    print()
    print("`bench/openrouter_tools.py:426` runs mypy as")
    print("`mypy <path> --no-error-summary --ignore-missing-imports` from the")
    print("repo root. There is NO mypy configuration file anywhere in the tree")
    print("and NO `bench/__init__.py`, so `bench` is a namespace package that")
    print("mypy will not traverse without being told to.")
    print()
    print("SO THE `mypy_check` TOOL EVERY PANEL SEAT IS OFFERED RETURNS")
    print("status 'ok' FOR A FILE WHOSE PROJECT TYPES IT NEVER RESOLVED. That is")
    print("a non-measurement presented as a pass, which is the shape this")
    print("project has already lost a convergence to.")
    print()
    print("NOT FIXED HERE, DELIBERATELY. The simplest sufficient repair is a")
    print("mypy config naming both roots (`mypy_path = .:bench`, namespace")
    print("packages on), which is 1 new file and 0 code changes. But it would")
    print("make mypy see project types in those files FOR THE FIRST TIME, and")
    print("one file alone already reports 140 errors across 18 files when its")
    print("imports do resolve. Turning that on could redden the board across")
    print("the project, so it is the founder's call and not a side effect of")
    print("this measurement.")
    _check("the import split is real", len(bare) > 0 and len(pkg) > 0,
           "one of the 2 import styles is absent, so the comparison is vacuous")

    print()
    print("=" * 72)
    if FAILURES:
        print(f"CONSISTENCY CHECKS FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print("   " + f)
        return 1
    print("ALL CONSISTENCY CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
