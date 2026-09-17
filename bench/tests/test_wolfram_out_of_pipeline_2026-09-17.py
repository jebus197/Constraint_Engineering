#!/usr/bin/env python3
"""No automated path can start the Wolfram kernel by accident. Executed, not read.

QUESTION 11, 2026-09-17. A read-only audit that morning ran a FAKE executable
named `wolframscript` and reached it from 2 automated paths: the test suite's
network guard allowed the spawn, and `execute_python`, the sandbox model-written
falsifiers run in, returned FAKE-WOLFRAMSCRIPT-REACHED. The seat launchers are
covered in test_seat_environment_carries_no_secrets_2026-09-17.py, and a real
`claude -p` seat by scripts/wolfram_seat_deny_probe_2026-09-17.py.

Every probe here uses a fake that writes a marker file when it runs, so "not
reached" is a file that does not exist rather than a message that did not print.
The real kernel is never started.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (str(ROOT), str(ROOT / "bench"), str(ROOT / "bench" / "tests")):
    if p not in sys.path:
        sys.path.insert(0, p)

import conftest as G  # noqa: E402
import falsifier_verify as FV  # noqa: E402
import wolfram_standard as W  # noqa: E402


@pytest.fixture
def fake(tmp_path):
    marker = tmp_path / "REACHED"
    b = tmp_path / "bin" / "wolframscript"
    b.parent.mkdir()
    b.write_text(f"#!/bin/sh\ntouch '{marker}'\necho FAKE-WOLFRAMSCRIPT-REACHED\n")
    b.chmod(0o755)
    return b, marker


class TestTheSuiteCannotStartIt:
    @pytest.mark.allow_outbound   # the subject IS the guard's refusal
    def test_by_name_and_by_absolute_path(self, fake):
        if not G.netguard_active():
            pytest.skip("netguard is not installed in this session (live dispatch opted in)")
        binary, marker = fake
        for argv in (["wolframscript", "-code", "1+1"], [str(binary), "-code", "1+1"],
                     ["WolframKernel", "-noprompt"]):
            with pytest.raises(FileNotFoundError, match="netguard denied"):
                subprocess.run(argv, capture_output=True, timeout=10)
        assert not marker.exists()

    def test_control_an_ordinary_binary_still_runs(self):
        assert subprocess.run(["true"], timeout=10).returncode == 0


class TestTheFalsifierSandboxRefusesIt:
    """STILL refuses, under either policy, and now for the founder's own reason
    rather than a blanket one: a falsifier is a stored artefact that anyone must
    be able to re-run without Wolfram installed (2026-09-17), and falsifiers run
    in parallel against 1 licensed kernel. The MODEL that writes a falsifier is
    free to use Wolfram itself, through the serial gate on its own PATH."""

    @pytest.mark.parametrize("form", ["absolute", "bash -c", "os.system", "Popen by name"])
    def test_every_spawn_form(self, fake, form):
        binary, marker = fake
        code = {
            "absolute": f"import subprocess; subprocess.run([{str(binary)!r}, '-code', '1+1'])",
            "bash -c": f"import subprocess; subprocess.run(['bash', '-c', {str(binary) + ' -code 1+1'!r}])",
            "os.system": "import os; os.system('wolframscript -code 1+1')",
            "Popen by name": "import subprocess; subprocess.Popen(['wolframscript', '-code', '1+1']).wait()",
        }[form]
        out = FV.execute_python(code, repo_root=str(ROOT))
        assert not marker.exists(), f"{form}: the fake kernel ran"
        assert "FAKE-WOLFRAMSCRIPT-REACHED" not in out
        assert out == W.SANDBOX_REFUSAL, out

    def test_control_an_ordinary_spawn_still_runs(self):
        out = FV.execute_python("import subprocess; print(subprocess.run(['echo', 'ok'], "
                                "capture_output=True, text=True).stdout.strip())", repo_root=str(ROOT))
        assert out == "ok", out

    def test_reverify_calls_it_error_not_a_verdict_and_not_an_integrity_fault(self, fake):
        binary, marker = fake
        code = (f"import subprocess\nr = subprocess.run([{str(binary)!r}, '-code', '1+1'], "
                "capture_output=True, text=True)\nassert r.stdout.strip() == '2', 'FALSIFIED'\n")
        verdict = FV.reverify_falsifier(code, repo_root=str(ROOT))
        assert not marker.exists()
        assert verdict == "ERROR", verdict

    def test_the_sandbox_environment_carries_no_secret_and_the_gate_first(self, monkeypatch, tmp_path):
        monkeypatch.setenv("OPENROUTER_API_KEY", "fake-openrouter")
        monkeypatch.setenv("ZENODO_TOKEN", "fake-zenodo")
        env = FV._sandbox_env(str(ROOT), bootstrap=str(tmp_path))
        assert "OPENROUTER_API_KEY" not in env and "ZENODO_TOKEN" not in env
        assert env["PATH"].split(":")[0] == str(W.DENY_GATE)
        assert env["PYTHONPATH"].split(":")[0] == str(tmp_path)


class TestEveryPanelSeatIsToldTheStandard:
    """Seats run with `--setting-sources ""`, so the standard in .claude/CLAUDE.md
    never reached them. It now travels in the dispatcher's SYSTEM string."""

    @pytest.fixture(scope="class")
    def system(self):
        import importlib.util
        import os
        old = os.environ.get("PANEL_ONLY")
        os.environ["PANEL_ONLY"] = "__none__"
        try:
            spec = importlib.util.spec_from_file_location(
                "_cmp_wolfram_probe", ROOT / "bench" / "confer_maths_panel_2026-09-05.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            assert mod.MODELS == [], "the probe import would have selected seats"
            return mod.SYSTEM
        finally:
            if old is None:
                os.environ.pop("PANEL_ONLY", None)
            else:
                os.environ["PANEL_ONLY"] = old

    def test_the_clause_is_in_the_real_system_string(self, system):
        assert W.panel_clause() in system

    def test_the_clause_states_the_rule_the_code_applies(self):
        # The failure shapes are the same under either policy; what changes is
        # whether the seat is told to use the tool or to leave it alone, which
        # test_wolfram_secondary_source_2026-09-17.py holds for both.
        for clause in (W.SERIAL_CLAUSE, W.DENY_CLAUSE):
            for prefix in W.FAILURE_PREFIXES:
                assert prefix in clause
            for needle in ("Out[", "UNVERIFIED", "Name::tag", "$Failed", "attribution"):
                assert needle in clause, needle
        assert "Do not run `wolframscript`" in W.DENY_CLAUSE
