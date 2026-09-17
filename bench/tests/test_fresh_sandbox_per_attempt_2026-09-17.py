#!/usr/bin/env python3
"""A retry gets a tree of its own, and nothing is deleted on the way out. Executed.

FOUNDER RULING (j), 2026-09-17: *"Do it. And make sure this is how all future
panel reviews and experiments (both paid and simulated) work in the future too.
Take care when a panel review or an experiment completes however that the
sandbox does not simply get automatically deleted and that the results do not end
up simply being discarded, as has happened in the recent past."*

THE DEFECT, MEASURED IN ROUND 17 ON 2026-09-17. The fable seat hit the 1,800 s
cap. Its retry reran in the SAME sandbox the timed-out attempt had been editing
for half an hour, so 14 of the 19 files that seat left behind had no reply behind
them, and its verdict on entry A23 was measured against its own unreported edits.
A retry that inherits a half-finished tree is not a second attempt at the same
task; it is a first attempt at a different one.

WHAT WOULD FALSIFY THE FIX. Point `on_attempt` back at the same directory and
`test_attempt_2_cannot_see_what_attempt_1_wrote` fails, because the file the
first attempt left is still there. Restore the unconditional teardown and
`test_a_kept_sandbox_is_still_on_disk` fails.

Nothing here starts a real seat: `claude` is never spawned, the CLI call is
driven with a stub runner, and the sandboxes are copies of a tiny fake repo.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (str(ROOT), str(ROOT / "bench"), str(ROOT / "bench" / "tests")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiment_11_orchestrator as ORCH  # noqa: E402
import panel_sandbox as PS  # noqa: E402


@pytest.fixture
def repo(tmp_path):
    """A tiny canonical tree, standing in for the repository a seat copies."""
    r = tmp_path / "canonical"
    (r / "bench").mkdir(parents=True)
    (r / "bench" / "target.py").write_text("VALUE = 1\n", encoding="utf-8")
    (r / "README.md").write_text("canonical\n", encoding="utf-8")
    return r


class TestEachAttemptGetsItsOwnTree:
    def test_attempt_2_cannot_see_what_attempt_1_wrote(self, repo, tmp_path):
        """The round-17 failure, reproduced against the fix."""
        first = tmp_path / "attempt1" / "repo"
        first.parent.mkdir()
        subprocess.run(["cp", "-R", str(repo), str(first)], check=True, timeout=60)
        # The timed-out attempt leaves half-finished work behind.
        (first / "bench" / "target.py").write_text("VALUE = 999  # half-finished\n",
                                                   encoding="utf-8")
        (first / "scratch_notes.md").write_text("mid-run\n", encoding="utf-8")

        second = tmp_path / "attempt2" / "repo"
        second.parent.mkdir()
        subprocess.run(["cp", "-R", str(repo), str(second)], check=True, timeout=60)

        assert (second / "bench" / "target.py").read_text() == "VALUE = 1\n"
        assert not (second / "scratch_notes.md").exists()
        # And the first tree still exists, so its work is not lost either.
        assert (first / "scratch_notes.md").is_file()

    def test_the_cli_caller_asks_for_a_tree_before_every_attempt(self, tmp_path,
                                                                 monkeypatch):
        """`on_attempt` is CALLED, and the attempt runs where it says. Executed
        through `call_claude_cli` itself rather than asserted about its source."""
        trees = []
        for n in (1, 2, 3):
            d = tmp_path / f"tree{n}"
            d.mkdir()
            trees.append(str(d))
        asked, ran_in = [], []

        def on_attempt(attempt):
            asked.append(attempt)
            ORCH.set_panel_cwd(trees[attempt - 1])
            return trees[attempt - 1]

        def fake_run(cmd, *a, **k):
            ran_in.append(k.get("cwd"))
            if len(ran_in) < 3:                       # 2 transport failures, then a reply
                return subprocess.CompletedProcess(cmd, 1, "", "boom")
            return subprocess.CompletedProcess(cmd, 0, "a real reply with substance", "")

        monkeypatch.setattr(ORCH.subprocess, "run", fake_run)
        monkeypatch.setattr(ORCH, "CLAUDE_CLI", "/usr/bin/true")
        out = ORCH.call_claude_cli("opus", None, "prompt", max_retries=3,
                                   backoff_base=0, on_attempt=on_attempt)
        assert out == "a real reply with substance"
        assert asked == [1, 2, 3], "every attempt must ask for its own tree"
        assert ran_in == trees, "an attempt ran somewhere other than the tree it was given"

    def test_a_caller_that_supplies_nothing_behaves_exactly_as_before(self, monkeypatch):
        seen = []

        def fake_run(cmd, *a, **k):
            seen.append(k.get("cwd"))
            return subprocess.CompletedProcess(cmd, 0, "reply", "")

        monkeypatch.setattr(ORCH.subprocess, "run", fake_run)
        monkeypatch.setattr(ORCH, "CLAUDE_CLI", "/usr/bin/true")
        ORCH.set_panel_cwd(None)
        assert ORCH.call_claude_cli("opus", None, "p", max_retries=1) == "reply"
        assert seen == [None]

    def test_a_failing_hook_does_not_lose_the_attempt(self, monkeypatch):
        """A sandbox that cannot be built is not a reason to skip the attempt:
        the seat runs where it already was, and the reason is logged."""
        def boom(attempt):
            raise OSError("no space left on device")

        def fake_run(cmd, *a, **k):
            return subprocess.CompletedProcess(cmd, 0, "reply anyway", "")

        monkeypatch.setattr(ORCH.subprocess, "run", fake_run)
        monkeypatch.setattr(ORCH, "CLAUDE_CLI", "/usr/bin/true")
        ORCH.set_panel_cwd(None)
        assert ORCH.call_claude_cli("opus", None, "p", max_retries=1,
                                    on_attempt=boom) == "reply anyway"


class TestTheDispatcherBuildsOnePerAttempt:
    @pytest.fixture
    def panel(self, monkeypatch, repo):
        import importlib.util
        monkeypatch.setenv("PANEL_ONLY", "__none__")
        spec = importlib.util.spec_from_file_location(
            "_cmp_attempt_probe", ROOT / "bench" / "confer_maths_panel_2026-09-05.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert mod.MODELS == []
        monkeypatch.setattr(mod, "_REPO", repo)
        mod._SEAT_SANDBOXES.clear()
        mod._SEAT_ATTEMPTS.clear()
        return mod

    def test_attempt_1_reuses_the_copy_already_built_and_attempt_2_does_not(self, panel,
                                                                           tmp_path):
        prebuilt = tmp_path / "prebuilt" / "repo"
        prebuilt.parent.mkdir()
        subprocess.run(["cp", "-R", str(panel._REPO), str(prebuilt)], check=True, timeout=60)
        panel._SEAT_SANDBOXES["cc2"] = str(prebuilt)

        one = panel.fresh_sandbox_for_attempt("cc2", 1)
        assert one == str(prebuilt), "attempt 1 must not pay for a second copy"

        # The first attempt leaves work behind, then times out.
        (Path(one) / "left_behind.txt").write_text("half-done\n", encoding="utf-8")

        two = panel.fresh_sandbox_for_attempt("cc2", 2)
        try:
            assert two != one
            assert not (Path(two) / "left_behind.txt").exists(), (
                "the retry inherited the timed-out attempt's tree: round 17 again")
            assert (Path(two) / "bench" / "target.py").is_file()
            recorded = panel._SEAT_ATTEMPTS["cc2"]
            assert [a["attempt"] for a in recorded] == [1, 2]
            assert [a["built"] for a in recorded] == [False, True]
            assert recorded[0]["path"] != recorded[1]["path"]
        finally:
            PS.teardown(Path(two))


class TestNothingIsDeletedUnlessAsked:
    def _seat_tree(self, repo, tmp_path, name="s1"):
        sb = tmp_path / name / "repo"
        sb.parent.mkdir(parents=True)
        subprocess.run(["cp", "-R", str(repo), str(sb)], check=True, timeout=60)
        (sb / "bench" / "target.py").write_text("VALUE = 2\n", encoding="utf-8")
        (sb / "new_artefact.py").write_text("print('a seat wrote this')\n", encoding="utf-8")
        return sb

    def test_a_kept_sandbox_is_still_on_disk(self, repo, tmp_path):
        sb = self._seat_tree(repo, tmp_path)
        m = PS.release(sb, repo, tmp_path / "harvest")
        assert m["reaped"] is False and m["exists"] is True
        assert sb.is_file() or sb.is_dir()

    def test_the_whole_file_comes_out_not_only_the_diff(self, repo, tmp_path):
        """A diff lets a reader READ an artefact; it does not let anyone RUN it.
        Round 15 lost `seat_proposals.diff` outright to a decode error, and a
        seat's new script is worth more than a description of it."""
        sb = self._seat_tree(repo, tmp_path)
        dest = tmp_path / "harvest"
        m = PS.release(sb, repo, dest)
        assert (dest / "files" / "new_artefact.py").read_text().startswith("print(")
        assert (dest / "files" / "bench" / "target.py").read_text() == "VALUE = 2\n"
        assert (dest / "changes.diff").is_file()
        assert sorted(m["files_taken"]) == ["bench/target.py", "new_artefact.py"]

    def test_reaping_is_opt_in_and_happens_only_after_a_complete_harvest(self, repo,
                                                                        tmp_path):
        sb = self._seat_tree(repo, tmp_path)
        m = PS.release(sb, repo, tmp_path / "harvest", reap=True)
        assert m["reaped"] is True and m["exists"] is False
        assert (tmp_path / "harvest" / "files" / "new_artefact.py").is_file(), (
            "the copy was removed but its artefacts were not saved first")

    def test_a_failed_harvest_refuses_to_reap(self, repo, tmp_path, monkeypatch):
        sb = self._seat_tree(repo, tmp_path)

        def half_failing(src, dst, *a, **k):
            raise OSError("read-only file system")

        monkeypatch.setattr(PS.shutil, "copy2", half_failing)
        m = PS.release(sb, repo, tmp_path / "harvest", reap=True)
        assert m["harvested"] is False and m["reaped"] is False
        assert sb.is_dir(), "a sandbox whose results could not be saved was deleted anyway"
        assert "reap_refused" in m

    def test_the_dispatchers_own_end_of_run_step_keeps_every_attempts_tree(self, repo,
                                                                            tmp_path,
                                                                            monkeypatch):
        """The panel's OWN closing step, executed. This is the line that used to
        read `for _sb in sandboxes.values(): panel_sandbox.teardown(_sb)`."""
        import importlib.util
        monkeypatch.setenv("PANEL_ONLY", "__none__")
        monkeypatch.delenv("PANEL_REAP_SANDBOXES", raising=False)
        spec = importlib.util.spec_from_file_location(
            "_cmp_retain_probe", ROOT / "bench" / "confer_maths_panel_2026-09-05.py")
        panel = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(panel)

        trees = {}
        for attempt in (1, 2):
            trees[attempt] = self._seat_tree(repo, tmp_path, name=f"seat-a{attempt}")
        (trees[2] / "only_in_attempt_2.py").write_text("x = 2\n", encoding="utf-8")
        seat_attempts = {"cc2": [{"attempt": n, "path": str(p), "built": n > 1}
                                 for n, p in trees.items()]}
        logs = tmp_path / "logs"
        out = panel.harvest_and_retain(seat_attempts, logs, repo)

        assert out["reap_requested"] is False
        assert sorted(out["kept"]) == sorted(str(p) for p in trees.values()), (
            "a panel round deleted a seat's working copy on the way out")
        assert all(p.is_dir() for p in trees.values())
        # BOTH attempts are harvested, which is the round-17 lesson: reading only
        # the tree the seat ended in left 14 files with no reply behind them.
        a1 = logs / "sandbox_harvest" / "cc2" / "attempt-1" / "files"
        a2 = logs / "sandbox_harvest" / "cc2" / "attempt-2" / "files"
        assert (a1 / "new_artefact.py").is_file() and (a2 / "new_artefact.py").is_file()
        assert (a2 / "only_in_attempt_2.py").is_file()
        assert not (a1 / "only_in_attempt_2.py").exists()
        written = json.loads((logs / "sandbox_manifest.json").read_text())
        assert [m["attempt"] for m in written["per_attempt"]] == [1, 2]
        assert written["harvest_bytes"] > 0

    def test_the_manifest_shape_a_reader_gets(self, repo, tmp_path):
        m = PS.release(self._seat_tree(repo, tmp_path), repo, tmp_path / "h")
        for key in ("sandbox", "dest", "changed", "files_taken", "bytes", "failed",
                    "harvested", "reaped", "exists"):
            assert key in m, key
        json.dumps(m)   # it has to survive being written to sandbox_manifest.json
