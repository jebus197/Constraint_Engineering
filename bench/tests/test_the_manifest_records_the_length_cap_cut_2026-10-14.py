#!/usr/bin/env python3
"""The composition manifest must record what the global length cap removed.

JOINT ROUND his_rulings_2026-10-13, J1 falsifier. With the pruner retired
(`coherence_pruning=False`, the live default), `compose()` renders LONGER text,
and the global phenotype length cap (composer.py, "Apply global phenotype
length cap", `PhenotypeTransform.max_directive_chars`) truncates the tail of
the render: for deepseek_v3 (cap 4000) the domain directive survives to ~49%
and the situation packet -- the per-dispatch review target and adversarial
brief -- to 1 char, while `manifest["packets"]` lists every packet at its FULL
length and `pruned_soft=[]`. The record claims delivery the cap removed.

Producer: scripts/the_cap_cuts_what_the_manifest_claims_2026-10-14.py.

RED on the tree as delivered by the 2026-10-13 round (no `length_cap` record in
the manifest). GREEN once `compose()` stamps `manifest["length_cap"]` with
{fired, chars_cut, packets_cut}. The repair changes NO delivered byte --
`rendered_text` must be byte-identical before and after -- so replay
comparability is asserted here, not assumed.
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.cdsfl_registry.composer import (  # noqa: E402
    compose, PHENOTYPE_TRANSFORMS,
)

SIT = dict(
    review_target="SIM target: a 400-line numerical integrator",
    code_extracts=(
        "def integrate(f,a,b,n):\n    h=(b-a)/n\n"
        "    return sum(f(a+i*h) for i in range(n))*h"
    ),
    adversarial_brief=(
        "SIM adversarial brief: attack the trapezoid-vs-rectangle claim."
    ),
)


def _compose(model, prune=False):
    return compose("software", model, coherence_pruning=prune, **SIT)


class TestTheManifestRecordsTheCap:
    def test_a_capped_composition_says_so(self):
        """deepseek_v3, pruning off: the cap fires and the manifest admits it."""
        c = _compose("deepseek_v3")
        assert c.rendered_text.endswith("[... truncated for model capacity]"), (
            "fixture no longer exercises the cap; re-derive this test")
        rec = c.manifest.get("length_cap")
        assert isinstance(rec, dict), (
            "manifest carries no `length_cap` record: the global phenotype "
            "length cap cut delivered text and the provenance record claims "
            "full delivery (J1, joint round 2026-10-13)")
        assert rec.get("fired") is True
        assert rec.get("chars_cut", 0) > 0

    def test_the_record_names_which_packets_lost_text(self):
        c = _compose("deepseek_v3")
        rec = c.manifest.get("length_cap") or {}
        cut_layers = {p["layer"] for p in rec.get("packets_cut", [])}
        assert "situation" in cut_layers, (
            "the situation packet (review target, adversarial brief) was cut "
            "to ~1 char and the record does not name it")
        assert "domain" in cut_layers, (
            "the domain directive lost ~51% of its text and the record does "
            "not name it")

    def test_an_uncapped_composition_records_fired_false(self):
        c = _compose("opus_4_6")
        assert not c.rendered_text.endswith(
            "[... truncated for model capacity]")
        rec = c.manifest.get("length_cap")
        assert isinstance(rec, dict) and rec.get("fired") is False
        assert rec.get("packets_cut") == []

    def test_the_repair_changes_no_delivered_byte(self):
        """The cap record is manifest-only: rendered text identical to the
        pre-record construction (cap slice + marker)."""
        for model in PHENOTYPE_TRANSFORMS:
            c = _compose(model)
            cap = PHENOTYPE_TRANSFORMS[model].max_directive_chars
            marker = "\n[... truncated for model capacity]"
            if c.rendered_text.endswith(marker):
                body = c.rendered_text[: -len(marker)]
                assert len(body) == cap, (
                    f"{model}: delivered byte count changed; the repair was "
                    f"required to be manifest-only")
            else:
                assert len(c.rendered_text) <= cap
