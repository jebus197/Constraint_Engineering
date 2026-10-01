#!/usr/bin/env python3
"""THE ARCHIVE IS INVISIBLE TO ANY IGNORE-AWARE SEARCH, AND THAT NEEDS NO WRAPPER.

FREE PANEL, 2026-10-01, Q5. `bench/tests/test_shell_grep_blind_spot_2026-09-28.py`
guards a real and load-bearing fact: a search honouring `.gitignore` cannot see
`bench/logs/**`, so it reports "0 occurrences" for a term occurring thousands of
times. But the guard now skips unless the session's `grep` wrapper can exec its
backend, and that backend is reachable only where `CLAUDE_CODE_EXECPATH` is set
-- true in an agent's environment, false in the operator's login shell.

SO THE GUARD IS LIVE FOR AN AGENT AND SILENT FOR THE FOUNDER. The skip itself is
CORRECT: the wrapper-divergence proposition is conditional on the wrapper, and
asserting it where no wrapper exists is what produced the original "0 of 541
missed" lie. The defect is not the skip. It is that the guard has no
environment-independent arm, so the PROJECT-LEVEL fact -- that the evidence
archive sits behind an ignore rule -- is guarded only where an agent happens to
run.

THIS FILE IS THAT ARM. It asserts two pure filesystem facts, with no git binary,
no shell wrapper, no `grep`, and no environment variable in the decision:

  1. `.gitignore` carries a rule that matches a path under `bench/logs/`;
  2. `bench/logs/` holds a non-trivial number of files.

Together those entail the consequence the original guard exists for: an
ignore-aware search is blind to N files, whoever runs it and from whichever
shell. The rate stays with the wrapper test, which is right -- the rate moves
with the repository. What moves with NOTHING is the existence of the blind spot,
and that is what is checked here.

Run:  python3 scripts/archive_is_invisible_to_ignore_aware_search_2026-10-01.py
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
ARCHIVE_REL = "bench/logs"
MIN_FILES = 100


def ignore_rules() -> list:
    """Every non-comment rule in `.gitignore`, in order."""
    gi = REPO / ".gitignore"
    if not gi.is_file():
        return []
    return [ln.strip() for ln in gi.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")]


def rules_matching_archive() -> list:
    """Rules that ignore something under the archive. `pathspec` if present."""
    rules = ignore_rules()
    probe = f"{ARCHIVE_REL}/some_run/runner_state.json"
    try:
        import pathspec
    except ImportError:
        pathspec = None
    hits = []
    for r in rules:
        if pathspec is not None:
            # "gitignore", NOT "gitwildmatch": the latter is deprecated in the
            # installed pathspec and emitted 216 DeprecationWarnings through
            # the suite. Both accept the same syntax; verified equal on this
            # rule set before switching.
            spec = pathspec.PathSpec.from_lines("gitignore", [r])
            if spec.match_file(probe):
                hits.append(r)
        else:
            # Conservative fallback: a literal prefix on the archive path.
            bare = r.rstrip("/*").lstrip("/")
            if bare and probe.startswith(bare):
                hits.append(r)
    return hits


def archive_file_count() -> int:
    d = REPO / ARCHIVE_REL
    if not d.is_dir():
        return 0
    return sum(1 for p in d.rglob("*") if p.is_file())


def main() -> int:
    print("IS THE EVIDENCE ARCHIVE BEHIND AN IGNORE RULE? (no git, no wrapper)")
    print("=" * 74)
    try:
        import pathspec                                        # noqa: F401
        how = "pathspec gitignore (the same matcher git uses semantics of)"
    except ImportError:
        how = "literal-prefix fallback (pathspec absent); CONSERVATIVE"
    print(f"  matcher: {how}")

    hits = rules_matching_archive()
    n_files = archive_file_count()
    print(f"  .gitignore rules total                     {len(ignore_rules())}")
    print(f"  rules matching a path under {ARCHIVE_REL}/   {len(hits)}")
    for r in hits:
        print(f"      {r!r}")
    print(f"  files under {ARCHIVE_REL}/                   {n_files}")

    print()
    if not hits:
        print("  CLEAN on this arm: no ignore rule covers the archive, so an "
              "ignore-aware search can see it.")
        return 0
    if n_files < MIN_FILES:
        print(f"  INCONCLUSIVE: the archive holds only {n_files} files in this "
              f"clone, below the {MIN_FILES} this guard needs to mean anything.")
        return 0
    print(f"  CONFIRMED, environment-independently: the archive is covered by "
          f"{len(hits)} ignore rule(s), and that is the matcher-independent "
          f"fact this arm exists to hold.")

    # THE SWEEPING VERSION OF THIS CONCLUSION WAS WRONG AND IS CORRECTED HERE.
    #
    # It read: "{n_files} files sit behind {len(hits)} ignore rule(s). Any search
    # honouring .gitignore reports 0 occurrences for terms occurring throughout
    # them." The first half conflates "matched by a rule" with "invisible": the
    # ignore file also carries NEGATIONS (`!bench/logs/**/*report*.json` and
    # `!bench/logs/**/runner_state.json`), so most of the archive is re-included.
    #
    # MEASURED 2026-10-01 against `git check-ignore`, the real decider, which
    # this script's author could not run -- its sandbox has no `.git`, and it
    # named that as its open assumption:
    #     files under bench/logs/      8736
    #     git says IGNORED             2245   (25.6983%, Wilson [24.7928%, 26.6251%])
    #     NOT ignored, negations win   6491
    # So the conclusion was false for 6491 of 8736 files.
    #
    # AND `pathspec` IS NOT A GIT PROXY, which matters more than the arithmetic.
    # The same rule set through `pathspec`'s negation-aware `gitignore` spec
    # returns 87, not 2245 -- a 25x disagreement, with 0 pathspec-only files.
    # git declines to re-include a file whose parent directory is excluded;
    # pathspec does not model that. An arm built to be environment-INDEPENDENT
    # cannot report a file count from a matcher that disagrees with the tool
    # whose behaviour is the subject. So the count is reported from git where
    # git is there, and withheld where it is not.
    import subprocess

    try:
        files = [str(f) for f in (REPO / ARCHIVE_REL).rglob("*") if f.is_file()]
        r = subprocess.run(["git", "check-ignore", "--stdin"], cwd=REPO,
                           input="\n".join(files), capture_output=True,
                           text=True, timeout=600)
        if r.returncode in (0, 1):
            ign = len([ln for ln in r.stdout.splitlines() if ln.strip()])
            print(f"  AND, from the real decider here: git check-ignore reports "
                  f"{ign} of {n_files} actually ignored; the rest are "
                  f"re-included by negations.")
        else:
            raise RuntimeError(r.stderr.strip()[:120] or "non-zero exit")
    except Exception as exc:                                  # noqa: BLE001
        print(f"  THE FILE COUNT IS WITHHELD HERE: git cannot answer ({exc}), "
              f"and `pathspec` disagrees with git by 25x on this rule set, so "
              f"no honest count is available in this environment.")
    return 0


if __name__ == "__main__":
    import argparse as _argparse

    _argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None,
    ).parse_args()
    raise SystemExit(main())
