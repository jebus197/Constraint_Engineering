#!/usr/bin/env python3
"""A classification of his prose that misfires may not publish a split.

THE DEFECT THIS GUARDS, AND IT IS 2 DEFECTS. First, the morning report of
2026-10-30 told the founder that 30 panel-labelled tickets split 19
unconditional, 6 conditional and 5 not-requests, and that 11 trace to a task
entry of which 10 are closed. No script in the tree computes any of those, so
10 figures reached him as prose about evidence, and were re-quoted twice the
same morning. Second, the producer written to give them a producer DISAGREED
with the report (21, 7, 2) and then disagreed with a hand reading on 2 of the 2
cases checked -- so neither split is quotable.

BOTH MISFIRES ARE SCOPE ERRORS, which is why widening the patterns is not the
fix and why this file pins the WITHHOLDING rather than a corrected number:

  * `fd6bd113d263`: the imperative pattern matched the word "verdict" inside
    *"I can't offer a verdict"*. A match inside a negation is the shape that
    made a reader match NOT FALSIFIED as FALSIFIED and cost a convergence.
  * `5b46f40b7ddb`: "Fix as necessary" gated the FIX, while the panel
    discussion in the next sentence is unconditional.

WHAT IS STILL SOUND AND IS PINNED HERE: the request count, that 0 of them carry
a task reference (so tracing needs the founder-responses reader rather than a
search), and that a date comparison is reported as a date comparison.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PROD = REPO / "scripts" / "what_do_the_panel_requests_actually_ask_2026-10-30.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("panelreq", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["panelreq"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def rep(mod):
    return mod.report()


class TestWhatIsSound:

    def test_the_request_count_is_reported(self, rep):
        assert rep["requests"] > 0

    def test_none_of_them_carries_a_task_reference(self, rep):
        """The reason tracing to an entry is NOT done by this script."""
        assert rep["task_ref_present"] == 0, (
            f"{rep['task_ref_present']} ticket(s) now carry a task_ref, so "
            f"tracing is newly possible and this producer should be extended "
            f"rather than left saying it cannot")

    def test_rounds_are_counted_and_the_claim_is_a_date_claim(self, rep):
        assert rep["rounds_mirrored"] > 0
        assert rep["min_rounds_after"] is not None


class TestTheSplitIsWithheldWhileTheRuleMisfires:

    def test_the_control_is_checked_at_all(self, rep):
        assert rep["hand_read_checked"] >= 2

    def test_the_split_is_not_published(self, rep):
        assert rep["split_publishable"] is False, (
            "the split is being published again. It may only be published when "
            "the rule agrees with every hand-read case, and the 2 recorded "
            "disagreements are SCOPE errors that pattern-widening does not fix")

    def test_no_share_is_emitted_while_it_is_withheld(self, rep):
        assert "unconditional_share" not in rep, (
            "a proportion with an interval was emitted for a split the producer "
            "itself refuses to publish, which is the flattering-measure shape")

    def test_the_disagreements_are_named_not_counted(self, rep):
        ds = rep["hand_read_disagreements"]
        assert ds, "no disagreement recorded, so the control cannot be biting"
        for d in ds:
            assert d["tid"] and d["rule_says"] and d["read_as"]
            assert d["rule_says"] != d["read_as"]


class TestTheRuleReallyDoesMisfire:
    """EXECUTED, so the recorded reason is not just a comment."""

    def test_the_imperative_pattern_matches_inside_a_negation(self, mod):
        assert mod.IMPERATIVE.search("I can't offer a verdict."), (
            "the pattern no longer matches a negated 'verdict'. If that was "
            "fixed deliberately, update HAND_READ and this test together")
        verdict, _ = mod.classify("Since your conflation is clearly nonsensical, "
                                  "I can't offer a verdict.")
        assert verdict == "UNCONDITIONAL", (
            f"classify now returns {verdict!r} for a refusal to give a verdict; "
            f"if that is a real repair, the recorded disagreement should go")

    def test_a_condition_on_one_clause_captures_the_next(self, mod):
        verdict, _ = mod.classify(
            "Verdict: Fix as necessary. Discuss your fix with Fable and CC2 in "
            "panel review, and ask them to confirm.")
        assert verdict == "CONDITIONAL", (
            f"classify now returns {verdict!r}; the recorded scope error may be "
            f"repaired, in which case HAND_READ and this test change together")

    def test_the_control_is_load_bearing(self, mod):
        """Emptying HAND_READ must make the split publishable again.

        Without this the withholding could be unconditional, and a test that
        cannot distinguish 'the control fired' from 'it always withholds' proves
        nothing about the control.
        """
        saved = dict(mod.HAND_READ)
        try:
            mod.HAND_READ.clear()
            r = mod.report()
            assert r["split_publishable"] is True
            assert "unconditional_share" in r
        finally:
            mod.HAND_READ.clear()
            mod.HAND_READ.update(saved)
        assert mod.report()["split_publishable"] is False


def test_help_costs_nothing(mod):
    with pytest.raises(SystemExit) as e:
        mod.main(["--help"])
    assert e.value.code == 0
