"""`composer_fallback` must be READ, and the budget warning must not overclaim.

TWO DEFECTS IN THE 2026-10-16 COMPOSER-PROVENANCE WORK, BOTH EXECUTED HERE.

1. `_composer_record_fields` (bench/reference_runner_v3.py) writes
   `composer_fallback: true` at 4 dispatch sites, on the stated and correct
   ground that "an absent key and a failed composition are different facts".
   Nothing read it. It was written at 4 sites and consumed at 0 -- the
   addition-nothing-reaches class confirmed 11 times in this project since
   2026-08-01, and the symmetric half of the additive standard.

   It was not merely inert. The same helper writes `directive_chars` and
   `prompt_chars_full` on the fallback branch, both AHEAD of `prompt_length`
   in `calibrate_coherence_thresholds`' `or`-chain, while `constraint_count`
   is absent there. So a fallback entry reached the `floor(c/70)/floor(c/4)`
   estimator on the FULL prompt size. The repair aimed at that estimator would
   have traded a visibly-constant artefact (1/25, forced at 3589 of 3709
   archived entries) for its asymptote 2/35 -- a number that VARIES, and so
   reads as measured, computed from a prompt into which the composer placed no
   constraints whatsoever.

2. The over-budget warning said "Coherence penalty κ(m,g) < 1 applies to
   effective detection". No κ of that kind exists anywhere in this repository;
   every `kappa` in the live tree is `kappa_set`, the convergence metric. The
   operator was told a detection penalty had been applied to the dispatch.
   None had, and with `_prune_for_coherence` retired by default (founder
   ruling 2026-10-13) the budget has no effectful consumer at all.

NEITHER FIX TOUCHES THE ARCHIVE. Archived entries carry no `composer_fallback`
key, so the `is True` guard leaves every one of them on the path it already
took. `test_an_archive_shaped_entry_calibrates_exactly_as_before` pins that.
"""

import json
import sys
import tempfile
import warnings
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.cdsfl_registry import composer as C  # noqa: E402

_RESP = "FINDING_ID: A\n\n" + ("x" * 400)


def _logdir(entries) -> Path:
    d = Path(tempfile.mkdtemp())
    (d / "r0.json").write_text(json.dumps(entries), encoding="utf-8")
    return d


def _archive_shaped(n: int = 8):
    """Exactly what the archive carries: a truncated `prompt_length` and nothing else."""
    return [{"model": "CC2-SIM", "prompt_length": 203, "response": _RESP,
             "metadata": {"findings_count": i % 4 + 1}} for i in range(n)]


def _with_fallback_keys(entries):
    """The 2026-10-16 record shape on a FAILED composition."""
    return [dict(e, metadata=dict(e["metadata"], composer_fallback=True,
                                  prompt_chars_full=6000 + i,
                                  directive_chars=6000 + i))
            for i, e in enumerate(entries)]


def _with_composed_keys(entries):
    """The 2026-10-16 record shape on a SUCCESSFUL composition."""
    return [dict(e, metadata=dict(e["metadata"], composer_fallback=False,
                                  constraint_density=0.01 + 0.004 * i,
                                  constraint_count=40 + i,
                                  prompt_chars_full=6000 + i,
                                  directive_chars=6000 + i))
            for i, e in enumerate(entries)]


class TestTheFallbackFlagIsConsumed:

    def test_a_fallback_entry_yields_no_calibrated_threshold(self):
        """The flag is read. A seat whose every entry is a fallback drops out."""
        out = C.calibrate_coherence_thresholds(_logdir(_with_fallback_keys(_archive_shaped())))
        assert "CC2-SIM" not in out, (
            "a composer fallback carries no constraint data, so no density may "
            f"be estimated from it; got {out}")

    def test_the_flag_is_what_does_it_and_not_the_absent_constraint_count(self):
        """Mutation guard: the SAME entries without the flag DO calibrate.

        Without this the test above would pass for the wrong reason -- e.g. if
        the entries were being dropped for lacking `constraint_count`. They are
        not: strip the flag and the estimator fires exactly as it did before.
        """
        ents = _with_fallback_keys(_archive_shaped())
        for e in ents:
            e["metadata"].pop("composer_fallback")
        out = C.calibrate_coherence_thresholds(_logdir(ents))
        assert "CC2-SIM" in out, (
            "with the flag removed these entries must still reach the "
            f"character estimator, or the guard above proves nothing; got {out}")

    def test_a_successful_composition_is_not_skipped(self):
        """The guard must not swallow the entries the whole repair exists for."""
        out = C.calibrate_coherence_thresholds(_logdir(_with_composed_keys(_archive_shaped())))
        assert "CC2-SIM" in out, (
            f"composer_fallback=False must calibrate from the recorded "
            f"density; got {out}")

    def test_an_archive_shaped_entry_calibrates_exactly_as_before(self):
        """Replay is untouched: 1/25, the value the producer measures.

        `floor(203/70)/floor(203/4) = 2/50 = 1/25`. If the guard had been
        written as a truthiness test rather than `is True`, or had keyed on the
        presence of the new char fields, this would move.
        """
        out = C.calibrate_coherence_thresholds(_logdir(_archive_shaped()))
        assert out["CC2-SIM"] == 0.04, out

    def test_the_fallback_number_the_guard_prevents_is_the_estimator_asymptote(self):
        """Names the quantity that WOULD have been reported, so the stake is explicit.

        `floor(c/70)/floor(c/4) -> 2/35 = 0.0571...` as c grows. A calibration
        drifting from 0.04 toward 0.0571 is not a measurement improving; it is
        the same character arithmetic on a longer string.
        """
        c = 6000
        assert (c // 70) / (c // 4) == 85 / 1500
        assert abs(85 / 1500 - 2 / 35) < 0.002


class TestTheBudgetWarningDoesNotOverclaim:

    def test_no_detection_penalty_is_asserted(self):
        """The retracted sentence must be gone, and the honest one present."""
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            C.compose(task_domain="mathematics", model="opus_4_6",
                      situation=None)
            # Force the branch regardless of today's density, by composing
            # against a budget of effectively zero.
            saved = dict(C.MODEL_COHERENCE_BUDGETS)
            try:
                C.MODEL_COHERENCE_BUDGETS["opus_4_6"] = 1e-9
                C.compose(task_domain="mathematics", model="opus_4_6",
                          situation=None)
            finally:
                C.MODEL_COHERENCE_BUDGETS.clear()
                C.MODEL_COHERENCE_BUDGETS.update(saved)
        msgs = [str(w.message) for w in caught]
        over = [m for m in msgs if "over coherence budget" in m]
        assert over, f"the over-budget branch did not fire; warnings were {msgs}"
        for m in over:
            assert "applies to effective detection" not in m, (
                "the warning still asserts a detection penalty that nothing in "
                f"this repository computes: {m}")
            assert "No detection penalty is applied" in m, m

    def test_the_only_kappa_in_the_registry_is_not_a_detection_penalty(self):
        """Source-level, and stated as such: this is the claim the fix rests on."""
        src = (REPO / "bench" / "cdsfl_registry" / "composer.py").read_text(encoding="utf-8")
        # The retracted claim must not reappear anywhere in the module.
        assert "κ(m,g) < 1 applies" not in src
