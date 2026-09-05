"""The three Exp 56 arm configs, validated by EXECUTION rather than by reading.

WHY THIS FILE EXISTS AND WHY IT IS SHAPED THIS WAY
--------------------------------------------------
A config that has not been driven through `launcher_core.build_runner_config_from_dict`
is an unverified config. This project has shipped SIX separate launcher-config-drop
defects -- routing (2026-07-12), max_contested_rounds (2026-07-27),
feedback_channel_enabled and the gamma/stall trio (2026-07-29, which would have run the
2x2 factorial's PRIMARY FACTOR on in every cell), severity_calibration_enabled
(2026-07-31) and max_irreducible_queue (2026-08-01) -- and a systematic sweep found 20
more still latent. Every one was silent: the JSON said one thing, the run did another,
and nothing on either side complained.

`test_launcher_no_silent_drops.py` already closes that class at the level of the
DATACLASS. It cannot close it at the level of a PARTICULAR CONFIG, because a key
misspelled in a JSON file is not a dataclass field and is therefore invisible to a
field-driven sweep. That is what this file adds: each shipped Exp 56 config is driven
through the real launcher path, key by key, and every value is required to arrive.

THE DISCRIMINATION, WHICH IS THE PART THAT MAKES IT EVIDENCE
------------------------------------------------------------
Asserting `getattr(runner_cfg, key) == json_value` passes trivially whenever the JSON
value happens to equal the dataclass default -- and most of them do, because these
configs were written from the arc's house style. Three tests in this project were
recently found to be substitution tautologies that passed with the model replaced by
the constant 42. So every key is ALSO driven with a PERTURBED value, and the resulting
RunnerConfig is required to change. A key that survives the first check and fails the
second is being served by the default, not by the config.

THE OTHER HALF: THREE MECHANISMS THAT WOULD SILENTLY UNDO ARM A
----------------------------------------------------------------
Exp 56 is the FIRST experiment in this project to declare a panel SUBSET. Every config
from Exp 40 to Exp 55 declared all 5 seats, so `cfg.models` and `exp_config.models`
always agreed and three sites that read the second list without intersecting the first
were latent. They are not latent for a 1-seat arm:

  * `_apply_routing` builds `models = [mc.label for mc in exp_config.models]` and hands
    it to `route()` as available_models. The ladder excludes the finding's own source
    model, so in Arm A the ladder is precisely the 4 vendors the arm exists to do
    without.
  * `_post_convergence_sweep` iterates `for mc in exp_config.models` with no filter.
  * `run_experiment` arms merge arbitration with `"panel": list(exp_config.models)`.

All three are switched OFF in all three arms, and the tests below DEMONSTRATE the leak
by executing the real code rather than by describing it, then assert that each config's
mitigation agrees with what was measured. The conditional shape is deliberate: if the
runner is repaired, these tests keep passing and stop constraining the configs, rather
than pinning a defect in place.

Nothing here dispatches a model. `load_experiment_config()` reads files; the sweep is
driven with a stub in place of `dispatch_to_model`; no test needs the network.
"""
from __future__ import annotations

import copy
import dataclasses
import json
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench import launcher_core  # noqa: E402
from bench.launcher_core import build_runner_config_from_dict  # noqa: E402
from bench.reference_runner_v3 import (  # noqa: E402
    RunnerConfig,
    TargetKindMismatch,
    resolve_target_kind,
)
from bench.routing import rank_falsifier_writers  # noqa: E402

CONFIG_DIR = REPO / "bench" / "exp56_configs"
ARM_FILES = (
    "d9_single_model_with_agents.json",
    "d9_multi_model_panel.json",
    "d11_seat_contrast_diversity_arm.json",
)

# Keys a comparison experiment is ALLOWED to vary between arms. Everything else
# must be byte-identical, because everything else is what "held constant" means.
ARM_VARIABLE_KEYS = {"models", "experiment_name"}

_ARGS = types.SimpleNamespace(resume=False)


def _load(name: str) -> dict:
    return json.loads((CONFIG_DIR / name).read_text(encoding="utf-8"))


def _live_keys(cfg: dict) -> dict:
    """The keys that are supposed to reach RunnerConfig.

    Underscore-prefixed keys are documentation by the arc's convention and are
    ignored by both ingestion paths -- except `_macrophage` and `_ouroboros`,
    which are folded into shadow_cell_config and are checked separately.
    """
    return {k: v for k, v in cfg.items() if not k.startswith("_")}


def _perturb(value):
    """Return a value guaranteed different from `value` and of a usable type."""
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, float):
        return value + 0.5
    if isinstance(value, str):
        return (value or "") + "_PERTURBED"
    if isinstance(value, list):
        return list(value) + ["_PERTURBED"]
    if isinstance(value, dict):
        out = dict(value)
        out["_PERTURBED"] = True
        return out
    raise AssertionError(f"no perturbation defined for {type(value).__name__}")


# ─────────────────────────────────────────────────────────────────────────────
# 0. The corpus is real. Without this every parametrised test below can pass
#    on an empty glob -- this project's governing failure mode in the clothes
#    of a green run.
# ─────────────────────────────────────────────────────────────────────────────

def test_all_three_arm_configs_exist_and_parse():
    found = sorted(p.name for p in CONFIG_DIR.glob("*.json"))
    assert found == sorted(ARM_FILES), (
        f"expected exactly the 3 Exp 56 arms in {CONFIG_DIR}, found {found}")
    for name in ARM_FILES:
        assert isinstance(_load(name), dict)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Every intended field arrives, and arrives BECAUSE the config said so.
# ─────────────────────────────────────────────────────────────────────────────

class TestEveryFieldSurvivesTheLauncher:

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_every_declared_key_is_a_runner_config_field(self, name):
        """A misspelled key is accepted in silence by both ingestion paths.

        `RunnerConfig.from_dict` filters to known fields and the launcher's
        catch-all does the same, so `max_round` instead of `max_rounds` is not
        an error anywhere -- it is a config that quietly runs at the default.
        """
        fields = {f.name for f in dataclasses.fields(RunnerConfig)}
        aliases = {"take_up_slack_enabled"}
        stray = [k for k in _live_keys(_load(name))
                 if k not in fields and k not in aliases]
        assert stray == [], (
            f"{name}: keys that reach neither RunnerConfig nor a known alias, "
            f"and would therefore be ignored in silence: {stray}")

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_every_declared_value_arrives_in_runner_config(self, name):
        cfg = _load(name)
        rc = build_runner_config_from_dict(copy.deepcopy(cfg), _ARGS)
        wrong = []
        for key, want in _live_keys(cfg).items():
            got = getattr(rc, key, "<MISSING>")
            if got != want:
                wrong.append(f"{key}: config={want!r} RunnerConfig={got!r}")
        assert wrong == [], (
            f"{name}: values dropped or altered on the launcher path:\n  "
            + "\n  ".join(wrong))

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_each_value_is_served_by_the_config_and_not_by_a_default(self, name):
        """The discrimination pass. Perturb one key at a time and require the
        RunnerConfig to follow. A key served by the dataclass default passes the
        test above and fails this one."""
        cfg = _load(name)
        inert = []
        for key, original in _live_keys(cfg).items():
            mutated = copy.deepcopy(cfg)
            mutated[key] = _perturb(original)
            rc = build_runner_config_from_dict(mutated, _ARGS)
            if getattr(rc, key, "<MISSING>") != mutated[key]:
                inert.append(
                    f"{key}: set to {mutated[key]!r}, RunnerConfig read "
                    f"{getattr(rc, key, '<MISSING>')!r}")
        assert inert == [], (
            f"{name}: these keys do not actually drive the run -- the config "
            f"value is ignored and a default is used:\n  " + "\n  ".join(inert))

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_both_ingestion_paths_agree(self, name):
        """The runner's own --config path and the launcher path must produce the
        same RunnerConfig. They are separate code and have diverged 6 times."""
        cfg = _load(name)
        via_launcher = build_runner_config_from_dict(copy.deepcopy(cfg), _ARGS)
        via_runner = RunnerConfig.from_dict(copy.deepcopy(cfg))
        disagree = []
        for f in dataclasses.fields(RunnerConfig):
            if f.name == "resume":  # launcher takes it from argv, from_dict does not
                continue
            a, b = getattr(via_launcher, f.name), getattr(via_runner, f.name)
            if a != b:
                disagree.append(f"{f.name}: launcher={a!r} runner={b!r}")
        assert disagree == [], (
            f"{name}: the two config paths disagree:\n  " + "\n  ".join(disagree))

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_shadow_blocks_reach_shadow_cell_config(self, name):
        """`_macrophage` and `_ouroboros` are the two underscore keys that are
        NOT documentation. If the fold stopped happening they would look like
        comments and the cells would run at their defaults."""
        cfg = _load(name)
        rc = build_runner_config_from_dict(copy.deepcopy(cfg), _ARGS)
        assert rc.shadow_cell_config.get("_macrophage") == cfg["_macrophage"]
        assert rc.shadow_cell_config.get("_ouroboros") == cfg["_ouroboros"]

    def test_the_perturbation_helper_actually_perturbs(self):
        """Without this the discrimination test above could pass by comparing a
        value to itself -- the same tautology it exists to catch."""
        for v in (True, False, 0, 7, 0.25, "", "x", [], ["a"], {}, {"a": 1}):
            assert _perturb(v) != v


# ─────────────────────────────────────────────────────────────────────────────
# 2. What is held constant is actually held constant.
# ─────────────────────────────────────────────────────────────────────────────

class TestArmsDifferOnlyInPanelComposition:

    def test_every_non_panel_key_is_identical_across_the_three_arms(self):
        loaded = {n: _live_keys(_load(n)) for n in ARM_FILES}
        keysets = {n: set(d) for n, d in loaded.items()}
        base_name = ARM_FILES[0]
        base_keys = keysets[base_name]
        for n, ks in keysets.items():
            assert ks == base_keys, (
                f"{n} declares a different key set from {base_name}: "
                f"only in {n}: {sorted(ks - base_keys)}; "
                f"only in {base_name}: {sorted(base_keys - ks)}")
        differing = []
        for key in sorted(base_keys - ARM_VARIABLE_KEYS):
            values = {n: loaded[n][key] for n in ARM_FILES}
            if len({json.dumps(v, sort_keys=True) for v in values.values()}) > 1:
                differing.append(f"{key}: {values}")
        assert differing == [], (
            "these keys vary between arms, so the comparison measures them as "
            "well as panel composition:\n  " + "\n  ".join(differing))

    def test_the_arms_really_do_differ_in_panel_composition(self):
        """The other direction. If `models` were accidentally made identical the
        test above would still pass and the experiment would have one arm run
        three times."""
        rosters = {n: tuple(_load(n)["models"]) for n in ARM_FILES}
        assert len(set(rosters.values())) == 3, f"arms are not distinct: {rosters}"
        sizes = {n: len(r) for n, r in rosters.items()}
        assert sizes["d9_single_model_with_agents.json"] == 1
        assert sizes["d11_seat_contrast_diversity_arm.json"] == 2
        assert sizes["d9_multi_model_panel.json"] == 5

    def test_experiment_names_are_distinct(self):
        """The log directory is derived from experiment_name. Two arms sharing a
        name would write into one another's run record."""
        names = [_load(n)["experiment_name"] for n in ARM_FILES]
        assert len(set(names)) == 3, f"experiment_name collision: {names}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. The declared seats and the declared target must be real, checked against
#    the live orchestrator and the live target-kind detector.
# ─────────────────────────────────────────────────────────────────────────────

def _live_seats() -> dict:
    exp_config = launcher_core.load_experiment_config()
    return {mc.label: mc for mc in exp_config.models}


class TestDeclarationsAreCheckedAgainstReality:

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_every_declared_seat_exists_in_the_orchestrator_roster(self, name):
        """A label the orchestrator does not know is dispatched to nobody: the
        round loop filters `exp_config.models` by `cfg.models`, so a typo
        silently removes a seat instead of failing."""
        seats = _live_seats()
        missing = [m for m in _load(name)["models"] if m not in seats]
        assert missing == [], (
            f"{name}: declared seats absent from the orchestrator roster "
            f"{sorted(seats)}: {missing}")

    def test_an_unknown_seat_label_would_be_detected(self):
        """Discrimination for the test above."""
        seats = _live_seats()
        assert "NotAModel" not in seats

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_declared_target_kind_matches_what_the_harness_detects(self, name):
        """`resolve_target_kind` REFUSES TO START on a mismatch, so a wrong
        declaration is a launch failure discovered after the first dispatch is
        already paid for. Checked here instead, for free."""
        cfg = _load(name)
        kind, _reason = resolve_target_kind(
            cfg["test_article"], None, cfg.get("target_kind") or None)
        assert kind == cfg["target_kind"]

    def test_a_wrong_target_kind_declaration_raises(self):
        """Discrimination: the check above is only worth having if the resolver
        actually objects."""
        with pytest.raises(TargetKindMismatch):
            resolve_target_kind("bench/cdsfl_registry/engine.py", None, "prose")

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_the_target_exists_and_is_the_same_file_in_every_arm(self, name):
        cfg = _load(name)
        target = REPO / cfg["test_article"]
        assert target.is_file(), f"{name}: target missing at {target}"
        assert cfg["test_article"] == _load(ARM_FILES[0])["test_article"]


# ─────────────────────────────────────────────────────────────────────────────
# 4. The three sites that read the FULL roster where they should read the
#    DECLARED one. Demonstrated by execution; the configs' mitigation is then
#    required to agree with the measurement.
# ─────────────────────────────────────────────────────────────────────────────

class TestSubsetPanelLeaks:

    def test_the_routing_ladder_built_from_the_full_roster_reaches_other_vendors(self):
        """MEASURED by calling the real ladder builder with the two candidate
        inputs. This is the whole reason routing is off in every arm.

        `_apply_routing` passes `[mc.label for mc in exp_config.models]`. With
        Arm A's declared roster of 1 the correct ladder is empty; with the full
        roster it is 4 rungs long, every one of them another vendor.
        """
        declared = _load("d9_single_model_with_agents.json")["models"]
        full = list(_live_seats())
        source = declared[0]
        correct = rank_falsifier_writers(declared, exclude=[source])
        leaked = rank_falsifier_writers(full, exclude=[source])
        assert correct == [], (
            "a 1-seat arm has no ladder above its own seat; if this is no "
            "longer true the arm's premise has changed")
        assert len(leaked) == len(full) - 1, (
            f"ladder built from the full roster: {leaked}")
        assert set(leaked) - {source}, "the leaked ladder reaches other seats"

    def test_routing_is_off_in_every_arm_while_the_ladder_reads_the_full_roster(self):
        """Conditional on the measurement above, not on a description of it. If
        the runner is repaired to intersect with `cfg.models`, the guard lifts."""
        full = list(_live_seats())
        declared = _load("d9_single_model_with_agents.json")["models"]
        ladder_leaks = bool(
            rank_falsifier_writers(full, exclude=declared[:1]))
        if not ladder_leaks:
            pytest.skip("ladder no longer reaches undeclared seats; guard moot")
        for name in ARM_FILES:
            assert _load(name)["routing_enabled"] is False, (
                f"{name} enables routing while `_apply_routing` builds its "
                f"ladder from the full orchestrator roster. In the 1-seat arm "
                f"that dispatches the very vendors the arm exists to do without.")

    def test_the_post_convergence_sweep_dispatches_to_undeclared_seats(self, monkeypatch):
        """EXECUTED, not read. The sweep is driven with a stub in place of
        `dispatch_to_model` and the seats it reaches are counted."""
        import bench.reference_runner_v3 as rr

        reached: list = []

        def _stub(mc, prompt, system, **kw):
            reached.append(getattr(mc, "label", str(mc)))
            return "", 0.0

        monkeypatch.setattr(rr, "dispatch_to_model", _stub)

        cfg = build_runner_config_from_dict(
            {**_load("d9_single_model_with_agents.json"),
             "post_convergence_sweep_rounds": 1}, _ARGS)
        registry = types.SimpleNamespace(entries={
            "C0001": {"status": "OPEN", "severity": 0.8,
                      "description": "a residual for the sweep to be offered"}})
        exp_config = launcher_core.load_experiment_config()

        rr._post_convergence_sweep(registry, exp_config, cfg, 3, repo_root=str(REPO))

        assert reached, "the sweep dispatched to nobody; the probe is not exercising it"
        undeclared = sorted(set(reached) - set(cfg.models))
        assert undeclared, (
            "expected the sweep to reach seats the config never declared")
        # And the mitigation the configs actually carry.
        for name in ARM_FILES:
            assert _load(name)["post_convergence_sweep_rounds"] == 0, (
                f"{name} enables the post-convergence sweep while the sweep "
                f"reaches undeclared seats {undeclared}")

    def test_merge_arbitration_is_off_in_every_arm(self):
        """The third site: `run_experiment` arms the arbitration context with
        `list(exp_config.models)`. Off in all three arms, which is a declared
        delta from every config exp40-exp55."""
        for name in ARM_FILES:
            assert _load(name)["merge_arbitration_enabled"] is False, name


# ─────────────────────────────────────────────────────────────────────────────
# 5. D11 -- the seat contrast, measured rather than asserted.
# ─────────────────────────────────────────────────────────────────────────────

def seat_field_diff(seat_a, seat_b) -> dict:
    """Fields on which two ModelConfigs differ, as {field: (a, b)}."""
    return {f.name: (getattr(seat_a, f.name), getattr(seat_b, f.name))
            for f in dataclasses.fields(seat_a)
            if getattr(seat_a, f.name) != getattr(seat_b, f.name)}


def precondition_met(seats: dict, required: list) -> tuple:
    """Evaluate a config's `required_seat_state` against a seat roster.

    Returns (met, unmet) where `unmet` lists human-readable failures. Kept as a
    plain function so it can be exercised against synthetic rosters, which is
    the only way to show it can answer both ways.
    """
    unmet = []
    for req in required:
        seat = seats.get(req["seat"])
        if seat is None:
            unmet.append(f"{req['seat']}: no such seat")
            continue
        got = getattr(seat, req["field"], "<MISSING>")
        if got != req["must_equal"]:
            unmet.append(
                f"{req['seat']}.{req['field']} is {got!r}, "
                f"needs {req['must_equal']!r}")
    return (not unmet), unmet


class TestSeatContrastArm:

    def _c(self) -> dict:
        return _load("d11_seat_contrast_diversity_arm.json")

    def test_the_precondition_names_real_seats_and_real_fields(self):
        seats = _live_seats()
        fields = {f.name for f in dataclasses.fields(next(iter(seats.values())))}
        for req in self._c()["_seat_contrast"]["required_seat_state"]:
            assert req["seat"] in seats, req
            assert req["field"] in fields, req

    def test_the_evaluator_answers_both_ways(self):
        """Discrimination. Two synthetic rosters, one satisfying the
        precondition and one not; the evaluator must separate them. Without
        this the launch-block test below could be passing on an evaluator that
        always says no."""
        required = self._c()["_seat_contrast"]["required_seat_state"]
        seats = _live_seats()
        restored = {k: dataclasses.replace(v) for k, v in seats.items()}
        restored["Codex"] = dataclasses.replace(restored["Codex"], api="codex_exec")
        lapsed = {k: dataclasses.replace(v) for k, v in seats.items()}
        lapsed["Codex"] = dataclasses.replace(lapsed["Codex"], api="openrouter")

        met_restored, _ = precondition_met(restored, required)
        met_lapsed, unmet_lapsed = precondition_met(lapsed, required)
        assert met_restored is True
        assert met_lapsed is False
        assert any("Codex.api" in u for u in unmet_lapsed), unmet_lapsed

    def test_launch_blocked_matches_the_measured_seat_state(self):
        """The forcing function. Whoever restores the Codex seat to `codex exec`
        must clear this flag in the same change, and whoever clears it without
        restoring the seat is caught here. It fails in both directions."""
        c = self._c()
        met, unmet = precondition_met(
            _live_seats(), c["_seat_contrast"]["required_seat_state"])
        assert c["_arm"]["launch_blocked"] is (not met), (
            f"config says launch_blocked={c['_arm']['launch_blocked']} but the "
            f"live roster says precondition met={met}. Unmet: {unmet}")

    def test_the_arm_is_not_null_today(self):
        """Arm C is only worth anything if its two seats receive different
        prompts. Weights, route and system-prompt file are identical at HEAD, so
        the composed phenotype is the entire remaining contrast. MEASURED by
        composing for both seats, not read off a table."""
        from bench.reference_runner_v3 import _compose_for_model
        c = self._c()
        pattern, domain = c["pattern"], c["domain"]
        a, b = c["models"]
        text_a = _compose_for_model(a, pattern, domain).rendered_text
        text_b = _compose_for_model(b, pattern, domain).rendered_text
        differs = text_a != text_b
        assert differs is c["_seat_contrast"]["measured_at_head"][
            "composed_phenotype_differs"], (
            f"config records composed_phenotype_differs="
            f"{c['_seat_contrast']['measured_at_head']['composed_phenotype_differs']}, "
            f"measured {differs} ({len(text_a)} vs {len(text_b)} chars). If the "
            f"phenotypes have been collapsed, Arm C is a null arm and the "
            f"design note must say so.")

    def test_the_recorded_context_budget_claim_is_still_true(self):
        """The config CORRECTS the standing record, which says the two seats
        differ in context budget (60K vs 80K). They do not. A correction that
        goes stale is the defect it was written to fix, so it is executed."""
        from bench.runner_core import CONTEXT_CHAR_BUDGET
        c = self._c()
        rec = c["_seat_contrast"]["measured_at_head"]
        equal = (CONTEXT_CHAR_BUDGET[rec["seat_a"]]
                 == CONTEXT_CHAR_BUDGET[rec["seat_b"]])
        assert equal is rec["context_char_budget_equal"], (
            f"config records context_char_budget_equal="
            f"{rec['context_char_budget_equal']}, measured {equal}: "
            f"{rec['seat_a']}={CONTEXT_CHAR_BUDGET[rec['seat_a']]}, "
            f"{rec['seat_b']}={CONTEXT_CHAR_BUDGET[rec['seat_b']]}")

    def test_the_two_seats_share_weights(self):
        """A CONDITION contrast requires identical weights. If the seats ever
        point at different models, Arm C stops splitting vendor diversity from
        condition diversity and becomes a second copy of Arm B."""
        seats = _live_seats()
        a, b = self._c()["models"]
        assert seats[a].model_id == seats[b].model_id, seat_field_diff(
            seats[a], seats[b])


# ─────────────────────────────────────────────────────────────────────────────
# 6. Cost. The design note quotes an upper bound on paid dispatches; the bound
#    is DERIVED from the configs, and the derivation lives here so the figure
#    travels with code that reproduces it.
# ─────────────────────────────────────────────────────────────────────────────

# Seats that bill per dispatch. CC2 runs on the Max subscription.
PAID_ROUTES = {"openrouter", "deepseek", "codex_exec", "google"}


def paid_seats(cfg: dict, seats: dict) -> list:
    return [m for m in cfg["models"] if seats[m].api in PAID_ROUTES]


def paid_review_dispatch_bound(cfg: dict, seats: dict) -> int:
    """Upper bound on BILLED REVIEW dispatches for one arm.

    paid seats x max_rounds x (1 + in-round re-ask), plus one connectivity
    probe per paid seat. DERIVED from the config, not measured from a run: it
    counts review dispatches and the preflight only. It does NOT count the
    tool-loop completions inside a single dispatch, the falsifier-gate
    re-asks, or any decomposed-dispatch fallback, all of which add tokens and
    some of which add calls. It is a floor for planning and a bound for the
    review path, and the note says so.
    """
    n_paid = len(paid_seats(cfg, seats))
    reask = 2 if cfg.get("inround_reask_enabled") else 1
    return n_paid * int(cfg["max_rounds"]) * reask + n_paid


class TestCostBound:

    def test_paid_seat_counts_match_what_each_config_declares(self):
        seats = _live_seats()
        for name in ARM_FILES:
            cfg = _load(name)
            assert len(paid_seats(cfg, seats)) == cfg["_arm"]["paid_seats"], (
                f"{name}: declared paid_seats={cfg['_arm']['paid_seats']}, "
                f"measured {paid_seats(cfg, seats)}")

    def test_the_single_model_arm_costs_no_paid_dispatches(self):
        seats = _live_seats()
        cfg = _load("d9_single_model_with_agents.json")
        assert paid_seats(cfg, seats) == []
        assert paid_review_dispatch_bound(cfg, seats) == 0

    def test_the_bound_quoted_in_the_design_note_is_reproduced_here(self):
        """The figures in D9_D11_Experiment_Design_2026-09-05.md come from this
        function applied to these configs. 0 + 64 + 4 for Arm B, 0 + 32 + 2 for
        Arm C, 102 in total."""
        seats = _live_seats()
        bounds = {n: paid_review_dispatch_bound(_load(n), seats)
                  for n in ARM_FILES}
        assert bounds["d9_single_model_with_agents.json"] == 0
        assert bounds["d9_multi_model_panel.json"] == 68
        assert bounds["d11_seat_contrast_diversity_arm.json"] == 34
        assert sum(bounds.values()) == 102

    def test_the_bound_responds_to_the_parameters_it_claims_to_use(self):
        """Discrimination: a bound that ignores max_rounds or the panel size is
        not a bound, it is a constant."""
        seats = _live_seats()
        cfg = _load("d9_multi_model_panel.json")
        base = paid_review_dispatch_bound(cfg, seats)
        longer = paid_review_dispatch_bound({**cfg, "max_rounds": cfg["max_rounds"] + 1}, seats)
        no_reask = paid_review_dispatch_bound({**cfg, "inround_reask_enabled": False}, seats)
        smaller = paid_review_dispatch_bound({**cfg, "models": ["CC2", "Codex"]}, seats)
        assert longer > base
        assert no_reask < base
        assert smaller < base


# ─────────────────────────────────────────────────────────────────────────────
# 7. Guards the arc already relies on, applied to the new configs.
# ─────────────────────────────────────────────────────────────────────────────

class TestArcInvariants:

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_the_frozen_target_is_frozen(self, name):
        """Three arms must review the same bytes. A target that repairs itself
        between arms makes the later arm an easier exam."""
        assert _load(name)["apply_fixes_back_enabled"] is False

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_cross_run_memory_is_off(self, name):
        """Immune memory persists findings ACROSS runs. Left on, whichever arm
        runs second inherits the first arm's findings and the experiment
        measures run order."""
        assert _load(name)["immune_memory_enabled"] is False

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_external_retrieval_is_off(self, name):
        o = _load(name)["_ouroboros"]
        assert o["api_access"] == []
        assert o["max_papers_per_round"] == 0
        assert not o.get("inject_brief") and not o.get("c_ext_enabled")

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_the_truth_criterion_is_on(self, name):
        """The primary metric is falsifier-gate CONFIRMED. With the gate off
        there is no answer-key-free truth criterion and the whole design, which
        deliberately does not wait on the seeded catalogue, collapses."""
        assert _load(name)["falsifier_gate_enabled"] is True

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_the_stall_detector_cannot_fire_via_gamma(self, name):
        """Config-level guard carried by every config since Exp 42: the stall
        thresholds sit above the gamma ceiling of 1.0."""
        cfg = _load(name)
        assert cfg["stall_gamma_terminate"] > 1.0
        assert cfg["stall_gamma_advisory"] > 1.0

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_neither_uncommissioned_mechanism_is_switched_on(self, name):
        """severity_calibration and the latent tagger are the subject of a
        separate outstanding item (D12) and no shipped config may enable them."""
        cfg = _load(name)
        assert not cfg.get("latent_tagger_enabled")
        assert not cfg.get("severity_calibration_enabled")

    @pytest.mark.parametrize("name", ARM_FILES)
    def test_the_launch_line_names_this_config(self, name):
        """Each config carries the one command that launches it. A launch line
        pointing at a sibling config is how an arm gets run twice and another
        not at all."""
        assert name in _load(name)["_launch"]
        assert "detached_launch.sh" in _load(name)["_launch"]


# ─────────────────────────────────────────────────────────────────────────────
# 8. The single-seat confirmation quorum, MEASURED by running the real status
#    updater rather than by reading the arithmetic.
# ─────────────────────────────────────────────────────────────────────────────

class TestSingleSeatQuorumDegenerates:
    """`_update_finding_statuses` computes the external panel size as
    `len(set(cfg.models) - {source_model})` and then
    `required = min(2, external_panel_size)` for severity >= 0.7. With one
    declared seat that is `min(2, 0) = 0`, and `independent_count >= 0` holds
    with no independent confirmation at all.

    The comment two lines above the arithmetic states the intended rule --
    "Floor: at least 1 independent external confirmation (source excluded)" --
    so the code disagrees with its own docstring. It has never fired because
    every config from Exp 40 to Exp 55 declared 5 seats; Arm A is the first to
    declare 1.

    Measured here, both ways, on the real registry and the real updater. The
    consequence for the design is the assertion at the end: while this holds,
    the primary metric must count falsifier-gate CONFIRMED only.
    """

    @staticmethod
    def _promote(models):
        import bench.reference_runner_v3 as rr
        from bench.dm._types import Finding
        reg = rr.FindingRegistry()
        f = Finding(finding_id="C0001", model_id="CC2", round_idx=0,
                    flaw_class="logic", severity=0.8, abstraction_index=0.5,
                    description="a critical raised by the only seat in the arm",
                    proposed_fix="", target_file="bench/cdsfl_registry/engine.py")
        cid = reg.register(f, "CC2")
        cfg = rr.RunnerConfig(experiment_name="quorum_probe", models=models,
                              test_article="bench/cdsfl_registry/engine.py")
        rr._update_finding_statuses(reg, 1, cfg)
        return reg.entries[cid]["status"]

    def test_a_five_seat_panel_does_not_promote_an_uncorroborated_critical(self):
        """The reference behaviour, and the discrimination for the test below:
        if this ever returned CORROBORATED the probe would be measuring nothing
        specific to panel size."""
        assert self._promote(
            ["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"]) == "OPEN"

    def test_a_one_seat_panel_promotes_it_with_zero_confirmations(self):
        single = self._promote(["CC2"])
        if single == "OPEN":
            pytest.skip(
                "the single-seat quorum now floors at 1; the hazard is closed "
                "and the guard below is moot")
        assert single == "CORROBORATED", single

    def test_the_arm_records_the_hazard_while_it_is_live(self):
        """A hazard that is real and undocumented is how a result gets reported
        as though it were clean."""
        if self._promote(["CC2"]) == "OPEN":
            pytest.skip("hazard closed upstream")
        arm = _load("d9_single_model_with_agents.json")["_arm"]
        assert "_single_seat_quorum_hazard" in arm, (
            "Arm A is exposed to a confirmation quorum that degenerates at "
            "panel size 1 and its config does not say so")
        assert "CORROBORATED" in arm["_single_seat_quorum_hazard"]
