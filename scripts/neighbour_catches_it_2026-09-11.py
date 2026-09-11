#!/usr/bin/env python3
"""Task A6, half I13: is a test green because a NEIGHBOUR catches the regression?

I13, confirmed once by mutation on 2026-09-09 and never measured: a test file can
be green while the thing its docstring claims to cover is broken, because some
OTHER file catches the breakage. The suite is red, so nothing ships -- but the
COVERAGE CLAIM is false, and the day the neighbour is deleted or narrowed the
hole opens silently.

HOW IT IS MEASURED HERE, mechanically and without guessing intent:

  1. pick a function S in a production module;
  2. find every test file whose text NAMES S -- those are the files CLAIMING to
     cover it;
  3. destroy S by making its body a bare `return None`;
  4. run the claimants TOGETHER WITH the wider affected set;
  5. a claimant that stays GREEN while some non-claimant goes RED is an I13
     instance: the coverage is real, the claim is misplaced.

WHY `return None` RATHER THAN A CLEVERER MUTANT. It is the strongest possible
break -- the function does nothing at all -- so a claimant that survives it
cannot be said to be checking the function in any sense. A subtle mutant would
confound "this test does not cover S" with "this test covers S loosely".

WHAT IT CANNOT SAY. A claimant may name S for a reason unrelated to covering it:
an import, a docstring reference, a list of symbols. So a surviving claimant is a
CANDIDATE, reported with the line that names S so a human can read it, never a
verdict. The measurement this produces is "how many claims are unbacked", and
that is the number nobody had.

SAFETY. Mutates a tracked file, reverts with `git checkout --` in a `finally`,
and refuses to start on a dirty tree.
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
TESTS = REPO / "bench" / "tests"


def tree_is_clean() -> bool:
    r = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                       capture_output=True, text=True)
    return r.returncode == 0 and not r.stdout.strip()


def claimants(symbol: str) -> list[str]:
    out = []
    for p in sorted(TESTS.glob("test_*.py")):
        t = p.read_text(encoding="utf-8", errors="replace")
        if symbol in t:
            out.append(f"bench/tests/{p.name}")
    return out


def destroy(text: str, symbol: str) -> str | None:
    """Replace `symbol`'s body with `return None`, preserving its signature."""
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == symbol:
            lines = text.splitlines(keepends=True)
            first = node.body[0]
            indent = " " * (first.col_offset)
            start = first.lineno - 1
            end = node.end_lineno
            return "".join(lines[:start]) + f"{indent}return None\n" + "".join(lines[end:])
    return None


def run(paths, timeout=3600):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p",
                        "no:cacheprovider", "--tb=no", *paths],
                       cwd=REPO, capture_output=True, text=True, timeout=timeout)
    red = sorted({ln.split("::")[0].replace("FAILED ", "")
                  for ln in r.stdout.splitlines() if ln.startswith("FAILED")})
    return red


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--module", required=True, help="repo-relative .py file")
    ap.add_argument("--symbol", required=True, action="append",
                    help="function to destroy; repeatable")
    a = ap.parse_args()

    if not tree_is_clean():
        print("REFUSING: the working tree is not clean.", file=sys.stderr)
        return 2
    target = REPO / a.module
    original = target.read_text(encoding="utf-8")

    rows = []
    for symbol in a.symbol:
        claims = claimants(symbol)
        if not claims:
            print(f"{symbol}: no test file names it at all -- UNCLAIMED")
            rows.append((symbol, [], [], []))
            continue
        mutated = destroy(original, symbol)
        if mutated is None:
            print(f"{symbol}: not a module-level function in {a.module}; skipped")
            continue
        base_red = run(claims)
        try:
            target.write_text(mutated, encoding="utf-8")
            red = run(claims)
        finally:
            subprocess.run(["git", "checkout", "--", a.module], cwd=REPO, check=False)
        assert target.read_text(encoding="utf-8") == original, "revert failed"
        newly = [f for f in red if f not in base_red]
        survivors = [c for c in claims if c not in newly and c not in base_red]
        rows.append((symbol, claims, newly, survivors))
        print(f"\n{symbol}: {len(claims)} claimant(s), {len(newly)} went red")
        for s in survivors:
            print(f"    SURVIVED the destruction of {symbol}: {s}")

    total_claims = sum(len(r[1]) for r in rows)
    total_surv = sum(len(r[3]) for r in rows)
    if total_claims:
        from statsmodels.stats.proportion import proportion_confint
        from scipy.stats import beta as sbeta
        lo, hi = proportion_confint(total_surv, total_claims, method="wilson")
        lo_c, hi_c = proportion_confint(total_surv, total_claims, method="beta")
        hi_s = (1.0 if total_surv == total_claims
                else sbeta.ppf(0.975, total_surv + 1, total_claims - total_surv))
        print(f"\nclaimants that survived the function being destroyed: "
              f"{total_surv}/{total_claims} = {total_surv / total_claims:.4%}")
        print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]  (statsmodels)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]  (statsmodels/beta)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_s:.4%}]  (scipy, agrees "
              f"to {abs(hi_s - hi_c):.1e})")
    print("\nA SURVIVOR IS A CANDIDATE, NOT A VERDICT. A file may name a symbol "
          "for a reason\nunrelated to covering it. The number is how many "
          "coverage claims are unbacked.")
    if not tree_is_clean():
        print("\n*** TREE NOT CLEAN AFTER THE RUN. ***", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
