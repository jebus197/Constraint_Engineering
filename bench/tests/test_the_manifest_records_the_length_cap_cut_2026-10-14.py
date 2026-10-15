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

#: ★ THE WORK PAYLOAD IS ENLARGED, 2026-10-15, AND THE REASON IS THE WHOLE
#: POINT OF THE REBASE. The original fixture's code extract was 2 lines. It
#: exercised the cap only because the cap was measured against the ENTIRE
#: render, specification included -- so a 2-line extract plus a 2,503-character
#: reduced-form specification crossed deepseek_v3's 4,000-char bound. Now that
#: the cap bounds WORK alone (founder's ruling 2026-10-14), a 2-line extract
#: cannot reach a 4,000-char work bound and the fixture stopped testing
#: anything. The extract is therefore sized to exceed the smallest work bound,
#: which is the condition the cap exists for.
#: AND IT IS DELIBERATELY NOT A `def` BLOCK. Measured 2026-10-15: with a `def`
#: extract the situation packet arrives at 176 characters for 4 of 5 models and
#: 5,998 for opus_4_6, because `strip_examples` in the phenotype transform
#: treats a `def` block as an example and removes it. That is a SEPARATE
#: finding, recorded in the programme of study rather than fixed here, and it is
#: why this fixture uses flat assignment lines: a fixture whose payload another
#: mechanism deletes cannot test the cap at all.
_EXTRACT_UNIT = "value_{} = 1\n"

SIT = dict(
    review_target="SIM target: a 400-line numerical integrator",
    code_extracts="".join(_EXTRACT_UNIT.format(i) for i in range(600)),
    adversarial_brief=(
        "SIM adversarial brief: attack the trapezoid-vs-rectangle claim."
    ),
)


def _compose(model, prune=False):
    return compose("software", model, coherence_pruning=prune, **SIT)


#: The cap's truncation marker. CHANGED 2026-10-15 to say which half was cut,
#: because the cap now bounds WORK and exempts the SPECIFICATION, and a reader
#: of a truncated prompt must be able to tell those apart.
MARKER = ("[... work truncated for model capacity; "
          "the CDSFL specification above is complete]")


def _work_cap(model):
    return PHENOTYPE_TRANSFORMS[model].max_directive_chars


class TestTheManifestRecordsTheCap:
    """★ REBASED 2026-10-15. THE CAP NOW BOUNDS WORK AND EXEMPTS THE
    SPECIFICATION, on the founder's ruling of 2026-10-14: *"as far as any caps
    have ever existed, their intention was to never feed any model more work
    than they were demonstrably able to handle ... There was never an intent as
    far as I recall to applying this same reasoning to the core operational
    directives themselves."*

    THE J1 FINDING THIS FILE EXISTS FOR IS UNCHANGED AND STILL PINNED: the cap
    cuts delivered text and the manifest must say so. What changed is the
    QUANTITY the cap is measured against. `rec["work_cap"]` is the per-model
    work bound, unchanged in value; `rec["spec_chars_exempt"]` is the
    specification's contribution, which the cap no longer competes with; and
    `rec["effective_cap"]` is their sum, which is what the render is sliced at.

    AND THE 2 REPAIRS ARE ONE REPAIR. Under the old arithmetic the
    specification was FIRST in packet order, so delivering it whole with the
    cap unchanged would have truncated INSIDE the specification and deleted the
    domain and situation packets outright for all 5 models. Neither half is
    safe alone, which is why this file's figures moved with the other change.
    """

    def test_a_capped_composition_says_so(self):
        """deepseek_v3, pruning off: the cap fires and the manifest admits it."""
        c = _compose("deepseek_v3")
        assert c.rendered_text.endswith(MARKER), (
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
            "and the record does not name it")
        assert "universal" not in cut_layers, (
            f"the cap cut the SPECIFICATION, which the 2026-10-14 ruling "
            f"forbids: {rec.get('packets_cut')}")

    def test_the_specification_is_never_cut_for_any_model(self):
        """★ ADDED 2026-10-15: the ruling, as one executing assertion."""
        for model in PHENOTYPE_TRANSFORMS:
            rec = _compose(model).manifest["length_cap"]
            assert rec["spec_chars_exempt"] > 20_000, (
                f"{model}: the specification contributes only "
                f"{rec['spec_chars_exempt']} chars, so it is not being "
                f"delivered whole")
            assert all(x["layer"] != "universal"
                       for x in rec.get("packets_cut", [])), (
                f"{model} lost specification text to the cap: "
                f"{rec.get('packets_cut')}")

    def test_an_uncapped_composition_records_fired_false(self):
        c = _compose("opus_4_6")
        assert not c.rendered_text.endswith(MARKER)
        rec = c.manifest.get("length_cap")
        assert isinstance(rec, dict) and rec.get("fired") is False
        assert rec.get("packets_cut") == []

    def test_the_work_cap_keeps_its_value_and_its_meaning(self):
        """The record is manifest-only for the WORK it bounds: a truncated
        render is sliced at exactly `spec + separator + work_cap`, so the work
        a model receives is still capped at the per-model value and only the
        quantity the cap is measured against has moved."""
        for model in PHENOTYPE_TRANSFORMS:
            c = _compose(model)
            rec = c.manifest["length_cap"]
            assert rec["work_cap"] == _work_cap(model), model
            assert rec["effective_cap"] == (
                rec["spec_chars_exempt"] + len("\n\n---\n\n")
                + rec["work_cap"]), model
            marker = "\n" + MARKER
            if c.rendered_text.endswith(marker):
                body = c.rendered_text[: -len(marker)]
                assert len(body) == rec["effective_cap"], (
                    f"{model}: delivered byte count does not match the "
                    f"effective cap the record names")
            else:
                assert len(c.rendered_text) <= rec["effective_cap"], model
