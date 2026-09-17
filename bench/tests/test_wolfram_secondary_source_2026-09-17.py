#!/usr/bin/env python3
"""Wolfram is enabled as the SECOND falsifier, queued against 1 kernel. Executed.

FOUNDER, 2026-09-17, reversing the default that shipped that morning: *"So fully
enable it. But we don't depend just on Wolfram ... Wolfram, although it should
always be used wherever possible, should remain the secondary/verification
source (a second falsifier), where our other relevant tools should also aways be
used and should remain primary in all cases"*, and *"Agents are not exempt from
using tools ... Every model and every agent should use tools wherever possible,
including Wolfram."*

EVERY TEST HERE CALLS THE THING IT IS ABOUT. The gate's entry point is run as a
subprocess against a FAKE `wolframscript` that records when it started and when
it stopped, so "serialised" is 2 disjoint intervals measured from the child's own
clock, not a claim about a lock.

THE REAL KERNEL IS NEVER STARTED, TWICE OVER. The fake's directory is the only
place on the test PATH holding that name -- the installed binary is at
/usr/local/bin, which is not on it -- and the suite's network guard denies a
spawn named `wolframscript` outright, which is asserted here rather than worked
around. That guard is why these tests run `bench/wolfram_standard.py serial`
directly instead of the 2-line shim a seat reaches: the shim IS a spawn of that
name. The shim is proved end-to-end against the real Engine, outside the suite,
by `scripts/wolfram_serial_gate_probe_2026-09-17.py`.

WHAT WOULD FALSIFY THE CENTRAL CLAIM. Remove the lock from `run_gated` and
`test_2_concurrent_calls_do_not_overlap` fails, because the fake's intervals
overlap. That is the whole reason the route is safe to enable: 3 concurrent
calls measured on 2026-08-02 gave 1 result and 2 "Connection closed by
WolframKernel".
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (str(ROOT), str(ROOT / "bench"), str(ROOT / "bench" / "tests")):
    if p not in sys.path:
        sys.path.insert(0, p)

import conftest as G  # noqa: E402
import experiment_11_orchestrator as ORCH  # noqa: E402
import wolfram_standard as W  # noqa: E402

GATE = W.SERIAL_GATE / "wolframscript"           # what a seat reaches
ENTRY = ROOT / "bench" / "wolfram_standard.py"   # what the shim execs, and what runs here

#: A fake kernel that reports its own start and end times and what it was given.
FAKE = """#!/usr/bin/env python3
import json, os, sys, time
start = time.time()
time.sleep(float(os.environ.get("FAKE_WOLFRAM_SLEEP", "0.4")))
with open(os.environ["FAKE_WOLFRAM_LOG"], "a") as fh:
    fh.write(json.dumps({"start": start, "end": time.time(), "args": sys.argv[1:]}) + "\\n")
sys.stdout.write(os.environ.get("FAKE_WOLFRAM_OUT", "4") + "\\n")
sys.stderr.write(os.environ.get("FAKE_WOLFRAM_ERR", ""))
sys.exit(int(os.environ.get("FAKE_WOLFRAM_EXIT", "0")))
"""


@pytest.fixture
def kernel(tmp_path):
    """A fake `wolframscript` on PATH, a private lock, and a private call log."""
    b = tmp_path / "bin" / "wolframscript"
    b.parent.mkdir()
    b.write_text(FAKE)
    b.chmod(0o755)
    env = dict(os.environ)
    env.update({
        # THE REAL KERNEL IS UNREACHABLE BY CONSTRUCTION, not by intention:
        # `wolframscript` is installed at /usr/local/bin only, which is not on
        # this PATH at all, and the fake is first. /usr/bin carries the python3
        # the gate runs under.
        "PATH": f"{b.parent}:/usr/bin:/bin",
        "FAKE_WOLFRAM_LOG": str(tmp_path / "calls.jsonl"),
        W.LOCK_ENV: str(tmp_path / "kernel.lock"),
        W.CALL_LOG_ENV: str(tmp_path / "gate.log"),
        "CDSFL_SEAT": "test-seat",
    })
    return {"env": env, "log": tmp_path / "calls.jsonl", "gate_log": tmp_path / "gate.log"}


def _run(kernel, args=("-code", "1+1"), **over):
    """Run the gate exactly as its shim does: same entry, same arguments."""
    env = dict(kernel["env"], **over)
    return subprocess.run([sys.executable, str(ENTRY), "serial", "--tool", "wolframscript",
                           "--", *args], capture_output=True, text=True, timeout=120, env=env)


class TestTheGateRunsTheKernelRatherThanRefusingIt:
    def test_it_passes_the_arguments_through_verbatim(self, kernel):
        r = _run(kernel, ("-code", "Integrate[x^2, x]"))
        assert r.returncode == 0
        assert r.stdout.strip() == "4"
        got = [json.loads(line) for line in kernel["log"].read_text().splitlines()]
        assert got[0]["args"] == ["-code", "Integrate[x^2, x]"], got

    def test_it_passes_the_exit_code_through_untouched(self, kernel):
        assert _run(kernel, FAKE_WOLFRAM_EXIT="7").returncode == 7

    def test_a_call_that_computed_carries_the_attribution_wolfram_requires(self, kernel):
        r = _run(kernel)
        assert W.attribution("local") in r.stderr

    def test_a_call_that_verified_nothing_is_marked_not_evidence(self, kernel):
        # A local kernel exits 0 on `1/0` while printing `Power::infy`, so the
        # exit code cannot carry this and the gate must annotate it.
        r = _run(kernel, FAKE_WOLFRAM_OUT="Power::infy: Infinite expression encountered.")
        assert r.returncode == 0, "the child's own exit code must survive"
        assert "[NOT EVIDENCE]" in r.stderr and "UNVERIFIED" in r.stderr
        assert W.attribution("local") not in r.stderr


class TestItIsQueuedAgainstTheSingleLicensedKernel:
    def test_2_concurrent_calls_do_not_overlap(self, kernel):
        results = []
        threads = [threading.Thread(target=lambda: results.append(_run(kernel)))
                   for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=120)
        assert [r.returncode for r in results] == [0, 0]
        calls = sorted((json.loads(line) for line in kernel["log"].read_text().splitlines()),
                       key=lambda c: c["start"])
        assert len(calls) == 2, calls
        assert calls[0]["end"] <= calls[1]["start"], (
            "the 2 calls overlapped: 1 licensed kernel was handed 2 at once")

    def test_a_held_queue_is_reported_as_not_a_blocker_and_never_calls_the_kernel(self, kernel):
        holder = threading.Event()
        done = threading.Event()

        def hold():
            with W.kernel_lock(wait=30, env=kernel["env"]) as got:
                assert got
                holder.set()
                done.wait(timeout=30)

        t = threading.Thread(target=hold)
        t.start()
        try:
            assert holder.wait(timeout=30)
            r = _run(kernel, **{W.LOCK_WAIT_ENV: "0.3"})
            assert r.returncode == W.BUSY_EXIT
            assert "NOT a blocker" in r.stderr
            assert not kernel["log"].exists(), "the kernel was called without the lock"
        finally:
            done.set()
            t.join(timeout=30)

    def test_run_local_honours_the_same_queue_and_makes_0_calls_when_busy(self, kernel):
        calls = []

        def runner(*a, **k):
            calls.append(a)
            raise AssertionError("run_local called the kernel while the queue was held")

        holder, done = threading.Event(), threading.Event()

        def hold():
            with W.kernel_lock(wait=30, env=kernel["env"]) as got:
                assert got
                holder.set()
                done.wait(timeout=30)

        t = threading.Thread(target=hold)
        t.start()
        try:
            assert holder.wait(timeout=30)
            os.environ[W.LOCK_ENV] = kernel["env"][W.LOCK_ENV]
            try:
                out = W.run_local("1+1", runner=runner, script="/bin/true", lock_wait=0.3)
            finally:
                os.environ.pop(W.LOCK_ENV, None)
            assert out["evidence"] is False and calls == []
            assert "queue" in out["reason"] and "not a blocker" in out["reason"]
        finally:
            done.set()
            t.join(timeout=30)

    def test_the_lock_path_cannot_move_with_a_rewritten_home_or_tmpdir(self):
        # 2 processes locking 2 different files are not serialised at all, and
        # both HOME and TMPDIR are rewritten in places in this project.
        assert os.path.isabs(W.LOCK_PATH)
        for var in ("HOME", "TMPDIR", "TMP", "TEMP"):
            assert var not in W.LOCK_PATH


class TestWolframIsNeverADependency:
    def test_an_absent_kernel_is_reported_as_not_a_blocker(self, kernel):
        r = _run(kernel, PATH="/usr/bin:/bin")
        assert r.returncode == 127
        assert "NOT a blocker" in r.stderr
        for tool in ("SymPy", "z3", "mpmath"):
            assert tool in r.stderr, "the fallback has to name the tools that are primary"

    def test_every_gated_call_is_recorded_so_the_route_can_be_measured(self, kernel):
        _run(kernel)
        _run(kernel, FAKE_WOLFRAM_OUT="Power::infy: Infinite expression encountered.")
        lines = kernel["gate_log"].read_text().splitlines()
        assert len(lines) == 2, lines
        assert "test-seat" in lines[0] and "EVIDENCE" in lines[0]
        assert "NOT_EVIDENCE" in lines[1]


class TestThePolicyReachesSeatsAndAgents:
    def test_the_default_is_serial_and_deny_is_still_selectable(self):
        assert W.policy({}) == "serial" == W.DEFAULT_POLICY
        assert W.policy({W.POLICY_ENV: "deny"}) == "deny"
        with pytest.raises(ValueError):
            W.policy({W.POLICY_ENV: "off"})

    @pytest.mark.parametrize("pol,gate", [("serial", W.SERIAL_GATE), ("deny", W.DENY_GATE)])
    def test_the_seat_path_carries_the_policys_gate_and_only_that_one(self, pol, gate):
        env = ORCH.seat_environment({"PATH": f"{W.DENY_GATE}:{W.SERIAL_GATE}:/usr/bin",
                                     W.POLICY_ENV: pol})
        parts = env["PATH"].split(os.pathsep)
        assert parts[0] == str(gate)
        assert parts.count(str(W.DENY_GATE)) + parts.count(str(W.SERIAL_GATE)) == 1
        assert "/usr/bin" in parts

    def test_a_serial_seat_is_not_told_to_refuse_the_tool_it_is_told_to_use(self):
        args = W.claude_cli_args("serial")
        assert "--disallowedTools" not in args
        assert all("wolframscript" not in a for a in args)
        assert "--disallowedTools" in W.claude_cli_args("deny")

    def test_the_gate_on_a_seats_path_is_executable_under_both_policies(self):
        for gate in (W.SERIAL_GATE, W.DENY_GATE):
            for name in ("wolframscript", "WolframKernel"):
                assert os.access(gate / name, os.X_OK), f"{gate.name}/{name}"

    def test_the_shim_execs_the_entry_point_these_tests_drive(self):
        # The shim is 2 lines of sh, and the suite may not run it (the netguard
        # denies the name), so this is the 1 place a text check is the only
        # option. What it asserts is the JOIN between the 2: that the shim
        # reaches `wolfram_standard.py serial`, which every test above executes.
        assert subprocess.run(["/bin/sh", "-n", str(GATE)], timeout=30).returncode == 0
        text = GATE.read_text()
        assert "wolfram_standard.py" in text and "serial" in text
        assert "--tool wolframscript" in text and '"$@"' in text

    @pytest.mark.allow_outbound   # the subject IS the guard's refusal
    def test_the_suite_still_cannot_start_a_kernel_through_the_gate(self, kernel):
        if not G.netguard_active():
            pytest.skip("netguard is not installed in this session (live dispatch opted in)")
        with pytest.raises(FileNotFoundError, match="netguard denied"):
            subprocess.run([str(GATE), "-code", "1+1"], capture_output=True,
                           timeout=30, env=kernel["env"])
        assert not kernel["log"].exists()

    @pytest.mark.parametrize("pol", ["serial", "deny"])
    def test_what_a_seat_is_told_matches_what_the_launcher_does(self, pol):
        clause = W.panel_clause(pol)
        if pol == "serial":
            assert "SECOND falsifier" in clause and "never a dependency" in clause
            assert "SymPy, z3, mpmath" in clause and "PRIMARY" in clause
            assert "Do not run `wolframscript`" not in clause
        else:
            assert "Do not run `wolframscript`" in clause
            assert "SECOND falsifier" not in clause
        for needle in ("UNVERIFIED", "Name::tag", "$Failed", "attribution", "Out["):
            assert needle in clause, needle
        for prefix in W.FAILURE_PREFIXES:
            assert prefix in clause

    def test_the_dispatchers_system_prompt_carries_the_clause_in_force(self):
        import importlib.util
        old = {k: os.environ.get(k) for k in ("PANEL_ONLY",)}
        os.environ["PANEL_ONLY"] = "__none__"
        try:
            spec = importlib.util.spec_from_file_location(
                "_cmp_wolfram_serial_probe", ROOT / "bench" / "confer_maths_panel_2026-09-05.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            assert mod.MODELS == [], "the probe import would have selected seats"
            assert W.panel_clause() in mod.SYSTEM
        finally:
            for k, v in old.items():
                os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)


class TestTheStoredFalsifierStaysOnDeny:
    """The 1 exception, and it is the founder's own condition rather than a
    preference: a falsifier is re-run by whoever reproduces the experiment, and
    "anyone running the project should not be required to install Wolfram"."""

    def test_the_sandbox_path_carries_the_refusing_gate_whatever_the_policy_is(self, monkeypatch):
        import falsifier_verify as FV
        for pol in ("serial", "deny"):
            monkeypatch.setenv(W.POLICY_ENV, pol)
            env = FV._sandbox_env(str(ROOT))
            assert env["PATH"].split(os.pathsep)[0] == str(W.DENY_GATE), pol

    def test_the_refusal_says_why_and_points_at_the_tools_that_are_primary(self):
        for needle in ("re-run without Wolfram", "in parallel", "SymPy", "UNVERIFIED"):
            assert needle in W.SANDBOX_REFUSAL, needle
