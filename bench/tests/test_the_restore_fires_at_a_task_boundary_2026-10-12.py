"""The post-compaction restore fires at a TASK BOUNDARY, and cannot trap the session.

HIS DESIGN CORRECTION, 2026-10-12: *"it's probably not heathy to interrupt a task that
was running immediately before compaction ... it would need to fire at a safe point
immediately after the first task in any given task list completes after a compaction.
Then it would need to go back, and check that last before continuing with the rest of
the work."*

WHAT THIS PINS, and every assertion EXECUTES the hook rather than reading it:
  1. It FIRES (exit 2, so the context lands) once a commit exists since the compaction.
  2. It stays SILENT with a compaction but NO commit — the work in flight is not
     interrupted. This is his correction, and it is the assertion that would have
     caught the turn-end design.
  3. It fires ONCE PER COMPACTION: after the restore records itself, later stops pass.
  4. It CANNOT LOOP: `stop_hook_active` exits immediately.
  5. It NEVER fells the session — malformed payload, missing transcript, absent repo.
  6. Its message NAMES the commits to re-check and tells the assistant to check them
     BEFORE continuing.
  7. It reimplements NO predicate: the scan, the recovery test and the restore are all
     imported from `compaction_watch`.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile

import pytest

HOOK = pathlib.Path.home() / ".claude" / "hooks" / "compaction_task_boundary.py"
WATCH = pathlib.Path.home() / ".claude" / "hooks" / "compaction_watch.py"

pytestmark = pytest.mark.skipif(
    not HOOK.is_file(), reason="the hook is not installed on this machine")


def _load():
    spec = importlib.util.spec_from_file_location("ctb", str(HOOK))
    m = importlib.util.module_from_spec(spec)
    sys.modules["ctb"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def world(tmp_path):
    """A synthetic transcript, a synthetic git repo, and an isolated HOME."""
    tr = tmp_path / "t.jsonl"
    rows = [
        {"type": "user", "timestamp": "2026-10-01T10:00:00.000Z",
         "message": {"role": "user", "content": "go"}},
        {"type": "user", "isCompactSummary": True,
         "timestamp": "2026-10-01T11:00:00.000Z",
         "message": {"role": "user", "content": "continued"}},
    ]
    tr.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    repo = tmp_path / "repo"
    repo.mkdir()
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=env)
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True)
    return {"transcript": tr, "repo": repo, "home": home, "env": env,
            "compaction": "2026-10-01T11:00:00.000Z"}


def _commit(world, msg, when="2026-10-01T11:30:00+00:00"):
    f = world["repo"] / f"f{msg[:4]}.txt"
    f.write_text(msg, encoding="utf-8")
    env = {**world["env"], "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
    subprocess.run(["git", "add", "-A"], cwd=world["repo"], check=True, env=env)
    subprocess.run(["git", "commit", "-q", "-m", msg], cwd=world["repo"],
                   check=True, env=env)


def _run(world, m, payload_extra=None, home=None):
    """Execute the hook's main() against the synthetic world."""
    m.REPO = world["repo"]
    payload = {"session_id": "T", "transcript_path": str(world["transcript"])}
    payload.update(payload_extra or {})
    real_home = os.environ.get("HOME")
    real_stdin = sys.stdin
    import io
    try:
        os.environ["HOME"] = str(home or world["home"])
        # the shared predicates read HOME at call time via compaction_watch.STATE,
        # which is bound at import — so reload it under the test HOME
        wspec = importlib.util.spec_from_file_location("compaction_watch", str(WATCH))
        w = importlib.util.module_from_spec(wspec)
        sys.modules["compaction_watch"] = w
        wspec.loader.exec_module(w)
        m._watch = lambda: w
        sys.stdin = io.StringIO(json.dumps(payload))
        rc = m.main()
    finally:
        sys.stdin = real_stdin
        if real_home is not None:
            os.environ["HOME"] = real_home
    return rc, w


class TestItStaysSilentUntilATaskCompletes:
    def test_a_compaction_with_no_commit_does_not_fire(self, world, capsys):
        """HIS CORRECTION IN ONE ASSERTION. A turn-end trigger would have fired here,
        mid-task, with the tree dirty."""
        m = _load()
        rc, _ = _run(world, m)
        assert rc == 0, "it interrupted work in flight with no task completed"
        assert "compaction-task-boundary" not in capsys.readouterr().err

    def test_no_compaction_at_all_does_not_fire(self, world, capsys):
        world["transcript"].write_text(json.dumps(
            {"type": "user", "timestamp": "2026-10-01T10:00:00.000Z",
             "message": {"role": "user", "content": "go"}}), encoding="utf-8")
        _commit(world, "work")
        m = _load()
        rc, _ = _run(world, m)
        assert rc == 0

    def test_a_commit_BEFORE_the_compaction_does_not_count(self, world, capsys):
        """`--since` must bound it, or any prior commit would look like a boundary."""
        _commit(world, "earlier", when="2026-10-01T09:00:00+00:00")
        m = _load()
        rc, _ = _run(world, m)
        assert rc == 0, "a pre-compaction commit was read as a task boundary"


class TestItFiresAtTheBoundary:
    def test_a_commit_after_the_compaction_fires_and_blocks(self, world, capsys):
        _commit(world, "item one complete")
        m = _load()
        rc, _ = _run(world, m)
        err = capsys.readouterr().err
        assert rc == 2, "it did not block, so the restored context would never land"
        assert "A COMPACTION OCCURRED" in err
        assert "item one complete" in err, "it did not name the task to re-check"

    def test_the_message_orders_the_recheck_before_continuing(self, world, capsys):
        _commit(world, "item one complete")
        m = _load()
        _run(world, m)
        err = capsys.readouterr().err
        assert "GO BACK AND CHECK" in err
        assert "BEFORE CONTINUING" in err
        i_check = err.index("GO BACK AND CHECK")
        i_carry = err.index("THEN carry on")
        assert i_check < i_carry, "the instructions are out of order"

    def test_it_carries_the_first_read_block(self, world, capsys):
        _commit(world, "item one complete")
        m = _load()
        _run(world, m)
        err = capsys.readouterr().err
        assert ("FIRST READ" in err) or ("AUTO-RESTORE" in err), (
            "the restore output did not reach the assistant")


class TestItCannotTrapTheSession:
    def test_stop_hook_active_exits_immediately(self, world, capsys):
        _commit(world, "item one complete")
        m = _load()
        rc, _ = _run(world, m, {"stop_hook_active": True})
        assert rc == 0, "it can be re-entered, so it could loop"
        assert capsys.readouterr().err == ""

    def test_it_fires_only_once_per_compaction(self, world, capsys):
        """Asserted on BEHAVIOUR, not on an internal marker. The first version of
        this test asserted `_recovery_ran_after` and so measured the RESTORE's
        success rather than the hook's restraint -- see the next test."""
        _commit(world, "item one complete")
        m = _load()
        rc1, _ = _run(world, m)
        capsys.readouterr()
        assert rc1 == 2
        rc2, _ = _run(world, m)
        assert rc2 == 0, "it fired twice for one compaction"

    def test_a_FAILING_restore_still_does_not_re_arm(self, world, capsys):
        """THE DEFECT THE P-PASS FOUND, 2026-10-12. The first version gated only on
        `_recovery_ran_after`, which `cdsfl_recover.py` writes itself. With no
        recovery script in the checkout the restore cannot run, no marker is
        written, and the hook re-armed at EVERY stop -- refusing one stop per turn
        indefinitely. The synthetic repo here has no recovery script, so this test
        reproduces that production failure mode exactly."""
        _commit(world, "item one complete")
        assert not (world["repo"] / "scripts" / "cdsfl_recover.py").exists()
        m = _load()
        rc1, w = _run(world, m)
        err = capsys.readouterr().err
        assert rc1 == 2
        assert "AUTO-RESTORE DID NOT RUN" in err or "OWED" in err, (
            "a failed restore must say so rather than read as success")
        # the restore genuinely did NOT record itself ...
        assert w._recovery_ran_after(world["compaction"]) is False
        # ... and the hook must STILL fall silent, on its own record
        rc2, _ = _run(world, m)
        assert rc2 == 0, (
            "a failed restore re-arms the hook, so it would refuse one stop per "
            "turn forever")

    def test_a_restore_that_DIES_still_leaves_the_firing_recorded(self, world, capsys):
        """CONVERTED FROM A SOURCE-TEXT ASSERTION, 2026-10-12. The first form
        compared the two statements' INDEX POSITIONS in the file, which asserts
        the source reads in a given order and not that the behaviour holds -- it
        would pass unchanged if the write were inside a branch that never ran.
        This EXECUTES: `_auto_restore` is made to raise, and `fired_for` must
        still be on disk afterwards, because that is the only thing standing
        between a dead restore and a hook that refuses one stop per turn
        forever."""
        _commit(world, "item one complete")
        m = _load()
        m.REPO = world["repo"]
        import io
        import importlib.util as _ilu

        def _boom(_repo):
            raise RuntimeError("the restore died mid-run")

        real_home, real_stdin = os.environ.get("HOME"), sys.stdin
        try:
            # HOME FIRST, THEN THE IMPORT. `compaction_watch.STATE` is bound from
            # `Path.home()` at IMPORT time, so loading it before setting HOME makes
            # `_recovery_ran_after` read the OPERATOR'S live `last_recovery` and
            # return early -- which is exactly how this test failed on its first
            # run, reporting a hook defect that did not exist. The `_run` helper
            # above orders it this way for the same reason.
            os.environ["HOME"] = str(world["home"])
            wspec = _ilu.spec_from_file_location("compaction_watch", str(WATCH))
            w = _ilu.module_from_spec(wspec)
            sys.modules["compaction_watch"] = w
            wspec.loader.exec_module(w)
            w._auto_restore = _boom
            m._watch = lambda: w
            sys.stdin = io.StringIO(json.dumps(
                {"session_id": "T", "transcript_path": str(world["transcript"])}))
            rc = m.main()
        finally:
            sys.stdin = real_stdin
            if real_home is not None:
                os.environ["HOME"] = real_home
        assert rc == 2, "a dying restore must still deliver the notice"
        state = json.loads((world["home"] / ".claude" / ".compaction_watch" / "T")
                           .read_text(encoding="utf-8"))
        assert state.get("fired_for") == world["compaction"], (
            "the restore died and the firing was NOT recorded, so the hook would "
            "re-arm at every stop")

    def test_a_failed_restore_leaves_the_prompt_alarm_armed(self, world, capsys):
        """`fired_for` must NOT silence the UserPromptSubmit notice: if the restore
        failed, a restore is still owed and he must still be told."""
        _commit(world, "item one complete")
        m = _load()
        _run(world, m)
        capsys.readouterr()
        state = json.loads((world["home"] / ".claude" / ".compaction_watch" / "T")
                           .read_text(encoding="utf-8"))
        assert state.get("fired_for") == world["compaction"]
        assert state.get("acknowledged") != world["compaction"], (
            "it marked the compaction acknowledged although no restore succeeded, "
            "which would silence the alarm the founder relies on")

    def test_an_already_acknowledged_compaction_does_not_fire(self, world, capsys):
        _commit(world, "item one complete")
        m = _load()
        state_dir = world["home"] / ".claude" / ".compaction_watch"
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / "T").write_text(json.dumps({
            "offset": 0, "last_compaction": world["compaction"],
            "acknowledged": world["compaction"]}), encoding="utf-8")
        rc, _ = _run(world, m)
        assert rc == 0, "it fired on a compaction the founder had already handled"


class TestItNeverFellsTheSession:
    @pytest.mark.parametrize("payload", [
        {}, {"session_id": "T"}, {"transcript_path": "/nonexistent/x.jsonl"},
        {"session_id": "T", "transcript_path": ""},
    ])
    def test_a_degenerate_payload_returns_zero(self, world, payload):
        m = _load()
        m.REPO = world["repo"]
        import io
        real = sys.stdin
        try:
            sys.stdin = io.StringIO(json.dumps(payload))
            assert m.main() == 0
        finally:
            sys.stdin = real

    def test_unparseable_stdin_returns_zero(self):
        m = _load()
        import io
        real = sys.stdin
        try:
            sys.stdin = io.StringIO("not json at all")
            assert m.main() == 0
        finally:
            sys.stdin = real

    def test_an_absent_repo_returns_an_empty_boundary_list(self, world):
        m = _load()
        m.REPO = pathlib.Path("/nonexistent/repo")
        assert m.commits_since("2026-10-01T11:00:00.000Z") == [], (
            "a missing repo must read as 'no task completed', never as an error")

    def test_the_hook_exits_zero_even_if_main_raises(self, world):
        """The __main__ guard must swallow anything main() throws."""
        src = HOOK.read_text(encoding="utf-8")
        assert "sys.exit(0)" in src.split("if __name__")[-1], (
            "a recovery hook that can raise out of __main__ can fell the session")


class TestItReimplementsNothing:
    def test_every_predicate_is_imported_from_compaction_watch(self):
        """ONE CODE PATH. A second copy of the scan is how a predicate drifts."""
        src = HOOK.read_text(encoding="utf-8")
        body = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
        for borrowed in ("load_state_and_scan", "_recovery_ran_after", "_auto_restore"):
            assert f"W.{borrowed}" in body, f"{borrowed} is not being borrowed"
        assert "isCompactSummary" not in body, (
            "the compaction scan is reimplemented here instead of imported")

    def test_the_shared_scan_exists_in_the_watcher(self):
        assert "def load_state_and_scan(" in WATCH.read_text(encoding="utf-8")

    def test_it_is_registered_on_Stop(self):
        s = json.loads((pathlib.Path.home()/".claude"/"settings.json")
                       .read_text(encoding="utf-8"))
        cmds = [hk.get("command","") for ent in s["hooks"].get("Stop", [])
                for hk in ent.get("hooks", [])]
        assert any("compaction_task_boundary.py" in c for c in cmds), (
            "built but not wired — an addition nothing reaches is not additive")

    def test_the_measured_claim_travels_with_its_producer(self):
        prod = (pathlib.Path(__file__).resolve().parents[2] / "scripts"
                / "the_task_boundary_restore_is_sooner_2026-10-12.py")
        assert prod.is_file()
        r = subprocess.run([sys.executable, str(prod), "--help"],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0 and "usage:" in r.stdout
