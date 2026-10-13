# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1979f9584827699976863da2476c2f4eae5940675bd6d830bbb39fd279884125
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
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

from bench.cdsfl_registry.composer import compose, build_interaction_pattern
import bench.reference_runner_v3 as rr

# The fixture test_falsifier_C0001_prune_inversion_2026-09-10.py measures
# pruning on: deepseek_v3 / software / meta_structured.
_MODEL, _DOMAIN, _PATTERN = "deepseek_v3", "software", "meta_structured"


def _compose(**kw):
    return compose(task_domain=_DOMAIN, model=_MODEL,
                   situation=build_interaction_pattern(_PATTERN), **kw)


class TestTheSwitch:
    def test_default_is_on_and_byte_identical_to_the_shipped_call(self):
        assert _compose().rendered_text == _compose(coherence_pruning=True).rendered_text

    def test_off_prunes_nothing_and_never_delivers_less(self):
        on = _compose(coherence_pruning=True)
        off = _compose(coherence_pruning=False)
        assert off.pruned_soft == []
        assert len(off.rendered_text) >= len(on.rendered_text)

    def test_this_fixture_actually_exercises_the_pruner(self):
        """Anti-vacuity: with pruning ON something IS pruned here, so the
        off-arm comparison above is a real contrast, not two identical runs."""
        on = _compose(coherence_pruning=True)
        assert on.pruned_soft, (
            "fixture no longer triggers pruning; pick one that does or this "
            "file proves nothing")


class TestItIsReachableFromARunnerConfig:
    def test_the_config_default_preserves_behaviour(self):
        assert rr.RunnerConfig().composer_coherence_pruning is True
        assert rr._COMPOSER_COHERENCE_PRUNING["on"] is True

    def test_the_mirror_reaches_compose_for_model(self):
        prev = rr._COMPOSER_COHERENCE_PRUNING["on"]
        try:
            rr._COMPOSER_COHERENCE_PRUNING["on"] = True
            on = rr._compose_for_model(_MODEL, _PATTERN, _DOMAIN)
            rr._COMPOSER_COHERENCE_PRUNING["on"] = False
            off = rr._compose_for_model(_MODEL, _PATTERN, _DOMAIN)
        finally:
            rr._COMPOSER_COHERENCE_PRUNING["on"] = prev
        assert on.pruned_soft and off.pruned_soft == [], (
            "flipping the mirror must flip the pruner, or the flag is an "
            "addition nothing reaches")
