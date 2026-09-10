"""The restore must read the FRESHER document first, and say how stale the rest are.

Task V5. WHY IT EXISTS, and it cost the founder a drive home.

On 2026-09-09 at 23:00 an assistant ran `rs`. The recovery script's FIRST READ
section named `experimental_notes/CDSFL_Agent_Operational_Plan.md` first, and a
line there said the answer-key sealing still awaited the founder. It did not: he
had driven back from his hotel and done it himself on 2026-09-07 at 22:03, 53
files into 1 archive, at the assistant's own request. The assistant read the
stale line and reported it back to him.

**THE CORRECT RECORD ALREADY EXISTED.** `CDSFL_MASTER_TASK_LIST.md`, written
2026-09-09 14:15, states both that he executed it AND that the tracker was stale
on it. That file was not in the FIRST READ section at all. So the restore read
the older document first, treated it as authoritative, and never offered the
newer one.

`OUTSTANDING_QUEUE_to_BR2.md` is the standing example rather than a
hypothetical: it was labelled the "live work queue" while 14 days old, with every
one of the founder's messages since arriving after it was last written. A
document written before he spoke cannot record what he said.
"""

import importlib.util
import os
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "rec", REPO / "scripts" / "cdsfl_recover.py")
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


@pytest.fixture
def lines():
    return R.first_read_lines(REPO)


def test_the_section_is_not_empty(lines):
    assert lines and any("last modified" in l for l in lines)


def test_the_master_task_list_is_offered_at_all(lines):
    """It was absent, which is why the correct record was never reached."""
    joined = "\n".join(lines)
    assert "CDSFL_MASTER_TASK_LIST.md" in joined, (
        "the canonical standing work list is not in FIRST READ, so a restore "
        "cannot reach the freshest record of what has been done")


def test_the_outcomes_companion_is_offered(lines):
    assert "CDSFL_OUTCOMES_LOG.md" in "\n".join(lines)


def test_the_entries_are_ordered_newest_first(lines):
    """THE PROPERTY. Order is the whole fix: the reader takes the first one."""
    stamps = []
    for i, l in enumerate(lines):
        if "last modified" in l:
            stamps.append(l.split("last modified")[1].split("   <--")[0].strip())
    assert len(stamps) >= 3, f"only {len(stamps)} dated entries"
    assert stamps == sorted(stamps, reverse=True), (
        f"FIRST READ is not ordered newest first: {stamps}")


def test_a_stale_entry_is_labelled_with_its_age(lines):
    """A reader must be told which document is old, not left to check mtimes."""
    joined = "\n".join(lines)
    assert "older than the newest above" in joined, (
        "no staleness is reported, so a 14-day-old file reads exactly like a "
        "fresh one")


def test_the_rule_for_a_disagreement_is_stated(lines):
    """The sealing error was a disagreement resolved the wrong way."""
    joined = " ".join(" ".join(lines).split())
    assert "the fresher one wins" in joined, joined[:300]
    assert "A stale document is not a second opinion" in joined


def test_a_deliberately_stale_file_is_flagged_in_days(tmp_path, monkeypatch):
    """EXECUTED against a real spread rather than asserted from the live tree.

    Builds a tree where one required file is 20 days old and checks the section
    both orders it last and names the gap in days."""
    notes = tmp_path / "experimental_notes"
    notes.mkdir()
    names = ["CDSFL_MASTER_TASK_LIST.md", "CDSFL_OUTCOMES_LOG.md",
             "CDSFL_Agent_Operational_Plan.md", "OUTSTANDING_QUEUE_to_BR2.md"]
    now = time.time()
    for n in names:
        p = notes / n
        p.write_text("x", encoding="utf-8")
        age = 20 * 86400 if n == "OUTSTANDING_QUEUE_to_BR2.md" else 0
        os.utime(p, (now - age, now - age))
    out = "\n".join(R.first_read_lines(tmp_path))
    assert "20.0 DAYS older" in out, out
    idx_fresh = out.index("CDSFL_MASTER_TASK_LIST.md")
    idx_stale = out.index("OUTSTANDING_QUEUE_to_BR2.md")
    assert idx_fresh < idx_stale, "the 20-day-old file was not ordered last"


def test_the_sort_is_load_bearing_when_declaration_order_disagrees(tmp_path):
    """THE TEST THAT ACTUALLY CATCHES A REMOVED SORT.

    Every other ordering test here passed with the sort replaced by `pass`,
    because the DECLARED order in `targets` happens to list the task list first
    and the task list happens to be newest. A fixture in which the two orders
    COINCIDE cannot tell a sorted list from an unsorted one — the same shape as
    the vacuous fixtures found 3 times earlier in this session.

    So this inverts them: the tracker is made newest and the task list oldest,
    against a declaration order that lists the task list first. Only a real sort
    puts the tracker on top."""
    notes = tmp_path / "experimental_notes"
    notes.mkdir()
    now = time.time()
    ages = {                                   # seconds old
        "CDSFL_MASTER_TASK_LIST.md": 10 * 86400,      # declared 1st, OLDEST
        "CDSFL_OUTCOMES_LOG.md": 8 * 86400,
        "CDSFL_Agent_Operational_Plan.md": 0,         # declared 3rd, NEWEST
        "OUTSTANDING_QUEUE_to_BR2.md": 5 * 86400,
    }
    for n, age in ages.items():
        p_ = notes / n
        p_.write_text("x", encoding="utf-8")
        os.utime(p_, (now - age, now - age))

    out = "\n".join(R.first_read_lines(tmp_path))
    i_tracker = out.index("CDSFL_Agent_Operational_Plan.md")
    i_list = out.index("CDSFL_MASTER_TASK_LIST.md")
    assert i_tracker < i_list, (
        "the freshest file was not put first when the declaration order "
        "disagreed with modification time — the sort is not doing anything")
    assert "10.0 DAYS older" in out, out


def test_a_missing_required_file_is_still_named_loudly(tmp_path):
    """Ordering must not swallow an absent file — it is reported, not skipped."""
    (tmp_path / "experimental_notes").mkdir()
    (tmp_path / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md").write_text("x")
    out = "\n".join(R.first_read_lines(tmp_path))
    assert "MISSING" in out and "REQUIRED reading and is absent" in out


# ---------------------------------------------------------------------------
# HERMETICITY — added 2026-09-10 after panel round 4 (fable, F2).
#
# The finding: `first_read_lines` built the Desktop mirror's path inline with
# `Path.home() / "Desktop" / ...`, so every `tmp_path` fixture above silently
# included the LIVE machine's Desktop file. fable found it exists on this machine
# with mtime 2026-09-09 23:39. No false-PASS path was demonstrated -- the
# declaration-order fixture defeats a removed sort regardless -- but a mirror
# with a future mtime would flake the "N DAYS older" assertions, and a lookup by
# basename can bind to the mirror instead of the repo copy.
#
# The repair hoisted it to `DESKTOP_MIRROR`. These tests are what REACHES that
# constant: an addition nothing reaches is not additive.
# ---------------------------------------------------------------------------

def test_the_desktop_mirror_is_a_module_constant(monkeypatch, tmp_path):
    """It must be substitutable, which an inline `Path.home()` call is not."""
    assert hasattr(R, "DESKTOP_MIRROR"), (
        "the Desktop mirror path is inline again; a fixture cannot displace it")
    fake = tmp_path / "not_the_real_desktop.md"
    fake.write_text("fixture mirror", encoding="utf-8")
    monkeypatch.setattr(R, "DESKTOP_MIRROR", fake)
    notes = tmp_path / "experimental_notes"
    notes.mkdir()
    for name in ("CDSFL_MASTER_TASK_LIST.md", "CDSFL_OUTCOMES_LOG.md",
                 "CDSFL_Agent_Operational_Plan.md"):
        (notes / name).write_text("x", encoding="utf-8")
    out = "\n".join(R.first_read_lines(tmp_path))
    assert str(fake) in out, "the substituted mirror was not used"
    assert str(Path.home() / "Desktop") not in out, (
        "the live machine's Desktop still leaked into a fixture run")


def test_the_real_mirror_is_still_offered_by_default():
    """The negative control: substituting it must not have removed it."""
    out = "\n".join(R.first_read_lines(REPO))
    assert str(R.DESKTOP_MIRROR) in out or not R.DESKTOP_MIRROR.exists(), (
        "the Desktop mirror is no longer offered on a real run; the hoist "
        "removed a capability instead of relocating it")
