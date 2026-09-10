#!/usr/bin/env python3
"""Refresh the founder's Desktop copies from the canonical repository files.

WHY THIS EXISTS. The founder reads 3 files from his Desktop and treats them as
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

#: canonical filename -> the same name on the Desktop. Kept as a list of names
#: rather than pairs because the mirror must never be renamed: the founder finds
#: these by their name.
MIRRORED = (
    "CDSFL_MASTER_TASK_LIST.md",
    "CDSFL_OUTCOMES_LOG.md",
    "CDSFL_Agent_Operational_Plan.md",
)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def drift() -> list[tuple[str, str, int]]:
    """(name, reason, byte difference) for every mirror that is not current."""
    out = []
    for name in MIRRORED:
        src, dst = REPO / "experimental_notes" / name, DESKTOP / name
        if not src.is_file():
            out.append((name, "the canonical file does not exist", 0))
            continue
        if not dst.is_file():
            out.append((name, "no Desktop copy exists at all", src.stat().st_size))
            continue
        if _sha(src) != _sha(dst):
            out.append((name, "diverged", src.stat().st_size - dst.stat().st_size))
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
    for name, why, _ in bad:
        src, dst = REPO / "experimental_notes" / name, DESKTOP / name
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
