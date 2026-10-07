#!/usr/bin/env python3
"""A seat cannot WRITE the canonical tree, proved by trying it.

THE GAP THIS CLOSES. `--allowedTools` withholds Write and Edit from every seat,
and `bench/experiment_11_orchestrator.py` has carried the comment "No file
modification" beside that flag since 2026-07-29. But Bash is granted -- it has
to be, because every STEM tool the seats are required to use runs through it --
and a shell redirection is not a tool call. `bench/panel_sandbox.py`'s own
header states the consequence: "The seat wrote anyway, through Bash, which no
tool-list can restrain." The cc2 seat reported the asymmetry again in the free
panel of 2026-09-30, where it was recorded as reported-and-unaddressed, and the
founder ruled: "Fix it."

WHAT WAS ALREADY THERE, AND WHY IT WAS NOT ENOUGH. Position (a sandbox COPY, so
every relative path is harmless) and DETECTION (a before/after fingerprint of
the canonical tree, so an absolute-path write is caught). Detection is not
prevention, and the founder's rule is prevention: "none of the models ... should
ever be able to reach the real repo, let alone edit it."

HOW THIS FILE TESTS IT. By EXECUTION, per `execute-do-not-grep`. A test that
read the profile text would prove only that the profile describes itself. Each
test below runs a real shell under the real control and asserts on what happened
to the real filesystem -- including that no probe file survives.

Run:  python3 -m pytest bench/tests/test_seat_cannot_write_the_canonical_tree_2026-10-01.py -q
"""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench import panel_sandbox as PS  # noqa: E402

#: Written INTO the canonical tree by the escape probes, and asserted absent
#: afterwards. Named so that a survivor is unmistakable in `git status`.
PROBE = REPO / "CANONICAL_WRITE_ESCAPE_PROBE_2026-10-01.tmp"

pytestmark = pytest.mark.skipif(
    shutil.which("sandbox-exec") is None,
    reason="no sandbox-exec on this host; confinement degrades to detection and "
           "`confine` reports NO_CONFINEMENT, which its own test below covers",
)


@pytest.fixture(autouse=True)
def _no_probe_survives():
    """A probe file left in the canonical tree would be a real escape."""
    if PROBE.exists():
        PROBE.unlink()
    yield
    assert not PROBE.exists(), (
        f"{PROBE} survived the test: a write reached the canonical tree")


def _run_confined(script: str, cwd: pathlib.Path) -> subprocess.CompletedProcess:
    argv, mech = PS.confine(["/bin/bash", "-c", script], REPO, cwd)
    assert mech == PS.CONFINED, f"confinement did not apply: {mech}"
    return subprocess.run(argv, cwd=str(cwd), capture_output=True,
                          text=True, timeout=120)


class TestTheCanonicalTreeIsNotWritable:
    def test_creating_a_new_file_in_the_canonical_tree_is_refused(self):
        with tempfile.TemporaryDirectory() as box:
            r = _run_confined(f"echo escaped > '{PROBE}'", pathlib.Path(box))
        assert r.returncode != 0, (
            f"the write succeeded; stdout={r.stdout!r} stderr={r.stderr!r}")
        assert "not permitted" in r.stderr.lower(), r.stderr[:300]
        assert not PROBE.exists()

    def test_appending_to_an_existing_tracked_file_is_refused(self):
        target = REPO / "README.md"
        if not target.is_file():
            pytest.skip("README.md absent")
        before = target.read_bytes()
        with tempfile.TemporaryDirectory() as box:
            r = _run_confined(f"echo x >> '{target}'", pathlib.Path(box))
        assert r.returncode != 0, r.stdout
        assert target.read_bytes() == before, (
            "README.md changed under a confined seat")

    def test_git_cannot_write_the_canonical_config(self):
        """The 2026-09-06 escape edited TRACKED FILES. git must be refused too.

        THE PROBE KEY IS UNIQUE PER RUN, AND THAT IS A REPAIR RATHER THAN A
        DECORATION. It was the fixed key `cdsfl.escapeprobe`, and the test never
        removed it. So a single historical lapse wrote a value that stayed in
        `.git/config` and failed this test on EVERY later run, for ever, while the
        confinement itself was working perfectly.

        Measured 2026-10-07: `cdsfl.escapeprobe` was present with value `1` and
        `.git/config` was last written on 2026-10-04 -- 3 days earlier -- while a
        live probe in the same minute was refused with "could not lock config file
        .git/config: Operation not permitted", exit 255, and left nothing behind.
        The guard was reporting a 3-day-old artefact of its own making as a current
        containment breach, which is the most expensive kind of false alarm: it
        makes a working control look broken.

        A unique key cannot collide with residue, so the assertion is about THIS
        run. The value is removed afterwards either way, so the test stops
        accumulating state in the repository it is checking.
        """
        key = f"cdsfl.escapeprobe{int(time.time() * 1000)}"
        try:
            with tempfile.TemporaryDirectory() as box:
                r = _run_confined(
                    f"git -C '{REPO}' config --local {key} 1",
                    pathlib.Path(box))
            combined = (r.stdout + r.stderr).lower()
            assert "not permitted" in combined or r.returncode != 0, combined[:300]
            got = subprocess.run(
                ["git", "-C", str(REPO), "config", "--local", "--get", key],
                capture_output=True, text=True)
            assert got.stdout.strip() == "", (
                f"a confined seat wrote the canonical git config ({key})")
        finally:
            subprocess.run(["git", "-C", str(REPO), "config", "--local",
                            "--unset", key], capture_output=True, text=True)

    def test_the_probe_would_be_visible_if_it_landed(self):
        """ANTI-VACUITY. The assertion above passes when the key is absent, and a
        key is absent when nothing wrote it OR when the read is broken. This writes
        one UNCONFINED and confirms the same read sees it, so an always-empty read
        cannot masquerade as containment."""
        key = f"cdsfl.readcheck{int(time.time() * 1000)}"
        try:
            subprocess.run(["git", "-C", str(REPO), "config", "--local", key, "1"],
                           capture_output=True, text=True, check=True)
            got = subprocess.run(
                ["git", "-C", str(REPO), "config", "--local", "--get", key],
                capture_output=True, text=True)
            assert got.stdout.strip() == "1", (
                "the read used by the containment assertion cannot see a value "
                "that IS there, so that assertion proves nothing")
        finally:
            subprocess.run(["git", "-C", str(REPO), "config", "--local",
                            "--unset", key], capture_output=True, text=True)


class TestWhatASeatMustStillBeAbleToDo:
    """A control that breaks the seat is not a control, it is an outage."""

    def test_a_seat_can_write_inside_its_own_sandbox(self):
        with tempfile.TemporaryDirectory() as box:
            r = _run_confined("echo ok > work.txt && cat work.txt",
                              pathlib.Path(box))
            assert r.returncode == 0, r.stderr[:300]
            assert r.stdout.strip() == "ok"
            assert (pathlib.Path(box) / "work.txt").is_file()

    def test_a_seat_can_still_read_the_canonical_tree(self):
        with tempfile.TemporaryDirectory() as box:
            r = _run_confined(f"head -1 '{REPO / 'README.md'}' >/dev/null "
                              f"&& echo readable", pathlib.Path(box))
        assert r.returncode == 0, r.stderr[:300]
        assert "readable" in r.stdout

    def test_the_stem_tools_still_run(self):
        """SymPy stays PRIMARY, so the control must not disturb it."""
        with tempfile.TemporaryDirectory() as box:
            r = _run_confined(
                "python3 -c 'import sympy, numpy; "
                "print(sympy.sqrt(16), numpy.mean([2,4,6]))'",
                pathlib.Path(box))
        assert r.returncode == 0, r.stderr[:400]
        assert "4 4.0" in r.stdout, r.stdout


class TestTheMechanismIsReportedAndNeverAssumed:
    def test_a_cwd_inside_the_canonical_tree_reports_that_it_cannot_confine(self):
        """`.claude/worktrees` is the live case: a blanket deny would break it."""
        argv, mech = PS.confine(["echo", "x"], REPO, REPO / ".claude")
        assert mech == PS.NOT_CONFINABLE
        assert argv == ["echo", "x"], "the command was altered anyway"

    def test_a_host_without_sandbox_exec_reports_the_absence(self, monkeypatch):
        monkeypatch.setattr(PS, "_sandbox_exec", lambda: None)
        with tempfile.TemporaryDirectory() as box:
            argv, mech = PS.confine(["echo", "x"], REPO, box)
        assert mech == PS.NO_CONFINEMENT
        assert argv == ["echo", "x"]
        assert "unavailable" in mech, (
            "the absence of the control must be readable in the record")

    def test_the_profile_uses_resolved_paths(self):
        """An unresolved /var path matches nothing, and that was measured."""
        with tempfile.TemporaryDirectory() as box:
            prof = PS.confinement_profile(REPO, pathlib.Path(box))
            text = prof.read_text(encoding="utf-8")
        assert str(REPO.resolve()) in text
        assert "deny file-write*" in text

    def test_the_dispatcher_actually_calls_it(self):
        """ANTI-UNREACHED-ADDITION. The control must be on the live path."""
        from bench.experiment_11_orchestrator import _confine_seat_command
        with tempfile.TemporaryDirectory() as box:
            argv, mech = _confine_seat_command(["echo", "x"], box)
        assert mech == PS.CONFINED, mech
        assert argv[0].endswith("sandbox-exec")

    def test_the_per_attempt_record_carries_the_mechanism(self):
        """The field a reader checks must exist on the live dispatch path.

        PARSED, NOT SEARCHED. The record is built inside a function that cannot
        run without a dispatch, so this cannot be executed -- but it can be
        read STRUCTURALLY, which a substring check is not: that would pass on a
        comment naming the field, and the project counts source-text
        assertions as a fragile class for exactly that reason.
        """
        import ast

        tree = ast.parse((REPO / "bench" / "experiment_11_orchestrator.py")
                         .read_text(encoding="utf-8"))
        pairs = [
            (k, v) for d in ast.walk(tree) if isinstance(d, ast.Dict)
            for k, v in zip(d.keys, d.values)
            if isinstance(k, ast.Constant) and k.value == "write_confinement"
        ]
        assert pairs, (
            "no dict literal in the dispatcher carries a `write_confinement` "
            "key, so nothing records which confinement was in force")
        names = [v.id for _k, v in pairs if isinstance(v, ast.Name)]
        assert names, (
            "the `write_confinement` key is present but its value is not the "
            "variable holding the mechanism, so the record may be a constant")
        assert any("confinement" in n for n in names), names


class TestTheControlPlaneIsNotAWayBackIn:
    """The config surfaces a LATER session executes are denied too.

    FOUND BY THE cc2 SEAT, 2026-10-01, running under this profile and attacking
    it as the brief asked: *"`~/.claude` is writable. A seat cannot write the
    repo, but it can write something the operator's NEXT session executes with
    full rights. The deny-list covers the artefact and not the agent that edits
    it."* It demonstrated the write and removed the file.

    That defeats the founder's rule without touching the repo, so it is the same
    finding one level out: a persistence route into the real tree by proxy.

    THE DENY IS SURGICAL BECAUSE A BLANKET ONE WAS ALREADY MEASURED TO BREAK THE
    SEAT. `~/.claude` holds both executed config and live CLI state. Only the
    executed surfaces are denied, and a real `claude -p` seat was run under the
    tightened profile afterwards to prove it still works.
    """

    EXECUTED = ("hooks", "plugins", "scheduled-tasks", "commands", "agents")
    EXECUTED_FILES = ("settings.json", "CLAUDE.md", "mcp_settings.json")
    STATE = ("cache", "sessions", "projects", "file-history", "debug")

    def _profile(self, box):
        prof = PS.confinement_profile(REPO, pathlib.Path(box))
        return prof.read_text(encoding="utf-8")

    def test_every_executed_surface_is_named_in_the_profile(self, tmp_path):
        text = self._profile(tmp_path)
        home = pathlib.Path(os.path.expanduser("~"))
        missing = [d for d in self.EXECUTED
                   if f'{home}/.claude/{d}"' not in text
                   and f'{(home / ".claude").resolve()}/{d}"' not in text]
        assert missing == [], f"executed surfaces left writable: {missing}"
        missing_f = [f for f in self.EXECUTED_FILES if f not in text]
        assert missing_f == [], f"executed config files left writable: {missing_f}"

    def test_a_write_to_the_hooks_directory_is_refused(self):
        """EXECUTED, not read off the profile text."""
        home = pathlib.Path(os.path.expanduser("~"))
        target = home / ".claude" / "hooks" / "_cdsfl_test_probe.tmp"
        if not (home / ".claude" / "hooks").is_dir():
            pytest.skip("no hooks directory on this machine")
        with tempfile.TemporaryDirectory() as box:
            r = _run_confined(f"echo escaped > '{target}'", pathlib.Path(box))
        assert r.returncode != 0, (
            "a seat can write the operator's hooks, which the next session "
            "executes with full rights")
        assert not target.exists()

    def test_the_cli_state_directories_stay_writable(self):
        """A control that kills the seat is an outage, not a control."""
        home = pathlib.Path(os.path.expanduser("~"))
        live = [d for d in self.STATE if (home / ".claude" / d).is_dir()]
        if not live:
            pytest.skip("none of the state directories exist here")
        d = live[0]
        probe = home / ".claude" / d / "_cdsfl_test_probe.tmp"
        with tempfile.TemporaryDirectory() as box:
            r = _run_confined(
                f"echo ok > '{probe}' && rm -f '{probe}'", pathlib.Path(box))
        assert r.returncode == 0, (
            f"~/.claude/{d} is denied, but it is CLI state rather than executed "
            f"config; denying it breaks the seat. stderr: {r.stderr[:200]}")
        assert not probe.exists()
