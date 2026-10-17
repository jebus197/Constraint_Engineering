"""The density ceiling is retired, and its calibrator refuses rather than no-ops.

HIS RULING, 2026-10-16, which is his LATEST word on the subject and supersedes
his earlier position that the recalibration "should be fixed, providing it
doesn't trim the operational directives": *"What would be the consequence of
retiring it completely? If there will be no consequence, then surely this is a
fourth and more sensible option? Why leave code in place that effectively does
nothing. The 'density' of a prompt shouldn't matter to a model, so long as the
core system/directives prompt survives untouched, and the overall prompt length
stays within a model's measured capability ceiling."*

WHY RETIREMENT PASSES THE ADDITIVE STANDARD, which requires a committed
measurement showing a replacement dominates rather than a judgement that it does.

  THE MECHANISM IS PROVABLY COUNTERPRODUCTIVE.
  `bench/tests/test_falsifier_C0001_prune_inversion_2026-09-10.py` establishes by
  z3 that "pruning shortened the text AND density did not worsen" is
  UNSATISFIABLE. Density is constraints over tokens, so removing text shrinks the
  denominator while the constraint count is unchanged: pruning to REDUCE density
  RAISES it. 6 tests, passing.

  THE REPLACEMENT IS NAMED AND ALREADY MEASURED. The operative bound is the one
  he states -- prompt LENGTH against a seat's measured capability, recorded as
  `max_successful_prompt_chars` and enforced by the decomposition guard at 0.9 of
  it. That is measured per seat from observed behaviour, where the density
  ceiling was a hand-set constant.

AND IT CLOSES TASK B8 BY SUPERSESSION rather than by work. B8 asked whether the
recalibration should be repaired, which meant emitting 2 extra fields per
dispatch into every run's records and invalidating replay against every older
run. Retiring the thing being calibrated costs none of that.

THE RETIREMENT RAISES RATHER THAN NO-OPPING. A retired function that silently
does nothing is indistinguishable from a working one, which is the defect class
this project keeps recording. And the original body is KEPT VISIBLE under a
`_retired_` name, because point-never-prune applies to code as well as to
sandboxes: a removal a reader cannot inspect is not reviewable.
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


@pytest.fixture(scope="module")
def composer():
    from bench.cdsfl_registry import composer as c
    return c


@pytest.fixture(scope="module")
def runner():
    from bench import reference_runner_v3 as m
    return m


def test_the_calibrator_refuses_rather_than_no_opping(composer):
    with pytest.raises(RuntimeError, match="RETIRED"):
        composer.update_coherence_budgets_from_experiments("bench/logs")


def test_the_refusal_names_his_ruling_and_the_replacement(composer):
    with pytest.raises(RuntimeError) as exc:
        composer.update_coherence_budgets_from_experiments("bench/logs")
    msg = str(exc.value)
    assert "founder ruling 2026-10-16" in msg, (
        "a refusal that does not name the ruling behind it reads as a bug")
    assert "max_successful_prompt_chars" in msg, (
        "a removal must name what replaces it, or it is a deletion")
    assert "prune_inversion" in msg, (
        "the refusal must cite the committed proof, so a reader can check it "
        "rather than take it on trust")


def test_the_original_body_is_kept_visible(composer):
    """Point, never prune: a removal a reader cannot inspect is not reviewable."""
    assert hasattr(composer, "_retired_update_coherence_budgets_from_experiments")
    assert hasattr(composer, "calibrate_coherence_thresholds"), (
        "the calibrator's arithmetic stays inspectable and testable")


def test_the_pruning_is_off_by_default_in_the_runner(runner):
    cls = next(o for o in (getattr(runner, n) for n in dir(runner))
               if dataclasses.is_dataclass(o)
               and any(f.name == "composer_coherence_pruning"
                       for f in dataclasses.fields(o)))
    d = {f.name: f.default for f in dataclasses.fields(cls)}
    assert d["composer_coherence_pruning"] is False, (
        "the ceiling is retired, so the pruning it drives must not default on")


def test_the_prune_inversion_proof_is_still_committed():
    """The whole retirement rests on this. If it goes, re-open the decision."""
    proof = REPO / "bench" / "tests" / "test_falsifier_C0001_prune_inversion_2026-09-10.py"
    assert proof.is_file(), (
        "the z3 proof that pruning cannot improve density is the evidence the "
        "additive standard requires for this removal. Without it the retirement "
        "is a judgement, not a measurement, and must be re-argued.")
    text = proof.read_text(encoding="utf-8")
    assert "z3" in text.lower(), "the proof must still be a solver result"


def test_the_pruning_still_runs_when_explicitly_asked(composer):
    """ANTI-VACUITY, and it matters here. Retiring the ceiling must not delete
    the behaviour its own falsifier needs to demonstrate the inversion. The
    C0001 proof calls `compose(..., coherence_pruning=True)`, so that path has
    to keep working or the evidence for the retirement stops being reproducible.
    """
    assert composer._prune_for_coherence is not None
    packets, pruned = composer._prune_for_coherence([], {}, 0.015)
    assert packets == [] and pruned == [], (
        "with no packets there is nothing to prune and nothing to report")
