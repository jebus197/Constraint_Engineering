"""A seat's sandbox copy of a report must not be counted as an archive record.

WHY THIS EXISTS. On 2026-09-30, committing the falsifier-root-cause panel round
put that round's sandbox harvest on disk. `sk_threshold_shadow`'s on-disk gate
count jumped 5086 -> 5972 while the git-tracked count held at 4499, and
`test_stated_gate_count_matches_measurement_2026-09-07` went red. Nothing had
been archived. The +886 was 136 harvest JSONs that are byte-identical (sha256) to
files already tracked at their canonical paths: the same gate results counted
once as archive and again once per dispatched seat, 14.8359% inflation.

The failing guard's own instructions pointed the wrong way -- "IF THIS TEST FAILS
BECAUSE THE ARCHIVE GREW, THE TEST IS RIGHT AND THE PROSE IS STALE. Restate the
claim with the new count AND recompute its interval." Correct in general, wrong
here: the archive had not grown, and obeying it would have published 5972 with a
freshly-computed interval around a number that was one seventh duplicate.

WHAT THIS FILE CHECKS, BY EXECUTION. `execute-do-not-grep`: a test that asserts
on the source text of the exclusion would assert only that the exclusion
describes itself. So each case below BUILDS a small archive on disk, one canonical
report plus N harvest copies of it, CALLS `route_1_structured`, and compares its
answer against the count that is arithmetically forced. The scale factor is the
point: with S seats the inflated answer is (1 + S) times the true one, so the
test fails loudly rather than by one.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from measure_sk_threshold_gate_fire_rate import (  # noqa: E402
    HARVEST_DIRS, route_1_structured,
)

#: 3 gate records in one report: 2 admitted, 1 rejected at the threshold.
REPORT = {"rounds": [{"fixes": [
    {"sk_result": {"passes_threshold": True, "sk": 0.91, "s_star": 0.5}},
    {"sk_result": {"passes_threshold": True, "sk": 0.77, "s_star": 0.5}},
    {"sk_result": {"passes_threshold": False, "sk": 0.12, "s_star": 0.5}},
]}]}
RECORDS_PER_REPORT = 3


def _build(logs: pathlib.Path, harvest_dir: str, seats: int) -> pathlib.Path:
    """One canonical report, then `seats` sandbox copies of the whole subtree."""
    run = logs / "run_20260930T000000Z"
    run.mkdir(parents=True)
    canonical = run / "run_report.json"
    canonical.write_text(json.dumps(REPORT), encoding="utf-8")
    for i in range(seats):
        dest = logs / "panel_round_2026-09-30" / harvest_dir / f"seat{i}" / "attempt-1" / "files"
        (dest / "bench" / "logs").mkdir(parents=True)
        shutil.copytree(run, dest / "bench" / "logs" / run.name)
    return canonical


@pytest.mark.parametrize("harvest_dir", HARVEST_DIRS)
@pytest.mark.parametrize("seats", [1, 2, 5])
def test_harvest_copies_are_not_counted(tmp_path, harvest_dir, seats):
    logs = tmp_path / "logs"
    logs.mkdir()
    _build(logs, harvest_dir, seats)

    got = route_1_structured(logs)
    assert got["total"] == RECORDS_PER_REPORT, (
        f"{seats} sandbox copies under {harvest_dir}/ inflated the archive from "
        f"{RECORDS_PER_REPORT} to {got['total']} records. A copy of a report made "
        f"for a seat is not a new archive record; with S seats the count scales "
        f"as (1 + S) x truth, so every published rate over this corpus would be "
        f"wrong by however many seats were dispatched."
    )
    assert got["harvest_copies_skipped"] == seats, (
        f"expected {seats} harvest JSON skipped, got "
        f"{got['harvest_copies_skipped']} -- the exclusion counted itself wrong, "
        f"so the figure it reports cannot be audited"
    )


@pytest.mark.parametrize("harvest_dir", HARVEST_DIRS)
def test_the_old_behaviour_is_still_reachable_and_still_inflates(tmp_path, harvest_dir):
    """The escape hatch must genuinely differ, or it is decoration.

    A flag that returns the same answer either way would let the exclusion be
    silently removed with every test still green -- the shape this project keeps
    finding in additions nothing reaches.
    """
    logs = tmp_path / "logs"
    logs.mkdir()
    _build(logs, harvest_dir, seats=4)

    excluded = route_1_structured(logs)["total"]
    included = route_1_structured(logs, include_harvest_copies=True)["total"]
    assert excluded == RECORDS_PER_REPORT
    assert included == RECORDS_PER_REPORT * 5, (
        f"4 seats plus the canonical report is 5 copies of {RECORDS_PER_REPORT} "
        f"records, so the unfiltered route must return {RECORDS_PER_REPORT * 5}; "
        f"it returned {included}"
    )
    assert included > excluded


def test_a_canonical_report_whose_path_merely_mentions_a_seat_is_still_counted(tmp_path):
    """The exclusion must key on the harvest DIRECTORY, not on a name anywhere.

    A run legitimately named after a seat, or a directory containing the word
    used elsewhere, must not be silently dropped from the archive -- that would
    be a removal, measured by nothing, of real evidence.
    """
    logs = tmp_path / "logs"
    run = logs / "confer_sandbox_harvesting_notes_20260930T000000Z"
    run.mkdir(parents=True)
    (run / "run_report.json").write_text(json.dumps(REPORT), encoding="utf-8")
    got = route_1_structured(logs)
    assert got["total"] == RECORDS_PER_REPORT, (
        "a directory whose name merely resembles a harvest path was excluded; "
        f"expected {RECORDS_PER_REPORT} records, got {got['total']}"
    )
    assert got["harvest_copies_skipped"] == 0


def test_the_real_archive_still_exercises_the_exclusion():
    """Executed against the actual corpus, not a fixture.

    DELIBERATELY PINS NO ABSOLUTE COUNT. The figures the correction turned on --
    5086 on disk, 4499 tracked -- are owned by ONE guard,
    `test_stated_gate_count_matches_measurement_2026-09-07`, which compares them
    against `sk_threshold_shadow`'s prose. Restating them here would create a
    second site to go stale, and a stale restated count is the single most
    repeated defect in this project's record: 8 recurrences, every one caught by
    the commit gate rather than by reading. So this test checks only what cannot
    go stale -- that the live corpus still CONTAINS harvest copies, and that the
    exclusion still changes the answer over it.

    If this skips, the harvest has been cleared and the fixture cases above are
    the only remaining coverage. That is a real loss of coverage, not a pass, so
    it says so.
    """
    logs = REPO / "bench" / "logs"
    if not logs.is_dir():
        pytest.skip("archive not present")
    excluded = route_1_structured(logs)
    included = route_1_structured(logs, include_harvest_copies=True)
    if excluded["harvest_copies_skipped"] == 0:
        pytest.skip("no harvest copies on disk, so the live corpus cannot "
                    "exercise the exclusion; the fixture cases above still do")
    assert included["total"] > excluded["total"], (
        f"{excluded['harvest_copies_skipped']} harvest JSON files are present on "
        f"disk, yet including them changes the count by "
        f"{included['total'] - excluded['total']}. Either the exclusion has "
        f"stopped taking effect, or those copies carry no gate records -- check "
        f"which before trusting any rate measured over this corpus."
    )
