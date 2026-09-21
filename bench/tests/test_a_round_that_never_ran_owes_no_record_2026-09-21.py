"""A brief is not a round. Executed against real directories, not grepped.

THE CIRCULARITY. `holds_review_output` is true for a BRIEF ALONE, and the
Section-P full-record guard used it to decide which rounds owe a FULL RECORD
note. So a round whose dispatch failed -- brief written, 0 seat replies -- was
required to publish a full, unfiltered record of replies that do not exist.
That demand cannot be met. The only ways to make it green are to delete the
brief or to fake the record, and both destroy evidence, which is the opposite of
what the directive asks for.

IT WAS NOT HYPOTHETICAL. Rounds 1 to 3 of the 2026-09-20 maths review each lost
seats to defects in the dispatch machinery -- the paid seats had no tool that
could read a file, an empty-content retry existed in the wrong tool loop, and a
forced-synthesis call carried a temperature one endpoint refuses. A total
dispatch failure was 1 defect away from happening.

MEASURED 2026-09-21. 2 directories in the archive hold a brief and 0 replies:
`panel_todays_fixes_20260906T175435Z` live, and
`maths_panel_2026-09-20_revised_model` in the tracked mirror. The second
POSTDATES the 2026-09-09 ruling and escaped the guard only because the guard
walks the live directory and that copy lives in the mirror. The defect was
latent by the luck of where a file sat, not by design.

AND THE SAME CONFLATION WAS MIS-LABELLING A FIGURE REPORTED TO THE FOUNDER.
`scripts/panel_condition_compliance_2026-09-10.py` printed "panel rounds with at
least 1 seat reply: 89" from the inclusive set, when 87 hold a reply. The label
stated the correct proposition and the set was the wrong one.

THE MIRROR IS DELIBERATELY NOT NARROWED. Preserving a brief whose dispatch
failed is right -- it is evidence of what was asked. Narrowing
`holds_review_output` would have fixed the guard by REMOVING that preservation,
which is a removal made to repair an addition's misuse. 2 questions, 2
predicates, and the test below holds both halves.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
LOGS = REPO / "bench" / "logs"


def _mod(rel: str):
    spec = importlib.util.spec_from_file_location("m_" + Path(rel).stem, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def mirror():
    return _mod("scripts/mirror_panel_records_2026-09-11.py")


@pytest.fixture
def brief_only_round(tmp_path):
    d = tmp_path / "panel_never_dispatched_20260921T000000Z"
    d.mkdir()
    (d / "BRIEF.md").write_text("# a brief whose dispatch failed\n", encoding="utf-8")
    return d


@pytest.fixture
def dispatched_round(tmp_path):
    d = tmp_path / "panel_really_ran_20260921T000000Z"
    d.mkdir()
    (d / "BRIEF.md").write_text("# a brief\n", encoding="utf-8")
    (d / "cc2.json").write_text(json.dumps({"ok": True, "response": "x"}), encoding="utf-8")
    return d


def test_a_brief_alone_is_preserved_but_is_not_a_dispatched_round(mirror, brief_only_round):
    assert mirror.holds_review_output(brief_only_round) is True, (
        "a brief must still be preserved by the mirror -- narrowing this would "
        "be a removal made to repair an addition's misuse"
    )
    assert mirror.was_dispatched(brief_only_round) is False


def test_a_round_with_a_seat_reply_is_dispatched(mirror, dispatched_round):
    assert mirror.holds_review_output(dispatched_round) is True
    assert mirror.was_dispatched(dispatched_round) is True


def test_the_two_predicates_are_not_the_same_question_on_the_real_archive(mirror):
    """If these ever agree everywhere, 1 of them is redundant -- say so loudly."""
    rs = mirror.archive_rounds()
    dispatched = [d for d in rs if mirror.was_dispatched(d)]
    brief_only = [d for d in rs if not mirror.was_dispatched(d)]
    assert len(rs) >= 80, f"archive unexpectedly small: {len(rs)}"
    assert brief_only, (
        "no brief-only round found in the archive; if this is genuinely true "
        "now, the guard below is untestable against real data and this test "
        "should be re-scoped rather than deleted"
    )
    assert len(dispatched) + len(brief_only) == len(rs)


def test_the_full_record_guard_does_not_demand_a_record_of_a_round_that_never_ran():
    """THE CIRCULARITY ITSELF, driven against the real guard. RED at the parent.

    A post-ruling directory holding a brief and 0 replies is created under
    `bench/logs`, the guard's own round selector is called, and the directory
    must NOT appear. Against the parent it appears, and the round is then asked
    for a full record of nothing.
    """
    guard = _mod("bench/tests/test_panel_rounds_have_a_full_record_2026-09-11.py")
    probe = LOGS / "panel_circularity_probe_20260921T235959Z"
    probe.mkdir(parents=True, exist_ok=False)
    try:
        (probe / "BRIEF.md").write_text("# never dispatched\n", encoding="utf-8")
        names = guard._post_ruling_rounds()
        assert probe.name not in names, (
            "a round with a brief and 0 seat replies was counted as a post-ruling "
            "round, so it owes a FULL RECORD of replies that do not exist"
        )
        # and the control: add one reply and it must be counted
        (probe / "cc2.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
        assert probe.name in guard._post_ruling_rounds(), (
            "the fix went too far: a round that DID run is no longer counted"
        )
    finally:
        for f in probe.iterdir():
            f.unlink()
        probe.rmdir()
    assert not probe.exists()


def test_the_compliance_figure_satisfies_the_label_it_is_printed_under(mirror):
    """"panel rounds with at least 1 seat reply" must count rounds with a reply.

    Executed against the compliance script's own population rather than against
    its printed text, so a change to either side fails here.
    """
    comp = _mod("scripts/panel_condition_compliance_2026-09-10.py")
    rs = comp.rounds()
    labelled = [d for d in rs if comp._mirror_module().was_dispatched(d)]
    independently = [d for d in rs
                     if any((d / n).is_file() for n in mirror.SEAT_FILES)]
    assert labelled == independently
    assert len(labelled) < len(rs), (
        "the corrected count equals the inclusive one, so this test would pass "
        "even with the defect present"
    )
