#!/usr/bin/env python3
"""THE SEAT-EVIDENCE FIGURE REPORTS 100% STRANDED WHEN GIT MERELY FAILS.

FOUND BY THE FREE PANEL, 2026-10-01, by re-executing the day-review brief's own
declared figures in the panel sandbox. The brief declares

    <!-- figure: seat_evidence_unpreserved | ... | 46 of 251 unpreserved -->

and the producer, re-run unchanged, printed `251 of 251 unpreserved`.

THE CAUSE IS NOT THE BACKLOG. `scripts/seat_evidence_is_gitignored_2026-09-30.py`
decides "tracked" by shelling out:

    r = subprocess.run(["git", "ls-files", "-z", "--"] + paths,
                       cwd=ROOT, capture_output=True, text=True)
    return {ROOT / s for s in r.stdout.split("\\0") if s}

`r.returncode` IS NEVER READ. Where git cannot answer -- a panel sandbox copy, a
source tarball, an `ARCHIVE`/`git archive` export, a Docker `COPY` that omits
`.git`, a container without the git binary -- stdout is empty, the tracked set is
empty, and EVERY row is classified UNPRESERVED. The figure does not error; it
reports the maximum possible stranding as a measurement.

BOTH DIRECTIONS OF THE SAME BUG ARE LIVE, which is why this is worth a fix
rather than a note. `_ignored()` has the identical shape, and its silent failure
points the OTHER way: no git, nothing reported ignored, so the same run prints a
reassuring "ignored by git: 0 of 251". One unchecked return code produces a
false alarm in one figure and a false clearance in the other, from one run.

AND IT IS LOAD-BEARING, because the brief says this survey carries "a
shrink-only ratchet over the existing backlog". A ratchet fed 251 where the
baseline is 46 fails on every git-less checkout; a ratchet whose baseline is
ever RECORDED in that state is permanently slack.

THE FIX IS TO READ THE RETURN CODE, and `git check-ignore`'s convention is the
part to get right: it exits 0 when something is ignored, **1 when nothing is**,
and 128 on a fatal error. So 1 is success-with-no-matches and must not raise.

This file FAILS (AssertionError) while either helper swallows a git failure, and
exits 0 once both refuse to answer from an empty result.

Run:  python3 scripts/seat_evidence_survey_trusts_git_2026-10-01.py
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
TARGET = REPO / "scripts" / "seat_evidence_is_gitignored_2026-09-30.py"


def _load():
    """Import the REAL target module. Nothing here is a retyped copy."""
    spec = importlib.util.spec_from_file_location("seat_evidence_real",
                                                  str(TARGET))
    m = importlib.util.module_from_spec(spec)
    sys.modules["seat_evidence_real"] = m
    spec.loader.exec_module(m)
    return m


def main() -> int:
    m = _load()
    print("DO THE SURVEY'S GIT HELPERS NOTICE THAT GIT FAILED?")
    print("=" * 74)

    failures = []
    with tempfile.TemporaryDirectory() as td:
        nogit = pathlib.Path(td)
        probe = nogit / "a_file.txt"
        probe.write_text("x", encoding="utf-8")

        # The module's own parameter for "where the repository is". Repointing
        # it is using the module, not reimplementing it.
        m.ROOT = nogit

        # Establish the premise by EXECUTION: git really does fail here.
        rc_ls = subprocess.run(["git", "ls-files", "-z", "--", "a_file.txt"],
                               cwd=nogit, capture_output=True, text=True)
        rc_ci = subprocess.run(["git", "check-ignore", "--stdin"], cwd=nogit,
                               input="a_file.txt", capture_output=True,
                               text=True)
        print(f"  premise: `git ls-files`     exit={rc_ls.returncode} "
              f"stdout={rc_ls.stdout!r}")
        print(f"  premise: `git check-ignore` exit={rc_ci.returncode} "
              f"stdout={rc_ci.stdout!r}")
        if rc_ls.returncode == 0:
            print("  NOT A VALID PROBE: git answered in a non-repository; "
                  "this falsifier cannot speak here.")
            return 0

        for name, fn in (("_tracked", m._tracked), ("_ignored", m._ignored)):
            try:
                got = fn([probe])
            except Exception as exc:                          # noqa: BLE001
                print(f"  {name:10s} RAISED {type(exc).__name__}: "
                      f"{str(exc)[:90]}   <-- correct")
                continue
            print(f"  {name:10s} RETURNED {got!r} with git at "
                  f"exit {rc_ls.returncode}   <-- SWALLOWED")
            failures.append(name)

    print()
    if failures:
        print(f"  FALSIFIED: {len(failures)} of 2 helpers answer from an empty "
              f"result after git failed: {', '.join(failures)}.")
        print("  Consequence: every row is classified UNPRESERVED ('251 of 251')")
        print("  while `ignored by git` reads a reassuring 0, from one run.")
        raise AssertionError(
            f"{failures} ignore git's return code, so a git-less checkout "
            f"reports maximum stranding as a measurement")
    print("  CLEAN: both helpers refuse to answer when git cannot.")
    return 0


if __name__ == "__main__":
    import argparse as _argparse

    _argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None,
    ).parse_args()
    raise SystemExit(main())
