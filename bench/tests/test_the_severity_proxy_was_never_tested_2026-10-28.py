"""The 0.7 proxy's agreement with its rubric was measured on a boundary band.

This guard EXECUTES the producer and asserts on what it returns. It does not
read its source text, because a source-text assertion proves only that the
module describes itself consistently -- `execute-do-not-grep`, and the converse
measured on 2026-10-28, when 9 of 36 suite failures were guards accusing correct
code.

WHAT EACH BLOCK WOULD CATCH IF IT WERE REVERTED, which is the test of whether
the assertion reaches anything:

  * `TestTheStoredResultReproduces` -- changing CUT, the audit file, or the
    judgeability filter moves the 2x2 and the kappa. The stored figures are the
    ones `.claude/CLAUDE.md` cites, so they are the thing a future edit must
    not silently move.
  * `TestTheCorpusIsABoundaryBand` -- the mechanism. If someone widens the
    audit corpus (which would be the right repair) these assertions go red and
    ask for the headline to be restated.
  * `TestTheNullIsUninformativeNotNegative` -- the finding itself. If the
    strong hypothesis's predicted in-band odds ratio ever falls OUTSIDE the
    measured interval, the corpus has become able to separate the hypotheses
    and the finding is retired.
  * `TestTheInstrumentItselfIsSound` -- the falsification this finding
    survived. Range restriction is not a blanket excuse: it must leave
    reader-reader agreement alone while crippling the proxy comparison. If
    reader agreement ever reads near chance too, the labels are the problem and
    this whole finding is wrong.
  * `TestTheCleanArmCannotBeLocated` -- the limit analysis cannot repair. If a
    per-item redaction flag ever appears, the blinded subsample becomes
    recoverable and a better measurement is available without new adjudication.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "the_severity_proxy_was_never_tested_2026-10-28.py"

# Small but FIXED: the producer seeds its own generator, so a pinned trial count
# makes the simulated figures reproducible rather than flaky. A flaky guard is
# worse than a red one (measured 2026-10-25: 4 of 8, fail/pass/fail).
TRIALS = 150


@pytest.fixture(scope="module")
def produced():
    if not PRODUCER.is_file():
        pytest.skip(f"producer absent at {PRODUCER}")
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("_sev_proxy_producer", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.measure(trials=TRIALS)


class TestTheStoredResultReproduces:
    """The figures the project's own directive cites must still compute."""

    def test_the_judgeable_set_is_unchanged(self, produced):
        assert produced["n_audited"] == 286
        assert produced["n_judgeable"] == 259, (
            "the judgeable set moved; every figure below is conditioned on it")

    def test_the_two_by_two_is_exact(self, produced):
        assert produced["table"] == [[114, 67], [51, 27]]

    def test_kappa_matches_the_directive_and_two_tools_agree(self, produced):
        assert produced["kappa"] == pytest.approx(-0.022688, abs=5e-7), (
            "`.claude/CLAUDE.md` cites kappa = -0.0227 for this comparison")
        assert produced["kappa"] == pytest.approx(produced["kappa_manual"], abs=1e-12), (
            "sklearn and the hand computation disagree; one of them is wrong")

    def test_the_fisher_result_matches_the_directive(self, produced):
        assert produced["fisher_p"] == pytest.approx(0.778818, abs=5e-7)
        assert produced["odds_ratio"] == pytest.approx(0.900790, abs=5e-7)

    def test_dichotomisation_is_not_the_cause(self, produced):
        """Ruled out BEFORE range restriction could be blamed."""
        assert produced["logit_p"] > 0.05, (
            "continuous severity now predicts the rubric inside the band, so "
            "the null was an artefact of cutting at 0.7 after all")
        assert produced["mw_p"] > 0.05
        assert produced["mean_sev_noncritical"] > produced["mean_sev_critical"], (
            "the mean severity of NON_CRITICAL items was HIGHER, which is what "
            "makes 'the proxy carries the signal' hard to sustain in the band")


class TestTheCorpusIsABoundaryBand:
    """The mechanism. Widening the corpus is the repair, and it fails here."""

    def test_the_band_is_narrow_against_the_real_sampling_frame(self, produced):
        assert produced["band_sd"] == pytest.approx(0.026915, abs=5e-7)
        assert produced["archive_sd"] == pytest.approx(0.224319, abs=5e-7)
        assert produced["sd_ratio"] > 8.0, (
            f"standard-error inflation fell to {produced['sd_ratio']:.4f}; if the "
            f"corpus has widened, restate the headline instead of keeping it")

    def test_the_archive_spans_the_full_range(self, produced):
        lo, hi = produced["archive_range"]
        assert lo == pytest.approx(0.0) and hi == pytest.approx(1.0), (
            "the band's narrowness only matters because the frame is wide")
        assert produced["archive_n"] >= 3237

    def test_the_band_holds_a_minority_of_archive_severities(self, produced):
        assert produced["share_in_band"] < 0.2, (
            f"{produced['share_in_band']:.6f} of archive severities fall in the "
            f"audited band")


class TestTheNullIsUninformativeNotNegative:
    """The finding. Retire it the day the corpus can separate the hypotheses."""

    def test_the_power_model_is_validated_on_the_real_fit(self, produced):
        rel = abs(produced["se_analytic"] - produced["se_observed"]) \
            / produced["se_observed"]
        assert rel < 0.05, (
            f"the analytic standard error is {rel:.4%} from the fit's own; the "
            f"power figures below rest on that agreement")

    def test_the_design_is_underpowered_against_a_strong_effect(self, produced):
        assert produced["power_vs_strong_in_band"] < 0.5, (
            f"power against the strong full-range effect is "
            f"{produced['power_vs_strong_in_band']:.4f}; above 0.5 the null "
            f"starts to carry real information and the finding weakens")

    def test_the_minimum_detectable_slope_is_calibrated(self, produced):
        assert 0.65 < produced["power_at_min_detectable"] < 0.92, (
            "the analytic minimum-detectable slope no longer delivers roughly "
            "80% power in simulation, so the 2 methods have diverged")
        assert produced["min_detectable_slope"] > produced["strong_slope"], (
            "the design can now detect the strong effect, which is exactly the "
            "condition under which this finding is retired")

    def test_the_first_order_step_is_not_load_bearing(self, produced):
        """exp(beta . delta-mean) is an APPROXIMATION of a dichotomised odds ratio.

        If it ever stops agreeing with the exact marginal figure, the headline
        has started resting on the approximation and must be requoted.
        """
        assert produced["or_predicted_first_order"] == pytest.approx(
            produced["or_predicted_mpmath"], abs=1e-9), "numpy and mpmath disagree"
        assert produced["or_first_order_relative_error"] < 0.01, (
            f"the first-order step is now {produced['or_first_order_relative_error']:.4%} "
            f"from the exact marginal odds ratio; quote the exact one only")
        assert produced["or_predicted_by_strong"] == pytest.approx(1.256464, abs=5e-7), (
            "the EXACT expected marginal odds ratio under the strong hypothesis")

    def test_the_observation_is_the_MODAL_outcome_under_the_strong_hypothesis(
            self, produced):
        """Stronger than "inside the interval", and trials-invariant by design."""
        assert produced["strong_draws_usable"] == 20000, (
            "the compatibility share must not move when --trials moves")
        assert produced["strong_share_inside_measured_ci"] == pytest.approx(
            0.792050, abs=5e-7), (
            f"{produced['strong_share_inside_measured_ci']:.6f} of draws under the "
            f"strong hypothesis land inside the measured interval. A fall below "
            f"0.5 would mean the observation is NOT typical under that hypothesis "
            f"and the finding weakens")
        assert produced["strong_median_or"] == pytest.approx(1.260417, abs=5e-7)

    def test_the_strong_hypothesis_predicts_what_was_observed(self, produced):
        """The decisive claim: both hypotheses predict the same interval."""
        assert produced["strong_prediction_inside_ci"] is True, (
            f"the strong hypothesis predicts an in-band odds ratio of "
            f"{produced['or_predicted_by_strong']:.6f} and the measured interval "
            f"is {produced['or_ci']}. If the prediction has fallen outside, this "
            f"corpus CAN now separate the hypotheses and the finding is wrong")

    def test_the_closed_form_is_recorded_as_optimistic(self, produced):
        """Why the analytic sample size must not be quoted."""
        n_closed = int(produced["n_analytic_closed_form"])
        near = min(produced["full_range_power"], key=lambda k: abs(k - n_closed))
        assert produced["full_range_power"][near] < 0.8, (
            f"simulation at n = {near} now reaches "
            f"{produced['full_range_power'][near]:.4f}; the closed form has "
            f"stopped being optimistic and the warning can be dropped")

    def test_the_costed_ask_is_sufficient(self, produced):
        assert produced["full_range_power"][63] > 0.85, (
            "the 63-item adjudication already costed no longer reaches power; "
            "recost it before asking him for it")


class TestTheInstrumentItselfIsSound:
    """The falsification this finding survived, and the condition that kills it."""

    def test_the_two_blind_readers_agree_far_above_chance(self, produced):
        assert produced["n_shared"] == 93
        assert produced["reader_kappa"] > 0.8, (
            f"reader-reader kappa is {produced['reader_kappa']:.6f}. Below 0.8 "
            f"the rubric labels are themselves noisy, and the fault moves from "
            f"the corpus to the instrument -- which makes this finding wrong")
        assert produced["reader_agreement"] > 0.9

    def test_both_readers_agree_with_the_proxy_at_chance(self, produced):
        """Restriction bites the continuous predictor, not the binary construct."""
        for k in ("reader1_vs_proxy_kappa", "reader2_vs_proxy_kappa"):
            assert abs(produced[k]) < 0.3, f"{k} = {produced[k]:+.6f}"
        assert produced["reader_kappa"] > 3 * max(
            abs(produced["reader1_vs_proxy_kappa"]),
            abs(produced["reader2_vs_proxy_kappa"])), (
            "the gap between reader-reader and reader-proxy agreement is what "
            "separates 'the corpus is wrong' from 'the labels are noise'")


class TestTheStrongestObjectionIsAnswered:
    """"The gate only acts AT the cut, so only in-band agreement matters."

    It is the objection most likely to retire this finding, and it is false by
    measurement rather than by argument. If these assertions ever fail, the
    gate's work HAS moved into the audited band and the objection becomes good.
    """

    def test_most_of_the_gates_work_happened_outside_the_audited_band(self, produced):
        assert produced["archive_outside_share"] == pytest.approx(0.867161, abs=5e-7)
        lo, hi = produced["outside_share_cp"]
        assert lo > 0.8, (
            f"only {produced['archive_outside_share']:.6f} of entries sit outside "
            f"the band; if this falls toward 0.5 the band is representative and "
            f"the objection stands")

    def test_the_gates_CONFIDENT_calls_are_the_unexamined_ones(self, produced):
        assert produced["critical_calls_unexamined_share"] == pytest.approx(
            0.794744, abs=5e-7), (
            "the share of CRITICAL calls made at a severity above the audited "
            "band. These are confident classifications, so a disagreement there "
            "is more consequential than one at the cut, not less")
        assert produced["critical_above_band"] == 1119
        assert produced["archive_critical"] == 1408

    def test_the_band_bounds_are_read_from_the_data(self, produced):
        lo, hi = produced["band_bounds"]
        assert (lo, hi) == pytest.approx((0.65, 0.74)), (
            "the band is measured from the audit corpus, not hard-coded; a "
            "different corpus must move these")


class TestTheCleanArmCannotBeLocated:
    """206 of 259 verdicts may have been formed with the number in view."""

    def test_no_per_item_redaction_flag_is_stored(self, produced):
        assert produced["per_item_redaction_flag_present"] is False, (
            "a per-item redaction flag now exists, so the blinded subsample can "
            "be located and measured on its own -- do that before asking him "
            "for fresh adjudications")

    def test_the_method_line_still_claims_partial_blinding(self, produced):
        assert "redacted from 80 of 286" in produced["method_line"], (
            "the audit's own method line no longer states the blinding it "
            "cannot evidence per item")
