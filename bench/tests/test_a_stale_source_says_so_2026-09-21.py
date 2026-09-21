"""A canonical source that has gone stale must SAY SO, in the file, at the top.

THE DEFECT THIS CLOSES, AND IT IS THE FOUNDER'S OWN COMPLAINT. On 2026-09-21 he
wrote: *"You have a habit of asking me more than once about the same things.
Sometimes multiple times. And each time I give you an answer, you forget."*

He is right, and the cause is not memory. It is measured, and the project already
diagnosed it on 2026-09-09: *"A source written before a founder message cannot
record what he said in it. That is the mechanism by which a decision he HAS made
keeps reappearing as one he has not. The defect is in the write-back, not in his
answering."* `scripts/decision_label_staleness_2026-09-09.py` reports **5 of 5**
canonical sources in that condition, 100.0%, Wilson [56.6%, 100.0%].

The script was written on 2026-09-09 and the write-back still had not happened
12 days later. THAT is why a checker is not enough: a script nobody runs is the
same as no script. This test runs it.

WHAT IT REQUIRES, AND WHY IT IS THE WEAK FORM ON PURPOSE. Not that sources be
fresh -- freshness cannot be legislated, and an old document is often exactly
right. Only that a source which has gone stale CARRIES A BANNER saying what
supersedes it, so a reader (human or agent) cannot mistake history for current
state. That is the difference between the 2 documents this session tripped over:
`RUNWAY_to_BR2_2026-08-18.md` carries a dated status banner and was read
correctly; `OUTSTANDING_QUEUE_to_BR2.md` carried none and was 29 days stale.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "decision_label_staleness_2026-09-09.py"

#: A source is allowed to be old. It is not allowed to be old and SILENT.
#: These phrases, in the first 40 lines, count as saying so.
BANNER = re.compile(
    r"supersede|out of date|do not read this as current|"
    r"★ ?status|kept as history|read it as history|not current truth|"
    r"canonical state is|the current work list is",
    re.I,
)

#: How many days before a source owes a banner. Chosen to sit well above the
#: normal update rhythm: `RECOVERY.md` and the task list are rewritten most days,
#: so this only bites on genuinely abandoned documents.
STALE_DAYS = 14


def _staleness_module():
    spec = importlib.util.spec_from_file_location("staleness", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_the_staleness_script_still_exists_and_imports():
    """A checker nobody can run is the shape this test exists to prevent."""
    assert SCRIPT.is_file(), f"the staleness checker is gone: {SCRIPT}"
    _staleness_module()


def _sources():
    """The canonical sources, taken from the script rather than re-listed here.

    Re-listing them is how 2 copies drift apart, which is the defect class
    `execute-do-not-grep` names. If the script's list changes, this test follows.
    """
    m = _staleness_module()
    for attr in ("SOURCES", "CANONICAL", "PATHS", "FILES"):
        if hasattr(m, attr):
            return [REPO / str(p) for p in getattr(m, attr)]
    pytest.skip("the staleness script exposes no source list to import")


def test_every_stale_canonical_source_carries_a_supersession_banner():
    """Old is fine. Old and silent is not."""
    import subprocess
    silent = []
    for path in _sources():
        if not path.is_file():
            continue
        # age from git, not the filesystem: a checkout resets mtimes
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(path.relative_to(REPO))],
            cwd=REPO, capture_output=True, text=True).stdout.strip()
        if not out:
            continue
        import time
        age_days = (time.time() - int(out)) / 86400
        if age_days < STALE_DAYS:
            continue
        head = "\n".join(path.read_text(errors="replace").splitlines()[:40])
        if not BANNER.search(head):
            silent.append(f"{path.relative_to(REPO)} ({age_days:.0f}d, no banner)")
    assert not silent, (
        "these canonical sources are stale and say nothing about it, so a reader "
        "will take them for current state — the exact mechanism by which a "
        "settled decision keeps being re-asked:\n  " + "\n  ".join(silent))


def test_the_banner_check_can_actually_fail(tmp_path):
    """A guard that cannot fail is not a guard.

    Executed against a fabricated stale-and-silent file rather than asserted.
    """
    silent = tmp_path / "silent.md"
    silent.write_text("# A document\n\nNo banner anywhere in this file.\n")
    head = "\n".join(silent.read_text().splitlines()[:40])
    assert not BANNER.search(head), "the pattern matched a file with no banner"

    loud = tmp_path / "loud.md"
    loud.write_text("# A document\n\n> ## SUPERSEDED — do not read this as "
                    "current state\n\nThe current work list is elsewhere.\n")
    head2 = "\n".join(loud.read_text().splitlines()[:40])
    assert BANNER.search(head2), "the pattern missed a real banner"


def test_the_queue_that_prompted_this_now_carries_one():
    """The specific file that was 29 days stale and silent on 2026-09-21."""
    q = REPO / "experimental_notes" / "OUTSTANDING_QUEUE_to_BR2.md"
    if not q.is_file():
        pytest.skip("the queue file has been retired")
    head = "\n".join(q.read_text(errors="replace").splitlines()[:40])
    assert BANNER.search(head), (
        "OUTSTANDING_QUEUE_to_BR2.md is the file whose 29-day silence caused a "
        "settled decision to be re-asked; it must say what supersedes it")
