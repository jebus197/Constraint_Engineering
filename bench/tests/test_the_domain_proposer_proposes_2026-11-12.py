#!/usr/bin/env python3
"""The domain proposer is EXECUTED here, and it proposes rather than decides.

★ WHY THIS FILE EXISTS. `bench/cdsfl_registry/domain_proposer.py` was written on
2026-11-12 to close a measured gap: by syntax tree over the reference runner,
**1** command-line domain argument with a hardcoded default, **0** functions
classifying a domain from task content, and **0 of 67** archived run states
recording which domain a run used. A new module with no test is the defect class
this project has 11 confirmed instances of -- an addition nothing reaches -- so
this guard exists before the module is relied on.

★ THE DISCRIMINATING TESTS DRIVE A CONSTRUCTED VOCABULARY, NOT THE LIVE CORPUS.
The live corpus happens to satisfy the properties below, so a test that only ran
against it could not see them break. 2 of the proposer's own rules were WRONG on
their first run and were caught exactly this way:

  * ambiguity was measured between the top 2 candidates whatever domain they
    belonged to, which scored the DOMAIN right 4 times of 4 and the ambiguity
    signal right only 2 times of 4. It is now measured against the nearest
    candidate in a DIFFERENT domain, because the consequence scale, the critical
    level and the encoding are all properties of the domain -- 2 subdomains of
    1 domain share all 3, so a close call between them changes nothing.
  * the score was nearly a raw overlap count, which would have handed every
    verdict to the longest encoding. The 22 boxes written on 2026-11-12 run 109
    to 142 lines against a mean of 65.2 for the 28 older ones, so length alone
    would have decided. It is normalised by the square root of the box size.

Costs nothing: reads local files, dispatches to no model, runs no pytest.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
MODULE = REPO / "bench" / "cdsfl_registry" / "domain_proposer.py"


@pytest.fixture(scope="module")
def P():
    assert MODULE.is_file(), f"the proposer is missing: {MODULE}"
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location("dp_guard", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestTheVocabularyIsDerivedAndNotInvented:
    def test_it_reads_the_real_encodings_and_finds_every_candidate(self, P):
        v = P.vocabulary()
        assert len(v) >= 40, f"only {len(v)} candidate(s) have a vocabulary"
        assert all(len(t) >= 50 for t in v.values()), (
            "a candidate with almost no distinctive terms cannot discriminate: "
            f"{sorted((len(t), k) for k, t in v.items())[:3]}")

    def test_no_hand_written_keyword_list_decides_a_domain(self):
        """A keyword list would be a 2nd source of truth about what a domain is,
        and would drift from the manifest the moment a subdomain was re-pathed."""
        src = MODULE.read_text(encoding="utf-8")
        for name in ("biology", "chemistry", "software", "mathematics"):
            # a domain name may appear in prose, but never as a dict key mapping
            # it to terms, which is what a hand-written table looks like
            assert f'"{name}": [' not in src and f"'{name}': [" not in src, (
                f"{name} appears to be mapped to a hand-written term list")

    def test_format_words_are_excluded_so_structure_cannot_score(self, P):
        v = P.vocabulary()
        for junk in ("constraints", "verification", "limitations"):
            carriers = [k for k, t in v.items() if junk in t]
            assert not carriers, (
                f"{junk!r} is a section heading present in every box and must "
                f"not be a distinctive term; it is in {len(carriers)}")


class TestItProposesAndNeverDecides:
    def test_the_return_shape_always_carries_an_ambiguity_flag(self, P):
        r = P.propose("a replica diverged after a network partition healed")
        assert set(r) >= {"domain", "subdomain", "ambiguous", "reason", "top"}
        assert isinstance(r["ambiguous"], bool)
        assert r["reason"], "a proposal with no stated reason cannot be overridden"

    def test_an_unmatchable_task_is_AMBIGUOUS_not_a_confident_guess(self, P):
        r = P.propose("zzzz qqqq")
        assert r["ambiguous"] is True, (
            "a task matching no distinctive term must escalate, not guess")

    def test_an_empty_task_does_not_crash_or_decide(self, P):
        r = P.propose("")
        assert r["ambiguous"] is True
        assert r["domain"] is None


class TestAmbiguityIsMeasuredAtDOMAINLevel:
    """CONSTRUCTED vocabularies: the live corpus exercises only some branches."""

    @staticmethod
    def _vocab(**kw):
        return {tuple(k.split("/")): set(v.split()) for k, v in kw.items()}

    def test_a_close_contest_WITHIN_one_domain_is_NOT_ambiguous(self, P):
        """Both candidates carry the same scale, so nothing needs asking."""
        v = {("mathematics", "proof"): {"converge", "monotone", "lemma", "bound"},
             ("mathematics", "applied"): {"converge", "monotone", "lemma", "model"}}
        r = P.propose("converge monotone lemma", v)
        assert r["domain"] == "mathematics"
        assert r["ambiguous"] is False, (
            "a contest confined to 1 domain must report as settled: "
            f"{r['reason']}")

    def test_a_close_contest_ACROSS_domains_IS_ambiguous(self, P):
        """The scale is not settled, so the surface must ask."""
        v = {("statistics", "inference"): {"pooled", "estimate", "fixed", "effect"},
             ("biology", "biomedical"): {"pooled", "estimate", "fixed", "dosing"}}
        r = P.propose("pooled estimate fixed", v)
        assert r["ambiguous"] is True, f"expected escalation: {r['reason']}"
        assert r.get("nearest_other_domain") not in (None, r["domain"])

    def test_a_clear_winner_across_domains_is_NOT_ambiguous(self, P):
        v = {("software", "distributed"): {"replica", "partition", "quorum",
                                           "linearizable", "heartbeat"},
             ("biology", "zoology"): {"burrow", "plumage", "forage"}}
        r = P.propose("replica partition quorum linearizable heartbeat", v)
        assert r["domain"] == "software"
        assert r["ambiguous"] is False, r["reason"]


class TestLengthCannotDecide:
    def test_a_long_box_does_not_win_on_size_alone(self, P):
        """The 22 new boxes run 109-142 lines against a mean of 65.2 for the 28
        older ones, so a raw overlap count would have decided every case by age.

        ★ THIS CASE WAS VACUOUS ON ITS FIRST RUN, 2026-11-12, AND A MUTATION
        HARNESS CAUGHT IT. The original gave both boxes the SAME 3 hits and named
        the domains "a" and "b". Under a raw count that is a TIE, and `score`
        breaks ties alphabetically -- so "a" won whether the normalisation was
        there or not, and removing the normalisation left the test GREEN. The
        tiebreak was deciding, not the property under test.

        REPAIRED BY MAKING THE RAW COUNT FAVOUR THE WRONG ANSWER: the long box
        now matches 4 terms to the short box's 3, AND its domain sorts FIRST, so
        both the count and the tiebreak point at it. Only the normalisation can
        return the short box, and the mutation now goes red.
        """
        short = {"alpha", "beta", "gamma"}
        long = {f"w{i}" for i in range(400)} | {"alpha", "beta", "gamma", "delta"}
        #: "a_long" sorts before "z_short", so the tiebreak favours the long box too
        v = {("a_long", "big"): long, ("z_short", "small"): short}
        r = P.propose("alpha beta gamma delta", v)
        assert r["domain"] == "z_short", (
            "the larger vocabulary won on size: normalisation is not working; "
            f"top={r['top']}")


class TestItRunsAndItsHelpIsFree:
    def test_help_answers_without_running_the_measurement(self):
        r = subprocess.run([sys.executable, str(MODULE), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr[-600:]
        assert r.stdout.lower().startswith("usage:")
        assert "PROPOSAL" not in r.stdout

    def test_it_proposes_from_the_command_line(self):
        r = subprocess.run(
            [sys.executable, str(MODULE),
             "two replicas disagree after a network partition healed and the "
             "clocks had drifted"],
            cwd=REPO, capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stderr[-800:]
        assert "PROPOSAL:" in r.stdout
        assert "ambiguous:" in r.stdout

    def test_the_vocab_size_report_runs(self):
        r = subprocess.run([sys.executable, str(MODULE), "--vocab-size"],
                           cwd=REPO, capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stderr[-600:]
        assert "distinctive term" in r.stdout
