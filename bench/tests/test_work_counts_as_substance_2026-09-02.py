"""A short reply is only a holding note if nothing else was produced.

`verdict_is_substantive` judges the REPLY. A dispatch produces an artefact SET:
a reply, a diff in the sandbox, a tool log.

MEASURED 2026-09-02. On the scale review, fable wrote 77,219 bytes across 12
files -- edits to decomposed_dispatch.py, routing.py, runner_core.py, the runner
and four test files -- and closed with a 126-character note. The predicate
rejected the note, retried, and recorded the dispatch as ok=False, chars=0. The
patch survived only because extraction runs in a `finally`.

Across 25 archived dispatches, 2 are recorded as failed while carrying a
substantive patch: 8.0%, Wilson [2.2%, 25.0%], 78,926 bytes in total. One
predates the retry gate, so the gate did not create the fault -- it made it
expensive, because a rejected reply is retried and then hard-fails.

It is also the wrong incentive. A reviewer running out of budget SHOULD write
its work down and point at it. Punishing that is how an overloaded reviewer's
output gets destroyed rather than salvaged.
"""

import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

from experiment_11_orchestrator import (  # noqa: E402
    accept_reply_or_work, verdict_is_substantive)

HOLDING_NOTE = "Suite still running - I'll finalize once it completes."


@pytest.fixture
def worktree(tmp_path):
    d = tmp_path / "wt"
    d.mkdir()
    def git(*a):
        return subprocess.run(["git", "-C", str(d), *a], capture_output=True,
                              text=True, timeout=60)
    subprocess.run(["git", "init", "-q", str(d)], timeout=60)
    git("config", "user.email", "t@t"); git("config", "user.name", "t")
    (d / "a.py").write_text("x = 1\n")
    git("add", "-A"); git("commit", "-qm", "init")
    return d


class TestWorkCountsAsSubstance:
    def test_a_short_reply_with_no_work_is_still_rejected(self, worktree):
        reason = accept_reply_or_work(worktree)(HOLDING_NOTE)
        assert reason is not None
        assert "bytes of work" in reason, (
            "the rejection must say how much work it looked for, or the next "
            "person cannot tell why it fired")

    def test_a_short_reply_beside_real_work_is_accepted(self, worktree):
        (worktree / "a.py").write_text("x = 1\n" + "# substantive work\n" * 400)
        assert accept_reply_or_work(worktree)(HOLDING_NOTE) is None, (
            "a reviewer that wrote 77kB of patch and summarised briefly had its "
            "whole dispatch discarded; that must not recur")

    def test_an_empty_reply_is_rejected_even_with_work(self, worktree):
        """Nothing said AND nothing pointed at is still empty."""
        (worktree / "a.py").write_text("x = 1\n" + "# work\n" * 400)
        assert accept_reply_or_work(worktree)("") == "empty"

    def test_a_full_reply_is_accepted_with_no_work_at_all(self, worktree):
        assert accept_reply_or_work(worktree)("y" * 900) is None

    def test_untracked_files_count_as_work(self, worktree):
        """A reviewer that writes a NEW test file has produced work."""
        (worktree / "test_new_thing.py").write_text("def test_x():\n    assert 1\n")
        acc = accept_reply_or_work(worktree, min_work_bytes=10)
        assert acc(HOLDING_NOTE) is None

    def test_it_survives_a_path_that_is_not_a_repo(self, tmp_path):
        """Telemetry failure must not turn into a rejection of good work."""
        acc = accept_reply_or_work(tmp_path / "nope")
        assert acc("y" * 900) is None            # long reply still fine
        assert acc(HOLDING_NOTE) is not None     # short reply, unverifiable work

    def test_none_worktree_degrades_to_the_reply_only_rule(self):
        acc = accept_reply_or_work(None)
        assert acc("y" * 900) is None
        assert acc(HOLDING_NOTE) is not None


class TestTheHarnessesUseIt:
    @pytest.mark.parametrize("script", [
        "bench/confer_panel_2026-08-28.py",
        "bench/confer_convergence_panel_2026-08-23.py",
    ])
    def test_the_panel_harness_passes_the_worktree(self, script):
        src = (REPO / script).read_text(encoding="utf-8")
        assert "accept_reply_or_work(wt)" in src, (
            f"{script} still judges the reply alone; a reviewer that writes its "
            f"work to the sandbox and summarises briefly will be discarded")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
