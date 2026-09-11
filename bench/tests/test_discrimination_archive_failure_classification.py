"""The archived Route-A failures, classified by cause.

CLONE-AWARE SINCE 2026-09-11, and the reason is measured. The fine-grained
causes below need every stored version of each target, and `_versions()` fetches
them with `git log --all` -- whose own docstring says the flag is load-bearing
because "the milestone merge squashed 107 commits that only exist on
`exp39-experimental`". That branch is LOCAL and was never pushed, so no clone
carries it. Measured in a fresh clone at 287c4ff:

    here      proposed_fix_makes_target_syntax_error            13
              patched_target_compiles_but_falsifier_errors      17
    a clone   errored_route_had_no_effective_patch              30

The 2 causes collapse into 1 because the baseline text is not there to patch.
`scripts/fresh_clone_census_2026-09-10.py` already records that branch as a
clone-only cause for `test_branch_supplies_versions_2026-09-10.py`; this file
was simply never told.

WHAT IS ASSERTED EVERYWHERE, because it does not depend on the branch: the
population size, the 67/30 split between the 2 unscored routes, and that every
classification is fully attributed. Only the breakdown of the 30 is conditional,
and when it is skipped the reason is named rather than the file going quiet.
"""
import collections
import importlib.util
import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "discrimination_control_archive",
    REPO / "scripts/discrimination_control_archive.py",
)
archive = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(archive)


#: The branch whose history supplies the stored target versions. LOCAL, never
#: pushed, so absent from every clone.
BRANCH = "exp39-experimental"


def _has_branch() -> bool:
    return subprocess.run(["git", "rev-parse", "--verify", BRANCH], cwd=REPO,
                          capture_output=True, text=True).returncode == 0


#: Causes that need the stored history to distinguish.
NEEDS_HISTORY = ("proposed_fix_makes_target_syntax_error",
                 "patched_target_compiles_but_falsifier_errors_after_fix")

EXPECTED_CAUSE_COUNTS = {
    "no_proposed_fix_recorded": 54,
    "malformed_patch_no_parseable_search_replace_block": 3,
    "search_block_matches_no_stored_target_version": 9,
    "search_block_matches_stored_version_but_not_firing_baseline": 1,
    "proposed_fix_makes_target_syntax_error": 13,
    "patched_target_compiles_but_falsifier_errors_after_fix": 17,
}


def test_archive_route_a_failures_are_classified_by_stable_cause():
    summary = archive.classify_route_a_failures()

    # THESE HOLD IN EVERY CHECKOUT. They are asserted before the conditional
    # block so a clone still checks the population rather than skipping the file.
    assert summary["n"] == 97
    assert len(summary["classifications"]) == 97
    assert collections.Counter(r["route_a"] for r in summary["classifications"]) == {
        "NO_APPLICABLE_FIX": 67,
        "INDETERMINATE_ERROR": 30,
    }

    if not _has_branch():
        counts = summary["counts"]
        # The coarse form must still add up, or the skip would hide a real
        # regression rather than a missing branch.
        assert counts.get("errored_route_had_no_effective_patch") == sum(
            EXPECTED_CAUSE_COUNTS[c] for c in NEEDS_HISTORY), counts
        for cause in EXPECTED_CAUSE_COUNTS:
            if cause not in NEEDS_HISTORY:
                assert counts[cause] == EXPECTED_CAUSE_COUNTS[cause], cause
        pytest.skip(
            f"no {BRANCH} in this checkout, so the stored target versions that "
            f"separate {NEEDS_HISTORY[0]} from {NEEDS_HISTORY[1]} are absent "
            f"and both collapse into errored_route_had_no_effective_patch. The "
            f"coarse form was checked above.")

    assert summary["counts"] == EXPECTED_CAUSE_COUNTS
    assert {r["cause"] for r in summary["classifications"]} == set(
        EXPECTED_CAUSE_COUNTS
    )
    assert not [
        r
        for r in summary["classifications"]
        if not r["run"] or not r["cid"] or not r["target"] or not r["detail"]
    ]


def test_classifier_keeps_the_two_measured_unscored_populations_separate():
    counts = archive.classify_route_a_failures()["counts"]

    if not _has_branch():
        pytest.skip(
            f"no {BRANCH} in this checkout; the 2 history-dependent causes "
            f"collapse, and the 67/30 split they sum to is asserted in "
            f"test_archive_route_a_failures_are_classified_by_stable_cause, "
            f"which does not skip.")

    no_applicable = (
        counts["no_proposed_fix_recorded"]
        + counts["malformed_patch_no_parseable_search_replace_block"]
        + counts["search_block_matches_no_stored_target_version"]
        + counts["search_block_matches_stored_version_but_not_firing_baseline"]
    )
    errored = (
        counts["proposed_fix_makes_target_syntax_error"]
        + counts["patched_target_compiles_but_falsifier_errors_after_fix"]
    )

    assert no_applicable == 67
    assert errored == 30
    assert counts["search_block_matches_no_stored_target_version"] == 9
