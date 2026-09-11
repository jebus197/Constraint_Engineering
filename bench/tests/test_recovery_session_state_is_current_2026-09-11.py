"""Task A23: RECOVERY.md's newest SESSION STATE must not fall behind the commits.

WHY THIS MATTERS MORE THAN TIDINESS. After a compaction the assistant reads
`resources/RECOVERY.md` as its picture of where the project is. On 2026-09-11 the
newest block was dated 2026-09-08 and named HEAD `beb39fb`, while HEAD was 3 days
and dozens of commits past it -- so the picture omitted the whole task-list
clearance arc, the fresh-clone work and 2 panel rounds. `rs` surfaced it.

AND "RUN SV" WOULD NOT HAVE FIXED IT. `scripts/cdsfl_sv.py --dry-run` reports
"Preserved manual content" for RECOVERY.md: it updates a timestamp and
DELIBERATELY does not regenerate the hand-written SESSION STATE block, flagging
the stamp so it says the body was preserved rather than implying freshness. The
entry that said "to be closed by the next sv" was wrong about the mechanism. The
block is written by hand, so a guard is the only thing that can notice it rotting.

WHAT THIS CHECKS, and what it deliberately does not. It checks that the newest
block names a commit reachable from HEAD and is not absurdly old. It does NOT
check the prose: no test can tell whether a recovery narrative is a good one, and
pretending otherwise would be a guard that fires on style.
"""
from __future__ import annotations

import datetime
import pathlib
import re
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RECOVERY = ROOT / "resources" / "RECOVERY.md"

#: How far behind HEAD the newest block may fall before it misleads a reader.
#: Generous on purpose: this is a rot detector, not a commit-by-commit ratchet.
MAX_COMMITS_BEHIND = 60


def _newest_block() -> tuple[str, str]:
    text = RECOVERY.read_text(encoding="utf-8")
    m = re.search(r"^## SESSION STATE — (.+?)\s*\(READ THIS FIRST\)\s*$",
                  text, re.M)
    assert m, "RECOVERY.md carries no SESSION STATE heading at all"
    start = m.end()
    nxt = re.search(r"^## SESSION STATE — ", text[start:], re.M)
    return m.group(1), text[start:start + (nxt.start() if nxt else len(text))]


class TestTheNewestBlockIsCurrent:
    def test_it_names_a_commit_reachable_from_head(self):
        _when, body = _newest_block()
        shas = re.findall(r"`([0-9a-f]{7,40})`", body)
        assert shas, "the newest SESSION STATE names no commit at all"
        reachable = []
        for sha in shas[:4]:
            r = subprocess.run(["git", "merge-base", "--is-ancestor", sha, "HEAD"],
                               cwd=ROOT, capture_output=True)
            reachable.append(r.returncode == 0)
        assert any(reachable), (
            f"none of the commits the newest SESSION STATE names ({shas[:4]}) is "
            f"an ancestor of HEAD; the block describes a tree that is not this "
            f"one")

    def test_it_is_not_far_behind_head(self):
        _when, body = _newest_block()
        shas = re.findall(r"`([0-9a-f]{7,40})`", body)
        best = None
        for sha in shas[:4]:
            r = subprocess.run(["git", "rev-list", "--count", f"{sha}..HEAD"],
                               cwd=ROOT, capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip().isdigit():
                n = int(r.stdout.strip())
                best = n if best is None else min(best, n)
        if best is None:
            pytest.skip("no commit in the newest block resolves in this clone")
        assert best <= MAX_COMMITS_BEHIND, (
            f"the newest SESSION STATE is {best} commits behind HEAD. After a "
            f"compaction this file IS the project's picture of itself; write a "
            f"new block rather than raising this number. Note that "
            f"`scripts/cdsfl_sv.py` deliberately PRESERVES this block and will "
            f"not write it for you.")

    def test_its_date_is_not_absurdly_old(self):
        when, _body = _newest_block()
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", when)
        assert m, f"the heading date is unparseable: {when!r}"
        d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        age = (datetime.date.today() - d).days
        assert age <= 21, (
            f"the newest SESSION STATE is {age} days old. This is the file a "
            f"post-compaction reader trusts most.")


class TestTheCheckIsNotVacuous:
    def test_there_is_more_than_one_block(self):
        """The file is a RECORD: older blocks are kept deliberately. If there
        were only one, 'newest' would be measuring nothing."""
        n = len(re.findall(r"^## SESSION STATE — ", RECOVERY.read_text(), re.M))
        assert n >= 3, f"only {n} SESSION STATE block(s); the history is gone"

    def test_the_newest_block_is_the_first_one(self):
        """Newest-first is the file's own convention and the reason the heading
        says READ THIS FIRST. If it ever became oldest-first, every assertion
        above would silently be about the wrong block."""
        text = RECOVERY.read_text(encoding="utf-8")
        dates = re.findall(r"^## SESSION STATE — (\d{4}-\d{2}-\d{2})", text, re.M)
        assert dates == sorted(dates, reverse=True), (
            f"SESSION STATE blocks are no longer newest-first: {dates[:5]}")
