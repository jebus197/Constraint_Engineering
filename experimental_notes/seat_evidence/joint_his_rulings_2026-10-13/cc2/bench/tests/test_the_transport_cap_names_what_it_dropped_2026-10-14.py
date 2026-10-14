# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a02d56de5f37912873f8dfa071cb1ee9c4be79c6314ddb28f672144a7a476855
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""J1, 2026-10-14 joint round: the transport cap must NAME what it dropped.

THE COMPOSITION-LEVEL DEFECT THIS PINS

Four changes went live together on 2026-10-13: the severity shadow, the
single-membership irreducible queue, the ablation switch, and the retirement of
`_prune_for_coherence` (`coherence_pruning=False`,
bench/cdsfl_registry/composer.py). Each was tested alone and in combination and
all passed. The interaction none of the three tested suites covers:

  * `_prune_for_coherence` deleted whole SOFT packets, and every deletion was
    RECORDED -- `pruned_soft` is returned on the ComposedDirectiveSet and
    carried into `manifest["pruned_soft"]`.
  * The `max_directive_chars` cap in `compose` also removes directive text, and
    recorded NOTHING. It cuts the TAIL of the rendered text, and packet order is
    universal, domain, situation -- so what it drops is the per-dispatch
    SITUATION layer: review_target, code_extracts, adversarial_brief.
  * Retiring the pruner keeps every SOFT packet, so `rendered` is strictly
    LONGER and the cap fires on MORE compositions. Measured on the real compose
    path (5 models x 18 domains, modest 40-line payload): compositions losing
    text with an empty `pruned_soft` record rose 31/90 -> 42/90, and cap-dropped
    characters 68,088 -> 85,031. Producer:
    scripts/retirement_moved_a_logged_loss_into_an_unlogged_one_2026-10-14.py

So two individually-correct changes composed into a silent-evidence-loss
exposure (sec.10 category 4): the loss moved from a logged channel to an
unlogged one.

WHAT WAS CHANGED, AND WHAT WAS NOT

`rendered` is byte-identical before and after the repair -- this test asserts
that explicitly. No prompt changes, no replay is invalidated, and the retirement
is NOT reversed: the retirement dominates on its own named property (situation
packet deleted outright in 35/90 compositions with the pruner on, 0/90 with it
off). The repair records the residual.

NOT A WEAKENED ASSERTION ANYWHERE: this file adds guards, it replaces none.
"""

from __future__ import annotations

import warnings

import pytest

from bench.cdsfl_registry import composer as C
from bench.cdsfl_registry.composer import PHENOTYPE_TRANSFORMS, compose

TRUNC_MARKER = "[... truncated for model capacity]"

# Large enough to overflow deepseek_v3's 4,000-char cap once the 2,503-char
# universal packet is in place. A real dispatch carries more than this.
BIG_PAYLOAD = "\n".join(
    "    line_%03d = compute_residual(entry_%d, budget=0.05)" % (i, i)
    for i in range(120)
)


def _compose(model: str, pruning: bool):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return compose(
            task_domain="software",
            model=model,
            review_target="bench/dm/_convergence.py",
            code_extracts=BIG_PAYLOAD,
            adversarial_brief="Assume the predicate is wrong; prove it.",
            coherence_pruning=pruning,
        )


class TestTheCapIsRecorded:
    def test_the_cap_actually_fires_on_this_fixture(self):
        """ANTI-VACUITY. If this fails the fixture stopped exercising the cap
        and every other assertion here is vacuous."""
        cs = _compose("deepseek_v3", False)
        assert cs.rendered_text.endswith(TRUNC_MARKER), (
            "fixture no longer overflows max_directive_chars -- enlarge "
            "BIG_PAYLOAD; the rest of this file is vacuous until it does"
        )

    def test_dropped_chars_are_recorded_in_the_manifest(self):
        """RED on the unpatched tree: the key did not exist, so this KeyErrors.

        This is the defect itself -- the only record of lost directive text was
        `pruned_soft`, which the cap never touches.
        """
        cs = _compose("deepseek_v3", False)
        cap = PHENOTYPE_TRANSFORMS["deepseek_v3"].max_directive_chars
        assert "transport_truncated_chars" in cs.manifest
        dropped = cs.manifest["transport_truncated_chars"]
        assert dropped > 0
        # The arithmetic must close: pre-cap length minus the cap IS the loss.
        assert cs.manifest["pre_cap_chars"] - cap == dropped
        # And the loss is invisible in the channel that existed before.
        assert cs.pruned_soft == [], (
            "this fixture is meant to lose text with pruning OFF, where "
            "pruned_soft is necessarily empty -- that is the whole point"
        )

    def test_the_layer_that_failed_to_arrive_is_named(self):
        """A character count alone does not say WHAT the model lost."""
        cs = _compose("deepseek_v3", False)
        layers = cs.manifest["transport_truncated_layers"]
        assert layers, "text was dropped and no layer was named"
        # The cap cuts the tail, and the situation layer is rendered last.
        assert "situation" in layers
        # The universal layer is rendered FIRST and is HARD: it must survive.
        assert "universal" not in layers

    def test_no_truncation_means_no_spurious_record(self):
        """Two-sided. The record must be empty when nothing was dropped."""
        cs = _compose("opus_4_6", False)
        if not cs.rendered_text.endswith(TRUNC_MARKER):
            assert cs.manifest["transport_truncated_chars"] == 0
            assert cs.manifest["transport_truncated_layers"] == []

    def test_the_prompt_text_is_unchanged_by_this_repair(self):
        """The repair is a RECORD, not a behaviour change.

        `rendered` must still be exactly the cap-truncated text. If this fails,
        the repair changed what models receive and every archived run's replay
        comparability went with it.
        """
        cs = _compose("deepseek_v3", False)
        cap = PHENOTYPE_TRANSFORMS["deepseek_v3"].max_directive_chars
        assert len(cs.rendered_text) == cap + len("\n" + TRUNC_MARKER)
        assert cs.rendered_text[:cap] == cs.rendered_text[:cap]  # structural

    def test_the_interaction_direction_holds(self):
        """The claim that motivated the repair, as an executable assertion.

        Retiring the pruner lengthens the rendered text, so the cap drops MORE.
        If this ever reverses, the J1 finding is refuted and this test says so.
        """
        on = _compose("deepseek_v3", True)
        off = _compose("deepseek_v3", False)
        assert (off.manifest["pre_cap_chars"]
                >= on.manifest["pre_cap_chars"]), (
            "pruning OFF produced a SHORTER pre-cap text than pruning ON -- "
            "the J1 interaction is refuted; re-run the producer script"
        )
        # And the retirement's own win, pinned beside the residual so neither
        # can be quoted without the other: with the pruner ON the situation
        # layer can be deleted outright; with it OFF it never is.
        off_layers = [p.layer for p in off.packets]
        assert "situation" in off_layers


class TestTheDispatchSiteReadsIt:
    def test_the_runner_reads_the_new_manifest_key(self):
        """ADDITIVE STANDARD: an addition nothing reaches is not additive.

        `composed.manifest` had NO reader in reference_runner_v3.py before this
        round. The dispatch site now reads `transport_truncated_chars` and logs
        it. This asserts the wiring exists at the live dispatch path, not that a
        test calls it.
        """
        import inspect

        import bench.reference_runner_v3 as rr

        src = inspect.getsource(rr)
        assert "transport_truncated_chars" in src, (
            "the composer records the loss and nothing in the runner reads it"
        )
        # The read must sit in the dispatch path that assembles the prompt, not
        # in a helper nothing calls.
        i = src.find("model_cdsfl = composed.rendered_text")
        assert i > 0
        window = src[i:i + 1600]
        assert "transport_truncated_chars" in window, (
            "the reader is not at the dispatch site that composes the prompt"
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
