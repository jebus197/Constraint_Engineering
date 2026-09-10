"""Task R5a: the materiality population 11 / 6 / 2 does not reproduce.

EXECUTED, NOT GREPPED. Every assertion here CALLS the measuring script and reads
its return values. A test that asserted on the script's source text would only
show the script describes itself consistently, which is the defect
`execute-do-not-grep` exists to stop.

THE POSITIVE CONTROL IS THE LOAD-BEARING TEST. A search that reports "nothing
reproduces this" is worthless if it could never report anything else. So one test
feeds the search a triple that IS a single measure -- the archives' own
`escalated` counts -- and requires it to find that measure. Without that, the null
result is unfalsifiable.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "materiality_population_2026-09-10.py"


@pytest.fixture(scope="module")
def mp():
    spec = importlib.util.spec_from_file_location("materiality_population", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def per_exp(mp):
    out = {}
    for exp in mp.CLAIMED:
        _, state = mp.load(exp)
        assert state is not None, f"exp{exp} has no archive to measure"
        out[exp] = mp.candidates(state)
    return out


class TestTheSearchCanActuallyFindThings:
    """Without these, a null result is not evidence."""

    def test_a_triple_that_IS_one_measure_is_found(self, mp, per_exp):
        """POSITIVE CONTROL. The `escalated` counts are 0, 1 and 6.

        Fed as the claim, the search must name `escalated == true`. If it cannot
        find a match that exists, its failure to find the real claim says
        nothing at all.
        """
        # `.get(..., 0)`: a field that is never true has no key at all, and an
        # absent count IS zero. Indexing it directly raised KeyError and would
        # have hidden the control behind an error rather than a verdict.
        truth = {e: per_exp[e].get("escalated == true", 0) for e in per_exp}
        hits = [set(k for k, v in per_exp[e].items() if v == truth[e])
                | ({"escalated == true"} if truth[e] == 0 else set())
                for e in per_exp]
        common = set.intersection(*hits)
        assert "escalated == true" in common, (
            "the search cannot find a definition that demonstrably reproduces a "
            "triple, so its null result on the real claim proves nothing")

    def test_the_search_space_is_large_enough_to_be_a_search(self, per_exp):
        for exp, cands in per_exp.items():
            assert len(cands) > 100, (
                f"exp{exp} offers only {len(cands)} candidate definitions; that "
                f"is a spot check, not a search")


class TestTheClaimDoesNotReproduce:
    def test_no_single_definition_yields_the_whole_triple(self, mp, per_exp):
        hits = [set(k for k, v in per_exp[e].items() if v == mp.CLAIMED[e])
                for e in per_exp]
        assert set.intersection(*hits) == set(), (
            "a definition now reproduces 11 / 6 / 2; the R5a ruling that it does "
            "not must be revisited rather than left standing")

    def test_each_figure_is_individually_reachable_or_not(self, mp, per_exp):
        """Stated so the null is not overread. The figures are not impossible."""
        for exp in per_exp:
            n = sum(1 for v in per_exp[exp].values() if v == mp.CLAIMED[exp])
            assert n >= 1, (
                f"exp{exp}'s claimed {mp.CLAIMED[exp]} is reachable by nothing at "
                f"all, which is a stronger claim than the ruling makes")

    def test_the_HIL_label_fails_for_2_of_the_3(self, mp, per_exp):
        """exp49's 11 and exp48's 6 match no HIL-labelled measure.

        exp47's 2 DOES match one -- the number of distinct models flagged for
        review -- and that is asserted here rather than glossed, because the
        first draft of this ruling claimed no HIL measure matched any figure and
        the script refuted it. A model count is still not a finding population,
        but the arithmetic coincidence is real and is recorded.
        """
        hil = ("escalated == true", "hil_escalated == true",
               "irreducible_escalation == true", "itc_hil_flags, entries",
               "itc_hil_flags, distinct models")
        matched = {e for e in per_exp
                   if any(per_exp[e].get(k, 0) == mp.CLAIMED[e] for k in hil)}
        assert matched == {47}, (
            f"the set of runs whose claimed figure a HIL-labelled measure can "
            f"produce has changed from {{47}} to {matched}")

    def test_the_measured_HIL_counts_run_the_other_way(self, per_exp):
        """The ordering is inverted, which no transcription error explains.

        Claimed: exp49 largest, exp47 smallest. Measured `escalated`: exp47
        largest, exp49 zero. The claim is not a mis-scaled version of the truth;
        it is ordered against it.
        """
        esc = {e: per_exp[e].get("escalated == true", 0) for e in per_exp}
        assert esc[47] > esc[48] > esc[49], esc
        assert esc[49] == 0, "exp49 has escalated findings after all"


class TestTheInnocentReadingCannotRescueIt:
    """CLOSING_2026-09-06.md:39 calls it "probably the right one". It is not."""

    def test_one_of_the_three_runs_takes_a_code_target(self, mp):
        import json
        kinds = {}
        for exp in mp.CLAIMED:
            path, _ = mp.load(exp)
            rep = sorted(path.parent.glob("exp*_report.json"))
            assert rep, f"exp{exp} has no report naming its target"
            kinds[exp] = json.loads(rep[0].read_text())["target_file"]
        assert kinds[47].endswith(".py"), kinds[47]
        assert kinds[48].endswith(".md") and kinds[49].endswith(".md"), kinds

    def test_the_code_run_is_readable_today_and_disagrees(self, mp, per_exp):
        """A code target needs no answer key, so 'uncheckable' cannot apply.

        exp47 claims 2. Its escalated count is 6, its hil_escalated 3, its
        irreducible 3. The excuse that covers the exam runs does not reach it.
        """
        c = per_exp[47]
        assert c.get("escalated == true", 0) == 6
        assert c.get("hil_escalated == true", 0) == 3
        assert c.get("irreducible_escalation == true", 0) == 3
        assert mp.CLAIMED[47] == 2


class TestTheRulingIsWrittenWhereTheQuestionIsAsked:
    def test_the_decisions_file_is_annotated_not_rewritten(self):
        """The founder's own rule from R4: that file records what was ASKED.

        Rewriting it would erase that a wrong population was put in front of him.
        The original wording must survive beside the ruling.
        """
        t = (ROOT / "experimental_notes"
             / "DECISIONS_AWAITING_YOU_2026-09-06.md").read_text()
        assert "11 Exp 49, 6 Exp 48, 2 Exp 47 HIL residuals" in t, (
            "the original claim was deleted; it is the record of what was asked")
        assert "R5a" in t, "the ruling is not written where the question is asked"

    def test_the_closing_report_carries_the_resolution(self):
        t = (ROOT / "experimental_notes" / "CLOSING_2026-09-06.md").read_text()
        assert "materiality_population_2026-09-10.py" in t, (
            "the closing report says the figures should not be quoted until "
            "something reproduces them, and does not name what settled it")
