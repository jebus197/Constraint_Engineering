"""The founder's machine is a fixed resource, and this guard holds the mechanism that says so.

HIS RULING, 2026-10-11: *"you will need to implement a permanent fix for this."* A fix nothing
executes is not a fix, so every assertion here CALLS the code or RUNS the hook. None inspects
source text, because a source-text assertion only proves a module describes itself consistently
(`execute-do-not-grep`, founder ruling 2026-09-04).

WHAT THIS WOULD CATCH. Reverting the hook to always-allow, loosening the budget so it no longer
refuses a pytest fan-out, unwiring the PreToolUse entry, or replacing a derived verdict with a
literal -- the last being the exact tautology found in 3 of 8 probes of the audit producer
earlier the same day.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "local_resource_budget_2026-10-11.py"
HOOK = Path.home() / ".claude" / "hooks" / "local_resource_budget.py"
SETTINGS = Path.home() / ".claude" / "settings.json"


def _load():
    spec = importlib.util.spec_from_file_location("lrb_guard", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["lrb_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTheBudgetIsDerivedAndClamped:
    def test_the_producer_exists_and_imports(self):
        assert PRODUCER.is_file(), f"the budget producer is missing: {PRODUCER}"
        assert _load() is not None

    def test_the_budget_never_leaves_its_bounds_on_any_machine(self):
        """CALLED, not read: 0 headroom must still yield 1, and never exceed the core ceiling."""
        m = _load()
        real = m.headroom_mib
        try:
            for fake in (0.0, 1.0, 364.6, 364.8, 65536.0, 1e9):
                m.headroom_mib = lambda v=fake: v
                b = m.budget("heavy")
                assert b["max_concurrent_agents"] >= 1, (fake, b)
                assert b["max_concurrent_agents"] <= b["core_ceiling"], (fake, b)
        finally:
            m.headroom_mib = real

    def test_more_headroom_never_lowers_the_budget(self):
        """Monotonicity, executed rather than taken from the SymPy proof in the docstring."""
        m = _load()
        real = m.headroom_mib
        try:
            seen = []
            for fake in (0.0, 500.0, 1000.0, 2000.0, 4000.0, 16000.0):
                m.headroom_mib = lambda v=fake: v
                seen.append(m.budget("heavy")["max_concurrent_agents"])
            assert seen == sorted(seen), f"budget not monotone in headroom: {seen}"
        finally:
            m.headroom_mib = real

    def test_heavy_work_is_never_given_a_larger_budget_than_light_work(self):
        m = _load()
        assert (m.budget("heavy")["max_concurrent_agents"]
                <= m.budget("light")["max_concurrent_agents"])

    def test_an_unknown_work_class_is_refused_rather_than_guessed(self):
        m = _load()
        with pytest.raises(SystemExit):
            m.budget("enormous")

    def test_no_claim_returns_a_hard_coded_boolean_verdict(self):
        """The tautology that 3 of 8 audit probes carried on 2026-10-11."""
        tree = ast.parse(PRODUCER.read_text(encoding="utf-8"))
        literal = []
        for n in ast.walk(tree):
            if isinstance(n, ast.FunctionDef) and n.name.startswith("claim_"):
                for sub in ast.walk(n):
                    if isinstance(sub, ast.Dict):
                        for k, v in zip(sub.keys, sub.values):
                            if (isinstance(k, ast.Constant)
                                    and k.value == "default_exceeds_capacity"
                                    and isinstance(v, ast.Constant)):
                                literal.append(n.name)
        assert not literal, f"verdict hard-coded in {literal}; it could not report a repair"

    def test_the_check_fanout_switch_actually_refuses(self):
        """exit 3 on an over-budget request, exit 0 within budget -- run, not read."""
        m = _load()
        cap = m.budget("heavy")["max_concurrent_agents"]
        over = subprocess.run([sys.executable, str(PRODUCER), "--check-fanout", str(cap + 40)],
                              capture_output=True, text=True, timeout=120)
        assert over.returncode == 3, (over.returncode, over.stderr[-400:])
        within = subprocess.run([sys.executable, str(PRODUCER), "--check-fanout", "1"],
                                capture_output=True, text=True, timeout=120)
        assert within.returncode == 0, (within.returncode, within.stderr[-400:])

    def test_help_is_free(self):
        """No runner in this project may cost anything on --help (founder ruling)."""
        r = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0 and "budget" in r.stdout.lower()


class TestTheHookRefusesDelegatedPytest:
    @staticmethod
    def _run(payload: dict):
        if not HOOK.is_file():
            pytest.skip(f"the PreToolUse hook is not installed in this checkout: {HOOK}")
        return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                              capture_output=True, text=True, timeout=120)

    def test_it_blocks_pytest_inside_an_agent(self):
        r = self._run({"tool_name": "Agent",
                       "tool_input": {"prompt": "run python3 -m pytest bench/tests/ -q"}})
        assert r.returncode == 2, (r.returncode, r.stdout[-300:], r.stderr[-300:])
        assert "cached" in r.stderr.lower(), "the refusal must name the remedy"

    def test_it_blocks_a_workflow_that_fans_out_and_runs_pytest(self):
        r = self._run({"tool_name": "Workflow",
                       "tool_input": {"script": "await parallel(xs.map(x=>()=>agent('pytest')))"}})
        assert r.returncode == 2, (r.returncode, r.stderr[-300:])

    #: THE DEPTH STATEMENTS HIS 2026-10-25 RULING REQUIRES OF EVERY FAN-OUT.
    #: A brief without them is refused, by design, whatever else it asks for --
    #: so a test of the ALLOW path has to carry them or it is testing the depth
    #: gate instead. Added 2026-10-28, after the full-suite baseline showed this
    #: test refused with the depth message rather than allowed.
    _DEPTH = ("HYPOTHESIS: the rung default is declared in exactly one place.\n"
              "FALSIFIED BY: finding the constant declared in 2 or more modules.\n"
              "WHY NOT ONE CONTEXT: the tree is large and the grep is mechanical.\n")

    def test_it_allows_a_read_only_agent_and_states_the_budget(self):
        r = self._run({"tool_name": "Agent",
                       "tool_input": {"prompt": self._DEPTH +
                                      "grep the tree for DEFAULT_MAX_RUNGS"}})
        assert r.returncode == 0, (r.returncode, r.stderr[-300:])
        assert "budget" in r.stdout.lower(), "an allowed call must still carry the budget"

    def test_a_read_only_agent_without_the_depth_statements_is_refused(self):
        """ANTI-VACUITY for the brief above: if the depth gate did not bite, the
        3 added lines would be decoration and the test above would pass without
        them. His ruling of 2026-10-25 is that a fan-out which cannot name its
        own falsifier is not breadth but delegation of the thinking."""
        r = self._run({"tool_name": "Agent",
                       "tool_input": {"prompt": "grep the tree for DEFAULT_MAX_RUNGS"}})
        assert r.returncode == 2, (r.returncode, r.stdout[-200:])
        assert "depth before breadth" in r.stderr.lower()

    def test_a_brief_breaking_both_rules_is_told_both(self):
        """THE 2026-10-28 REPAIR. The depth check was placed before the pytest
        prohibition with its own early return, so a brief that broke both was
        refused for the depth statements alone and the operator was never told
        the remedy that protects the machine. Half a refusal is worse than
        either half, because the operator fixes what they were told about and
        the second refusal looks like a new problem."""
        r = self._run({"tool_name": "Agent",
                       "tool_input": {"prompt": "run python3 -m pytest bench/tests/ -q"}})
        assert r.returncode == 2
        low = r.stderr.lower()
        assert "cached" in low, f"the pytest remedy is missing: {r.stderr[-300:]}"
        assert "depth before breadth" in low, (
            f"the depth requirement is missing: {r.stderr[-300:]}")

    def test_it_never_blocks_cc1s_own_pytest(self):
        """The gate is on DELEGATED work. Blocking the orchestrator's own suite would be a
        regression that stops the project testing itself."""
        r = self._run({"tool_name": "Bash",
                       "tool_input": {"command": "python3 -m pytest bench/tests/ -q"}})
        assert r.returncode == 0, (r.returncode, r.stderr[-300:])

    def test_it_fails_open_on_malformed_input(self):
        if not HOOK.is_file():
            pytest.skip("hook not installed")
        r = subprocess.run([sys.executable, str(HOOK)], input="not json at all",
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, "a broken payload must never jam the session"


class TestTheMechanismIsWiredAndRecorded:
    def test_the_hook_is_wired_as_a_pretooluse_gate(self):
        if not SETTINGS.is_file():
            pytest.skip("no settings.json in this environment")
        d = json.loads(SETTINGS.read_text(encoding="utf-8"))
        pre = d.get("hooks", {}).get("PreToolUse", [])
        cmds = [hk.get("command", "") for e in pre for hk in e.get("hooks", [])]
        assert any("local_resource_budget.py" in c for c in cmds), (
            "the budget hook is not wired; an unwired gate is not a gate")

    def test_the_ruling_is_recorded_where_a_reader_would_look(self):
        cm = REPO / ".claude" / "CLAUDE.md"
        assert cm.is_file()
        t = cm.read_text(encoding="utf-8")
        assert "THE FOUNDER'S MACHINE IS A FIXED RESOURCE" in t
        assert "364.7" in t, "the measured per-process peak must travel with the rule"
        assert "ultracode" in t.lower(), "his ultracode vocabulary must be recorded"
