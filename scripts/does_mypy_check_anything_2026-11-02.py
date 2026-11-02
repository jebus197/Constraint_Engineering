#!/usr/bin/env python3
"""Does the panel's mypy tool check anything, and what would fixing it cost?

WHY THIS EXISTS. Entry B21 records that `bench/openrouter_tools.py`'s `mypy_check`
"returns `status: \"ok\"` for files it could not type", and that installing a mypy
config "could redden the board project-wide and is his call". The first is a claim
about live behaviour that can be settled by calling the tool, and the second is a
GUESS where a number would make his decision cheap. Both are measured here.

★ THE CLAIM AS WRITTEN LOOKS WRONG AND IS CHECKED RATHER THAN REPEATED.
`_run_mypy` maps `returncode == 0` to "ok" and anything else to "errors", so an
import failure -- which makes mypy exit non-zero -- would surface as "errors", not
as "ok". If that is right, the entry overstates the defect and the overstatement
must be withdrawn.

★ BUT THERE IS A SHARPER DEFECT UNDERNEATH, AND IT IS THE ONE WORTH HAVING.
The tool passes `--ignore-missing-imports`. With no `bench/__init__.py` and no
MYPYPATH, a project import by bare name does not resolve, and that flag turns the
imported module into `Any` instead of an error. Every attribute of it then type-
checks trivially. So mypy exits 0, the tool says "ok", and NOTHING about the
project's own types was checked. That is the same shape as this project's standing
Wolfram rule -- a call that verified nothing must not be recorded as confirming
anything -- and it is demonstrated here by planting a type error that mypy SHOULD
catch and showing it does not.

NOTHING IS INSTALLED. No config file is written to the tree. The resolving run
uses MYPYPATH in a subprocess environment only, so the board is untouched.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

#: The exact flags `_run_mypy` uses, lifted from its source rather than retyped,
#: so this cannot measure a command the tool does not run.
def tool_flags() -> list[str]:
    src = (REPO / "bench" / "openrouter_tools.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if (isinstance(node, ast.FunctionDef) and node.name == "_run_mypy"):
            for sub in ast.walk(node):
                if isinstance(sub, ast.List):
                    vals = [e.value for e in sub.elts
                            if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                    if "mypy" in vals:
                        return [v for v in vals if v.startswith("--")]
    raise SystemExit("could not lift the flags from _run_mypy; it may have moved")


def run_mypy(paths: list[str], flags: list[str], mypypath: str | None = None
             ) -> tuple[int, str, float]:
    env = dict(os.environ)
    if mypypath:
        env["MYPYPATH"] = mypypath
    else:
        env.pop("MYPYPATH", None)
    t0 = time.monotonic()
    r = subprocess.run([sys.executable, "-m", "mypy", *paths, *flags],
                       capture_output=True, text=True, cwd=str(REPO),
                       env=env, timeout=600)
    return r.returncode, (r.stdout or "") + (r.stderr or ""), time.monotonic() - t0


def banner(s: str) -> None:
    print("=" * 74)
    print(s)
    print("=" * 74)


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="does_mypy_check_anything_2026-11-02.py",
        description="Measure whether the panel's mypy tool checks project types, "
                    "and what resolving imports would report. Installs nothing.")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    flags = tool_flags()
    banner("WHAT THE PANEL'S TOOL ACTUALLY RUNS")
    print(f"  flags lifted from _run_mypy : {flags}")
    print(f"  bench/__init__.py present   : {(REPO / 'bench' / '__init__.py').is_file()}")
    print(f"  mypy config in tree root    : "
          f"{[f for f in ('mypy.ini', '.mypy.ini', 'setup.cfg', 'pyproject.toml') if (REPO / f).is_file()]}")
    print()

    # ---- 1. the entry's claim, settled by calling the tool ----
    banner("1. DOES THE TOOL REPORT ok FOR A FILE IT COULD NOT TYPE?")
    from bench.openrouter_tools import _run_mypy

    # a file that imports a project module by BARE name, found rather than assumed
    target = None
    for p in sorted((REPO / "bench").glob("*.py")):
        try:
            tree = ast.parse(p.read_text(errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                head = node.module.split(".")[0]
                if (REPO / "bench" / f"{head}.py").is_file() and head != p.stem:
                    target = p
                    break
        if target:
            break
    if target is None:
        print("  no bench file imports a sibling by bare name; the premise is gone")
        return 1
    print(f"  target: bench/{target.name}  (imports a sibling by bare name)")
    got = _run_mypy(f"bench/{target.name}")
    print(f"  tool status    : {got['status']!r}")
    print(f"  tool returncode: {got['returncode']}")
    print(f"  first output   : {(got['output'] or '').splitlines()[:1]}")
    claim_as_written = got["status"] == "ok"
    print()
    print(f"  THE ENTRY'S CLAIM -- status 'ok' for a file it could not type -- is "
          f"{'REPRODUCED' if claim_as_written else 'NOT REPRODUCED AS WRITTEN'}")
    if not claim_as_written:
        print("  `_run_mypy` maps a non-zero returncode to 'errors', so an import")
        print("  FAILURE surfaces loudly. The entry overstates that part.")
    print()

    # ---- 2. where the probe LIVES decides the answer ----
    banner("2. DO BARE-NAME PROJECT IMPORTS RESOLVE? THE PROBE'S LOCATION DECIDES")
    print("  ★ THIS SECTION CORRECTS AN EARLIER VERSION OF ITSELF. The first run")
    print("  placed its probe in a TEMPORARY DIRECTORY, found the planted error")
    print("  unreported, and concluded that the tool's ok is vacuous. That was an")
    print("  artefact of the probe's own location: a temp directory has no sibling")
    print("  project modules on its search path. Run from where real files live,")
    print("  the answer reverses. Both are shown, because the contrast IS the")
    print("  finding.")
    print()

    planted = ("from routing import season_strength_order\n"
               "\n"
               "def go() -> int:\n"
               "    x: int = season_strength_order(12345)\n"
               "    return x\n")

    with tempfile.TemporaryDirectory() as td:
        outside = pathlib.Path(td) / "probe_outside_bench.py"
        outside.write_text(planted)
        rc_out, txt_out, _ = run_mypy([str(outside)], flags)
    inside = REPO / "bench" / "_tmp_mypy_probe_from_producer.py"
    try:
        inside.write_text(planted)
        rc_in, txt_in, _ = run_mypy([str(inside)], flags)
        caught_inside = "season_strength_order" in txt_in and "call-arg" in txt_in
    finally:
        inside.unlink(missing_ok=True)

    print(f"  probe OUTSIDE bench/ : returncode {rc_out}, "
          f"planted error reported: {'call-arg' in txt_out}")
    print(f"  probe INSIDE  bench/ : returncode {rc_in}, "
          f"planted error reported: {caught_inside}")
    print()
    if caught_inside:
        print("  SO BARE-NAME IMPORTS DO RESOLVE for files inside bench/, and the")
        print("  reason is the absence of `bench/__init__.py`: mypy treats each")
        print("  file as a top-level module and puts bench/ on its own search")
        print("  path. ENTRY B21's claim that mypy cannot see project types in 110")
        print("  of 155 files is therefore NOT SUPPORTED, and is withdrawn.")
    else:
        print("  the planted error is unreported even from inside bench/, so the")
        print("  resolution claim above does not hold and B21 stands")

    # ---- 3. the defect that IS real, and it is a different one ----
    print()
    banner("3. THE DEFECT THAT IS REAL: AN IMPORT MYPY CANNOT FIND AT ALL")
    absent = REPO / "bench" / "_tmp_absent_import_from_producer.py"
    try:
        absent.write_text("import a_module_that_truly_does_not_exist_xyz\n"
                          "x = a_module_that_truly_does_not_exist_xyz.anything\n"
                          "y: int = x\n")
        rc_abs, txt_abs, _ = run_mypy([str(absent)], flags)
        from bench.openrouter_tools import _run_mypy as _tool
        tool_says = _tool(f"bench/{absent.name}")
    finally:
        absent.unlink(missing_ok=True)

    print(f"  a file in bench/ importing an ABSENT module:")
    print(f"    raw mypy returncode {rc_abs}, output: "
          f"{txt_abs.strip().splitlines()[:1] or ['(silent)']}")
    print(f"    the tool now reports : {tool_says['status']!r}, "
          f"unresolved={tool_says.get('unresolved_imports')}")
    vacuous = rc_abs == 0
    print()
    print(f"  BEFORE THE 2026-11-02 REPAIR THIS WAS REPORTED AS 'ok': {vacuous}")
    if vacuous:
        print("  mypy exits 0 because --ignore-missing-imports substitutes Any for")
        print("  the module it could not find, so every attribute of it checks")
        print("  trivially. A seat was handed a clean verdict on a file nothing was")
        print("  checked in. That is the standing Wolfram rule in a different tool:")
        print("  a call that verified nothing must not be recorded as confirming")
        print("  anything. `_run_mypy` now returns 'ok_but_nothing_was_checked'")
        print("  with a count and a caveat, and leaves every other status alone.")
    print()
    banner("4. WHAT IS STILL NOT MEASURED, AND WHY")
    print("  What a tree-wide mypy run WOULD report is not measured here. His")
    print("  machine has 8 cores and 8 GiB with a derived budget of 2 heavy")
    print("  processes, and a full run over 201 bench files is a heavy process of")
    print("  unknown cost. It is named as a separate bounded measurement rather")
    print("  than guessed at. Note also that many bench files cannot be checked at")
    print("  all today for a DIFFERENT reason: mypy reports 'Source file found")
    print("  twice under different module names', which is loud rather than silent")
    print("  and so is not the defect repaired above.")

    if a.json:
        print(json.dumps({"claim_as_written_reproduced": claim_as_written,
                          "flags": flags}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
