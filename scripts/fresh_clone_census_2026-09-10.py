#!/usr/bin/env python3
"""Task A2: what a fresh `git clone` plus the full suite actually does, and why.

`measured-rate-travels-with-its-script`. The task-list entry quoted "11 failed,
5487 passed, exit 1, against 0 failures in the working tree" from 2026-09-09 with
no producing script. Both halves of that sentence were wrong by 2026-09-10.

MEASURED 2026-09-10, before any repair, both runs full-suite:

  fresh clone at 52acec8   22 failed, 6592 passed, 18 skipped, 1 xfailed, exit 1
  working tree, same HEAD  6 failed  (10 in the raw log; 4 were casualties of
                           edits made WHILE the suite ran and pass on re-run)

So the count had DOUBLED in a day, the growth was the maintainer's own new
tests, and the premise "0 failures in the working tree" was false.

THE CAUSES, and they are not one thing. Every entry below was established by
running the test in both trees and reading the failure, never by reading source.

The census is a committed table rather than a parse of a log, because a log is
not evidence of a diagnosis -- it is evidence of a symptom. Each row names what
broke, the mechanism, and the repair, and `--check` re-runs the named tests in
this checkout so the table cannot quietly go stale.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: (test file, cause key, one-line mechanism, repair)
CENSUS = [
    ("bench/tests/test_precommit_guard_2026-09-09.py", "environment",
     "a fresh clone has no core.hooksPath, and the skip meant to detect that "
     "asked whether `git config --get user.email` was empty -- which falls back "
     "to GLOBAL config, so the branch was unreachable on any machine with a git "
     "identity",
     "onboarding stamps `cdsfl.onboarded` in --local config; the test uses that"),
    ("bench/tests/test_repo_paths_predicate_2026-09-09.py", "gitignored-by-design",
     "`bench/results` is a declared archive root that .gitignore:7 excludes "
     "entirely (0 tracked files), so it cannot exist in a clone",
     "the check reads 'exists OR is named in .gitignore'; an unbacked root "
     "still fails, proved by a negative control"),
    ("bench/tests/test_operational_scripts.py", "import-time-io",
     "compose_all_2026-08-23.py read an untracked JSON index AT MODULE LEVEL, "
     "so importing it -- and apply_v3.py, which imports it for 2 literals -- "
     "raised FileNotFoundError",
     "the index is loaded lazily and says once when it is absent"),
    ("bench/tests/test_branch_supplies_versions_2026-09-10.py", "local-only-ref",
     "exp39-experimental is a LOCAL branch that was never pushed, so no clone "
     "can carry it, and the early return skipped the methodological caveat",
     "the caveat prints on both paths and the absence is named"),
    ("bench/tests/test_stated_gate_count_matches_measurement_2026-09-07.py",
     "corpus-differs",
     "the pinned figure 4142 was measured over the maintainer's on-disk archive; "
     "a clone measures 3507, the difference being 610 untracked JSON files",
     "the tracked corpus is what prose pins; the on-disk figure is still stated "
     "and still checked where it can be"),
    ("bench/tests/test_falsifier_cannot_read_the_key.py", "stale-absolute-path",
     "archived falsifiers carry the absolute path of the checkout they were "
     "written in; elsewhere the containment guard refuses them",
     "the archive audit classifies a location artefact separately, with a "
     "control proving it cannot excuse a real escape"),
    ("bench/tests/test_execution_based_matcher_2026-09-05.py", "stale-absolute-path",
     "the same defect with a cost: 5 of 15 exp44 rows were refused, so the "
     "headline 12 of 15 came out 7 of 15 for every reader",
     "_retarget_falsifier rebases a foreign checkout of THIS project onto the "
     "overlay at replay; the containment guard is untouched"),
    ("bench/tests/test_panel_conditions_are_met_2026-09-10.py", "corpus-absent",
     "panel round logs are untracked, so a clone holds 0 seat replies and the "
     "anti-vacuity guard fired",
     "claim and anti-vacuity guard skip TOGETHER with the reason, so neither "
     "can pass vacuously"),
    ("bench/tests/test_derived_docs_match_their_generators_2026-09-01.py",
     "corpus-absent",
     "build_experiment_report.py reads an untracked run log, so it exits "
     "non-zero and the document it backs cannot be re-derived",
     "a FileNotFoundError naming an ABSENT path under a declared archive root "
     "skips; anything else still fails"),
    ("bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py", "cascade",
     "this test runs the real pre-commit hook, which runs the gate, which "
     "contained the corpus-differs failure above",
     "fixed by fixing its cause; no change here"),
    ("bench/tests/test_precommit_gate_cost_2026-09-10.py", "both-trees",
     "the collected count was written twice -- in the entry and as a literal in "
     "the test -- so corrections needed 2 edits and the 5th made 1",
     "the entry carries a machine-readable declaration and the test reads it"),
    ("bench/tests/test_citation_content_2026-09-10.py", "both-trees",
     "notes cite the runner by line number; editing the runner moves every "
     "symbol below the edit, and the guard's own --fix was run by nothing",
     "the hook runs --fix at stage 0, repair before check"),
    ("bench/tests/test_experiment_run_ledger_2026-08-26.py", "both-trees",
     "the ledger is derived and cites the runner by line, so it goes stale on "
     "any runner edit; and a clone holds fewer artefacts than it declares",
     "the ledger declares its corpus, --check tolerates a SMALLER one only, and "
     "the hook refreshes it at stage 0 -- refusing to shrink it"),
    ("bench/tests/test_immune_memory_consumption.py", "both-trees",
     "study_programme_report (task 9.1) reads sk_result to count "
     "threshold_shadow blocks and was not in the allowlist",
     "admitted with the evidence; the R_k assertion that actually holds the "
     "line is unchanged"),
    ("bench/tests/test_panel_cwd_reaches_worker_threads_2026-09-08.py", "both-trees",
     "the guard searched a 400-character window of SOURCE for the worker-mirror "
     "assignment; a comment grew, the window stopped reaching, and it went red "
     "while the wiring was correct",
     "apply_panel_cwd extracted so the guard CALLS it -- execute-do-not-grep -- "
     "plus a reachability check that run_experiment still calls it"),
]


def check() -> int:
    """Re-run every named test HERE, so the census cannot go stale silently."""
    files = sorted({row[0] for row in CENSUS})
    missing = [f for f in files if not (REPO / f).is_file()]
    if missing:
        print(f"census names files that no longer exist: {missing}", file=sys.stderr)
        return 2
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                        "--tb=no", *files], cwd=REPO, capture_output=True,
                       text=True, timeout=3600)
    tail = [ln for ln in r.stdout.splitlines() if "passed" in ln or "failed" in ln]
    print(f"census re-run in {REPO}:")
    print("  " + (tail[-1] if tail else "(no summary line)"))
    for ln in r.stdout.splitlines():
        if ln.startswith("FAILED"):
            print("  " + ln[:150])
    return 0 if r.returncode == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="re-run every test the census names, in this checkout")
    args = ap.parse_args()

    by_cause: dict[str, list] = {}
    for row in CENSUS:
        by_cause.setdefault(row[1], []).append(row)

    print(f"fresh-clone failure census, {len(CENSUS)} test files, "
          f"{len(by_cause)} distinct causes\n")
    for cause, rows in sorted(by_cause.items(), key=lambda kv: -len(kv[1])):
        print(f"{cause}  ({len(rows)} file(s))")
        for f, _c, mech, fix in rows:
            print(f"    {f}")
            print(f"      why : {mech}")
            print(f"      fix : {fix}")
        print()

    n = len(CENSUS)
    clone_only = sum(1 for r in CENSUS if r[1] != "both-trees")
    from statsmodels.stats.proportion import proportion_confint
    lo_w, hi_w = proportion_confint(clone_only, n, method="wilson")
    lo_c, hi_c = proportion_confint(clone_only, n, method="beta")
    from scipy.stats import beta as sbeta
    hi_s = sbeta.ppf(0.975, clone_only + 1, n - clone_only)
    print(f"clone-only failures: {clone_only} of {n} files = {clone_only / n:.4%}")
    print(f"  Wilson 95%          : [{lo_w:.4%}, {hi_w:.4%}]  (statsmodels)")
    print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]  (statsmodels/beta)")
    print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_s:.4%}]  (scipy cross-check, "
          f"upper agrees to {abs(hi_s - hi_c):.1e})")
    print(f"\nthe other {n - clone_only} were red in the MAINTAINER'S tree too, "
          f"which the entry's premise denied.")

    if args.check:
        return check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
