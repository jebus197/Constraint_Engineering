#!/usr/bin/env python3
"""The Wolfram standard's shared helper does what `.claude/CLAUDE.md` says, by execution.

The local-kernel fixtures below are REAL outputs, captured 2026-09-17 from
`wolframscript -code ...` on the local Wolfram Engine, 1 call at a time, and
computed with Wolfram Language. 2 of them are the reason the rule is per route:
`1/0` and the incomplete expression `f[` both EXIT 0 while printing a Wolfram
message, so an exit-code check alone counts them as results.

No test here starts the kernel. `run_local` is driven through an injected runner.
"""
from __future__ import annotations

import datetime as dt
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))

import wolfram_standard as W  # noqa: E402

# (code, stdout, exit code, is_evidence) as the local kernel returned them.
REAL_LOCAL = [
    ("1+1", "2", 0, True),
    ("Integrate[x^2, {x, 0, 1}]", "1/3", 0, True),
    ("$LicenseExpirationDate", "DateObject[{2026, 10, 8}, Day]", 0, True),
    ("1/0", "                                 1\nPower::infy: Infinite expression - encountered.\n"
            "                                 0\nComplexInfinity", 0, False),
    ("f[", "ToExpression::sntxi: Incomplete expression; more input is needed.", 0, False),
]


class TestClassify:
    @pytest.mark.parametrize("code,out,rc,want", REAL_LOCAL, ids=[r[0] for r in REAL_LOCAL])
    def test_real_local_outputs(self, code, out, rc, want):
        assert W.classify("local", out, rc)[0] is want

    @pytest.mark.parametrize("text,rc", [
        ("wolframscript: The Wolfram Engine is not activated or experiencing a license-related problem.", 1),
        ("Connection closed by WolframKernel", 0),
        ("WolframKernel location could not be determined", 0),
        ("$Failed", 0),
        ("$Aborted", 0),
        ("2", 1),
        ("", 0),
        ("[Timeout after 120s]", None),
        ("2", None),
    ])
    def test_local_failures_are_not_evidence(self, text, rc):
        ok, why = W.classify("local", text, rc)
        assert ok is False and why

    @pytest.mark.parametrize("text,want", [
        ("[HTTP Error 401]", False), ("[Timeout after 30s]", False), ("[Error] gateway", False),
        ("2", False), ("Out[1]= 2", True),
    ])
    def test_connector(self, text, want):
        assert W.classify("connector", text)[0] is want

    def test_an_unknown_route_is_refused(self):
        with pytest.raises(ValueError):
            W.classify("mcp", "Out[1]= 2", 0)


class TestAttribution:
    def test_every_route_names_wolfram(self):
        for route in ("local", "connector"):
            assert "Wolfram" in W.attribution(route)


class TestRunLocal:
    def _runner(self, results, calls):
        def run(cmd, **kw):
            calls.append(cmd)
            out, rc = results[min(len(calls), len(results)) - 1]
            return subprocess.CompletedProcess(cmd, rc, out, "")
        return run

    def test_a_transient_failure_is_retried_once(self):
        calls = []
        r = W.run_local("1+1", runner=self._runner([("Connection closed by WolframKernel", 1), ("2", 0)], calls),
                        script="/fake/wolframscript")
        assert r["evidence"] and r["attempts"] == 2 and len(calls) == 2
        assert "Wolfram" in r["attribution"]

    def test_a_persistent_failure_stops_after_2_calls(self):
        calls = []
        r = W.run_local("1+1", runner=self._runner([("$Failed", 0)], calls), script="/fake/wolframscript")
        assert not r["evidence"] and len(calls) == 2 and r["attribution"] is None

    def test_a_good_result_is_not_retried(self):
        calls = []
        r = W.run_local("1+1", runner=self._runner([("2", 0)], calls), script="/fake/wolframscript")
        assert r["evidence"] and len(calls) == 1

    def test_a_timeout_is_not_evidence(self):
        def run(cmd, **kw):
            raise subprocess.TimeoutExpired(cmd, 1)
        r = W.run_local("1+1", runner=run, script="/fake/wolframscript")
        assert not r["evidence"] and r["attempts"] == 2


class TestLicence:
    def test_parse(self):
        assert W.parse_licence_expiry("DateObject[{2026, 10, 8}, Day]") == W.RECORDED_LICENCE_EXPIRY

    @pytest.mark.parametrize("today,warns", [
        (dt.date(2026, 9, 17), False), (dt.date(2026, 9, 24), True),
        (dt.date(2026, 10, 8), True), (dt.date(2026, 10, 9), True)])
    def test_warning_window(self, today, warns):
        assert (W.licence_warning(today=today) is not None) is warns

    def test_expired_says_expired(self):
        assert "EXPIRED" in W.licence_warning(today=dt.date(2026, 10, 9))


class TestTheDenyLayer:
    @pytest.mark.parametrize("name", ["wolframscript", "WolframKernel"])
    def test_the_gate_refuses_with_the_modules_own_message(self, name):
        gate = W.DENY_GATE / name
        r = subprocess.run(["sh", str(gate), "-code", "1+1"], capture_output=True, text=True, timeout=30)
        assert r.returncode == 3 and r.stdout.strip() == W.DENY_MESSAGE

    def test_the_gate_is_executable(self):
        import os
        assert all(os.access(W.DENY_GATE / n, os.X_OK) for n in ("wolframscript", "WolframKernel"))

    def test_the_cli_deny_matches(self):
        r = subprocess.run([sys.executable, str(ROOT / "bench" / "wolfram_standard.py"), "deny"],
                           capture_output=True, text=True, timeout=30)
        assert r.returncode == 3 and r.stdout.strip() == W.DENY_MESSAGE

    def test_help_is_inert(self):
        r = subprocess.run([sys.executable, str(ROOT / "bench" / "wolfram_standard.py"), "--help"],
                           capture_output=True, text=True, timeout=30)
        assert r.returncode == 0 and W.DENY_MESSAGE not in r.stdout

    def test_gated_path_puts_the_gate_first_once(self):
        env = W.gated_path(W.gated_path({"PATH": "/usr/local/bin:/usr/bin"}))
        parts = env["PATH"].split(":")
        assert parts[0] == str(W.DENY_GATE) and parts.count(str(W.DENY_GATE)) == 1
        assert parts[1:] == ["/usr/local/bin", "/usr/bin"]

    def test_real_wolframscript_never_returns_a_gate(self, tmp_path):
        real = tmp_path / "bin" / "wolframscript"
        real.parent.mkdir()
        real.write_text("#!/bin/sh\n")
        real.chmod(0o755)
        found = W.real_wolframscript(f"{W.DENY_GATE}:{real.parent}")
        assert found == str(real)

    @pytest.mark.parametrize("blob,hit", [
        ("wolframscript -code 1+1", True), ("/usr/local/bin/wolframscript", True),
        ("bash -c 'wolframscript -code 1+1'", True), ("x; WolframKernel -noprompt", True),
        ("/Applications/Wolfram Engine.app/Contents/MacOS/WolframKernel", True),
        ("/Applications/Wolfram Engine.app/Contents/MacOS/wolfram", True),
        ("python3 bench/wolfram_standard.py deny", False), ("echo wolframscripting", False),
        ("sympy", False)])
    def test_kernel_re(self, blob, hit):
        assert bool(W.KERNEL_RE.search(blob)) is hit


class TestTheOperatorHooksKnowWolfram:
    """Question 11 reached the 2 operator hooks that speak about STEM tools."""

    @pytest.fixture(scope="class")
    def hook(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("ffafp_w", ROOT / "hooks" / "ffafp_audit.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_a_local_evaluation_is_a_stem_trace(self, hook):
        assert hook.bash_signals("wolframscript -code 'Integrate[x^2, {x, 0, 1}]'")["stem"] == ["wolframscript"]

    def test_a_search_for_the_word_is_not(self, hook):
        assert hook.bash_signals("grep -rn wolframscript bench/")["stem"] == []

    def test_a_connector_call_is_a_stem_trace(self, hook):
        turn = {"n_tools": 0, "mutations": [], "first_mut": None, "last_mut": None,
                "searches": [], "stem": [], "test_idx": [], "failable_idx": [], "read_paths": []}
        hook.record_tool(turn, "mcp__0c7b955d__WolframLanguageEvaluator", {"code": "1+1"})
        assert turn["stem"] == ["wolfram"]

    def test_the_sy_obligation_carries_the_failed_call_rule(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("mc_w", ROOT / "hooks" / "mc_commands.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        assert "verified NOTHING" in m._OBLIGATION["sy"] and "attribution" in m._OBLIGATION["sy"]
