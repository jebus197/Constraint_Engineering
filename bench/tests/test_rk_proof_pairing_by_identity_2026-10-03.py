#!/usr/bin/env python3
"""The worked proof must be paired to the finding that WROTE it, not to an index.

WHAT WENT WRONG. `validate_round_rk` paired CORROBORATION sections to findings by
POSITION, on a comment's assumption that "both are in document order". Measured on
study_run1b round 7, the 6 seats emitted 3, 27, 8, 29, 6 and 6 sections against 4
registered findings. So:

  * a finding whose index exceeded the section count was stamped SKIP whatever it
    had written -- C0073 carried a block `_validate_rk_computation` returns PASS on
    (model_rk 0.49, recomputed 0.4851, delta 0.0049) and was stored SKIP/None/None,
    which left its severity unproven, which put it in the A4 blocker, which blocked
    convergence; and
  * where the counts merely misaligned, finding i's claimed R_k was checked against
    finding j's parameters -- a PASS that validates the wrong arithmetic, silently.

These tests EXECUTE both pairings against the same text and compare the outputs
(`execute-do-not-grep`): a source-text assertion could only show the module agrees
with itself, and this defect is precisely a producer and a consumer disagreeing
while each describes itself correctly.

The fix is ADDITIVE in both directions. `_extract_corroboration_sections` keeps its
signature and its behaviour, because the frozen v1 runner, 2 committed panel
falsifiers, `scripts/measure_rk_proof_compliance.py` and
`test_rk_clip_stops_at_an_arrow_2026-09-22` all read the old shape. Positional
pairing is RETAINED as the fallback, so a seat that emits no FINDING_ID is read
exactly as before. Nothing is removed; a correct path is added ahead of a wrong one.
"""
import pathlib
import re
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import reference_runner_v3 as R  # noqa: E402


class _F:
    """A Finding stand-in carrying only what validate_round_rk reads."""

    def __init__(self, finding_id, model_id):
        self.finding_id = finding_id
        self.model_id = model_id


# A response holding 2 blocks. The FIRST belongs to a finding that did not survive
# into the registry (merged, withdrawn, deduped -- all routine). Only the SECOND is
# registered. Positional pairing hands the survivor the FIRST block; identity
# pairing hands it its own.
TWO_BLOCKS = """FINDING_ID: F100
a claim that was later merged away
CORROBORATION.
R_old = 0.90
eta = 0.10
d = 0.10
p = 0.10
q = eta*d*p = 0.001
R_det = 0.90*(1-0.001)/(1-0.001*0.90) = 0.8993
S_k = 0.10
R_k = 0.8993
---
FINDING_ID: F609
the finding that survived into the registry
CORROBORATION.
R_old = 0.50
eta   = 0.35
d     = 0.80
p     = 0.85
q     = eta*d*p = 0.2380
R_det = 0.50*(1-0.2380)/(1-0.2380*0.50) = 0.4325
S_k   = 0.10
R_k = 0.4851
"""

NO_IDS = re.sub(r'FINDING_ID:\s*\S+\n', '', TWO_BLOCKS)


def _only_survivor():
    return [_F("F609", "Fable-SIM")]


class TestIdentityBeatsPosition:
    def test_the_two_pairings_disagree_on_this_text(self):
        """Premise check. If they agreed, the rest of this file proves nothing."""
        sections = R._extract_corroboration_sections(TWO_BLOCKS)
        owned = dict(R._extract_corroboration_sections_with_ids(TWO_BLOCKS))
        assert len(sections) == 2, f"expected 2 sections, got {len(sections)}"
        positional = R._validate_rk_computation(sections[0])      # what the old code used
        by_identity = R._validate_rk_computation(owned["F609"])    # what F609 actually wrote
        assert positional[1] != by_identity[1], (
            "PREMISE DEAD: position and identity select the same block here, so "
            "this text cannot demonstrate the defect"
        )
        # the survivor's own number is 0.4851; the merged-away finding's is 0.8993
        assert by_identity[1] == pytest.approx(0.4851, abs=1e-4)
        assert positional[1] == pytest.approx(0.8993, abs=1e-4)

    def test_validate_round_rk_now_uses_the_finding_own_block(self):
        out = R.validate_round_rk(_only_survivor(), {"Fable-SIM": TWO_BLOCKS})
        rows = out["Fable-SIM"]
        assert len(rows) == 1
        fid, status, model_rk, recomputed = rows[0]
        assert fid == "F609"
        assert status in R._RK_PROOF_ACCEPTED, (
            f"F609 wrote a recomputable block; status should be PASS/WARN, got {status}"
        )
        assert model_rk == pytest.approx(0.4851, abs=1e-4), (
            f"model_rk {model_rk} is not F609's own 0.4851 -- it has been paired "
            f"with another finding's arithmetic"
        )

    def test_the_seat_alias_form_still_matches(self):
        """A registry id is often the alias (Fable-SIM_F609) while the response
        writes the bare id (F609). Containment must bridge that, or every real
        run falls back to position and the fix is cosmetic."""
        out = R.validate_round_rk([_F("Fable-SIM_F609", "Fable-SIM")],
                                  {"Fable-SIM": TWO_BLOCKS})
        fid, status, model_rk, _ = out["Fable-SIM"][0]
        assert model_rk == pytest.approx(0.4851, abs=1e-4), (
            f"alias {fid} did not reach its own block; model_rk={model_rk}"
        )


class TestNothingWasTakenAway:
    def test_the_old_extractor_is_byte_for_byte_unchanged_in_behaviour(self):
        """9+ callers read this shape, including the frozen v1 runner."""
        sections = R._extract_corroboration_sections(TWO_BLOCKS)
        assert isinstance(sections, list)
        assert all(isinstance(s, str) for s in sections), (
            "the old extractor must keep returning plain strings"
        )
        assert len(sections) == 2

    def test_position_is_still_used_when_no_id_is_present(self):
        """Additive standard: a seat emitting no FINDING_ID must behave exactly as
        before, not become a SKIP."""
        owned = R._extract_corroboration_sections_with_ids(NO_IDS)
        assert owned and all(o is None for o, _ in owned), (
            "this fixture is supposed to carry no ids"
        )
        out = R.validate_round_rk([_F("F609", "Fable-SIM")], {"Fable-SIM": NO_IDS})
        _, status, model_rk, _ = out["Fable-SIM"][0]
        sections = R._extract_corroboration_sections(NO_IDS)
        expected = R._validate_rk_computation(sections[0])
        assert (status, model_rk) == (expected[0], expected[1]), (
            "with no ids available the result must equal the old positional result"
        )

    def test_a_finding_with_no_block_at_all_is_still_SKIP(self):
        out = R.validate_round_rk([_F("F999", "Fable-SIM")],
                                  {"Fable-SIM": "no corroboration anywhere here"})
        _, status, model_rk, recomputed = out["Fable-SIM"][0]
        assert status == "SKIP" and model_rk is None and recomputed is None


class TestTheC0073Shape:
    def test_a_finding_past_the_section_count_is_no_longer_a_spurious_skip(self):
        """The exact run-1b failure: more findings than the index can reach, but the
        finding's OWN block is present and recomputable."""
        findings = [_F(f"FPAD{i}", "Fable-SIM") for i in range(3)] + \
                   [_F("F609", "Fable-SIM")]
        out = R.validate_round_rk(findings, {"Fable-SIM": TWO_BLOCKS})
        rows = {fid: (st, mrk) for fid, st, mrk, _ in out["Fable-SIM"]}
        st, mrk = rows["F609"]
        assert st in R._RK_PROOF_ACCEPTED, (
            f"F609 sits at index 3 with only 2 sections; under positional pairing "
            f"it was SKIP. It wrote a valid block, so it must now be proven. got {st}"
        )
        assert mrk == pytest.approx(0.4851, abs=1e-4)


class TestTheMutation:
    def test_restoring_positional_pairing_breaks_the_identity_result(self):
        """A fix with no mutation check is a hypothesis. Rebuild the OLD pairing by
        hand over the same text and assert it gets the wrong answer -- so if someone
        reverts the loop, the first test above fails rather than passing vacuously."""
        sections = R._extract_corroboration_sections(TWO_BLOCKS)
        findings = _only_survivor()
        old_rows = []
        for i, f in enumerate(findings):
            if i < len(sections):
                old_rows.append((f.finding_id,) + R._validate_rk_computation(sections[i]))
            else:
                old_rows.append((f.finding_id, "SKIP", None, None))
        old_mrk = old_rows[0][2]
        new_mrk = R.validate_round_rk(findings, {"Fable-SIM": TWO_BLOCKS})["Fable-SIM"][0][2]
        assert old_mrk != new_mrk, (
            "the old and new pairings agree on this text, so the fix is untested"
        )
        assert old_mrk == pytest.approx(0.8993, abs=1e-4)
        assert new_mrk == pytest.approx(0.4851, abs=1e-4)
