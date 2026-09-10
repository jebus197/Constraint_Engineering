#!/usr/bin/env python3
"""Refresh the founder's Desktop copies from the canonical repository files.

WHY THIS EXISTS. The founder reads 4 files from his Desktop and treats them as
current. On 2026-09-10 at 10:30 BST, 2 of the 3 had silently diverged: the master
task list was 29,044 bytes short and 3.45 h behind, the outcomes log 5,016 bytes
short and 3.40 h behind. He asked, that morning, whether the companion file "on
my desktop (which I presume you have been updating)" was current. It was not.

THE SAME FAILURE ALREADY COST HIM A JOURNEY. On 2026-09-09 a restore read a stale
line and told him an answer-key sealing awaited him; he had driven home from his
hotel and done it himself 2 days earlier. Task V5 fixed the ORDERING so the
freshest document is read first. It did not stop a mirror drifting, and the
restore could not even see 2 of the 3 mirrors until this was written.

MIRRORING IS NOT ARCHIVING. These copies are conveniences. The repository copy is
canonical, by founder ruling of 2026-08-05, because an unversioned file on one
machine is a single point of failure. Nothing here ever copies Desktop -> repo.

Run with --check to report drift without writing, which is what a test uses.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DESKTOP = Path.home() / "Desktop"

#: (repository path, Desktop filename) for every mirror the founder reads.
#:
#: PAIRS, NOT NAMES, AND THE SINGLE DECLARATION FOR THE WHOLE PROJECT.
#: This was a tuple of bare NAMES until 2026-09-10, on the stated reasoning that
#: "the mirror must never be renamed: the founder finds these by their name".
#: That reasoning was false at the time it was written. `RUNWAY_to_BR2_2026-08-18.md`
#: declares its own mirror, at its line 229, as `~/Desktop/CDSFL_RUNWAY.md` -- a
#: DIFFERENT name. A names-only structure cannot express a renamed mirror, so the
#: renamed one was simply left out, and a SECOND hand-written table grew up inside
#: `bench/tests/test_documentation_drift_guards_2026-08-25.py` to hold the 2 the
#: guard checked. The 2 tables then disagreed: 4 real mirrors, 3 refreshed here,
#: 2 guarded there, 1 in both. The RUNWAY was GUARDED BY A TEST AND REFRESHED BY
#: NOTHING, and the task list and outcomes log were refreshed by this script and
#: guarded by nothing.
#:
#: HOW THAT SURFACED. On 2026-09-10 the section-R commit edited the RUNWAY, the
#: drift guard went red, and the commit hook exited 1 -- 6 stages BEFORE the stage
#: that refreshes mirrors. The repair sat downstream of the check that needed it,
#: so every future commit touching a mirrored file was refused, permanently, and
#: the master task list is one of the mirrored files.
#:
#: The panel had already named the hand list. `bench/logs/panel_fixes_20260901T123808Z/fable.json`
#: records, on 2026-09-01: "DECLARED_MIRRORS in the drift-guard test is a hand
#: list, while the docs' own text is the truth source". That finding was filed and
#: not acted on for 9 days.
#:
#: EVERY PAIR BELOW IS CONFIRMED BY A DECLARATION IN THE PROJECT'S OWN PROSE, and
#: `test_desktop_mirrors_stay_current_2026-09-10.py` checks that in both
#: directions: no pair here that the documents do not declare, and no document
#: declaring a mirror of itself that is missing from here.
MIRRORS = (
    ("experimental_notes/CDSFL_MASTER_TASK_LIST.md", "CDSFL_MASTER_TASK_LIST.md"),
    ("experimental_notes/CDSFL_OUTCOMES_LOG.md", "CDSFL_OUTCOMES_LOG.md"),
    ("experimental_notes/CDSFL_Agent_Operational_Plan.md", "CDSFL_Agent_Operational_Plan.md"),
    ("experimental_notes/RUNWAY_to_BR2_2026-08-18.md", "CDSFL_RUNWAY.md"),
    # THE 5TH MIRROR, FOUND BY PANEL ROUND 8 (2026-09-10). Declared 3 times in
    # the notes -- operational tracker item C3 says, verbatim, "Mirrored
    # `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md` ->
    # `~/Desktop/CDSFL_Consolidated_Plan_2026-04-21.md`" -- and the Desktop copy
    # EXISTS and IS DIVERGED today (md5 8ad4019e vs b515c9dd; the repo copy
    # carries the 2026-08-05 _suppression.py correction the Desktop never
    # received, per Document_Estate_Audit_2026-08-06.md:421, which also records
    # the document as CORE / KEEP_AND_CONVERT, i.e. still a live instruction).
    # It escaped the 2026-09-10 sweep because the reverse-direction regex
    # required the `~/Desktop/` path within 20 non-backtick characters of the
    # word "mirror", and the C3 phrasing puts the REPO path there first. It is
    # a RENAMED mirror, so the old names-only table could never have held it.
    ("experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md",
     "CDSFL_Consolidated_Plan_2026-04-21.md"),
)

#: Retained so any existing reader keeps working, and DERIVED so it can never
#: again disagree with the table it summarises.
MIRRORED = tuple(desktop_name for _, desktop_name in MIRRORS)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def drift() -> list[tuple[str, str, int]]:
    """(Desktop name, reason, byte difference) for every mirror not current."""
    out = []
    for repo_rel, desktop_name in MIRRORS:
        src, dst = REPO / repo_rel, DESKTOP / desktop_name
        if not src.is_file():
            out.append((desktop_name, "the canonical file does not exist", 0))
            continue
        if not dst.is_file():
            out.append((desktop_name, "no Desktop copy exists at all",
                        src.stat().st_size))
            continue
        if _sha(src) != _sha(dst):
            out.append((desktop_name, "diverged",
                        src.stat().st_size - dst.stat().st_size))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report drift and exit 1 if any; write nothing")
    a = ap.parse_args()

    bad = drift()
    if a.check:
        for name, why, delta in bad:
            print(f"  {name}: {why}"
                  + (f", canonical is {delta:+,} bytes" if delta else ""))
        print(f"  {len(bad)} of {len(MIRRORED)} Desktop copies are not current")
        return 1 if bad else 0

    if not DESKTOP.is_dir():
        print("  no Desktop directory on this machine; nothing to mirror")
        return 0
    by_desktop_name = {d: r for r, d in MIRRORS}
    for name, why, _ in bad:
        src, dst = REPO / by_desktop_name[name], DESKTOP / name
        if not src.is_file():
            print(f"  SKIPPED {name}: {why}")
            continue
        shutil.copy2(src, dst)
        # VERIFIED, not assumed. A copy that silently failed would leave the
        # founder reading a stale file believing it had just been refreshed,
        # which is the exact defect this script exists to end.
        assert _sha(src) == _sha(dst), f"{name} did not copy identically"
        print(f"  refreshed {name} ({why})")
    if not bad:
        print(f"  all {len(MIRRORED)} Desktop copies were already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
