"""A panel brief must name DISAGREEMENT as an output field, not hope for it.

THE ROUND THIS EXISTS FOR. `integrity_advisory_r2_2026-10-02`, the STAR round of
2026-10-02. Its blind predecessor made "STRONGEST DISAGREEMENT WITH THIS BRIEF'S
OWN FRAMING — mandatory" an output field, and BOTH seats carried a disagreement.
The star brief replaced the output shape with RESOLUTION / WHO WAS RIGHT /
EVIDENCE / FIX / WHAT WOULD REFUTE THIS / CONFIDENCE and dropped the field,
asking for disagreement only as prose in the termination section. One of the 2
seats then omitted it, and `TestP5DisagreementIsPreserved` caught the round.

WHY A STAR ROUND IS THE DANGEROUS ONE. Its purpose is to reconcile, so it is the
round most able to produce agreement by DEFERENCE — which is not evidence, and
which this project does not accept as confirmation of anything
(`feedback_no_model_voting`).

WHAT JUSTIFIES THE CHECK: THE TEMPLATE ALREADY REQUIRED IT. The output section
of `bench/directives/universal/panel_brief_template.md` asks for "the strongest
disagreement with the brief's own framing" by name, and passes this check
unchanged. The defect was a validator that permitted divergence from the standard
it exists to enforce; 12 of 95 archived briefs diverged and nothing caught them.

WHAT IS NOT ESTABLISHED, AND AN EARLIER VERSION OF THIS FILE IMPLIED IT WAS.
Whether naming the field changes what seats return is UNPROVEN. Over 50 rounds
carrying both a brief and replies, 32 of 38 with the field had every seat state a
disagreement against 9 of 12 without it: Fisher exact two-sided p = 6.675478e-01,
within-period p = 6.187658e-01, scipy and mpmath agreeing to 1e-9. The round
above is consistent with chance. The check is kept for template conformance
alone, and this file does not claim otherwise.

WHY THE CHECK IS SECTION-SCOPED, AND THE FIRST VERSION WAS NOT. A whole-document
regex is defeated by a star brief, because a star brief embeds the previous
round's replies VERBATIM -- the word appears on 7 lines of the defective brief,
so a document-wide check PASSES the very brief it was written for, while that
brief's OUTPUT SECTION names no disagreement at all. Measured over all 95
archived briefs by `scripts/brief_disagreement_field_effect_2026-10-02.py`:

    section-scoped  : refuses 12 of 95 (12.6316%, Wilson [7.3757%, 20.7921%])
    whole-document  : refuses 15 of 95 (15.7895%, Wilson [9.8085%, 24.4296%])
                      and does NOT refuse the defective round

THE 2 FIGURES THAT STOOD HERE FIRST WERE BOTH FALSE -- "78 of 95 (82.1053%)" and
"1 of the 3 briefs carrying an output section" -- measured on 3 briefs read by
hand rather than on the archive. That is the check-one-member-then-assert-a-
universal shape this project has withdrawn claims for 11 times before; this is
the 12th.

Recorded as a Section P shortfall in
`bench/directives/universal/section_p_shortfalls.json`.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
VALIDATOR = REPO / "scripts" / "panel_brief_validate.py"
BLIND = REPO / "bench" / "logs" / "integrity_advisory_2026-10-02" / "BRIEF.md"
STAR = REPO / "bench" / "logs" / "integrity_advisory_r2_2026-10-02" / "BRIEF.md"

pytestmark = pytest.mark.skipif(not VALIDATOR.is_file(), reason="validator absent")

MARKER = "state its DISAGREEMENT: NOT FOUND"


def _validate(path: pathlib.Path) -> str:
    r = subprocess.run([sys.executable, str(VALIDATOR), str(path)],
                       capture_output=True, text=True, timeout=900, cwd=REPO)
    return r.stdout + r.stderr


class TestTheCheckCatchesTheRoundItExistsFor:

    @pytest.mark.skipif(not STAR.is_file(), reason="the star brief is not in this tree")
    def test_the_star_brief_is_refused(self):
        assert MARKER in _validate(STAR), (
            "the brief that lost a seat's disagreement is no longer refused")

    @pytest.mark.skipif(not BLIND.is_file(), reason="the blind brief is not in this tree")
    def test_the_blind_brief_is_not_refused(self):
        """ANTI-OVERREACH: the brief that DID carry the field must pass."""
        assert MARKER not in _validate(BLIND)


class TestTheScopeIsTheWholePoint:

    @pytest.mark.skipif(not STAR.is_file(), reason="the star brief is not in this tree")
    def test_a_whole_document_regex_would_have_MISSED_it(self):
        """THE REASON FOR SECTION SCOPING, pinned as a measurement.

        If this ever fails, the star brief stopped embedding the previous
        round's replies and the scoping rationale needs re-stating -- it does
        not mean the scoping became unnecessary.
        """
        text = STAR.read_text(encoding="utf-8", errors="ignore")
        assert re.search(r"strongest disagreement", text, re.I), (
            "the phrase is absent entirely, so a document-wide check would have "
            "caught it and the scoping rationale no longer holds as written")
        # ...and it is inside an EMBEDDED REPLY, not in the brief's own ask.
        first_embed = text.find("# ROUND 1, SEAT")
        where = text.lower().find("strongest disagreement")
        assert first_embed != -1 and where > first_embed, (
            "the phrase is in the brief's own body, not an embedded reply")

    def test_the_template_itself_passes(self):
        """PRODUCER AND CONSUMER MUST AGREE, by execution and not by reading.

        The check enforces the template; if the template ever stops naming the
        field, the validator would refuse the canonical standard itself.
        """
        tpl = REPO / "bench" / "directives" / "universal" / "panel_brief_template.md"
        if not tpl.is_file():
            pytest.skip("template absent")
        assert MARKER not in _validate(tpl), (
            "the validator now refuses the template it exists to enforce")

    def test_the_check_is_scoped_to_the_output_section_in_source(self):
        """`execute-do-not-grep` applies to the SCOPE, which has no behaviour of
        its own to call: assert the check sits in the section-scoped branch."""
        src = VALIDATOR.read_text(encoding="utf-8")
        i = src.find("The output check is SECTION SCOPED")
        j = src.find("state its DISAGREEMENT")
        assert i != -1 and j != -1 and j > i, (
            "the disagreement check moved out of the section-scoped block; a "
            "document-wide version passes the brief it exists to refuse")


class TestTheFieldMustBeReadableByTheDetector:
    """A BRIEF COULD DECLARE A FIELD NOTHING WOULD EVER RECOGNISE.

    Found 2026-10-06 by writing one. The joint round's brief asked for
    `## Residual disagreement`, which satisfies the validator's loose `\\bdisagree`
    search and is INVISIBLE to `carries_disagreement`, whose heading alternative
    requires the word to open the line. Both seats disagreed substantively and the
    round was recorded as having lost its disagreement.

    The validator's predicate was WEAKER than the detector's: 2 predicates about
    the same field, each individually correct, disagreeing about what counts. The
    repair binds the validator to the detector's own imported definition rather
    than widening the detector, because the 2026-10-02 entry records that widening
    makes it match mentions as well as assertions.
    """

    def _validate(self, text, tmp_path):
        import importlib.util
        import sys
        p = tmp_path / "BRIEF.md"
        p.write_text(text, encoding="utf-8")
        spec = importlib.util.spec_from_file_location(
            "pbv_under_test", REPO / "scripts" / "panel_brief_validate.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules["pbv_under_test"] = m
        spec.loader.exec_module(m)
        return m

    def test_a_qualified_heading_is_refused(self, tmp_path):
        m = self._validate("x", tmp_path)
        body = "- `## Residual disagreement` — a real body, not 'none'.\n"
        assert not m._field_the_detector_can_read(body), (
            "`## Residual disagreement` was accepted, and the reply detector "
            "cannot match it, so every seat's reply would be recorded as having "
            "lost its disagreement")

    def test_the_canonical_heading_is_accepted(self, tmp_path):
        m = self._validate("x", tmp_path)
        assert m._field_the_detector_can_read("- `## Disagreement` — a real body\n")
        assert m._field_the_detector_can_read(
            "- the strongest disagreement with the brief's own framing\n")

    def test_the_validator_and_the_detector_share_one_definition(self, tmp_path):
        """ANTI-DRIFT. The pattern must be IMPORTED, never copied."""
        src = (REPO / "scripts" / "panel_brief_validate.py").read_text(
            encoding="utf-8")
        assert "panel_condition_compliance_2026-09-10.py" in src, (
            "the validator does not import the detector's definition, so the 2 "
            "predicates can drift apart again")
        assert "DISAGREEMENT_RE" in src

    def test_the_live_template_still_passes(self, tmp_path):
        m = self._validate("x", tmp_path)
        tpl = (REPO / "bench" / "directives" / "universal"
               / "panel_brief_template.md")
        if not tpl.is_file():
            pytest.skip("the template is not on this checkout")
        assert m._field_the_detector_can_read(tpl.read_text(encoding="utf-8")), (
            "the canonical template would now be refused by its own validator")
