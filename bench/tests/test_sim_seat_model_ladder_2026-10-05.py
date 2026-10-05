#!/usr/bin/env python3
"""A simulated seat may be answered by its own model, and uniform stays uniform.

WHY THIS EXISTS. Until 2026-10-05 every simulated seat was answered by ONE model,
`bench/tools/sim_dispatch_shim.py` defaulting to `opus`, across what its own comment
records as 8 call sites in 7 enclosing functions. Two costs followed.

COST 1, MONEY, measured by `scripts/where_the_plan_went_2026-10-04.py`: dispatches
carrying a reply were 6.6959% simulated before 2026-10-01, Wilson [6.0633%, 7.3894%],
and 100% after, Wilson [95.5765%, 100.0000%]. So Max-plan dispatches per active day
rose **5.7828x** even though TOTAL dispatches per day fell to **0.3872x** of the old
rate — the mix changed, not the volume. Every one of those is the most expensive
model available.

COST 2, FIDELITY, and it runs opposite to the shim's own warning. That warning says a
stand-in weaker than the seats it replaces "under-finds, and the run looks cleaner
than the real one will be". That is an argument against a uniformly WEAK bench and
none at all against a MIXED one: the real panel is 6 vendors of differing capability,
so 6 identical seats removes the diversity the panel exists to exploit.

THE PROPERTY THESE TESTS HOLD. The ladder must be ADDITIVE — it adds a path and
removes none — so a run that does not ask for it must dispatch exactly as every run
before this date did. Nothing here calls a model: `subprocess.run` is replaced with a
recorder, so the tests read the command that WOULD have been dispatched.
"""
import pathlib
import sys
import types

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.tools import sim_dispatch_shim as SHIM  # noqa: E402


class _Seat:
    def __init__(self, label):
        self.label = label


def _model_for(monkeypatch, label, **shim_kwargs):
    """The --model argument the shim WOULD pass, without dispatching anything."""
    seen = {}

    def _fake_run(cmd, *a, **kw):
        seen["cmd"] = cmd
        i = cmd.index("--model")
        seen["model"] = cmd[i + 1]
        return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(SHIM.subprocess, "run", _fake_run)
    dispatch = SHIM.make_shim(**shim_kwargs)
    try:
        dispatch(_Seat(label), "prompt", "")
    except Exception:
        pass  # downstream parsing is not what this test measures
    assert "model" in seen, "the shim never reached subprocess.run"
    return seen["model"]


class TestThePremiseIsAlive:
    def test_the_ladder_constant_exists_and_names_real_seats(self):
        assert isinstance(SHIM.DEFAULT_LADDER, dict) and SHIM.DEFAULT_LADDER
        assert "Fable-SIM" in SHIM.DEFAULT_LADDER
        assert "CC2-SIM" in SHIM.DEFAULT_LADDER

    def test_only_models_this_project_already_dispatches_are_named(self):
        """No invented model id. The roster in .claude/CLAUDE.md lists `opus` for
        cc2 and `fable` for fable; nothing else may appear here without a ruling."""
        allowed = {"opus", "fable"}
        unknown = set(SHIM.DEFAULT_LADDER.values()) - allowed
        assert not unknown, (
            f"the ladder names model id(s) this project does not dispatch: {unknown}"
        )

    def test_the_shipped_default_is_empty_so_nothing_changes_unasked(self):
        assert SHIM.SEAT_MODEL_LADDER == {}


class TestUniformIsUnchanged:
    """The additive half: a run that does not ask for the ladder behaves exactly as
    every run before 2026-10-05 did."""

    @pytest.mark.parametrize("label", ["CC2-SIM", "Fable-SIM", "Gemini-SIM",
                                       "Codex-SIM", "ChatGPT-SIM", "DeepSeek-SIM"])
    def test_every_seat_gets_the_single_model_when_no_map_is_given(
            self, monkeypatch, label):
        assert _model_for(monkeypatch, label, model="opus") == "opus"

    def test_an_explicit_single_model_still_reaches_every_seat(self, monkeypatch):
        assert _model_for(monkeypatch, "Fable-SIM", model="sonnet") == "sonnet"


class TestTheLadderActuallyChangesTheDispatch:
    def test_fable_seat_is_answered_by_fable(self, monkeypatch):
        got = _model_for(monkeypatch, "Fable-SIM", model="opus",
                         seat_models=SHIM.DEFAULT_LADDER)
        assert got == "fable", (
            f"Fable-SIM dispatched as {got!r}; the ladder is not reaching the command"
        )

    def test_cc2_seat_is_answered_by_opus(self, monkeypatch):
        assert _model_for(monkeypatch, "CC2-SIM", model="fable",
                          seat_models=SHIM.DEFAULT_LADDER) == "opus"

    def test_the_bench_is_genuinely_mixed(self, monkeypatch):
        got = {lbl: _model_for(monkeypatch, lbl, model="opus",
                               seat_models=SHIM.DEFAULT_LADDER)
               for lbl in SHIM.DEFAULT_LADDER}
        assert len(set(got.values())) > 1, (
            f"every seat resolved to the same model {set(got.values())} — the "
            f"ladder is uniform in disguise and buys neither cost nor diversity"
        )


class TestPartialMapsFallBack:
    def test_a_seat_the_map_does_not_name_uses_the_single_model(self, monkeypatch):
        partial = {"Fable-SIM": "fable"}
        assert _model_for(monkeypatch, "Fable-SIM", model="opus",
                          seat_models=partial) == "fable"
        assert _model_for(monkeypatch, "DeepSeek-SIM", model="opus",
                          seat_models=partial) == "opus"

    def test_an_empty_map_is_the_same_as_no_map(self, monkeypatch):
        assert _model_for(monkeypatch, "Fable-SIM", model="opus",
                          seat_models={}) == "opus"


class TestTheLauncherCanSelectIt:
    """An option nothing can select is an addition nothing reaches."""

    def test_the_flag_exists_and_offers_both_modes(self):
        """EXECUTED, not matched. The launcher's own parser is run.

        The first draft matched `'"--seat-models"' in src`, which the source-text
        assertion census counts and which a comment could satisfy. Running
        `--help` is free by the project's own contract (a `--help` must never cost
        money) and proves the flag reaches a real parser.
        """
        import subprocess
        r = subprocess.run(
            [sys.executable,
             str(REPO / "bench" / "tools" / "run_simulated_experiment.py"), "--help"],
            capture_output=True, text=True, timeout=120, cwd=str(REPO))
        assert r.returncode == 0, f"--help exited {r.returncode}: {r.stderr[:400]}"
        out = r.stdout
        assert "--seat-models" in out, (
            f"the launcher's parser does not offer --seat-models; --help says:\n"
            f"{out[:600]}")
        assert "uniform" in out and "ladder" in out, (
            "both modes must be selectable, else the ladder cannot be chosen")

    def test_an_unknown_mode_is_refused(self):
        """The choices are ENFORCED, not decorative — so a typo cannot silently
        fall back to uniform and quietly disable the capability ladder."""
        import subprocess
        r = subprocess.run(
            [sys.executable,
             str(REPO / "bench" / "tools" / "run_simulated_experiment.py"),
             "--seat-models", "not-a-real-mode", "--help"],
            capture_output=True, text=True, timeout=120, cwd=str(REPO))
        assert r.returncode != 0, (
            "an unrecognised --seat-models value was ACCEPTED, so a typo would "
            "run the whole experiment on uniform seats without saying so")
        assert "invalid choice" in (r.stderr + r.stdout).lower()

    def test_install_accepts_and_forwards_the_map(self):
        import inspect
        assert "seat_models" in inspect.signature(SHIM.install).parameters
        assert "seat_models" in inspect.getsource(SHIM.install)
