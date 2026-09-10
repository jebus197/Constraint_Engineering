#!/usr/bin/env python3
"""Task A3: guard the CONTENT of a cited line, not merely the file.

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

THE DEFECT. A hand-written `path:LINE` citation breaks the moment anything is
inserted above it, and the existing citation guard checks only that the FILE
exists -- `cdsfl_utils.SUPPRESS_LINE` says so in as many words: "the FILE exists;
line numbers NOT checked". The run ledger self-heals because it has a generator.
Hand-written citations do not. This project moved the same citation 3 times in
one day on 2026-09-10, and the runner grew by roughly 90 lines that evening.

THE CHECK, AND WHY IT IS BY AST RATHER THAN BY TEXT. A citation is usually
preceded by the symbol it is about, in backticks. If that symbol is a function or
class, its true span is known exactly, and the question "does this citation point
inside the thing it names" is decidable. A text search would be defeated by the
symbol appearing in a comment 400 lines away; an AST span is not.

WHAT IT CANNOT CHECK, STATED RATHER THAN HIDDEN. A citation with no backticked
symbol before it, or one naming something that is not a def or a class, is
reported as UNCHECKABLE and counted separately. Folding those into the pass count
would be the "a guard that cannot fail" defect, and folding them into the fail
count would invent findings.
"""
from __future__ import annotations

import ast
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Files whose line citations are worth guarding. Extend deliberately.
CITED = ("bench/reference_runner_v3.py",)

#: Where citations are written.
SEARCH = ("experimental_notes/**/*.md", "bench/tests/*.py", "scripts/*.py",
          "resources/*.md", ".claude/*.md")

IDENT = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")


def spans(path: str) -> dict:
    tree = ast.parse((REPO / path).read_text(encoding="utf-8"))
    return {n.name: (n.lineno, getattr(n, "end_lineno", n.lineno))
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def citing_files():
    seen = set()
    for pat in SEARCH:
        for p in REPO.glob(pat):
            if p.is_file() and p not in seen:
                seen.add(p)
                yield p


def check(target: str):
    sp = spans(target)
    rx = re.compile(re.escape(target) + r":(\d+)")
    n_lines = len((REPO / target).read_text(encoding="utf-8").splitlines())
    good, bad, unchecked, past_end = [], [], 0, []
    for p in citing_files():
        txt = p.read_text(encoding="utf-8", errors="replace")
        for m in rx.finditer(txt):
            line = int(m.group(1))
            if line > n_lines:
                past_end.append((p, line))
            ids = IDENT.findall(txt[max(0, m.start() - 220):m.start()])
            anchor = next((i for i in reversed(ids) if i in sp), None)
            if anchor is None:
                unchecked += 1
                continue
            lo, hi = sp[anchor]
            (good if lo <= line <= hi else bad).append((p, line, anchor, lo, hi))
    return good, bad, unchecked, past_end, n_lines


def main() -> int:
    rc = 0
    for target in CITED:
        good, bad, unchecked, past_end, n_lines = check(target)
        total = len(good) + len(bad) + unchecked
        print(f"--- {target} ({n_lines:,} lines) ---")
        print(f"  citations found        : {total}")
        print(f"  checkable (anchored)   : {len(good) + len(bad)}")
        print(f"  UNCHECKABLE (no symbol): {unchecked}")
        print(f"  pointing past the end  : {len(past_end)}")
        print(f"  inside the named symbol: {len(good)}")
        print(f"  OUTSIDE it             : {len(bad)}")
        if good or bad:
            from statsmodels.stats.proportion import proportion_confint
            k, n = len(bad), len(good) + len(bad)
            lo, hi = proportion_confint(k, n, method="wilson")
            lo_c, hi_c = proportion_confint(k, n, method="beta")
            print(f"  {k}/{n} = {k / n:.4%}  Wilson [{lo:.4%}, {hi:.4%}]  "
                  f"Clopper-Pearson [{lo_c:.4%}, {hi_c:.4%}]")
        for p, line, anchor, lo, hi in bad:
            rel = p.relative_to(REPO)
            print(f"    {rel}:{line} names `{anchor}`, which spans {lo}-{hi} "
                  f"(off by {lo - line:+d})")
            rc = 1
    if rc:
        print("\n  A citation that names a symbol must point inside it. Repair the")
        print("  line number, or cite the symbol and drop the number.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
