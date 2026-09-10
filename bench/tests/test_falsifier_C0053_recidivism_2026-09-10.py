"""Task 2.2: the falsifier exp47 C0053 never got, written and proved non-vacuous.

THE FINDING, verbatim from `bench/logs/exp47_.../runner_state.json`, C0053,
raised by Gemini at severity 0.8: "The cross-round recidivism check in
`check_sibling_admissibility` falsely penalizes models for fixing previously
rejected alternatives. When a model adds a missing contrast statement to a prior
alternative, `parse_contrast_statement` strips the new contrast statement from
the body. The resulting `alternative_text` is identical to the prior round's
`alternative_text`. The recidivism check then scores them as 1.0 isomorphic and
rejects the fixed alternative with `recidivism_near_copy`."

IT WAS RECORDED `UNCONFIRMED` WITH `falsifier_verdict: UNTOOLABLE` AND AN EMPTY
`falsifier_code`, and it was escalated to the human queue. Nothing was untoolable
about it: it is a claim about 2 named functions in a module that is still in this
repository. "Untoolable" meant nobody wrote the tool.

THE FINDING WAS CORRECT AND THE DEFECT IS ALREADY FIXED. `_recidivism_text` folds
the contrast statement back in for the cross-round comparison, and the source
comment beside it names Gemini's exact scenario. So this file does 2 things a
falsifier is for: it demonstrates the CURRENT code is right, and -- by reverting
the fix in memory -- it demonstrates that the demonstration could fail. A
falsifier that cannot fail confirms nothing, which is the vacuity this project
found in 8 of its own mutation tests on 2026-09-09.

WHY IT MATTERS BEYOND ONE FINDING. C0053 carries 3 pairs in
`experimental_notes/data/adjudication_by_repair.json` as NO_BASELINE --
"CONFIRMED/NO_FALSIFIER (no version reproduces both)". A missing falsifier is an
equipment failure that blocks adjudication, not a hard case.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.dm._divergence import (  # noqa: E402
    AlternativeRecord,
    DivergenceConfig,
    _recidivism_text,
    check_sibling_admissibility,
    parse_contrast_statement,
    score_isomorphism,
)

#: The scenario, in the finding's own terms. A prior-round alternative with NO
#: contrast statement, and this round's FIX: the same argument plus the contrast
#: statement that was missing. A system that punishes this punishes the repair.
BODY = ("The retry budget is truncated because the watchdog caps wall clock at a "
        "multiple of the timeout while the configured budget is the timeout times "
        "the retry count, so a seat dies inside its allowance.")
CONTRAST_LINE = ("Contrast: unlike the primary finding, which attributes the "
                 "timeout to model latency, this attributes it to configuration.")


def _record(body: str, contrast: str | None) -> AlternativeRecord:
    """Built from the REAL dataclass, whose fields were read rather than assumed.

    A first version passed `alternative_id=`, which does not exist. The class
    carries `primary_finding_id`, `alternative_text` and `contrast_statement`,
    among others -- checked with `dataclasses.fields` rather than guessed from
    the finding's prose.
    """
    return AlternativeRecord(
        primary_finding_id="C0001", alternative_text=body, dimension=None,
        contrast_statement=contrast)


class TestTheFindingsPremiseIsReal:
    """Gemini's mechanism, checked step by step rather than taken on trust."""

    def test_the_contrast_line_really_is_stripped_from_the_body(self):
        full = f"{BODY}\n{CONTRAST_LINE}"
        statement, stripped = parse_contrast_statement(full)
        assert statement, "the contrast line was not recognised at all"
        assert stripped.strip() == BODY.strip(), (
            "the premise of C0053 no longer holds: the contrast line is not "
            "stripped from the body, so the rest of the finding cannot follow")

    def test_and_that_makes_the_two_bodies_identical(self):
        """The step that turns a repair into a near-copy."""
        _s, stripped = parse_contrast_statement(f"{BODY}\n{CONTRAST_LINE}")
        assert score_isomorphism(BODY, stripped) == pytest.approx(1.0), (
            "the fixed alternative's stripped body is no longer identical to "
            "the prior round's, so the 1.0 score C0053 describes cannot arise")


class TestTheDefectIsFixed:
    def test_the_repair_is_not_scored_as_a_near_copy(self):
        """THE FALSIFIER. It fails if and only if the defect is present."""
        prior = _record(BODY, None)
        fixed = _record(BODY, CONTRAST_LINE)
        assert score_isomorphism(_recidivism_text(prior),
                                 _recidivism_text(fixed)) < 1.0, (
            "adding a previously-missing contrast statement still scores 1.0 "
            "against the prior round, so the recidivism check punishes the "
            "exact repair it should reward -- C0053 is live again")

    def test_the_gate_admits_the_repaired_alternative(self):
        """The finding is about a REJECTION, so the rejection is what is tested."""
        # THE REAL SIGNATURE: (alternatives, config, prior_round_alternatives),
        # and it takes a LIST and mutates in place. Read from the source, not
        # inferred from the finding's wording.
        fixed = _record(BODY, CONTRAST_LINE)
        check_sibling_admissibility(
            [fixed], config=DivergenceConfig(),
            prior_round_alternatives=[_record(BODY, None)])
        recidivist = [r for r in fixed.rejection_reasons
                      if "recidivism_near_copy" in r]
        assert not recidivist, (
            f"the repaired alternative was rejected as a near-copy: {recidivist}")


class TestTheFalsifierCanActuallyFail:
    """WITHOUT THIS, THE 2 TESTS ABOVE PROVE NOTHING.

    The fix is `_recidivism_text`, which folds the contrast statement back in.
    Reverting it means comparing `alternative_text` alone -- exactly the
    pre-fix behaviour C0053 describes. The comparison must then score 1.0.
    """

    def test_reverting_the_fix_reproduces_the_defect_exactly(self):
        prior = _record(BODY, None)
        fixed = _record(BODY, CONTRAST_LINE)
        # The pre-fix expression, written out rather than monkeypatched, so what
        # is being reverted is visible in the test itself.
        pre_fix_prior = prior.alternative_text
        pre_fix_fixed = fixed.alternative_text
        assert score_isomorphism(pre_fix_prior, pre_fix_fixed) == pytest.approx(1.0), (
            "the pre-fix comparison no longer scores 1.0, so this control does "
            "not reproduce the defect and the tests above are unproven")

    def test_the_two_differ_which_is_what_the_fix_changed(self):
        prior = _record(BODY, None)
        fixed = _record(BODY, CONTRAST_LINE)
        pre = score_isomorphism(prior.alternative_text, fixed.alternative_text)
        post = score_isomorphism(_recidivism_text(prior), _recidivism_text(fixed))
        assert pre > post, (
            f"the fix changed nothing: pre-fix {pre:.4f}, post-fix {post:.4f}")
