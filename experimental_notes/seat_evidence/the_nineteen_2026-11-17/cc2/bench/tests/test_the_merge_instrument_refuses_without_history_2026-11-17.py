# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_nineteen_2026-11-17', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4bc10c8ab3b3919c02e7b2b5844bae33b9bdb94abff447ecfca1badf76c5edad
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The merge-safety instrument must REFUSE without git, never report all-clear.

★ THE DEFECT, found 2026-11-17 by a free panel seat answering entry B170 and
REPRODUCED BEFORE IT WAS REPORTED. `scripts/what_is_safe_to_merge_to_main_2026-10-16.py`
helper `sh()` discarded `returncode` and returned `stdout`. With no `.git`, every
git call returned the empty string, so `changed()` returned `[]`, every
classification bucket collapsed to 0, `interval()` printed `n=0`, and the script
EXITED 0 while printing "a MERGE, not a fast-forward" and "B7's repair held."

WHY A GUARD RATHER THAN A NOTE. The instrument exists to answer whether a
620-plus-commit branch is safe to merge to `main`. "Could not look" rendering as
"looked and found nothing" is the exact failure shape this project names
repeatedly, and the repair is only additive if something reaches it -- the
symmetric clause of `additive-standard`.

WHY THE SUBJECT IS EXECUTED AND NOT GREPPED. `execute-do-not-grep`: a test that
asserts the file contains the string `returncode` establishes only that the file
describes itself consistently. `sh()` is CALLED here against a command that
really fails, and `main()` is DRIVEN in a directory that really has no history.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SUBJECT = REPO / "scripts" / "what_is_safe_to_merge_to_main_2026-10-16.py"


@pytest.fixture(scope="module")
def mod():
    assert SUBJECT.is_file(), f"the merge instrument is missing: {SUBJECT}"
    spec = importlib.util.spec_from_file_location("merge_instrument", SUBJECT)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        spec.loader.exec_module(m)
    finally:
        sys.path.pop(0)
    return m


def test_sh_raises_rather_than_returning_empty_on_a_failing_command(mod):
    """A non-zero git call must raise, not hand back an empty string."""
    assert hasattr(mod, "NoHistory"), (
        "the instrument no longer declares a refusal type, so a failed git call "
        "has nowhere to go but back to the caller as empty output")
    with pytest.raises(mod.NoHistory):
        # `--this-flag-does-not-exist` makes git exit non-zero in ANY directory,
        # so this case does not depend on the test environment having no repo.
        mod.sh("git", "rev-parse", "--this-flag-does-not-exist")


def test_sh_still_returns_stdout_when_the_command_succeeds(mod):
    """ANTI-VACUITY. A helper that raised on everything would pass the test
    above while destroying the instrument, so the success path is pinned too."""
    assert mod.sh("git", "--version").startswith("git version")


def test_the_instrument_exits_non_zero_where_there_is_no_history(tmp_path):
    """END TO END: run the real script in a directory with no `.git`.

    Before the 2026-11-17 repair this exited 0 and printed an all-clear. The
    assertion is on the EXIT STATUS, because that is what a caller reads.
    """
    r = subprocess.run([sys.executable, str(SUBJECT)],
                       cwd=tmp_path, capture_output=True, text=True, timeout=120)
    assert r.returncode != 0, (
        "the merge instrument reported successfully from a directory with no "
        f"git history; stdout was:\n{r.stdout[-800:]}")
    blob = (r.stdout + r.stderr).lower()
    assert "refus" in blob, (
        "the instrument failed without SAYING it could not look, which leaves "
        f"a reader unable to tell a refusal from a clean result:\n{blob[-800:]}")
    assert "b7's repair held" not in blob, (
        "the instrument printed its all-clear line while unable to read any "
        "history at all")
