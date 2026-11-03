"""A decision put to him must admit a ruling of his already on record.

HIS CHALLENGE, 2026-11-03: whether the decisions put to him were all new issues
he had never ruled on before. The detector that exists for that question,
`scripts/which_open_entries_already_have_his_ruling_2026-10-30.py`, answered 0 of
12 -- and it was looking in the wrong place. It reads COMMIT MESSAGES only, while
the surface that records a verdict beside a decision is the report's own detail
file, whose `ruled` and `his_words` fields hold 10 entries.

THE ANSWER, ONCE THE RIGHT SURFACE IS READ: 0 of 10 hide it. Every entry
carrying a ruling of his acknowledges it in the text he reads, 4 of them inside
their own decision section and the rest elsewhere in the report -- C0001 under
outstanding work, in the words "YOU RULED THIS ON 2026-11-01; the work is
outstanding".

AND THE FIRST VERSION OF THE FIX WAS WRONG, WHICH IS WHY THIS GUARD EXISTS. It
inferred "presented as a decision" from the PRESENCE of an `options` field and
checked for acknowledgement in `title` and `what` only. That reported 6 of 10
unacknowledged, and all 6 were FALSE POSITIVES: C0001 carries options yet is not
rendered as a numbered decision, and its acknowledgement is fuller than the
fields the predicate read. A proxy for what a generator renders is not what it
renders. The detector now RUNS the generator and reads its output.

THE LOAD-BEARING TESTS ARE THE PLANTED ONES. The live answer is 0, and a
detector that reports 0 because it is blind is indistinguishable from one that
reports 0 because nothing is wrong -- so an unacknowledged section is planted
here and must be flagged.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PROD = (REPO / "scripts"
        / "which_open_entries_already_have_his_ruling_2026-10-30.py")


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("_ruling_guard", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_ruling_guard"] = m
    spec.loader.exec_module(m)
    return m


ACKNOWLEDGED = """\
### 3. B99 — something that needs him
**What it is.** You ruled on 1 November that the thing should be done.
**Your options.**
"""

UNACKNOWLEDGED = """\
### 3. B99 — something that needs him
**What it is.** The thing has never been settled and a choice is required.
**Your options.**
"""


class TestThePlantedCases:
    def test_an_unacknowledged_decision_is_flagged(self, mod):
        """THE ANTI-VACUITY CASE. Without this, a live 0 proves nothing."""
        assert mod._presented_idents(UNACKNOWLEDGED) == {"B99"}
        assert mod._acknowledged_in_report("B99", UNACKNOWLEDGED) is False, (
            "a section that never admits his ruling must be flagged")

    def test_an_acknowledged_decision_is_not_flagged(self, mod):
        assert mod._acknowledged_in_report("B99", ACKNOWLEDGED) is True

    @pytest.mark.parametrize("phrase", [
        "You ruled on 1 November",
        "you already ruled this",
        "That ruling stands and is not reopened",
        "Permission is granted",
        "I accept your recommendation",
        "you have settled its shape",
        "YOU RULED THIS ON 2026-11-01; the work is outstanding",
    ])
    def test_every_acknowledgement_form_in_live_use_is_recognised(self, mod, phrase):
        """Each of these is a form the live report actually uses. A predicate
        that missed one would accuse a compliant entry, which is how the first
        version produced 6 false positives."""
        assert mod._acknowledged_in_report(
            "B99", f"### 3. B99 - x\n{phrase}\n") is True, (
            f"the live acknowledgement form {phrase!r} is not recognised")

    def test_acknowledgement_outside_the_decisions_list_still_counts(self, mod):
        """C0001's case: not a numbered decision, acknowledged elsewhere."""
        report = ("### 1. B98 - other\n**What it is.** x\n\n"
                  "- **C0001** - **YOU RULED THIS ON 2026-11-01; outstanding**\n")
        assert mod._presented_idents(report) == {"B98"}
        assert mod._acknowledged_in_report("C0001", report) is True

    def test_a_presented_heading_is_read_from_the_numbering(self, mod):
        report = "### 1. B21 - a\n### 2. B71 - b\n### 10. B96 - c\n"
        assert mod._presented_idents(report) == {"B21", "B71", "B96"}


class TestTheLiveState:
    def test_no_entry_hides_a_ruling_of_his(self, mod):
        det = mod.detail_rulings()
        if not det:
            pytest.skip("the detail file is not readable here")
        assert len(det) >= 5, (
            f"only {len(det)} entries carry a ruling of his, so the assertion "
            f"below would be close to vacuous")
        bad = sorted(i for i, v in det.items() if not v["acknowledged"])
        assert not bad, (
            "these entries record a ruling of his and the text he reads does "
            f"not say so, which costs him the decision twice: {bad}")

    def test_the_two_channels_are_reported_apart(self, mod):
        a = mod.analyse()
        for key in ("suspects", "unacknowledged", "n_with_his_words"):
            assert key in a, f"{key} is not reported"
        assert a["suspects"] is not a["unacknowledged"], (
            "the commit channel and the detail channel must stay distinct; a "
            "single opaque count would hide which surface was blind")
