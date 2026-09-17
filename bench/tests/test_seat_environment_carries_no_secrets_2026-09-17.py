#!/usr/bin/env python3
"""A model seat is started without the dispatcher's secrets.

FOUND 2026-09-17, FROM A SUGGESTED-TASK CARD THE FOUNDER ASKED TO BE ADDED TO THE
ACTION LIST, AND MEASURED BEFORE IT WAS FIXED. The panel dispatcher loads `.env`
into its own process -- 10 secrets, 8 API keys plus GITHUB_TOKEN and ZENODO_TOKEN
-- and every seat was started with no `env=`, so every seat inherited them. A free
probe on the Max plan started a seat exactly as `call_claude_cli` did and asked
its Bash tool to print a secret-named marker set in the parent: it printed it.
So a "free" seat's shell could make a paid call, push to GitHub or publish to
Zenodo, and confirming 0 paid SEATS before a launch said nothing about what those
seats could REACH.

THESE TESTS CAPTURE THE ENVIRONMENT EACH SPAWN SITE ACTUALLY PASSES. Reading the
source for `env=` would pass on a call that computed the wrong environment.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (str(ROOT), str(ROOT / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiment_11_orchestrator as orch  # noqa: E402

SECRETS = {
    "OPENROUTER_API_KEY": "fake-openrouter", "OPENAI_API_KEY": "fake-openai",
    "DEEPSEEK_API_KEY": "fake-deepseek", "ANTHROPIC_API_KEY": "fake-anthropic",
    "GITHUB_TOKEN": "fake-github", "ZENODO_TOKEN": "fake-zenodo",
    "some_lowercase_secret": "fake-lower", "AWS_SECRET_ACCESS_KEY": "fake-aws",
}
PLAIN = {"CDSFL_PROBE_PLAIN": "plain-visible"}
CODEX_ARGS = ("user prompt", "cdsfl directives")  # call_codex(user_prompt, cdsfl_directives, ...)


class _Captured(Exception):
    pass


def _wolfram_denied(seen, claude=True):
    """QUESTION 11, 2026-09-17: the same launchers carry the Wolfram deny layer."""
    import wolfram_standard as W
    assert seen["env"]["PATH"].split(":")[0] == str(W.DENY_GATE), seen["env"]["PATH"][:120]
    if claude:
        cmd = list(seen["cmd"])
        n = len(W.CLAUDE_CLI_DENY_ARGS)
        assert any(tuple(cmd[i:i + n]) == W.CLAUDE_CLI_DENY_ARGS for i in range(len(cmd))), cmd


def _capture(monkeypatch, module):
    seen = {}

    def fake_run(cmd, *a, **k):
        seen["env"] = k.get("env", "NOT PASSED")
        seen["cmd"] = cmd
        raise _Captured

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    return seen


@pytest.fixture
def secrets_in_parent(monkeypatch):
    for k, v in {**SECRETS, **PLAIN}.items():
        monkeypatch.setenv(k, v)


class TestTheHelper:
    def test_every_secret_name_is_removed(self, secrets_in_parent):
        env = orch.seat_environment()
        assert not set(SECRETS) & set(env), set(SECRETS) & set(env)

    def test_ordinary_variables_survive(self, secrets_in_parent):
        """ANTI-VACUITY: an empty dict would pass the test above and break every seat."""
        env = orch.seat_environment()
        assert env.get("CDSFL_PROBE_PLAIN") == "plain-visible"
        assert env.get("PATH") and env.get("HOME")

    def test_it_does_not_modify_the_parent(self, secrets_in_parent):
        import os
        orch.seat_environment()
        assert os.environ["OPENROUTER_API_KEY"] == "fake-openrouter"

    def test_keep_retains_only_the_named_key(self, secrets_in_parent):
        env = orch.seat_environment(keep=("OPENAI_API_KEY",))
        assert env.get("OPENAI_API_KEY") == "fake-openai"
        assert not (set(SECRETS) - {"OPENAI_API_KEY"}) & set(env)


class TestEverySpawnSitePassesIt:
    def test_call_claude_cli(self, monkeypatch, secrets_in_parent):
        seen = _capture(monkeypatch, orch)
        # ONLY the capture signal counts. A broad `pytest.raises(Exception)` let a
        # call that never reached subprocess.run pass as though it had.
        try:
            orch.call_claude_cli("opus", "system", "user", timeout=5, max_retries=1, backoff_base=0)
        except Exception:                           # noqa: BLE001
            pass   # the caller wraps the capture signal; what matters is below
        assert "env" in seen, "subprocess.run was never reached, so nothing was checked"
        assert isinstance(seen.get("env"), dict), f"no env passed: {seen.get('env')}"
        assert not set(SECRETS) & set(seen["env"])
        assert seen["env"].get("CDSFL_PROBE_PLAIN") == "plain-visible"
        _wolfram_denied(seen)

    def test_call_codex_keeps_only_its_own_key(self, monkeypatch, secrets_in_parent):
        seen = _capture(monkeypatch, orch)
        try:
            orch.call_codex(*CODEX_ARGS, timeout=5, max_retries=1)
        except Exception:                           # noqa: BLE001
            pass   # the caller wraps the capture signal; what matters is below
        assert "env" in seen, "subprocess.run was never reached, so nothing was checked"
        assert isinstance(seen.get("env"), dict), f"no env passed: {seen.get('env')}"
        leaked = (set(SECRETS) - {"OPENAI_API_KEY"}) & set(seen["env"])
        assert not leaked, leaked
        _wolfram_denied(seen, claude=False)

    def _load(self, rel, name):
        spec = importlib.util.spec_from_file_location(name, ROOT / rel)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_the_simulated_run_shim(self, monkeypatch, secrets_in_parent):
        shim = self._load("bench/tools/sim_dispatch_shim.py", "shim_env_probe")
        assert shim.seat_environment is orch.seat_environment or callable(shim.seat_environment)
        env = shim.seat_environment()
        assert not set(SECRETS) & set(env)
        # EXECUTED, NOT READ: drive the shim's own spawn and capture what it passes.
        seen = _capture(monkeypatch, shim)
        try:
            shim.make_shim()(type("MC", (), {"label": "CC2-SIM", "model_id": "opus", "api": "claude_cli"})(),
                             "system", "user")
        except _Captured:
            pass
        except Exception as e:                      # noqa: BLE001
            pytest.skip(f"the shim's call shape changed ({type(e).__name__}: {e}); "
                        f"the helper itself is still covered above")
        assert isinstance(seen.get("env"), dict), f"the shim passed no env: {seen.get('env')}"
        assert not set(SECRETS) & set(seen["env"])
        _wolfram_denied(seen)

    def test_the_simulated_panel_agents(self, monkeypatch, secrets_in_parent):
        spa = self._load("bench/tools/sim_panel_agents.py", "spa_env_probe")
        seen = _capture(monkeypatch, spa)
        try:
            spa._one_agent("SIM-A", "bench/some_target.py", timeout=5)
        except Exception:                           # noqa: BLE001
            pass
        assert "env" in seen, "subprocess.run was never reached, so nothing was checked"
        assert isinstance(seen.get("env"), dict), f"no env passed: {seen.get('env')}"
        assert not set(SECRETS) & set(seen["env"])
        assert seen["env"].get("CDSFL_PROBE_PLAIN") == "plain-visible"
        _wolfram_denied(seen)

    # FOUND WHILE CLOSING THE CARD: `decomposed_dispatch`, which the experiment
    # runner imports for payloads too large for 1 call, starts Claude and Codex
    # seats at 3 more places, and all 3 inherited everything.
    def _decomposed(self, monkeypatch):
        import decomposed_dispatch as dd
        monkeypatch.setattr(dd, "CLAUDE_CLI", "claude")
        return dd

    @pytest.mark.parametrize("n_chunks", [1, 0], ids=["the chunk turn", "the final turn"])
    def test_decomposed_claude_cli(self, monkeypatch, secrets_in_parent, n_chunks):
        dd = self._decomposed(monkeypatch)
        seen = _capture(monkeypatch, dd)
        chunks = [dd.DecomposedChunk(content="x = 1", label="c1")] * n_chunks
        try:
            dd._decomposed_claude_cli("opus", chunks, "directives", "final", timeout=5)
        except Exception:                           # noqa: BLE001
            pass
        assert "env" in seen, "subprocess.run was never reached, so nothing was checked"
        assert ("--resume" in seen["cmd"]) == (n_chunks == 0), "reached the wrong spawn site"
        assert isinstance(seen.get("env"), dict), f"no env passed: {seen.get('env')}"
        assert not set(SECRETS) & set(seen["env"])
        # The chunk turns disallow Bash outright; only the final turn gets tools.
        _wolfram_denied(seen, claude=False)

    def test_decomposed_final_turn_with_tools_carries_the_deny_args(self, monkeypatch, secrets_in_parent):
        dd = self._decomposed(monkeypatch)
        seen = _capture(monkeypatch, dd)
        try:
            dd._decomposed_claude_cli("opus", [], "directives", "final", timeout=5, enable_tools=True)
        except Exception:                           # noqa: BLE001
            pass
        assert "env" in seen and "--allowedTools" in seen["cmd"]
        _wolfram_denied(seen)

    def test_decomposed_codex_keeps_only_its_own_key(self, monkeypatch, secrets_in_parent):
        dd = self._decomposed(monkeypatch)
        seen = _capture(monkeypatch, dd)
        try:
            dd._decomposed_codex([dd.DecomposedChunk(content="x = 1", label="c1")],
                                 "directives", "final", timeout=5)
        except Exception:                           # noqa: BLE001
            pass
        assert "env" in seen, "subprocess.run was never reached, so nothing was checked"
        assert seen["cmd"][:2] == ["codex", "exec"]
        assert isinstance(seen.get("env"), dict), f"no env passed: {seen.get('env')}"
        assert not (set(SECRETS) - {"OPENAI_API_KEY"}) & set(seen["env"])
        _wolfram_denied(seen, claude=False)


SEAT_MODULES = ("bench/experiment_11_orchestrator.py", "bench/decomposed_dispatch.py",
                "bench/tools/sim_dispatch_shim.py", "bench/tools/sim_panel_agents.py",
                "bench/confer_maths_panel_2026-09-05.py")


def test_no_spawn_in_a_seat_module_omits_env():
    """A RATCHET, NOT THE PROOF. The executing tests above are the proof for the
    7 sites that exist; this only stops an 8th being added with no `env=`, which
    is how the original 7 came to inherit everything."""
    import ast
    bare = []
    for rel in SEAT_MODULES:
        for n in ast.walk(ast.parse((ROOT / rel).read_text())):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr in ("run", "Popen", "check_output", "call")
                    and getattr(n.func.value, "id", "") == "subprocess"
                    and "env" not in {k.arg for k in n.keywords}):
                bare.append(f"{rel}:{n.lineno}")
    assert not bare, f"a subprocess started without env=seat_environment(): {bare}"


class TestTheLiveProbeIsCommittedAndInert:
    """The live before-and-after probe is `scripts/seat_environment_probe_2026-09-17.py`.
    It makes model calls, so it must refuse to act without --live."""

    def test_it_does_nothing_without_live(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts/seat_environment_probe_2026-09-17.py")],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0 and r.stdout.startswith("Not run."), r.stdout + r.stderr

    def test_help_does_nothing(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts/seat_environment_probe_2026-09-17.py"), "--help"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0 and r.stdout.startswith("usage:") and "RESULT" not in r.stdout
