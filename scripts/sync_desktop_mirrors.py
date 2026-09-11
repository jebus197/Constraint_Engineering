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
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DESKTOP = Path.home() / "Desktop"


def real_desktop() -> Path:
    """The founder's ACTUAL Desktop, read from the passwd database, not `$HOME`.

    `Path.home()` honours `$HOME`, and the drills in
    `test_desktop_mirrors_stay_current_2026-09-10.py` set `$HOME` to a temporary
    directory on purpose -- so comparing `DESKTOP` against `Path.home()` cannot
    tell a drill from an escape: under a faked `$HOME` they are the same path.
    Keying on the passwd entry separates them, because a drill cannot move it.

    This is the difference between asking "is this the Desktop?" and asking "is
    this HIS Desktop?", and only the second question is the one that matters.
    """
    try:
        import pwd
        return Path(pwd.getpwuid(os.getuid()).pw_dir) / "Desktop"
    except (ImportError, KeyError, OSError):
        return Path.home() / "Desktop"


def refuse_reason() -> str | None:
    """Why this run must NOT write the founder's real Desktop, or None if it may.

    MEASURED 2026-09-11, and this is not a hypothetical. A full-suite run in a
    fresh clone overwrote `~/Desktop/CDSFL_OUTCOMES_LOG.md` with the clone's own
    older copy -- 27,669 bytes over 34,082, a 6,413-byte loss of the file the
    founder actually reads. `scripts/cdsfl_recover.py` reported the divergence 13
    minutes later and the pre-commit mirror refresh put it back, so nothing was
    lost permanently; that was luck, not design. Attributed by running each of 43
    candidate test files under a fake HOME holding sentinels:
    `bench/tests/test_precommit_guard_2026-09-09.py` wrote all 5 mirrors.

    THE CAUSE IS THAT `DESKTOP` IS ABSOLUTE AND `REPO` IS NOT. A scratch fixture
    or a clone moves `REPO` and leaves `DESKTOP` pointing at the one real
    Desktop, so the wrong source is copied over the right destination. This is
    the same shape as task A2: a path that escapes its sandbox because it was
    never relative to it.

    2 INDEPENDENT RULES, AND BOTH ARE NEEDED -- also measured. The environment
    IS inherited through `git` into the hook, so the pytest rule fires for an
    ordinary hook test; but `test_precommit_guard`'s own `test_no_python3` builds
    a PATH with only `git` in it, so a rule that depended on the interpreter
    seeing pytest would miss other shapes. The temp-root rule catches any clone,
    whether or not a test is running.

    A DRILL THAT POINTS `DESKTOP` SOMEWHERE ELSE IS NEVER REFUSED. The existing
    tests that monkeypatch `DESKTOP` or set a fake HOME still exercise every line
    of the copy path -- refusing those would make this guard a disabled feature
    rather than a scoped one.
    """
    if DESKTOP.resolve() != real_desktop().resolve():
        return None  # pointed at a fake: a drill, and drills must still run
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return ("a test is running and DESKTOP is the founder's real one; a "
                "suite must never rewrite the files he reads")
    try:
        tmp = Path(tempfile.gettempdir()).resolve()
        repo = REPO.resolve()
        if repo == tmp or tmp in repo.parents:
            return (f"the source repository is under {tmp}, so it is a clone or "
                    f"a scratch fixture and not the founder's checkout")
    except OSError:
        pass
    return None


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

    refused = refuse_reason()
    if refused is not None:
        # LOUD, AND EXIT 0. The commit this hook runs inside is legitimate; it is
        # only the mirroring that is wrong here. Failing the commit would turn a
        # correct refusal into a broken clone.
        print(f"  REFUSED to refresh the Desktop mirrors: {refused}")
        return 0
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
