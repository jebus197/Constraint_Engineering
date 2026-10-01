#!/usr/bin/env python3
"""FALSIFIER: the seat-evidence measurement miscomputes SILENTLY without git.

THE DEFECT, found by the free day-review panel of 2026-10-01. `survey()` in
`scripts/seat_evidence_is_gitignored_2026-09-30.py` decides preservation with
`git check-ignore` and `git ls-files`. Both helpers swallow a non-zero git exit
and return an EMPTY set. So in any environment where git cannot answer -- a
tarball, a fresh export, OR THE PANEL SANDBOX, which `panel_sandbox.build()`
strips of `.git` -- every row comes back `ignored=False, tracked=False`, i.e.
EVERY seat file is reported "unpreserved" and NONE "ignored".

WHY THAT IS ABOVE THRESHOLD (verification-integrity, section 10 category 3):
  * The declared brief figure `seat_evidence_unpreserved` is "46 of 251". Run in
    a git-less clone it recomputes "251 of 251", so `panel_brief_validate.py`
    re-executing the figure gets a DIFFERENT number than the brief declares --
    a spurious validation failure whose result depends on WHO ran it. The brief
    EXCLUDED the grep-wrapper figure for exactly this environment-dependence;
    this figure has the same defect and was declared anyway.
  * `test_seat_evidence_stranding_does_not_grow_2026-10-01.py`'s premise test
    asserts `ignored == len(rows)`; git-less that is `0 == 251` and the suite
    goes RED -- green for the operator (plain git), red for an agent in the
    sandbox. The Q5 inversion, realised in a committed test.

THIS FALSIFIER IMPORTS THE REAL MODULE (no retyped copy) and:
  FALSIFIED  if git is unavailable here AND survey() returns rows yet does NOT
             raise -- i.e. it silently produced a verdict it cannot support.
  clean exit if survey() raises the GitUnavailable the fix introduces, or if git
             IS available (the defect cannot be shown in that environment).

Run:  python3 scripts/falsify_seat_evidence_git_dependence_2026-10-01.py
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
MOD = REPO / "scripts" / "seat_evidence_is_gitignored_2026-09-30.py"


def _git_can_answer() -> bool:
    try:
        r = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                           cwd=str(REPO), capture_output=True, text=True)
    except OSError:
        return False
    return r.returncode == 0 and r.stdout.strip() == "true"


def _load():
    spec = importlib.util.spec_from_file_location("se_measure", MOD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["se_measure"] = m
    spec.loader.exec_module(m)
    return m


def main() -> int:
    m = _load()
    git_ok = _git_can_answer()
    print(f"git can answer here: {git_ok}")
    if git_ok:
        print("git IS available in this environment, so the silent-miscompute "
              "defect cannot be demonstrated here. Clean exit (not a refutation).")
        return 0

    GitUnavailable = getattr(m, "GitUnavailable", None)
    try:
        rows = m.survey()
    except Exception as exc:                                     # noqa: BLE001
        if GitUnavailable is not None and isinstance(exc, GitUnavailable):
            print(f"survey() correctly REFUSED under git-absence: {exc}")
            print("The fix is in force: the measurement signals rather than "
                  "silently miscomputes. Clean exit.")
            return 0
        print(f"survey() raised an UNEXPECTED {type(exc).__name__}: {exc}")
        print("FALSIFIED")  # an unrelated crash is still a broken measurement
        return 1

    in_tree_but_untracked = [r for r in rows if r["in_tree"] and not r["tracked"]]
    none_ignored = sum(1 for r in rows if r["ignored"]) == 0
    print(f"rows={len(rows)}  in_tree_but_untracked={len(in_tree_but_untracked)}  "
          f"none_ignored={none_ignored}")
    # LENGTH, NOT TRUTH -- see the same note in
    # scripts/day_review_brief_figures_2026-10-01.py.
    if len(rows) > 0 and in_tree_but_untracked and none_ignored:
        print("FALSIFIED: survey() returned a full verdict with git unable to "
              "answer -- every in-tree file reported untracked and nothing "
              "ignored. The measurement is silently wrong in this environment.")
        return 1
    print("survey() returned rows that are not obviously git-blind; defect not "
          "demonstrated. Clean exit.")
    return 0


if __name__ == "__main__":
    import argparse as _argparse
    _argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None,
    ).parse_args()
    raise SystemExit(main())
