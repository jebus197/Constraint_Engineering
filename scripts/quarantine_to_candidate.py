#!/usr/bin/env python3
"""Turn a quarantined direct-write into a proper gate candidate.

WHY. On 2026-08-22 a model working T01 wrote its fix straight into the working tree
instead of returning a patch, twice, and CC1's `git add -A` committed it both
times. The writes were reverted and quarantined rather than deleted, because the
WORK may well be sound even though the ROUTE was wrong.

Deleting it would punish a model for a hole CC1 left open (the Claude CLI grants
Bash, and Bash is a superset of Write; set_panel_cwd existed for exactly this and
had never been called). Leaving it in the tree would be worse: unreviewed, ungated
code, which is the category this whole experiment exists to end.

So it is converted into the required SEARCH/REPLACE + TEST_FILE form and put
through the SAME gate as every other candidate -- fail at parent, pass with the
patch, no new suite failure. It earns its place or it does not.

    python3 scripts/quarantine_to_candidate.py <runner.diff> <test.py> [--evaluate]
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def hunks_to_search_replace(diff_text: str) -> list:
    """Convert unified-diff hunks into (path, search, replace) triples.

    Context lines are included on BOTH sides so the SEARCH block is anchored in the
    file rather than floating. A hunk whose context is ambiguous is the caller's
    problem to notice -- the gate will reject it, which is the correct outcome.
    """
    out, path = [], None
    for m in re.finditer(r"^\+\+\+ b/(\S+)$", diff_text, re.M):
        path = m.group(1)
    if not path:
        return out
    for hunk in re.split(r"^@@[^\n]*@@[^\n]*$", diff_text, flags=re.M)[1:]:
        search, replace = [], []
        for line in hunk.splitlines():
            if line.startswith("+++") or line.startswith("---"):
                continue
            if line.startswith("-"):
                search.append(line[1:])
            elif line.startswith("+"):
                replace.append(line[1:])
            elif line.startswith(" "):
                search.append(line[1:]); replace.append(line[1:])
            elif line == "":
                search.append(""); replace.append("")
        while search and search[-1] == "" and replace and replace[-1] == "":
            search.pop(); replace.pop()
        if search and replace and search != replace:
            out.append((path, "\n".join(search), "\n".join(replace)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    # nargs="?" deliberately: with required positionals argparse reports those
    # first and NEVER emits "unrecognized arguments", so an unknown flag would be
    # masked by a missing-argument error. Validated below instead.
    ap.add_argument("diff", nargs="?")
    ap.add_argument("test", nargs="?")
    ap.add_argument("--evaluate", action="store_true")
    ap.add_argument("--parent", default="HEAD")
    args = ap.parse_args()

    if not args.diff or not args.test:
        ap.error("both a diff and a test file are required")
    triples = hunks_to_search_replace(pathlib.Path(args.diff).read_text())
    test_src = pathlib.Path(args.test).read_text()
    test_rel = f"bench/tests/{pathlib.Path(args.test).name}"

    parts = []
    for path, s, r in triples:
        parts.append(f"<<<< SEARCH {path}\n{s}\n==== REPLACE\n{r}\n>>>>\n")
    parts.append(f"\nTEST_FILE: {test_rel}\n\n```python\n{test_src}```\n")
    candidate = "\n".join(parts)
    print(f"  {len(triples)} hunk(s) converted; test {test_rel} "
          f"({len(test_src.splitlines())} lines)")

    outp = pathlib.Path(args.diff).with_suffix(".candidate.md")
    outp.write_text(candidate, encoding="utf-8")
    print(f"  candidate written: {outp}")

    if args.evaluate:
        from bench import build_acceptance as BA
        v = BA.evaluate(candidate, parent=args.parent)
        print(f"\n  outcome        : {v.outcome}")
        print(f"  detail         : {v.detail}")
        print(f"  test at parent : {v.test_at_parent}")
        print(f"  test w/ patch  : {v.test_with_patch}")
        print(f"  suite after    : {v.suite_after}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
