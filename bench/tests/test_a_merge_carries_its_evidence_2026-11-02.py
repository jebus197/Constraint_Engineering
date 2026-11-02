#!/usr/bin/env python3
"""A MERGED finding must carry the evidence its own status declares it requires.

RUNWAY ITEM 1.6, from `experimental_notes/Runway_Status_And_Is_It_Safe_To_Merge_2026-10-16.md`:
*"Item 1.6 is the merged-finding semantics, which either folds or stops claiming
to."*

THE SEMANTICS STOPPED CLAIMING ON 2026-10-24. The status table at
`bench/reference_runner_v3.py` records that DUPLICATE had been folded into
MERGED, *"so MERGED silently became the harness's word for a duplicate as well as
for its own case"*, and narrows it to the founder's condition (a) alone: 2
findings are 1 defect, with the repairs possibly differing, and where they differ
the loser is DEPRECATED rather than merged away. Its `evidence_required` now
reads: an `adjudicate_by_repair` verdict SAME IN BOTH DIRECTIONS.

★ AND NOTHING CHECKED THAT. Measured 2026-11-02: of 296 archived MERGED entries,
0 carry that evidence -- every one holds only a `merged_into` pointer. The DATE
SPLIT is what makes this mild rather than severe, and the 2 readings are
different claims: 210 of the 296 come from runs PREDATING the correction
(0.709459, Wilson 95% [0.655317, 0.758235]), 0 come from runs on or after it, and
86 sit in runs whose directory name carries no parseable stamp and are left
UNCLASSIFIED rather than counted on the flattering side. So the requirement is
UNEXERCISED, not unenforced.

★ WHICH IS EXACTLY WHY THIS FILE EXISTS RATHER THAN A NOTE SAYING SO.
`feedback_a_regression_guard_must_not_need_a_live_defect_2026-10-31` records 0 of
625 guards blocking because each waited on a real failure to assert against. A
trigger written in prose -- "the first run that produces a MERGED entry tests
it" -- is an unwired addition, which `additive-standard` refuses. So the rule is
enforced in 2 ways here:

  * DATE-GATED over the live archive, which passes today on 0 entries and fires
    the moment a run on or after the cut produces a merge carrying only a
    pointer. That half is currently VACUOUS and says so.
  * CONSTRUCTED, so the predicate is exercised now rather than when it matters.
    Without this the file would be indistinguishable from one that checks
    nothing, which is the 25-of-25 and 35-of-37 shape met repeatedly today.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

LOGS = REPO / "bench" / "logs"
#: The date the status narrowed its meaning and declared its evidence.
CUT = "20261024"
#: Any field that could carry a both-directions adjudication verdict.
EVIDENCE_FIELDS = ("adjudicate_by_repair", "merge_adjudication",
                   "merge_evidence", "both_directions", "merge_verdict")


def _merged_rows():
    """(run name, run stamp or None, entry) for every archived MERGED entry."""
    out = []
    for f in sorted(LOGS.glob("*/runner_state.json")):
        m = re.search(r"(20\d{6})T\d{6}Z", f.parent.name)
        stamp = m.group(1) if m else None
        try:
            j = json.loads(f.read_text(errors="ignore"))
        except Exception:                                    # noqa: BLE001
            continue
        e = (j.get("registry") or {}).get("entries") or {}
        e = list(e.values()) if isinstance(e, dict) else list(e)
        for x in e:
            if str(x.get("status", "")).upper() == "MERGED":
                out.append((f.parent.name, stamp, x))
    return out


def has_evidence(entry: dict) -> bool:
    """Does this entry carry a both-directions adjudication verdict?

    A `merged_into` pointer is NOT that evidence: it records the DESTINATION of
    the merge, not that a counterfactual repair found the 2 findings to be 1
    defect in both directions. Treating the pointer as evidence is precisely
    the conflation the 2026-10-24 correction removed.
    """
    for k, v in entry.items():
        if any(t in k.lower() for t in EVIDENCE_FIELDS) and v:
            return True
    return False


# ---- the declaration itself, so the rule cannot be quietly dropped --------
def test_the_status_still_declares_the_evidence_it_requires():
    src = (REPO / "bench" / "reference_runner_v3.py").read_text()
    assert "adjudicate_by_repair verdict SAME in BOTH" in src, (
        "MERGED no longer declares a both-directions evidence requirement. If "
        "that is intended, this guard must be re-derived rather than left "
        "asserting a rule the product has dropped.")
    assert "NOT a duplicate" in src, (
        "MERGED no longer says it is not a duplicate claim; the 2026-10-24 "
        "correction has been lost")


# ---- the CONSTRUCTED half, which is what makes this non-vacuous ----------
def test_a_pointer_alone_is_NOT_evidence():
    assert not has_evidence({"merged_into": "C0011"}), (
        "a merged_into pointer was accepted as evidence; it names the "
        "destination of a merge, not a both-directions adjudication")


def test_a_both_directions_verdict_IS_evidence():
    assert has_evidence({"merged_into": "C0011",
                         "adjudicate_by_repair": "SAME both ways"})
    assert has_evidence({"merge_verdict": {"a_to_b": "SAME", "b_to_a": "SAME"}})


def test_an_empty_evidence_field_does_not_count():
    """A present-but-empty field is the shape that makes a check look satisfied."""
    for empty in ("", None, {}, [], 0, False):
        assert not has_evidence({"adjudicate_by_repair": empty}), (
            f"an empty evidence field ({empty!r}) was accepted")


# ---- the DATE-GATED half over the live archive ---------------------------
def test_no_post_correction_merge_lacks_its_evidence():
    """THE TRIGGER. Passes on 0 entries today and says so.

    Runs with no parseable stamp are EXCLUDED rather than assumed old: 86 of
    the 296 are in that state, and counting them as pre-correction would be
    assuming the answer this test exists to find.
    """
    rows = _merged_rows()
    assert rows, "no MERGED entry anywhere; this test has nothing to range over"
    post = [(r, s, e) for r, s, e in rows if s and s >= CUT]
    offenders = [(r, e.get("canonical_id")) for r, s, e in post
                 if not has_evidence(e)]
    assert not offenders, (
        f"{len(offenders)} MERGED entr(ies) from runs on or after {CUT} carry no "
        f"both-directions evidence, so the status claims a requirement the "
        f"harness does not enforce: {offenders[:5]}")
    if not post:
        pytest.skip(
            f"VACUOUS TODAY, DELIBERATELY RECORDED: 0 of {len(rows)} archived "
            f"MERGED entries come from a run on or after {CUT}, so the "
            f"requirement is UNEXERCISED rather than unenforced. This fires on "
            f"the first run that produces a merge.")


def test_the_pre_correction_population_is_measured_and_not_hidden():
    """The 210 that predate the rule are a fact worth keeping visible.

    If this count ever falls to 0 the archive has been rewritten, and if the
    unstamped count falls the directory naming has changed -- either is worth
    knowing before a figure quoted from it is trusted.
    """
    rows = _merged_rows()
    pre = sum(1 for _r, s, _e in rows if s and s < CUT)
    unstamped = sum(1 for _r, s, _e in rows if not s)
    assert pre + unstamped <= len(rows)
    assert pre > 0, (
        "no MERGED entry predates the correction, which contradicts the "
        "measurement of 210 recorded in the runway; re-derive before citing it")
    assert unstamped > 0, (
        "no unstamped run remains, so the 86 unclassified entries recorded in "
        "the runway are stale and that figure must be re-derived")
