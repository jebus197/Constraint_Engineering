"""Every model, under every condition, dispatches WITH tools.

FOUNDER RULING 2026-08-30: "all models under all conditions (including agents in
simulated runs), 2- or 5-model paid panel reviews, and in actual live/paid
experiments, should always have tool use enabled and enforced without exception,
as per the standing CDSFL directive: TOOLS DECIDE, NOT VOTES. Make sure this will
indeed invariably be true in all cases."

A model that cannot RUN anything can only assert, and a panel of models that can
only assert is a vote. That is the one thing this project exists not to be.

WHAT WAS WRONG. `enable_tools` defaulted to False and the round dispatch
forwarded `cfg.falsifier_gate_enabled`, so any gate-off configuration ran a
panel with no execute_python loop at all. Both defaults are now True and the
round dispatch passes True unconditionally.

THE ONE REMAINING EXCEPTION, RECORDED RATHER THAN HIDDEN. Of the five dispatch
routes, four can carry tools:

    claude_cli   native, via --allowedTools
    openrouter   dispatch passes a tools list
    deepseek     dispatch passes a tools list
    codex_exec   agentic CLI; `codex exec` runs tools itself

`call_gemini` has NO tools parameter, so on the live panel Gemini is dispatched
without them. That is 5 of 6 panellists tooled, not 6 of 6, and closing it means
implementing Google function-calling, which is not a change to make untested.
This file pins the gap so it cannot be quietly forgotten, and it will go RED the
moment somebody adds the parameter -- at which point the exception is deleted.
"""
import ast
import inspect
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import reference_runner_v2 as R
import runner_core as RC
import experiment_11_orchestrator as ORCH

ORCH_SRC = pathlib.Path(ORCH.__file__).read_text(encoding="utf-8")
RUNNER_SRC = pathlib.Path(R.__file__).read_text(encoding="utf-8")


class TestDefaultsAreOn:
    def test_dispatch_single_model_defaults_to_tools_on(self):
        assert inspect.signature(
            R._dispatch_single_model).parameters["enable_tools"].default is True

    def test_runner_core_worker_defaults_to_tools_on(self):
        assert inspect.signature(
            RC._dispatch_worker).parameters["enable_tools"].default is True

    def test_no_dispatch_path_hardcodes_tools_off(self):
        offenders = [ln for ln in RUNNER_SRC.splitlines()
                     if "enable_tools=False" in ln and not ln.strip().startswith("#")]
        assert offenders == [], offenders


class TestTheRoundDispatchDoesNotGateOnTheFalsifierGate:
    """The specific regression: tools used to ride on falsifier_gate_enabled."""

    def test_round_dispatch_passes_true_not_the_gate(self):
        tree = ast.parse(RUNNER_SRC)
        bad = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            src = ast.unparse(node)
            if "_dispatch_single_model" not in src:
                continue
            if "falsifier_gate_enabled" in src:
                bad.append(node.lineno)
        assert bad == [], (
            f"a round dispatch at line(s) {bad} still forwards "
            f"falsifier_gate_enabled as enable_tools, so a gate-off run would "
            f"dispatch a panel that can only vote"
        )


class TestEveryRouteThatCanCarryToolsDoes:
    TOOLED = ("call_claude_cli", "call_openrouter", "call_deepseek")

    @pytest.mark.parametrize("route", TOOLED)
    def test_the_route_accepts_or_grants_tools(self, route):
        fn = getattr(ORCH, route, None)
        assert fn is not None, f"{route} has gone"
        body = ast.unparse(next(
            n for n in ast.walk(ast.parse(ORCH_SRC))
            if isinstance(n, ast.FunctionDef) and n.name == route))
        assert ("tools" in inspect.signature(fn).parameters
                or "allowedTools" in body), f"{route} lost its tool path"

    def test_codex_runs_an_agentic_cli(self):
        """codex_exec needs no tools parameter: the CLI runs tools itself."""
        body = ast.unparse(next(
            n for n in ast.walk(ast.parse(ORCH_SRC))
            if isinstance(n, ast.FunctionDef) and n.name == "call_codex"))
        assert "subprocess" in body


class TestThereIsNoLongerAnException:
    """The exception is closed. Founder ruling 2026-08-30: "There is to be no
    exceptions from tool use. Not now, not in the future, just as there should
    never have been in the past."

    `call_gemini` now accepts tools and runs a Google function-calling loop.
    VERIFIED WITH ONE PAID CALL on 2026-08-31, not by inspection: asked for the
    Wilson interval of 126/246 -- a real project number no model recalls -- it
    returned 0.4500, 0.5740 to four places in 6.4 seconds, which is only
    obtainable by running statsmodels. See bench/tools/gemini_tool_switch_test.py.
    """

    def test_gemini_accepts_tools(self):
        assert "tools" in inspect.signature(ORCH.call_gemini).parameters

    def test_dispatch_passes_tools_on_the_google_route(self):
        tree = ast.parse(ORCH_SRC)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "dispatch")
        body = ast.unparse(fn)
        i = body.find("call_gemini(")
        assert i > 0 and "tools=" in body[i:i + 500], (
            "the google route stopped receiving tools — it is Gemini's FAILOVER "
            "route and the one decomposed_dispatch uses, so this reintroduces a "
            "silent loss of tool use exactly where it is hardest to notice"
        )

    def test_the_gemini_tool_loop_exists(self):
        assert hasattr(ORCH, "_run_gemini_tool_loop")

    def test_one_tool_schema_serves_both_wire_formats(self):
        """The OpenAI schema is translated, not duplicated, so a change to the
        tool's description cannot drift between routes."""
        assert hasattr(ORCH, "_openai_tools_to_gemini")

    def test_dispatch_defaults_to_tools_on(self):
        assert inspect.signature(ORCH.dispatch).parameters["enable_tools"].default is True


class TestSimulatedAgentsGetTools:
    def test_the_shim_grants_a_shell(self):
        src = (pathlib.Path(__file__).resolve().parents[1]
               / "tools" / "sim_dispatch_shim.py").read_text(encoding="utf-8")
        assert "--allowedTools" in src and "Bash" in src, (
            "simulated panellists must be able to RUN a falsifier, not only "
            "describe one"
        )
