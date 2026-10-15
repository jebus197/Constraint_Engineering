"""The coherence-pruner ablation switch: default-on byte-identical, off is
reachable from a RunnerConfig, and off never delivers LESS directive text.

2026-10-13 FREE PANEL, ITEM 5. The brief proposed retiring the pruner by
hand-trimming the directive set until "the pruner has nothing to do". That
mechanism is BACKWARDS for this pruner: `_count_constraints` reads only the
merged TOML policy, so the density `_prune_for_coherence` enforces has a text-
independent numerator, and SHORTENING the text RAISES density (SymPy:
d(L2)-d(L1) = 4*C*(L1-L2)/(L1*L2) > 0 for L2 < L1; z3 'shorter AND density did
not worsen' unsat; committed proof in
test_falsifier_C0001_prune_inversion_2026-09-10.py). A hand-trimmed canon
would trigger MORE pruning, not none. Retirement therefore needs an ablation
measurement, not a hope -- this switch is the instrument the next simulated
run uses, per the 2026-07-18 pruning review's own lean-vs-full gate.
"""
import types

import contextlib

from bench.cdsfl_registry.composer import (
    MODEL_COHERENCE_BUDGETS, compose, build_interaction_pattern,
)
import bench.reference_runner_v3 as rr


@contextlib.contextmanager
def tightened_budget(value: float = 1e-6):
    """★ ADDED 2026-10-15. The live grid no longer exceeds any budget, so the
    pruner cannot be exercised on it, and a test that cannot exercise the
    mechanism proves nothing about the ablation arm.

    WHY THE LIVE GRID CHANGED. Delivering the project's own specification whole
    (founder's ruling 2026-10-14) multiplies the rendered length by about 5.7,
    and that length is the DENOMINATOR of `constraint_density` while
    `constraint_count` comes from the TOML policy and does not grow. Measured
    2026-10-15: 0 of 50 real compositions over budget, 0.0000%, Wilson
    [0.0000%, 7.1348%]; max density 0.002835 against a smallest budget of 0.010,
    3.5277 times below it. Producer:
    `scripts/the_spec_is_not_work_2026-10-15.py`.

    THE BUDGETS ARE STALE BY CONSTRUCTION AND ARE NOT HAND-RETUNED. The project
    derives them from experiment logs
    (`update_coherence_budgets_from_experiments`), and the next 2 free runs are
    where that measurement comes from. Until then the ablation arm's
    REACHABILITY is what these tests pin, with the budget supplied explicitly.
    """
    saved = dict(MODEL_COHERENCE_BUDGETS)
    try:
        for model in saved:
            MODEL_COHERENCE_BUDGETS[model] = value
        MODEL_COHERENCE_BUDGETS.setdefault(_MODEL, value)
        MODEL_COHERENCE_BUDGETS[_MODEL] = value
        yield
    finally:
        MODEL_COHERENCE_BUDGETS.clear()
        MODEL_COHERENCE_BUDGETS.update(saved)

# The fixture test_falsifier_C0001_prune_inversion_2026-09-10.py measures
# pruning on: deepseek_v3 / software / meta_structured.
_MODEL, _DOMAIN, _PATTERN = "deepseek_v3", "software", "meta_structured"


def _compose(**kw):
    return compose(task_domain=_DOMAIN, model=_MODEL,
                   situation=build_interaction_pattern(_PATTERN), **kw)


class TestTheSwitch:
    def test_the_default_is_now_OFF_because_he_retired_it(self):
        """REPLACED ON HIS RULING, 2026-10-13, and it pins the opposite default.

        This asserted the default was ON and byte-identical to the shipped
        call, which was correct when the switch was built hours earlier. He
        then ruled: *"I also agree the mechanical directive pruner should be
        retired. We have no way of knowing what it feeds, or has been feeding
        our models. We can achieve the same pruning goal by hand, probably with
        more accuracy, so that the models get fed the same set of core
        directives every single time an experiment is run."*

        NOTHING IS REMOVED -- passing the flag still prunes, so the
        lean-versus-full ablation remains runnable. The assertion is inverted,
        not deleted, and the mechanism's reachability is pinned below.
        """
        assert _compose().rendered_text == _compose(
            coherence_pruning=False).rendered_text, (
            "the default no longer matches the un-pruned composition, so the "
            "retirement is not in force")

    def test_off_prunes_nothing_and_never_delivers_less(self):
        on = _compose(coherence_pruning=True)
        off = _compose(coherence_pruning=False)
        assert off.pruned_soft == []
        assert len(off.rendered_text) >= len(on.rendered_text)

    def test_the_pruner_is_inert_on_the_live_grid_and_that_is_recorded(self):
        """★ REBASED 2026-10-15. The live grid exceeds no budget, so pruning ON
        and OFF are identical there. Named rather than discovered later."""
        on = _compose(coherence_pruning=True)
        assert on.pruned_soft == [], (
            "a live composition is pruned again, so a coherence budget or a "
            "directive file has changed; remeasure `tightened_budget`'s "
            "docstring figures before editing this")

    def test_the_pruner_still_works_when_a_budget_is_actually_binding(self):
        """Anti-vacuity, preserved: the mechanism is still REACHABLE, which is
        what the additive standard requires of a retained capability."""
        with tightened_budget():
            on = _compose(coherence_pruning=True)
            off = _compose(coherence_pruning=False)
        assert on.pruned_soft, (
            "the pruner prunes nothing even with the budget forced to 1e-6, so "
            "the ablation arm the 2026-07-18 review requires cannot be run")
        assert off.pruned_soft == []
        assert len(off.rendered_text) >= len(on.rendered_text)


class TestItIsReachableFromARunnerConfig:
    def test_the_config_default_is_retired_and_the_flag_still_works(self):
        """His ruling at the config layer, plus proof the capability survives.

        A retirement that removed the mechanism would breach the additive
        standard; a retirement that left the default ON would not be a
        retirement. Both halves are asserted here.
        """
        assert rr.RunnerConfig().composer_coherence_pruning is False, (
            "the runner still prunes by default; his 2026-10-13 retirement is "
            "not in force")
        assert rr.RunnerConfig(composer_coherence_pruning=True
                               ).composer_coherence_pruning is True, (
            "the pruner can no longer be switched back on, so the ablation "
            "arm the 2026-07-18 review requires cannot be run")
        # THE MODULE MIRROR CARRIES THE SAME RETIREMENT. It existed to let
        # `_compose_for_model` see the config without threading it through, so
        # a mirror still defaulting ON would silently prune while the config
        # said otherwise -- the two-copies-of-one-rule shape this round already
        # found once, in the queue count against the alarm collector.
        assert rr._COMPOSER_COHERENCE_PRUNING["on"] is False, (
            "the module mirror still defaults to pruning, so a dispatch would "
            "prune while RunnerConfig says it is retired")

    def test_the_mirror_reaches_compose_for_model(self):
        """★ REBASED 2026-10-15: the budget is supplied explicitly, because the
        live grid no longer binds it. The PROPERTY is unchanged -- flipping the
        mirror must flip the pruner, or the flag is an addition nothing
        reaches."""
        prev = rr._COMPOSER_COHERENCE_PRUNING["on"]
        try:
            with tightened_budget():
                rr._COMPOSER_COHERENCE_PRUNING["on"] = True
                on = rr._compose_for_model(_MODEL, _PATTERN, _DOMAIN)
                rr._COMPOSER_COHERENCE_PRUNING["on"] = False
                off = rr._compose_for_model(_MODEL, _PATTERN, _DOMAIN)
        finally:
            rr._COMPOSER_COHERENCE_PRUNING["on"] = prev
        assert on.pruned_soft and off.pruned_soft == [], (
            "flipping the mirror must flip the pruner, or the flag is an "
            "addition nothing reaches")
