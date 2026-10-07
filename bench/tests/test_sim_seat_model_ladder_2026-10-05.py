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
        """No invented model id. EVERY ENTRY WAS PROBED BEFORE IT WAS ALLOWED.

        Widened 2026-10-07 from {opus, fable} on the founder's ruling that the
        simulated runs "can involve a mix of models from Anthropic". The previous
        comment said "nothing else may appear here without a ruling"; this is that
        ruling, and the admission test is a DISPATCH rather than a belief: each id
        was sent through the aliveness probe at a 16-token ceiling on 2026-10-07 and
        answered -- opus 6.60 s, fable 5.69 s, sonnet 7.24 s, haiku 3.97 s.

        `opusplan` answered too and is deliberately NOT allowed: it is a routing
        alias serving different models for planning and execution, so the record
        could not say which model replied, and provenance is precisely what the
        founder does want a name to carry.
        """
        allowed = {"opus", "fable", "sonnet", "haiku"}
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
    def test_every_seat_is_answered_by_the_model_the_map_names(self, monkeypatch):
        """THE PROPERTY IS FAITHFULNESS, NOT A NAME COINCIDENCE.

        Until 2026-10-07 this was 2 tests asserting that the seat labelled Fable
        was answered by `fable` and the seat labelled CC2 by `opus`. Those passed
        because the map happened to pair like with like, so they could not tell a
        faithfully applied map from a lucky one -- and they encoded exactly the
        assumption the founder has now ruled against: "the only thing that should
        impact on capability is measured capability. A models name should have
        little to do with it."

        The map is now an arbitrary round-robin, so the seat label and the backing
        model are deliberately decoupled, and the only thing worth asserting is
        that the dispatch honours whatever the map says. That holds under any
        remap, and it still fails if the ladder stops reaching the command.
        """
        for seat, expected in sorted(SHIM.DEFAULT_LADDER.items()):
            # Start from a model the map does NOT name, so a pass cannot come from
            # the default leaking through.
            other = "haiku" if expected != "haiku" else "opus"
            got = _model_for(monkeypatch, seat, model=other,
                             seat_models=SHIM.DEFAULT_LADDER)
            assert got == expected, (
                f"{seat} dispatched as {got!r} but the map names {expected!r}; "
                f"the ladder is not reaching the command")

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


class TestTheLadderCanActuallyDiscriminate:
    """A MAP WITH 1 DISTINCT MODEL IS NOT A LADDER, and a map with 2 is barely one.

    The founder's ruling is that routing should rank on MEASURED capability. A
    statistic can only separate behaviours the roster actually contains, so the
    simulated ladder's job is to supply real variety for the measurement to find.
    Until 2026-10-07 it mapped 6 seats onto 2 models, so it could distinguish 2
    behaviours however many seats were dispatched.
    """

    def test_the_ladder_carries_at_least_3_distinct_models(self):
        distinct = set(SHIM.DEFAULT_LADDER.values())
        assert len(distinct) >= 3, (
            f"the simulated ladder resolves to {len(distinct)} distinct model(s) "
            f"{sorted(distinct)}; a measured capability statistic cannot separate "
            f"more behaviours than the roster contains")

    def test_no_single_model_answers_most_of_the_roster(self):
        """One model holding the majority would make the measurement mostly a
        measurement of that model."""
        from collections import Counter
        c = Counter(SHIM.DEFAULT_LADDER.values())
        top, n = c.most_common(1)[0]
        assert n <= len(SHIM.DEFAULT_LADDER) / 2, (
            f"{top!r} answers {n} of {len(SHIM.DEFAULT_LADDER)} seats")

    def test_the_launcher_now_defaults_to_the_ladder(self):
        """His ruling, and the reason the ladder was inert: the flag defaulted to
        uniform, so the map above was never consulted."""
        import ast
        import pathlib as _pl
        src = (_pl.Path(__file__).resolve().parents[1] / "tools"
               / "run_simulated_experiment.py").read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(src)):
            if not (isinstance(node, ast.Call)
                    and getattr(node.func, "attr", None) == "add_argument"):
                continue
            flags = [a.value for a in node.args
                     if isinstance(a, ast.Constant) and isinstance(a.value, str)]
            if "--seat-models" not in flags:
                continue
            for kw in node.keywords:
                if kw.arg == "default":
                    assert ast.literal_eval(kw.value) == "ladder", (
                        "the launcher still defaults to uniform, so the ladder is "
                        "consulted by nothing")
                    return
        raise AssertionError("--seat-models not found in the launcher")
