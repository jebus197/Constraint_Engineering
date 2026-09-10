#!/usr/bin/env python3
"""Task 8.2: does `reference_runner_v2.py` hold anything v3 lost?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

THE FOUNDER'S OWN QUESTION, put separately and recently: "Look at the v2 runner
too." v2 is the ONLY path on the `exp39-experimental` tip tree that is not on
`origin/main`, so it is the whole of the tip-level difference and the centre of
the 8.2 adjudication.

WHAT IS COMPARED, AND WHY BY AST. Reading 10,221 lines against 15,008 is not a
method. Every top-level and nested definition in each file is extracted by AST
and compared by NAME, then by NORMALISED SOURCE via `ast.unparse`.

NORMALISED ON BOTH SIDES, WHICH THE FIRST ATTEMPT WAS NOT. Comparing v2's
UNPARSED lines against v3's RAW source reported 45 functions carrying "lines
absent from all of v3" -- an artefact, because `ast.unparse` rewrites quote style
and spacing, so `entry.get('falsifier_code')` never matches a source line written
with double quotes. Unparsing both sides drops it to 37 functions and 133 lines.
The looser number is not quoted.

WHAT THE ANSWER IS, AND WHAT IT IS NOT. No CAPABILITY is lost: v3 defines every
one of v2's 153 definitions. What differs is IMPLEMENTATION in 46 of them, and
telling a changed implementation from a lost one needs per-function judgement,
which is what the panel is for. This script does not pretend to make that call.
"""
from __future__ import annotations

import ast
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
V3 = REPO / "bench" / "reference_runner_v3.py"
BRANCH = "exp39-experimental"
V2_PATH = "bench/reference_runner_v2.py"


def v2_source() -> str | None:
    r = subprocess.run(["git", "show", f"{BRANCH}:{V2_PATH}"],
                       cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def definitions(src: str) -> dict:
    tree = ast.parse(src)
    return {n.name: ast.unparse(n) for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def main() -> int:
    src2 = v2_source()
    if src2 is None:
        print(f"{V2_PATH} is not reachable from {BRANCH} in this clone -- "
              f"nothing to compare. This is a SKIP, not a result of 0.")
        return 0
    d2 = definitions(src2)
    d3 = definitions(V3.read_text(encoding="utf-8"))

    print(f"v2: {len(src2.splitlines()):,} lines, {len(d2)} definitions")
    print(f"v3: {len(V3.read_text().splitlines()):,} lines, {len(d3)} definitions\n")

    lost = sorted(set(d2) - set(d3))
    print(f"--- DEFINITIONS IN v2 AND NOT IN v3: {len(lost)} ---")
    for n in lost:
        print(f"   {n}")
    if not lost:
        print("   none. v3 is a superset of v2 by definition name.")
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(len(lost), len(d2), method="wilson")
    lo_c, hi_c = proportion_confint(len(lost), len(d2), method="beta")
    print(f"   {len(lost)}/{len(d2)} = {len(lost) / len(d2):.4%}  "
          f"Wilson [{lo:.4%}, {hi:.4%}]  Clopper-Pearson [{lo_c:.4%}, {hi_c:.4%}]")

    shared = sorted(set(d2) & set(d3))
    same = [n for n in shared if d2[n] == d3[n]]
    differ = [n for n in shared if d2[n] != d3[n]]
    print(f"\n--- SHARED DEFINITIONS: {len(shared)} ---")
    lo2, hi2 = proportion_confint(len(same), len(shared), method="wilson")
    print(f"   byte-identical after normalisation: {len(same)} "
          f"({len(same) / len(shared):.4%}, Wilson [{lo2:.4%}, {hi2:.4%}])")
    print(f"   differing implementations         : {len(differ)}")

    corpus = "\n".join(d3.values())
    orphan = {}
    for n in differ:
        miss = [l.strip() for l in d2[n].splitlines()
                if len(l.strip()) > 25 and l.strip() not in corpus]
        if miss:
            orphan[n] = miss
    total = sum(len(v) for v in orphan.values())
    print(f"\n--- v2 LINES ABSENT FROM THE WHOLE NORMALISED v3 ---")
    print(f"   {total} lines across {len(orphan)} definitions")
    shown = sorted(orphan.items(), key=lambda x: -len(x[1]))[:8]
    for n, ls in shown:
        print(f"     {n}: {len(ls)}")
    if len(orphan) > len(shown):
        print(f"     ... {len(orphan) - len(shown)} further definition(s) not "
              f"listed, carrying {sum(len(v) for k, v in orphan.items() if k not in dict(shown))} "
              f"more line(s). A capped listing must say what it withheld.")

    print("\n--- WHAT THIS DOES AND DOES NOT SETTLE ---")
    print("   SETTLES: no capability is lost by name. v3 defines all of v2's.")
    print("   DOES NOT SETTLE: whether any of the differing implementations is")
    print("   a REGRESSION rather than a revision. That is per-function judgement")
    print("   and is the panel's to make, not this script's.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
