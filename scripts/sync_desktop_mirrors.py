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


#: Every root a clone or a scratch fixture plausibly lives under. A SET, because
#: `tempfile.gettempdir()` alone is environment-dependent: with `TMPDIR` unset it
#: returns `/tmp`, and a clone under `/var/folders` then escapes the rule
#: entirely. Panel round 15, fable, verified by subprocess.
SCRATCH_ROOTS = ("/tmp", "/private/tmp", "/var/tmp", "/private/var/tmp",
                 "/var/folders", "/private/var/folders", "/dev/shm")

#: Names the checkout allowed to write this Desktop. Lives ON the Desktop,
#: because the Desktop is the resource being protected and it is the only place
#: a clone does not carry a copy of.
MARKER = ".cdsfl_canonical_checkout"


def scratch_roots() -> list[Path]:
    """Resolved scratch roots, including whatever TMPDIR currently says."""
    out = []
    for r in (tempfile.gettempdir(), *SCRATCH_ROOTS):
        try:
            rp = Path(r).resolve()
        except OSError:
            continue
        if rp not in out:
            out.append(rp)
    return out


def _under(path: Path, roots: list[Path]) -> Path | None:
    try:
        rp = path.resolve()
    except OSError:
        return None
    for root in roots:
        if rp == root or root in rp.parents:
            return root
    return None


def refuse_reason_for(desktop: Path, passwd_desktop: Path, passwd_reliable: bool,
                      repo: Path, under_pytest: bool, roots: list[Path],
                      canonical: str | None) -> str | None:
    """The whole decision, with every input explicit. None means "may write".

    A PURE FUNCTION BECAUSE THE FIRST VERSION COULD NOT BE TESTED WHERE IT
    MATTERED. It read `os.environ`, `Path.home()` and the passwd database
    directly, so `sudo`, a passwd-less container and a clone outside the scratch
    tree were all unreachable from a test -- and all 3 were live holes. Panel
    round 15 found them by executing the guard, not by reading it.

    THE DRILL EXEMPTION NOW REQUIRES DISPLACEMENT **TO SCRATCH**, not mere
    difference. The old rule said "if DESKTOP is not the passwd user's Desktop,
    this is a drill" -- and under `sudo` macOS keeps `$HOME` while `getuid()`
    becomes 0, so `passwd_desktop` becomes `/var/root/Desktop`, the paths differ,
    and the guard turned ITSELF OFF on the highest-privilege run there is. It
    failed OPEN, which is the worse direction: a clone gets through. Both seats
    found this independently and both rated it the sharpest of the round.

    UNRELIABLE IDENTIFICATION NOW FAILS CLOSED. If the passwd entry cannot be
    read at all, the old code fell back to `Path.home()` and carried on; now the
    drill exemption is withheld, so the other rules still apply.
    """
    in_scratch_desktop = _under(desktop, roots) is not None
    if in_scratch_desktop:
        return None  # displaced to scratch: a drill, and drills must still run
    if not passwd_reliable:
        # FAILS CLOSED, AND THE DOCSTRING SAID SO BEFORE THE CODE DID. The first
        # version only WITHHELD the drill exemption when identification was
        # unreliable and then carried on to return None -- so the claim "fails
        # closed" was true of the prose and not of the behaviour. Panel round 15
        # (cc2) supplied the case that exposed it.
        #
        # UNCONDITIONAL, and the weaker version is the one to argue against.
        # An earlier draft refused only when the Desktop ALSO named no canonical
        # checkout, on the reasoning that a marker is positive evidence
        # independent of the passwd database. That is true, and it is still the
        # wrong trade for a guard whose failure destroyed a file: failing closed
        # here costs a printed refusal on a platform the founder does not use,
        # and failing open costs the file. The seat's stricter rule is adopted
        # over my own weaker one for that reason.
        return ("the user cannot be identified from the passwd database, so "
                "nothing establishes that this writer is the founder's own")
    if passwd_reliable and desktop.resolve() != passwd_desktop.resolve():
        # Different, but NOT displaced to scratch. Under the old rule this
        # returned None. It is now only a reason to keep checking.
        pass
    if under_pytest:
        return ("a test is running and DESKTOP is a real Desktop; a suite must "
                "never rewrite the files the founder reads")
    root = _under(repo, roots)
    if root is not None:
        return (f"the source repository is under {root}, so it is a clone or a "
                f"scratch fixture and not the founder's checkout")
    if canonical is not None:
        try:
            here = str(repo.resolve())
        except OSError:
            here = str(repo)
        if canonical != here:
            return (f"this Desktop is registered to {canonical}, and this "
                    f"checkout is {here}; a second checkout may not overwrite "
                    f"the mirrors of the first")
    return None


def real_desktop() -> Path:
    """The founder's actual Desktop, read from the passwd database, not `$HOME`.

    `Path.home()` honours `$HOME`, and the drills set `$HOME` to a temporary
    directory on purpose, so comparing against it cannot tell a drill from an
    escape. The passwd entry does not move.

    THIS IS NO LONGER THE WHOLE TEST. See `refuse_reason_for`: under `sudo` the
    passwd entry moves to root's and the mismatch meant "drill", which turned the
    guard off. Displacement TO SCRATCH is the test now; this stays because
    knowing the passwd Desktop is still useful, and `passwd_reliable` reports
    whether it could be read at all.
    """
    return _passwd_desktop()[0]


def _passwd_desktop() -> tuple[Path, bool]:
    """(Desktop from the passwd database, whether it could be read)."""
    try:
        import pwd
        return Path(pwd.getpwuid(os.getuid()).pw_dir) / "Desktop", True
    except (ImportError, KeyError, OSError):
        return Path.home() / "Desktop", False


def preserve_before_overwrite(dst: Path) -> Path | None:
    """Keep the bytes about to be replaced. Returns where they went, or None.

    ADOPTED FROM PANEL ROUND 15 (cc2), AND IT IS THE ONLY RULE HERE ABOUT BYTES
    RATHER THAN PATHS -- which is why it is right in every case a path rule gets
    wrong. `refuse_reason_for` decides whether a writer is legitimate by
    reasoning about where it lives, and every hole found in it so far has been a
    location it did not anticipate: a privileged run, a relocated scratch root, a
    clone in a home directory. This rule does not care where the writer is. If
    the bytes differ, the old ones are kept.

    That converts the one hole still open -- a Desktop with no marker, written by
    a clone outside the scratch tree -- from SILENT LOSS into something
    recoverable, which is the difference that mattered on 2026-09-11: the founder
    got his file back only because the repository copy happened to be canonical
    and a later commit happened to restore it.

    ONE SLOT, NOT A HISTORY. The copy goes to a single hidden name per mirror and
    is replaced each time. An unbounded set of dated backups accumulating on his
    Desktop would be a second defect, and git already holds the history; this
    exists to survive the minutes between a bad write and noticing it.

    DOT-PREFIXED AND NOT MATCHING `CDSFL_*`, deliberately: cc2's own refutation
    condition for this rule was that a Desktop tool globbing `CDSFL_*.md` might
    pick the preserved copy up and show it as a real document.
    """
    if not dst.is_file():
        return None
    keep = dst.parent / f".cdsfl-superseded-{dst.name}"
    try:
        shutil.copy2(dst, keep)
    except OSError:
        return None
    return keep


def registered_checkout(desktop: Path) -> str | None:
    """The checkout this Desktop is registered to, or None."""
    try:
        t = (desktop / MARKER).read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return t or None


def refuse_reason() -> str | None:
    """Why this run must NOT write the founder's real Desktop, or None.

    MEASURED 2026-09-11, and this is not hypothetical. A full-suite run in a
    fresh clone overwrote `~/Desktop/CDSFL_OUTCOMES_LOG.md` with the clone's own
    older copy -- 27,669 bytes over 34,082, a 6,413-byte loss of the file the
    founder actually reads. Attributed by running each of 43 candidate test files
    under a fake HOME holding sentinels: exactly 1 rewrote them.

    A thin wrapper over `refuse_reason_for`, which holds the reasoning.
    """
    passwd, reliable = _passwd_desktop()
    return refuse_reason_for(
        desktop=DESKTOP, passwd_desktop=passwd, passwd_reliable=reliable,
        repo=REPO, under_pytest=bool(os.environ.get("PYTEST_CURRENT_TEST")),
        roots=scratch_roots(), canonical=registered_checkout(DESKTOP))


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
    ap.add_argument("--register-canonical", action="store_true",
                    help="record THIS checkout as the one allowed to write the "
                         "Desktop mirrors; refuses from a scratch clone")
    a = ap.parse_args()

    if a.register_canonical:
        # A SCRATCH CLONE MAY NOT CLAIM OWNERSHIP. Without this the mechanism
        # inverts: the clone that caused the incident registers itself and then
        # refuses the founder's own checkout, which is the worse direction.
        if _under(REPO, scratch_roots()) is not None:
            print(f"  REFUSED: {REPO} is under a scratch root; a clone may not "
                  f"register itself as the canonical checkout", file=sys.stderr)
            return 4
        if not DESKTOP.is_dir():
            print("  no Desktop directory on this machine; nothing to register")
            return 0
        (DESKTOP / MARKER).write_text(str(REPO.resolve()) + "\n", encoding="utf-8")
        print(f"  registered {REPO.resolve()} as the canonical checkout for "
              f"{DESKTOP}")
        return 0

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
        kept = preserve_before_overwrite(dst)
        shutil.copy2(src, dst)
        # VERIFIED, not assumed. A copy that silently failed would leave the
        # founder reading a stale file believing it had just been refreshed,
        # which is the exact defect this script exists to end.
        assert _sha(src) == _sha(dst), f"{name} did not copy identically"
        print(f"  refreshed {name} ({why})"
              + (f"; superseded bytes kept at {kept.name}" if kept else ""))
    if not bad:
        print(f"  all {len(MIRRORED)} Desktop copies were already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
