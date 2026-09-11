#!/usr/bin/env python3
"""Task A6, half I11: which source-text tests break on an edit that changes nothing?

THE CENSUS SAYS HOW MANY TESTS ASSERT ON PYTHON SOURCE TEXT. It cannot say which
of them are FRAGILE, because some are the only check available -- a shell hook
has no importable surface -- and a test that pins a list which must not shrink is
legitimately about the text.

FRAGILITY IS A PROPERTY OF BEHAVIOUR UNDER AN IRRELEVANT EDIT, so it is measured
by making one. Two edits, deliberately different in strength:

  EOF     a comment appended after the last line. The weakest possible change:
          no line number above it moves, no symbol moves, nothing executes
          differently. A test that reddens here is asserting on the file's
          bytes and nothing else.
  INSIDE  a comment line inserted inside a function body, mid-file. This is the
          realistic case and it is the one that fired 4 times on 2026-09-10 and
          09-11 -- in every instance a COMMENT GREW and a window, an index or a
          body slice stopped reaching what it was looking for.

WHAT IS NOT CLAIMED. A red test under INSIDE is not automatically a defect: a
guard on line-number citations SHOULD notice that lines moved, and this reports
such a test rather than condemning it. The number that matters is how many
break under EOF, where no honest check can have an opinion.

SAFETY. The mutation is applied to a tracked file and reverted with
`git checkout --` in a `finally`, and the script REFUSES to start unless the
working tree is clean, so a revert cannot destroy uncommitted work.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
TARGET_DEFAULT = "bench/reference_runner_v3.py"

MARKER = "# A6 INERT MUTATION -- a comment that changes nothing executable.\n"


def tree_is_clean() -> bool:
    r = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                       capture_output=True, text=True)
    return r.returncode == 0 and not r.stdout.strip()


def tests_reading(target: str) -> list[str]:
    """Test files whose text names `target`, by basename or repo-relative path."""
    base = pathlib.PurePosixPath(target).name
    out = []
    for p in sorted((REPO / "bench" / "tests").glob("test_*.py")):
        t = p.read_text(encoding="utf-8", errors="replace")
        if base in t or target in t:
            out.append(f"bench/tests/{p.name}")
    return out


def _insert_inside(text: str) -> str:
    """Put the comment on the first line INSIDE a function body."""
    lines = text.splitlines(keepends=True)
    for i, ln in enumerate(lines):
        if re.match(r"^def [A-Za-z_]", ln):
            # the line after the def's docstring, or right after the def
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith(('"""', "'''")):
                j += 1
            indent = "    "
            lines.insert(j, indent + MARKER)
            return "".join(lines)
    return text + MARKER


def run(paths: list[str], timeout: int = 3600) -> tuple[int, list[str]]:
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p",
                        "no:cacheprovider", "--tb=no", *paths],
                       cwd=REPO, capture_output=True, text=True, timeout=timeout)
    failed = sorted({ln.split("::")[0].replace("FAILED ", "")
                     for ln in r.stdout.splitlines() if ln.startswith("FAILED")})
    return r.returncode, failed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--target", default=TARGET_DEFAULT)
    ap.add_argument("--mode", choices=("eof", "inside", "both"), default="both")
    a = ap.parse_args()

    if not tree_is_clean():
        print("REFUSING: the working tree is not clean. This script mutates a "
              "tracked file and reverts with `git checkout --`, which would "
              "destroy uncommitted work.", file=sys.stderr)
        return 2

    target = REPO / a.target
    if not target.is_file():
        print(f"no such target: {a.target}", file=sys.stderr)
        return 2

    paths = tests_reading(a.target)
    print(f"target                : {a.target}")
    print(f"test files naming it  : {len(paths)}")

    original = target.read_text(encoding="utf-8")
    rc0, baseline = run(paths)
    print(f"baseline              : exit {rc0}, {len(baseline)} failing file(s)")
    for b in baseline:
        print(f"    (already red) {b}")

    results = {}
    modes = ("eof", "inside") if a.mode == "both" else (a.mode,)
    for mode in modes:
        try:
            target.write_text(original + MARKER if mode == "eof"
                              else _insert_inside(original), encoding="utf-8")
            rc, failed = run(paths)
        finally:
            subprocess.run(["git", "checkout", "--", a.target], cwd=REPO, check=False)
        assert target.read_text(encoding="utf-8") == original, (
            "the revert did not restore the file; STOP and check git status")
        newly = [f for f in failed if f not in baseline]
        results[mode] = newly
        print(f"\nMODE {mode.upper()}: {len(newly)} file(s) newly red")
        for f in newly:
            print(f"    {f}")

    n = len(paths)
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sbeta
    for mode, newly in results.items():
        k = len(newly)
        lo, hi = proportion_confint(k, n, method="wilson")
        lo_c, hi_c = proportion_confint(k, n, method="beta")
        hi_s = 1.0 if k == n else sbeta.ppf(0.975, k + 1, n - k)
        print(f"\n{mode}: {k}/{n} = {k / n:.4%}")
        print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]  (statsmodels)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]  (statsmodels/beta)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_s:.4%}]  (scipy, agrees "
              f"to {abs(hi_s - hi_c):.1e})")

    if "eof" in results:
        print("\nA FILE RED UNDER EOF IS ASSERTING ON BYTES. Nothing above the "
              "appended line\nmoved and nothing executes differently, so no "
              "honest check can have an opinion.")
    # THE FINAL CHECK IS ABOUT THE REVERT, NOT ABOUT THE TREE. The first version
    # re-used the entry guard, and a file created in another terminal WHILE the
    # 20-minute run was in flight made it print "THE TREE IS NOT CLEAN AFTER THE
    # RUN" -- an alarm about something the script neither touched nor could
    # affect. An alarm that fires on the ordinary case is on its way to being
    # ignored, which is this project's own sentence about 2 other alarms.
    dirty = subprocess.run(["git", "status", "--porcelain", "--", a.target],
                           cwd=REPO, capture_output=True, text=True).stdout.strip()
    if dirty:
        print(f"\n*** {a.target} IS STILL MODIFIED AFTER THE RUN. The revert "
              f"failed; inspect before continuing. ***", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
