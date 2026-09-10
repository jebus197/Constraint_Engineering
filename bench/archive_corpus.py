"""Which archived artefacts this checkout actually holds, and what to do when it does not.

WHY THIS EXISTS, task A2, 2026-09-10. `.gitignore:41` excludes `bench/logs/**`
apart from a small allow-list of report shapes, BY DESIGN -- the archive was 353
MB across 5,840 files before that rule. So the maintainer's working tree and a
fresh `git clone` hold different corpora: 6,770 JSON files against 6,160 tracked,
and whole families (`sim45_*`, `panel_round*`) are absent from a clone entirely.

A test that measures over the archive therefore has 3 possible states, and
collapsing them is what made the suite red for every reader:

  the artefacts are HERE and agree      -> pass
  the artefacts are HERE and disagree   -> FAIL. This is the defect the test
                                           exists for and nothing here softens it.
  the artefacts are NOT HERE            -> the test cannot run. Say so, name what
                                           is missing and why, and skip.

THE THIRD STATE MUST NEVER BE REACHED BY A TEST THAT COULD HAVE RUN. `shortfall`
compares against a DECLARED population, so a checkout that holds the artefacts
and disagrees with them still fails. A test that skips whenever it is unhappy is
not a test, and this project has found 8 of its own guards vacuous that way.

AND A SKIP MUST BE LOUD. pytest reports skips with their reason; a reader who
runs the suite sees "the panel round logs are not committed, so the no-paid-seat
claim cannot be verified from this checkout", which is a true and useful
statement about what the repository can and cannot prove about itself.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: The line of .gitignore that does the excluding, quoted in every skip reason so
#: a reader can go and look rather than take the message on trust.
IGNORE_RULE = ".gitignore:41 (`bench/logs/**`, with an allow-list for reports)"


def tracked_under(directory: Path) -> set[Path] | None:
    """The git-tracked files under `directory`, or None if git cannot answer."""
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--", "."],
                             cwd=directory, capture_output=True, text=True,
                             timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return {(directory / rel).resolve() for rel in out.stdout.split("\0") if rel}


def untracked_archive_files() -> int:
    """How many archive files this checkout holds that a clone would not.

    0 means this checkout IS what a reader gets, which is the useful thing to
    know before quoting any archive-derived figure.
    """
    if not LOGS.is_dir():
        return 0
    tracked = tracked_under(LOGS)
    if tracked is None:
        return 0
    return len({p.resolve() for p in LOGS.rglob("*") if p.is_file()} - tracked)


def shortfall(observed: int, needed: int, what: str) -> str | None:
    """A skip reason when this checkout holds too few artefacts, else None.

    `needed` is the population the test was WRITTEN against. Passing the same
    number the test asserts on would make this a tautology; it must be the
    minimum at which the measurement means anything.
    """
    if observed >= needed:
        return None
    return (f"this checkout holds {observed} {what}, and the measurement needs "
            f"at least {needed}. Most of bench/logs/ is excluded by "
            f"{IGNORE_RULE}, so a clone legitimately sees fewer. The claim is "
            f"NOT verified here and is NOT reported as passing.")


def missing(paths: Iterable[Path], what: str) -> str | None:
    """A skip reason when named artefacts are absent from this checkout."""
    gone = [str(p.relative_to(REPO)) if str(p).startswith(str(REPO)) else str(p)
            for p in paths if not p.exists()]
    if not gone:
        return None
    return (f"{what} needs artefacts this checkout does not hold: {gone}. "
            f"Excluded by {IGNORE_RULE}.")
