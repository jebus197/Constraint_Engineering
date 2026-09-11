#!/usr/bin/env python3
"""Task A2: RUN the suite in a fresh clone, rather than asserting that it passes.

`measured-rate-travels-with-its-script`. A2's claim is a MEASUREMENT -- "the
suite passes in a fresh clone" -- so the thing that produces it has to be
committed. Until this file, nothing in the repository performed a clone at all.

WHY THAT MATTERED, twice. The claim was made on 2026-09-10 and again on
2026-09-11 and was false both times; each time it was found by a person cloning
by hand. A2's declared evidence,
`bench/tests/test_fresh_clone_suite_2026-09-10.py`, guards the individual
repairs -- the replay rebase, the onboarding stamp, the archive-root predicate --
and never clones anything. `scripts/fresh_clone_census_2026-09-10.py` re-runs
the named tests in THIS checkout, which is the tree whose greenness was never in
doubt. Both instruments were sound and neither could see the claim.

THE 2026-09-11 RESULT, at HEAD d92564e^, which is what prompted this file:

    clone at HEAD   3 failed, 6952 passed, 38 skipped, 1 xfailed
    working tree    6988 passed, 0 failed

The cause was that the pre-commit repairs wrote the working tree and never
staged what they wrote, so every commit shipped the unrepaired content and the
repair lagged 1 commit behind. Fixed in `hooks/stage0_restage.sh`.

WHAT THIS REPORTS THAT A BARE PYTEST RUN DOES NOT: whether the working tree is
CLEAN. A clone measures HEAD. If the tree is dirty, a green clone says nothing
about what the next commit will ship -- which is exactly the gap that hid the
defect above for 2 days. The line is printed either way, never as a warning
buried in a summary.

COST, measured on this machine 2026-09-11: the clone alone is 5.3 s to 6.6 s and
549 MB across 4 variants (`--no-hardlinks` 6.58 s, `--depth 1` 5.27 s, plain
local path with hardlinks 2.98 s at 581 MB). The bulk is the CHECKOUT, not the
history, so `--depth 1` buys almost nothing. The full suite in the clone is
roughly 25 minutes. `--subset` exists so the machinery can be exercised in
seconds by a test; the default is the whole suite, because that is the claim.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: The files that have historically failed ONLY in a clone. Named so `--subset`
#: has a meaningful default beyond "something fast", and so the set is auditable.
CLONE_SENSITIVE = (
    "bench/tests/test_citation_content_2026-09-10.py",
    "bench/tests/test_experiment_run_ledger_2026-08-26.py",
    "bench/tests/test_measurement_survey_is_safe_2026-09-11.py",
    "bench/tests/test_precommit_guard_2026-09-09.py",
    "bench/tests/test_repo_paths_predicate_2026-09-09.py",
    "bench/tests/test_operational_scripts.py",
)

_RESULT_RE = re.compile(
    r"^(?=.*\b\d+ (?:passed|failed|error))(.*\bin [\d.]+s.*)$", re.M)


def working_tree_is_clean(repo: Path = REPO) -> tuple[bool, str]:
    """Is there uncommitted work a clone cannot see?

    NOT `returncode == 0 and not stdout`. `git status` exits 0 on a clean tree
    AND on many failures, and this project has already been bitten by reading an
    empty stdout from a failed git command as "clean" -- exit 128 with no output
    was read as "untracked" in `overstated_entries` 1 round after the identical
    fault was fixed in `orphan_figures`. A non-zero exit is reported as UNKNOWN,
    never as clean.
    """
    r = subprocess.run(["git", "status", "--porcelain"], cwd=repo,
                       capture_output=True, text=True)
    if r.returncode != 0:
        return False, f"UNKNOWN (git status exited {r.returncode}: {r.stderr.strip()})"
    dirty = [ln for ln in r.stdout.splitlines() if ln.strip()]
    if not dirty:
        return True, "clean"
    shown = [ln[3:] for ln in dirty[:6]]
    more = len(dirty) - len(shown)
    # STATE THE REMAINDER. A list cut to 6 under a heading that reads as
    # complete is a silent falsehood; " ..." says there is more and not how
    # much. Held by test_operational_scripts.py::
    # TestTruncatedListsStateTheirRemainder, which caught this the hour it was
    # written.
    tail = f", and {more} more" if more else ""
    return False, f"{len(dirty)} uncommitted path(s): " + ", ".join(shown) + tail


def head(repo: Path = REPO) -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "UNKNOWN"


def run(targets: list[str], keep: bool = False,
        timeout: int = 7200) -> tuple[int, str, str]:
    """Clone HEAD into a temporary directory and run pytest there.

    Returns (pytest exit code, the result line, the clone path).
    """
    tmp = tempfile.mkdtemp(prefix="cdsfl_fresh_clone_")
    dest = Path(tmp) / "clone"
    c = subprocess.run(
        ["git", "clone", "-q", "--no-hardlinks", f"file://{REPO}", str(dest)],
        capture_output=True, text=True, timeout=1800)
    if c.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        raise SystemExit(f"clone failed ({c.returncode}): {c.stderr.strip()}")

    cloned_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=dest,
                                 capture_output=True, text=True).stdout.strip()
    if cloned_head != head():
        shutil.rmtree(tmp, ignore_errors=True)
        raise SystemExit(
            f"the clone is at {cloned_head[:8]} and this tree is at "
            f"{head()[:8]}; refusing to report a measurement of a different "
            f"commit as this one's")

    p = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *targets],
        cwd=dest, capture_output=True, text=True, timeout=timeout)
    blob = (p.stdout or "") + (p.stderr or "")
    m = _RESULT_RE.findall(blob)
    line = m[-1].strip() if m else "(pytest printed no result line)"
    failed = [ln for ln in blob.splitlines() if ln.startswith(("FAILED", "ERROR"))]
    shown, more = failed[:40], max(0, len(failed) - 40)
    if more:
        shown.append(f"... and {more} more FAILED/ERROR line(s) not shown")
    if not keep:
        shutil.rmtree(tmp, ignore_errors=True)
    return p.returncode, line, "\n".join(shown)


def main() -> int:
    # NO `answer_help` HERE, deliberately. This script HAS a parser, and
    # answer_help would intercept `--help` first and print `usage: ... [-h]`,
    # hiding --subset, --only, --keep and --timeout from the reader. The helper
    # exists for scripts with NO parser; using it where argparse already works
    # would make the help text worse, which is the opposite of its purpose.
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--subset", action="store_true",
                    help="run only the historically clone-sensitive files")
    ap.add_argument("--only", action="append", default=[],
                    help="run exactly this test path in the clone (repeatable)")
    ap.add_argument("--keep", action="store_true",
                    help="leave the clone on disk and print its path")
    ap.add_argument("--timeout", type=int, default=7200)
    a = ap.parse_args()

    targets = a.only or (list(CLONE_SENSITIVE) if a.subset else ["bench/tests/"])
    clean, why = working_tree_is_clean()
    print(f"HEAD                : {head()[:8]}")
    print(f"working tree        : {why}")
    if not clean:
        print("  A CLONE MEASURES HEAD. Uncommitted work is not in it, so a green")
        print("  result below says nothing about what the next commit will ship.")
    print(f"running in the clone: {' '.join(targets)}")
    code, line, failures = run(targets, keep=a.keep, timeout=a.timeout)
    print(f"\nfresh clone result  : {line}")
    print(f"pytest exit code    : {code}")
    if failures:
        print("failing:")
        for ln in failures.splitlines():
            print(f"  {ln}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
