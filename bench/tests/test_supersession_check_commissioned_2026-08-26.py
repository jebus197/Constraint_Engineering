"""Commissioning test for scripts/supersession_check.py, and the record of a
withdrawn claim.

WHAT WAS CLAIMED AND WITHDRAWN. On 2026-08-25 this assistant wrote, in
test_documentation_drift_guards_2026-08-25.py and in a note on the founder's
desk, that cross-document supersession "is not mechanically detectable and is
not attempted", and that defect 1 in that file's list "would still not be
caught". The founder asked: "Is not mechanically detectable? For sure?"

It was wrong, and the tool below refutes it. GENERAL supersession -- any
assertion anywhere overturned by any later text -- is indeed not detectable.
But the defect that actually bit this project was not general. It was:

    RUNWAY_to_BR2_2026-08-18.md line 28   "EVERYTHING IS ON HOLD PENDING NINE
                                           FOUNDER DECISIONS"
    same block, next line                  named the file holding them
    that file                              carried "# FOUNDER RULINGS" already

Both halves are machine-readable, so the pair is detectable, and the checker
fires on the exact historical file (git c8f63ec~1) that the withdrawn claim
said it could not.

WHAT THIS FILE ASSERTS. Not that the script imports. That the script gives
DIFFERENT answers to a stale hold and to each of the three things that look
like one and are not -- because a checker that fires on everything is as
useless as one that fires on nothing, and the first version fired on a
four-month-old log entry in ONBOARDING.md.
"""
import subprocess
import sys
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts/supersession_check.py"

# A file that IS ruled on, referenced by every fixture below.
RULED_FILE = "experimental_notes/Decisions_Inventory_2026-08-22.md"

STALE_HOLD = """\
# Runway

**EVERYTHING IS ON HOLD PENDING NINE FOUNDER DECISIONS, 2026-08-22 03:47 BST.**
**The list is `{ruled}` (+ Desktop TTS).**
**Nothing is built and nothing is run until it is answered.**
""".format(ruled=RULED_FILE)

MARKED_SUPERSEDED = STALE_HOLD + "\n**SUPERSEDED -- retained as the record of what was ASKED.**\n"

HISTORICAL_ENTRY = """\
# Onboarding

## Current State

- **AN EARLIER SHIFT (2026-04-22, 02:15 BST):**

  **Pending founder decisions.** (1) Scope of focused confer round.
  The list is `{ruled}`.

- **A LATER SHIFT (2026-08-24, 03:31 BST):**

  Work continued.
""".format(ruled=RULED_FILE)

HOLD_ON_AN_UNRULED_FILE = """\
# Runway

**EVERYTHING IS ON HOLD PENDING NINE FOUNDER DECISIONS.**
**The list is `docs/GLOSSARY.md`.**
"""


def _run(tmp_path, name, body):
    """Exit 1 == stale hold found, 0 == clean. Reports only; never edits."""
    f = tmp_path / name
    f.write_text(body, encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPT), "--path", str(f)],
                       capture_output=True, text=True, cwd=REPO)
    return r.returncode, r.stdout


@pytest.mark.skipif(not (REPO / RULED_FILE).is_file(),
                    reason=f"fixtures reference {RULED_FILE}, which is absent")
class TestItDiscriminates:
    def test_known_bad_a_live_stale_hold_is_found(self, tmp_path):
        code, out = _run(tmp_path, "stale.md", STALE_HOLD)
        assert code == 1, "a live hold naming an already-ruled file was not reported"
        assert RULED_FILE in out, "the report does not name the file it checked"

    def test_known_good_an_explicit_supersession_marker_clears_it(self, tmp_path):
        code, _ = _run(tmp_path, "marked.md", MARKED_SUPERSEDED)
        assert code == 0, (
            "a block the author already marked SUPERSEDED still reported as stale; "
            "the check would then be unsilenceable and would be ignored"
        )

    def test_known_good_an_older_dated_log_entry_is_a_record_not_a_claim(self, tmp_path):
        """The false positive that shaped the tool: resources/ONBOARDING.md:514,
        a hold recorded inside a 2026-04-22 entry with later entries below it."""
        code, out = _run(tmp_path, "history.md", HISTORICAL_ENTRY)
        assert code == 0, (
            "a four-month-old hold inside a superseded log entry reported as live. "
            f"An append-only history would fire forever. Output:\n{out}"
        )

    def test_known_good_a_hold_on_a_file_with_no_rulings_stands(self, tmp_path):
        code, _ = _run(tmp_path, "unruled.md", HOLD_ON_AN_UNRULED_FILE)
        assert code == 0, (
            "a hold whose named file contains no rulings marker was reported stale; "
            "genuinely open decisions would be flagged as answered"
        )

    def test_the_four_answers_are_not_all_the_same(self, tmp_path):
        """The commissioning assertion proper: known-bad and known-good differ."""
        bad = _run(tmp_path, "b.md", STALE_HOLD)[0]
        goods = [_run(tmp_path, f"g{i}.md", body)[0] for i, body in enumerate(
            (MARKED_SUPERSEDED, HISTORICAL_ENTRY, HOLD_ON_AN_UNRULED_FILE))]
        assert bad == 1 and set(goods) == {0}, (
            f"checker does not discriminate: stale->{bad}, non-stale->{goods}"
        )


def test_it_fires_on_the_real_historical_defect():
    """Against the actual file from git, not a fixture. This is the case the
    withdrawn claim named as uncatchable."""
    hist = subprocess.run(
        ["git", "show", "c8f63ec~1:experimental_notes/RUNWAY_to_BR2_2026-08-18.md"],
        capture_output=True, text=True, cwd=REPO)
    if hist.returncode != 0:
        pytest.skip("commit c8f63ec is not reachable in this clone")
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        f = pathlib.Path(d) / "RUNWAY_historical.md"
        f.write_text(hist.stdout, encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT), "--path", str(f)],
                           capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 1, (
        "the checker does not fire on the real 2026-08-24 defect it was written "
        "for; the withdrawn claim would then have been correct after all"
    )
    assert "Decisions_Inventory" in r.stdout


def test_the_current_tree_carries_no_stale_hold():
    """Runs the check as a guard, not only as a subject."""
    r = subprocess.run([sys.executable, str(SCRIPT)],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, f"stale hold(s) in the tree:\n{r.stdout}"
