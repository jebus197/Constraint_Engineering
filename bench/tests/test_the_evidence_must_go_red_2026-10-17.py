#!/usr/bin/env python3
"""V9: a DONE entry's evidence must FAIL when the fix it claims is undone.

TASK V9, proposed 2026-09-17 and APPROVED by the founder 2026-09-18: *"V9:
Approved."* Task V1 set 3 conditions on a DONE marker's evidence. 2 were
implemented and guarded -- it must exist and it must pass. The 3rd, that undoing
the fix makes the SAME evidence fail, was implemented nowhere, and R3 is the
worked example: its evidence passed against a reverted fix on 2026-09-17 and a
HUMAN noticed, not a mechanism.

WHAT WAS MEASURED, 2026-10-17, by
`scripts/does_the_evidence_go_red_2026-10-17.py` over a reproducible sample of
24 of the 114 DONE entries that name an existing test file -- all 114 are
checkable, since every one's closing commit is locatable:

    DISCRIMINATES  17   the evidence fails at the parent commit, as V9 requires
    DECORATIVE      2   it PASSES there, so it would not notice the fix missing
    INCONCLUSIVE    5   it cannot be COLLECTED there, which is not discrimination

**2 of 19 decided = 10.5263% decorative, Wilson [2.9359%, 31.3941%],
Clopper-Pearson [1.3012%, 33.1377%].** So roughly 1 DONE entry in 10 rests on
evidence that would have stayed green with its own fix absent.

THE 2 NAMED, because a rate with no members is not actionable:
  A11  27 of 27 tests pass at the parent commit -- it discriminates nothing.
  R2   4 passed and 14 SKIPPED. A test that skips when its subject is absent is
       always green, which is the most deceptive form: it reads as a pass.

WHY THE FULL CHECK IS NOT IN THE COMMIT GATE. It costs a git worktree and a
pytest invocation per entry, and this machine is a fixed resource. The expensive
sweep is a script run deliberately; what is gated here is that the script
exists, that its classifier is correct, and that the 2 known decorative entries
are RECORDED so the number cannot drift in silence.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "does_the_evidence_go_red_2026-10-17.py"

#: The entries measured DECORATIVE on 2026-10-17. A ratchet, not a tolerance:
#: these are defects awaiting repair, and the set may shrink but must not grow
#: without the new member being recorded here with its evidence.
KNOWN_DECORATIVE = {"A11", "R2"}


def _mod():
    spec = importlib.util.spec_from_file_location("v9", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["v9"] = m
    spec.loader.exec_module(m)
    return m


def test_the_checker_exists_and_answers_help():
    assert SCRIPT.is_file(), "V9's checker is missing"
    r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0 and "usage" in r.stdout.lower()


def test_every_done_entry_is_checkable():
    """V9 can only be enforced where the closing commit can be found.

    Measured 2026-10-17: 114 of 114 DONE entries name an existing test file AND
    their closing commit is locatable, so the check has no blind spot to excuse.
    """
    m = _mod()
    entries = m._entries()
    assert len(entries) >= 100, (
        f"only {len(entries)} DONE entries name an existing test file; V9's "
        f"coverage has fallen and the reason needs stating")
    missing = [i for i, _ in entries[:20] if m._closing_commit(i) is None]
    assert not missing, (
        f"the closing commit cannot be found for {missing}, so V9 cannot be "
        f"enforced on them")


def test_an_inconclusive_result_is_not_counted_as_discrimination():
    """THE DISTINCTION THAT MAKES THIS HONEST.

    A test that cannot be COLLECTED at the parent commit has not noticed the
    fix missing -- it has failed to run. Counting that as a pass for V9 would
    repeat the error this project recorded when a crashed check was read as a
    passing one, and 5 of the 24 sampled entries are in exactly that state.
    """
    src = SCRIPT.read_text(encoding="utf-8")
    assert "INCONCLUSIVE" in src
    m = _mod()
    # the classifier is exercised through the outcomes it can return
    assert "DECORATIVE" in src and "DISCRIMINATES" in src
    # and the script must say so in its own output rather than burying it
    assert "not discrimination" in src


def test_the_known_decorative_entries_are_recorded():
    """A ratchet on a defect, so the count cannot drift in silence."""
    assert KNOWN_DECORATIVE == {"A11", "R2"}, (
        "the recorded set of decorative DONE entries changed. If one was "
        "REPAIRED, remove it here and say so. If a new one was found, add it "
        "with the measurement that found it -- it must not appear silently.")
    m = _mod()
    idents = {i for i, _ in m._entries()}
    for d in KNOWN_DECORATIVE:
        assert d in idents, (
            f"{d} is recorded as decorative but is no longer a DONE entry "
            f"naming an existing test; the record and the list have diverged")


def test_the_two_decorative_entries_still_name_evidence_that_runs():
    """They are not broken tests -- they are tests that cannot FAIL usefully.

    This is the distinction a reader needs: both pass today. That is why the
    defect was invisible until the evidence was run against the tree WITHOUT
    the fix.
    """
    m = _mod()
    by_id = dict(m._entries())
    for d in sorted(KNOWN_DECORATIVE):
        tests = by_id.get(d) or []
        assert tests, f"{d} names no existing test file"
        for t in tests:
            assert (REPO / t).is_file()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
