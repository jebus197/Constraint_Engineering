#!/usr/bin/env python3
"""The non-curing closures are a NAMED SET, not a count.

HIS RULING, 2026-10-30: *"I accept your recommendation."* against recording the
non-curing closures as a named population rather than reopening them in a
sealed archive.

WHY A SET AND NOT A COUNT, which is the whole point of the artefact: 2 runs can
both report 23 non-curing closures and share not one finding between them, so a
later run matching the count establishes nothing. The recorded identities are
what a comparison can actually be made against.

THE 2 INSTRUMENTS MUST AGREE. The producer keys on
`fix_efficacy.outcome == "FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER"`;
`scripts/e1_population_recount_falsifier_2026-09-22.py` reaches the same
population through an independent implementation over an independent glob. The
producer executes it and refuses to write if they disagree.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

DATA = REPO / "experimental_notes" / "data" / "non_curing_closures_2026-10-31.json"
PRODUCER = (REPO / "scripts" /
            "the_non_curing_population_is_named_2026-10-31.py")


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("ncpop", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def recorded():
    assert DATA.is_file(), (
        "the named population has not been written; run the producer with "
        "--write")
    return json.loads(DATA.read_text())


class TestItIsASetNotACount:
    def test_every_identity_names_a_run_and_a_finding(self, recorded):
        ids = recorded["identities"]
        assert ids, "the population is empty"
        for row in ids:
            assert row.get("run"), row
            assert row.get("canonical_id"), row

    def test_the_identities_are_distinct(self, recorded):
        ids = [(r["run"], r["canonical_id"]) for r in recorded["identities"]]
        assert len(ids) == len(set(ids)), (
            "the population double-counts; a record stored in 2 files was "
            "counted twice, which is the exact defect "
            "e1_population_recount_falsifier_2026-09-22.py exists to catch")

    def test_the_count_matches_the_set(self, recorded):
        assert recorded["counts"]["archive_non_curing"] == \
            len(recorded["identities"]), (
                "the recorded count and the recorded set disagree, so one of "
                "them is wrong and neither can be cited")

    def test_every_row_carries_what_a_comparison_needs(self, recorded):
        for r in recorded["rows"]:
            for field in ("run", "canonical_id", "outcome", "flaw_class"):
                assert field in r, (field, r)
            assert r["outcome"] == "FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER", r


class TestTheProducerStillAgreesWithTheOlderInstrument:
    def test_the_cross_check_runs_and_agrees(self, mod, recorded):
        xc = mod.cross_check(recorded["counts"]["claim_scope_non_curing"])
        assert xc.get("ran") is True, xc
        assert xc.get("agree") is True, (
            "the 2 independent implementations disagree: %r" % (xc,))

    def test_the_claim_scope_figure_is_the_dated_one(self, recorded):
        """23 of 124 is the figure the 2026-09-22 claim names. A later arm must
        not silently overwrite a dated measurement."""
        assert recorded["counts"]["claim_scope_records"] == 124
        assert recorded["counts"]["claim_scope_non_curing"] == 23

    def test_the_whole_archive_figure_is_larger_and_separate(self, recorded):
        c = recorded["counts"]
        assert c["archive_records"] > c["claim_scope_records"]
        assert c["archive_non_curing"] > c["claim_scope_non_curing"], (
            "the archive-wide figure is not larger than the claim scope, so "
            "either the scoping broke or the glob did")


class TestTheOutcomeVocabularyIsMeasuredNotInvented:
    def test_the_producer_names_the_outcome_the_archive_actually_uses(self, mod):
        assert mod.NON_CURING_OUTCOME == "FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER"

    def test_an_invented_outcome_finds_nothing(self, mod, monkeypatch):
        """The first version of the producer invented a vocabulary and returned
        0 of 659 while the record count matched exactly -- the signature of a
        predicate error. This proves the guard would catch that recurrence."""
        monkeypatch.setattr(mod, "NON_CURING_OUTCOME", "not_cured")
        got = mod.collect()
        assert got["records"] > 100, (
            "the collection itself broke, so this test is not measuring the "
            "classification")
        assert len(got["rows"]) == 0, (
            "an invented outcome value matched something, so the vocabulary is "
            "not as tight as the producer claims")
