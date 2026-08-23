import collections
import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "discrimination_control_archive",
    REPO / "scripts/discrimination_control_archive.py",
)
archive = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(archive)


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

    assert summary["n"] == 97
    assert summary["counts"] == EXPECTED_CAUSE_COUNTS
    assert len(summary["classifications"]) == 97
    assert {r["cause"] for r in summary["classifications"]} == set(
        EXPECTED_CAUSE_COUNTS
    )
    assert collections.Counter(r["route_a"] for r in summary["classifications"]) == {
        "NO_APPLICABLE_FIX": 67,
        "INDETERMINATE_ERROR": 30,
    }
    assert not [
        r
        for r in summary["classifications"]
        if not r["run"] or not r["cid"] or not r["target"] or not r["detail"]
    ]


def test_classifier_keeps_the_two_measured_unscored_populations_separate():
    counts = archive.classify_route_a_failures()["counts"]

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
