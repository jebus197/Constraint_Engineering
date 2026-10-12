#!/usr/bin/env python3
"""Which test files have a VISIBLE record of catching a defect, and which have none.

HIS QUESTION, 2026-10-12: *"there may be a question of if all these tests are necessary
to begin with?"* -- asked after noting the real risk that tests come to test other tests.
He approved this measurement and asked for it BEFORE anything is trimmed.

WHAT THIS CANNOT TELL YOU, AND IT IS THE FIRST THING TO READ
------------------------------------------------------------
A guard that silently holds a line for months appears in NO commit message. Its value is
precisely that nothing ever happened. So **a test with no record here is UNKNOWN, not
useless**, and this output is not a list of things to delete. Treating it as one would be
the `execute-do-not-grep` error in a new costume: inferring a property from the absence
of a text match.

What it CAN establish is the opposite direction, which is the useful one: the tests that
demonstrably earned their place, by being named in a commit that also describes a defect
being found or repaired. That set is a floor on the suite's value, never a ceiling.

HOW A TEST IS CREDITED
  * NAMED -- the commit message mentions the file.
  * CREATION -- the commit that first adds the file. Every test has exactly 1, so being
    named only at creation is the NORMAL case for a guard that has never had to fire.
  * CAUGHT -- named in a commit whose message carries defect language AND is not that
    file's own creation commit. This is the discriminating case: somebody wrote about a
    defect and named this test in the same breath, after it already existed.

THE DEFECT VOCABULARY is this project's own, taken from how its commit messages actually
read: failed, caught, found, defect, red, regression, broke, mutation, refuted,
withdrawn, wrong, bug. A message needs 1 of those AND a test filename.

A --help COSTS NOTHING: reads `git log`, no dispatch, no network, no test execution.
"""
from __future__ import annotations

import collections
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
# THE HYPHEN IS LOAD-BEARING AND ITS ABSENCE INVALIDATED THE FIRST RUN.
# This project names test files with dates -- `test_foo_2026-08-30.py` -- so a
# class of `[A-Za-z0-9_]` cannot match a single dated file, which is most of
# them. The first run reported 527 of 571 files "never named in any commit",
# 0.9229, and that figure was an artefact of this regex rather than a fact about
# the suite. A false zero from a wrong predicate: the same class of error this
# session met 4 other times, and the reason the figure was withdrawn before use.
TEST_RE = re.compile(r"(test_[A-Za-z0-9_.-]*?\.py)")
DEFECT_RE = re.compile(
    r"\b(fail(?:ed|s|ing)?|caught|found|defect|red|regression|broke|broken|mutation|"
    r"refut(?:ed|es)|withdrawn|wrong|bug)\b", re.I)


def commits() -> list[tuple[str, str]]:
    """(sha, full message) for every commit on every ref, oldest first."""
    r = subprocess.run(
        ["git", "log", "--all", "--reverse", "--pretty=%H%x00%B%x1e"],
        cwd=str(REPO), capture_output=True, text=True)
    out = []
    for rec in (r.stdout or "").split("\x1e"):
        rec = rec.strip("\n")
        if not rec or "\x00" not in rec:
            continue
        sha, msg = rec.split("\x00", 1)
        out.append((sha.strip(), msg))
    return out


def creation_commit() -> dict[str, str]:
    """The commit that first ADDED each test file, by basename."""
    r = subprocess.run(
        ["git", "log", "--all", "--reverse", "--diff-filter=A",
         "--pretty=format:%H", "--name-only", "--", "bench/tests/"],
        cwd=str(REPO), capture_output=True, text=True)
    out, sha = {}, None
    for line in (r.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        if re.fullmatch(r"[0-9a-f]{40}", line):
            sha = line
        elif line.endswith(".py") and sha:
            out.setdefault(pathlib.Path(line).name, sha)
    return out


def live_tests() -> set[str]:
    return {p.name for p in (REPO / "bench" / "tests").glob("test_*.py")}


def ci(k: int, n: int) -> str:
    if n == 0:
        return "n=0"
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats
    lo, hi = proportion_confint(k, n, method="wilson")
    clo = stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0
    chi = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return f"Wilson [{lo:.4f}, {hi:.4f}]  CP [{clo:.4f}, {chi:.4f}]"


def _answer_help(doc, path, args):
    """Answer `--help` AND refuse an unknown flag, through the shared helper.

    WIRED AFTER REPEATING THE DEFECT A FOURTH TIME IN ONE DAY. This script shipped
    with a bare `argv[1] in ("-h", "--help")` block, so
    `--this-flag-does-not-exist` exited 0 AND ran the whole 1,702-commit
    measurement -- in `test_operational_scripts`'s own words, *"an unrecognised
    argument that reads as success is the 118-day no-op again"*. The identical fault
    was found in 3 other scripts this morning and fixed with this same helper, which
    is the point: the fix existed and was not reached for.
    """
    import sys as _sys
    _sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(doc, path, list(args))


def main(argv: list[str]) -> int:
    _answer_help(__doc__, __file__, argv[1:])

    live = live_tests()
    created = creation_commit()
    named = collections.Counter()
    caught = collections.Counter()
    caught_examples: dict[str, str] = {}

    msgs = commits()
    for sha, msg in msgs:
        hits = set(TEST_RE.findall(msg))
        if not hits:
            continue
        is_defect = bool(DEFECT_RE.search(msg))
        for name in hits:
            if name not in live:
                continue
            named[name] += 1
            # CREDITED ONLY IF IT ALREADY EXISTED. Being named in your own creation
            # commit says nothing about having caught anything.
            if is_defect and created.get(name) != sha:
                caught[name] += 1
                caught_examples.setdefault(name, msg.splitlines()[0][:96])

    n = len(live)
    never = sorted(t for t in live if named[t] == 0)
    only_creation = sorted(t for t in live if named[t] > 0 and caught[t] == 0)
    has_caught = sorted(t for t in live if caught[t] > 0)

    print(f"commits scanned on all refs : {len(msgs)}")
    print(f"live test files             : {n}")
    print()
    print("THIS IS A FLOOR ON VALUE, NOT A HIT LIST. A guard that has never had to fire")
    print("appears in no message, so 'no record' means UNKNOWN and never 'useless'.")
    print()
    print(f"  demonstrably CAUGHT something : {len(has_caught):>4} = "
          f"{len(has_caught)/n:.4f}")
    print(f"      {ci(len(has_caught), n)}")
    print(f"  named, but never in a defect  : {len(only_creation):>4} = "
          f"{len(only_creation)/n:.4f}")
    print(f"      {ci(len(only_creation), n)}")
    print(f"  never named in any commit     : {len(never):>4} = {len(never)/n:.4f}")
    print(f"      {ci(len(never), n)}")
    print()
    print("THE 15 MOST-CREDITED TEST FILES (named in a defect commit after creation):")
    for name, c in caught.most_common(15):
        print(f"  {c:>3}x  {name}")
        print(f"        e.g. {caught_examples[name]}")
    print()
    print("A SAMPLE OF THE NEVER-NAMED, to show what the category actually contains:")
    for t in never[:12]:
        print(f"  {t}")
    if len(never) > 12:
        print(f"  ... and {len(never)-12} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
