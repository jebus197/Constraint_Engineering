"""The overlap record: who ACTUALLY raised a finding, not just who filed first.

WHY THIS EXISTS. `source_model` names one model. Measured 2026-09-02 (0C.49):
2 of 2,050 archived findings are recorded as raised by more than one model --
not because co-discovery is rare, but because when two models find one defect
the runner mints two unlinked canonicals and merges the second away. The overlap
signal is destroyed at exactly the moment it is created. A saturation curve
built from `source_model` is therefore linear BY CONSTRUCTION: one was built,
returned 0.201 per seat, and was withdrawn as an artefact of the schema.

Without an overlap statistic none of the established coverage estimators can
run at all, which is why the founder ruled this the item everything else waits
on (decision 7 of the 2026-09-03 sheet, approved 2026-09-04).

WHAT IS ASSERTED HERE, AND WHY IT EXECUTES. Every assertion below calls the
registry and inspects what it actually wrote. None reads the runner's source
text. That is deliberate: on 2026-09-04 a source-text test let a diagnostic ship
that returned a constant, because the producer and the consumer disagreed about
a key while each described itself correctly.
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

from reference_runner_v3 import Finding, FindingRegistry  # noqa: E402


def _finding(**kw) -> Finding:
    d = dict(finding_id="f1", model_id="CC2", round_idx=0, flaw_class=2,
             severity=0.8, abstraction_index=0.5, description="Test finding")
    d.update(kw)
    return Finding(**d)


class TestRegistrationSeedsTheRecord:
    def test_one_occasion_per_registration(self):
        reg = FindingRegistry()
        cid = reg.register(_finding(finding_id="a1", round_idx=2), "CC2")
        occ = reg.entries[cid]["occasions"]
        assert len(occ) == 1, f"expected 1 occasion at registration, got {occ}"
        assert occ[0]["model"] == "CC2"
        assert occ[0]["round"] == 2
        assert occ[0]["alias"] == "a1"
        assert occ[0]["via"] == "register"

    def test_source_model_is_untouched(self):
        """12 live consumers read source_model. This change must not move it."""
        reg = FindingRegistry()
        cid = reg.register(_finding(), "Gemini")
        assert reg.entries[cid]["source_model"] == "Gemini"


class TestAMergeCarriesTheOccasionAcross:
    """The single line that makes co-discovery visible."""

    def _two_models_one_defect(self):
        reg = FindingRegistry()
        keep = reg.register(_finding(finding_id="a1", round_idx=0), "CC2")
        dupe = reg.register(_finding(finding_id="b1", round_idx=1), "Fable")
        reg.resolve(dupe, "MERGED", round_idx=1, merged_into=keep)
        return reg, keep, dupe

    def test_the_target_gains_the_duplicates_occasion(self):
        reg, keep, _ = self._two_models_one_defect()
        occ = reg.entries[keep]["occasions"]
        assert len(occ) == 2, (
            "a merge is the runner saying these two reports are one defect; "
            f"the duplicate's occasion must survive it. Got {occ}")
        assert {o["model"] for o in occ} == {"CC2", "Fable"}

    def test_the_carried_occasion_records_where_it_came_from(self):
        reg, keep, dupe = self._two_models_one_defect()
        carried = [o for o in reg.entries[keep]["occasions"] if o["via"] == "merge"]
        assert len(carried) == 1
        assert carried[0]["merged_from"] == dupe
        assert carried[0]["merged_round"] == 1

    def test_the_overlap_count_is_now_derivable(self):
        """The whole point: distinct models per finding, which source_model cannot give."""
        reg, keep, _ = self._two_models_one_defect()
        distinct = {o["model"] for o in reg.entries[keep]["occasions"]}
        assert len(distinct) == 2, (
            "source_model would report 1 here, which is the artefact that made "
            "the saturation curve linear by construction")


class TestRepeatedMergesCannotInflateTheCount:
    """Ghost individuals: failing to re-recognise one biases the estimator up."""

    def test_merging_the_same_duplicate_twice_adds_nothing(self):
        reg = FindingRegistry()
        keep = reg.register(_finding(finding_id="a1"), "CC2")
        dupe = reg.register(_finding(finding_id="b1", round_idx=1), "Fable")
        reg.resolve(dupe, "MERGED", round_idx=1, merged_into=keep)
        first = len(reg.entries[keep]["occasions"])
        reg.resolve(dupe, "MERGED", round_idx=2, merged_into=keep)
        assert len(reg.entries[keep]["occasions"]) == first, (
            "a re-merge must not mint a second occasion for the same "
            "(model, round, alias); that is the ghost-individual pathology")

    def test_a_genuinely_distinct_second_duplicate_does_count(self):
        reg = FindingRegistry()
        keep = reg.register(_finding(finding_id="a1"), "CC2")
        d1 = reg.register(_finding(finding_id="b1", round_idx=1), "Fable")
        d2 = reg.register(_finding(finding_id="c1", round_idx=2), "Codex")
        reg.resolve(d1, "MERGED", round_idx=1, merged_into=keep)
        reg.resolve(d2, "MERGED", round_idx=2, merged_into=keep)
        assert len(reg.entries[keep]["occasions"]) == 3
        assert {o["model"] for o in reg.entries[keep]["occasions"]} == {"CC2", "Fable", "Codex"}


class TestTheRefusedMergesRecordNothing:
    """A merge the guards refuse must not carry occasions either."""

    def test_a_self_merge_carries_nothing(self):
        reg = FindingRegistry()
        cid = reg.register(_finding(), "CC2")
        reg.resolve(cid, "MERGED", round_idx=1, merged_into=cid)
        assert len(reg.entries[cid]["occasions"]) == 1

    def test_a_phantom_target_carries_nothing(self):
        reg = FindingRegistry()
        cid = reg.register(_finding(), "CC2")
        reg.resolve(cid, "MERGED", round_idx=1, merged_into="C9999")
        assert len(reg.entries[cid]["occasions"]) == 1

class TestARefusedMergeWritesNothing:
    """cc2, panel review 2026-09-04. THE GAP MY OWN P-PASS MISSED.

    The class below this one covered self-merge and phantom-target. Both return
    early, ABOVE the carry. The refusal that matters happens BELOW it: `MERGED`
    is in TOOL_ONLY_STATUSES, so a caller passing adjudicator="model" has the
    merge REFUSED -- the duplicate ends WITHHELD with merged_into None. The carry
    nonetheless ran, and the target permanently gained an occasion tagged
    via="merge", naming a merged_from that was never merged.

    A model's unverified assertion was writing the record that feeds coverage
    estimation. That is votes deciding where tools must, in the field added to
    make co-discovery measurable. Executed, not argued: cc2 reproduced it, and
    so did I before fixing it.
    """

    def _refused(self):
        reg = FindingRegistry()
        keep = reg.register(_finding(finding_id="a1"), "CC2")
        dupe = reg.register(_finding(finding_id="b1", round_idx=1), "Fable")
        reg.resolve(dupe, "MERGED", round_idx=1, merged_into=keep,
                    adjudicator="model")
        return reg, keep, dupe

    def test_the_merge_really_was_refused(self):
        reg, _, dupe = self._refused()
        assert reg.entries[dupe]["status"] == "WITHHELD"
        assert reg.entries[dupe].get("merged_into") is None

    def test_the_target_gains_nothing_from_a_refused_merge(self):
        reg, keep, _ = self._refused()
        occ = reg.entries[keep]["occasions"]
        assert len(occ) == 1, (
            "a merge the runner REFUSED must not write the overlap record; "
            f"a model's assertion would be deciding, not a tool. Got {occ}")
        assert all(o["via"] == "register" for o in occ)

    def test_a_TOOL_merge_is_still_carried(self):
        """The guard must not have been bought by disabling the feature."""
        reg = FindingRegistry()
        keep = reg.register(_finding(finding_id="a1"), "CC2")
        dupe = reg.register(_finding(finding_id="b1", round_idx=1), "Fable")
        reg.resolve(dupe, "MERGED", round_idx=1, merged_into=keep)  # tool
        assert len(reg.entries[keep]["occasions"]) == 2
        assert {o["model"] for o in reg.entries[keep]["occasions"]} == {"CC2", "Fable"}


class TestTheDedupKeyIsCanonicalIdNotAlias:
    """cc2, same review. The old key was stricter than the registry's own.

    `(model, round, alias)` collides when one model reuses a finding_id within a
    round for two genuinely distinct defects. The registry mints SEPARATE
    canonicals for those, so the old key contradicted the registry's identity
    notion and undercounted -- biasing coverage DOWN, while the refused-merge
    bug biased it UP. They do not cancel.
    """

    def test_two_distinct_defects_sharing_an_alias_both_count(self):
        reg = FindingRegistry()
        keep = reg.register(_finding(finding_id="a1"), "CC2")
        d1 = reg.register(_finding(finding_id="dup", round_idx=1,
                                   description="null deref in parser"), "Fable")
        d2 = reg.register(_finding(finding_id="dup", round_idx=1,
                                   description="race in scheduler"), "Fable")
        reg.resolve(d1, "MERGED", round_idx=1, merged_into=keep)
        reg.resolve(d2, "MERGED", round_idx=1, merged_into=keep)
        occ = reg.entries[keep]["occasions"]
        assert len(occ) == 3, (
            "3 distinct canonicals were merged; an alias-keyed dedup returns 2 "
            f"and undercounts the recapture. Got {len(occ)}: {occ}")
        assert len({o["from_canonical"] for o in occ}) == 3

    def test_re_merging_the_same_canonical_still_adds_nothing(self):
        reg = FindingRegistry()
        keep = reg.register(_finding(finding_id="a1"), "CC2")
        dupe = reg.register(_finding(finding_id="b1", round_idx=1), "Fable")
        reg.resolve(dupe, "MERGED", round_idx=1, merged_into=keep)
        first = len(reg.entries[keep]["occasions"])
        reg.resolve(dupe, "MERGED", round_idx=2, merged_into=keep)
        assert len(reg.entries[keep]["occasions"]) == first
