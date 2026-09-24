"""On a prose target the effect gates may REJECT but may never ADMIT.

WHY THIS FILE EXISTS. `bench/tests/test_prose_acceptance_stem.py` passes 175 of
175 and never sets `sk_score_prose_listings`. It executes one configuration of
two, so the guard runs and runs the wrong half. Every test here is parameterised
over BOTH flag values, so the property is pinned in the configuration that can
actually break it.

THE MEASURED DEFECT this pins shut (panel seat, 2026-09-22): with the flag on,
all 5 harmful fixes in the adversarial set scored ADMISSIBLE
(0.5333/0.8333/1.0000/1.0000/0.7333) and every one pulled R_k off 0.5000.
"""
import contextlib
import io

import pytest

from bench.reference_runner_v3 import (
    SK_ADMISSIBLE, SK_NO_SCORE, SK_REJECTED, _evaluate_sk_for_findings,
    _gates_introduced_new_defects, compute_sk,
)

from bench.tests.test_prose_acceptance_stem import (
    _copy_for_edit, _fix_text, _real_baseline, _register, FindingRegistry,
    FIXTURES, KEYS,
)


@pytest.fixture(params=KEYS)
def fixture(request):
    """The same five adversarial documents the acceptance suite uses. Declared
    here rather than imported, because a pytest fixture imported by name is not
    registered with this module's collector."""
    return next(f for f in FIXTURES if f.key == request.param)

BOTH_FLAGS = pytest.mark.parametrize("flag", [False, True],
                                     ids=["flag_off", "flag_on"])

# The three harms carrying a signal any static tool can see. The other two --
# `metrology` (corrupts measured evidence) and `algorithms` (improves the metric
# while destroying the function) -- are semantic and scored a clean
# e3 = e4 = 1.0. They must be UNSCORED, never admitted.
STATICALLY_VISIBLE = {"structural", "statistics", "numerical"}


def _sk(fixture, patches, flag):
    with contextlib.redirect_stdout(io.StringIO()):
        return compute_sk(_fix_text(fixture, patches, fixture.doc_path),
                          fixture.document, str(fixture.doc_path),
                          score_prose_listings=flag,
                          baseline=_real_baseline(fixture))


class TestNoProseFixIsEverAdmitted:
    """The one-sided rule, in both configurations."""

    @BOTH_FLAGS
    def test_the_harmful_fix_is_not_admitted(self, fixture, flag):
        assert _sk(fixture, fixture.harmful_fix, flag).tristate != SK_ADMISSIBLE

    @BOTH_FLAGS
    def test_even_the_correct_fix_is_not_admitted(self, fixture, flag):
        """A clean static sweep is not evidence a prose fix is correct.

        This is the half the founder's design turns on: an unscoreable fix is
        not a defective one, so the outcome is NO_SCORE -- not ADMISSIBLE, and
        not REJECTED either."""
        assert _sk(fixture, fixture.correct_fix, flag).tristate == SK_NO_SCORE

    @BOTH_FLAGS
    def test_an_unscored_fix_moves_rk_in_neither_direction(self, fixture, flag,
                                                           tmp_path):
        """Property 2, through the round-loop entry point."""
        for label, patches in (("harmful", fixture.harmful_fix),
                               ("correct", fixture.correct_fix)):
            registry = FindingRegistry()
            sub = tmp_path / f"{label}-{flag}"
            sub.mkdir(parents=True, exist_ok=True)
            copy = _copy_for_edit(fixture, sub)
            cid = _register(registry, _fix_text(fixture, patches, copy), copy)
            with contextlib.redirect_stdout(io.StringIO()):
                stats = _evaluate_sk_for_findings(
                    registry, fixture.document, str(copy),
                    _real_baseline(fixture), round_idx=1,
                    score_prose_listings=flag)
            res = registry.entries[cid]["sk_result"]
            assert stats["admissible"] == 0, f"{label} admitted with flag={flag}"
            if res["tristate"] == SK_NO_SCORE:
                # The founder's rule in its exact words: an unscoreable fix is
                # not a defective one, so it moves risk in NEITHER direction.
                assert res["R_new"] == pytest.approx(res["R_old"]), (
                    f"{label}/flag={flag}: NO_SCORE moved R_k "
                    f"{res['R_old']} -> {res['R_new']}")
            else:
                # A REJECTED fix is measured, not unmeasured, so Property 2
                # does not bind it. What DOES bind: a rejection may never be
                # paid out as a risk REDUCTION. Recorded rather than asserted
                # away -- the pipeline writes no R_k at all on a rejection, so
                # risk is left exactly where it stood. Whether a demonstrated
                # harmful fix ought to RAISE R_k is a live design question and
                # the founder's to settle; this pins only that it never lowers
                # it.
                assert res["tristate"] == SK_REJECTED
                assert "R_new" not in res or (
                    res["R_new"] >= res["R_old"]), (
                    f"{label}/flag={flag}: a REJECTED fix lowered R_k")


class TestTheRuleStillDiscriminates:
    """Anti-vacuity: 'reject everything' would pass the class above and teach
    the machinery nothing. The flag must BUY something."""

    def test_the_statically_visible_harms_are_actively_rejected(self, fixture):
        expected = (SK_REJECTED if fixture.key in STATICALLY_VISIBLE
                    else SK_NO_SCORE)
        assert _sk(fixture, fixture.harmful_fix, True).tristate == expected

    def test_and_with_the_flag_off_none_of_them_are(self, fixture):
        """The flag is what buys the rejection; without it there is no signal
        at all. This is the additive claim, stated as a test."""
        assert _sk(fixture, fixture.harmful_fix, False).tristate == SK_NO_SCORE

    def test_no_correct_fix_is_ever_rejected(self, fixture):
        assert _sk(fixture, fixture.correct_fix, True).tristate != SK_REJECTED


class TestTheHelperChargesOnlyWhatTheFixIntroduced:
    """A listing that was already dirty must not condemn a fix that left it
    exactly as dirty. The gates' own detail strings carry NEW separately from
    TOTAL and the helper keys on NEW."""

    def test_pre_existing_defects_are_not_charged_to_the_fix(self):
        assert _gates_introduced_new_defects({
            "e3_ruff": {"detail": "2 total, 0 new (baseline: 2)"},
            "e4_bandit": {"detail": "3 HIGH/1 MEDIUM "
                                    "(baseline: 3H/1M, new: 0H/0M)"}}) == []

    def test_newly_introduced_defects_are(self):
        reasons = _gates_introduced_new_defects({
            "e3_ruff": {"detail": "5 total, 1 new (baseline: 4)"},
            "e4_bandit": {"detail": "1 HIGH/0 MEDIUM "
                                    "(baseline: 0H/0M, new: 1H/0M)"}})
        assert len(reasons) == 2
        assert "1 new diagnostic" in reasons[0] and "1 new HIGH" in reasons[1]

    def test_an_unreadable_detail_is_silence_not_an_accusation(self):
        assert _gates_introduced_new_defects({"e3_ruff": {"detail": "garbled"},
                                              "e4_bandit": {}}) == []
        assert _gates_introduced_new_defects({}) == []


class TestThePythonPathIsUntouched:
    """`_scoring_prose` is False for every `.py` target, so no archived verdict
    and no Python run moves. Pinned by execution rather than by reading."""

    def test_a_python_target_is_still_scored_and_can_still_be_admitted(
            self, tmp_path):
        src = "def f(a, b):\n    return a + b\n"
        mod = tmp_path / "m.py"
        mod.write_text(src)
        fix = (f"<<<< SEARCH {mod}\n    return a + b\n"
               f"==== REPLACE\n    return a * b\n>>>>\n")
        for flag in (False, True):
            with contextlib.redirect_stdout(io.StringIO()):
                res = compute_sk(
                    fix, src, str(mod), score_prose_listings=flag,
                    baseline={"ruff_violations": 0,
                              "bandit_findings": {"high": 0, "medium": 0}})
            assert res.tristate == SK_ADMISSIBLE, flag
            assert "_prose_one_sided" not in res.gate_details
