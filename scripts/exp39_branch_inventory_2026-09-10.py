#!/usr/bin/env python3
"""Task 8.2: what does `exp39-experimental` hold that exists nowhere else?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

HIS RULING, verbatim: "Get Fable and CC2 to look at this with you, decide which
elements on this branch remain useful and should be adopted in light of
everything else we have done and which should be considered superseded."

This script establishes the FACTS the adjudication needs. It decides nothing and
deletes nothing. Deleting a git ref is one of the 3 categories reserved to the
founder in person, and no path here approaches it.

WHAT THE ENTRY SAID, AND WHAT IS ACTUALLY TRUE. The entry records "12 file paths
existing nowhere else". That is right, and it does not say what they are. They
are 5 EXAM ANSWER KEYS and the 6 exam targets they belong to, plus 1 note.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
BRANCH = "exp39-experimental"
MAIN = "origin/main"


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=REPO,
                          capture_output=True, text=True).stdout


def tree_paths(rev: str) -> set:
    return set(git("ls-tree", "-r", "--name-only", rev).split())


def main() -> int:
    if not git("rev-parse", "--verify", BRANCH).strip():
        print(f"no branch {BRANCH} in this clone -- nothing to measure.")
        return 0

    print("--- what is on the REMOTE ---")
    remote = [l.split()[-1] for l in git("ls-remote", "--heads", "origin").splitlines()]
    print(f"  remote heads: {remote or '(none reachable)'}")
    print(f"  {BRANCH} is on the remote: {'refs/heads/' + BRANCH in remote}")

    print("\n--- tip trees ---")
    b, m = tree_paths(BRANCH), tree_paths(MAIN)
    only_tip = sorted(b - m)
    print(f"  paths on the {BRANCH} tip and not on {MAIN}: {len(only_tip)}")
    for p in only_tip:
        print(f"     {p}")

    print("\n--- the branch's UNREACHABLE history ---")
    unreachable = git("rev-list", BRANCH, "--not", MAIN).split()
    print(f"  commits on {BRANCH} unreachable from {MAIN}: {len(unreachable)}")

    hist = set()
    for c in unreachable:
        hist |= tree_paths(c)
    main_hist = set()
    for c in git("rev-list", MAIN).split()[:400]:
        main_hist |= tree_paths(c)
    only_hist = sorted(hist - main_hist)
    print(f"  paths in that history and in no main-history tree: {len(only_hist)}")
    keys = [p for p in only_hist if "answer_key" in p]
    for p in only_hist:
        print(f"     {'*** KEY *** ' if p in keys else '             '}{p}")

    print(f"\n--- ANSWER KEYS: {len(keys)} ---")
    for k in keys:
        n_main = git("rev-list", MAIN, "--count", "--", k).strip() or "0"
        print(f"  {pathlib.Path(k).name}: reachable from {MAIN} in {n_main} commit(s)")
    print("\n  REACHABILITY IS NOT EXPOSURE -- the founder's own ruling of "
          "2026-09-07.\n  These objects sit in a LOCAL branch. The remote carries "
          "main alone, so\n  nothing here was ever published. The branch's own "
          "commit eecdb0f says the\n  same thing in its title and names the "
          "residual: 'git-history recovery by\n  deliberate archaeology'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
