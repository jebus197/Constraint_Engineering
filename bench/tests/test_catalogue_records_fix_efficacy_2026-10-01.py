#!/usr/bin/env python3
"""The exported finding catalogue says whether the proposed FIX worked.

THE DEFECT, found by the cc2 seat in the free panel review of 2026-09-30 and
ruled on by the founder with one word, "Add it". `export_finding_catalogue`
carried `demonstrated` and `falsifier_verdict` -- both about whether the DEFECT
was shown -- and no field at all about whether the FIX was. A fix measured and
found not to cure its own falsifier was invisible to anyone reading the exported
record, against the founder's standing ruling that wrong fixes and failures be
recorded and open to HIL inspection.

THE DATA WAS ALREADY THERE, which is what made it worth fixing rather than
designing. Measured over
`bench/logs/commissioning_arm1_panel_20260921T215405Z/runner_state.json`: 69 of
69 registry entries carry a `fix_efficacy` dict, and 16 of them read
FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER. The export simply dropped it.

WHY TRI-STATE AND NOT A BOOLEAN. `bench/fix_efficacy.py` says in its own
comment that "the fix did not cure it" and "the instrument could not look" must
never be the same value, "which is the distinction the whole project keeps
having to relearn". A boolean `fix_cured_its_falsifier` would have merged 28
never-measured entries with the 25 that cured, in the reassuring direction.

Run:  python3 -m pytest bench/tests/test_catalogue_records_fix_efficacy_2026-10-01.py -q
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.fix_efficacy import (  # noqa: E402
    ALL_OUTCOMES,
    CONCLUSIVE_OUTCOMES,
    FIX_CURES,
    FIX_INEFFECTIVE,
    NO_FALSIFIER,
    OUTCOME_MEANINGS,
)
from bench.reference_runner_v3 import export_finding_catalogue  # noqa: E402

#: The run the measurement above was taken on.
ARCHIVE = (REPO / "bench" / "logs"
           / "commissioning_arm1_panel_20260921T215405Z" / "runner_state.json")

FIELDS = ("fix_efficacy_outcome", "fix_efficacy_meaning",
          "fix_efficacy_measured", "fix_cured_its_falsifier")


def _archived_entries() -> dict:
    if not ARCHIVE.is_file():
        pytest.skip(f"archive absent: {ARCHIVE}")
    doc = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    return (doc.get("registry") or {}).get("entries") or {}


class TestTheVocabularyAndItsGlossCannotDrift:
    """Both live in `bench/fix_efficacy.py`, so this holds them in step."""

    def test_every_outcome_constant_has_a_meaning(self):
        constants = {FIX_CURES, FIX_INEFFECTIVE, NO_FALSIFIER}
        missing = [c for c in constants if c not in OUTCOME_MEANINGS]
        assert missing == [], (
            f"an outcome a reader can receive carries no gloss: {missing}")
        assert set(ALL_OUTCOMES) == set(OUTCOME_MEANINGS)

    def test_no_meaning_is_empty_or_a_restatement_of_its_key(self):
        for name, meaning in OUTCOME_MEANINGS.items():
            assert len(meaning) > 40, f"{name} gloss is too thin: {meaning!r}"
            assert meaning != name

    def test_conclusive_means_the_probe_reached_a_verdict_about_the_fix(self):
        assert set(CONCLUSIVE_OUTCOMES) == {FIX_CURES, FIX_INEFFECTIVE}
        for name in ALL_OUTCOMES:
            if name not in CONCLUSIVE_OUTCOMES:
                assert name.startswith(("INDETERMINATE", "NOT_PROBED")), (
                    f"{name} is excluded from CONCLUSIVE_OUTCOMES but does not "
                    f"read as an instrument failure")


class TestTheExportCarriesTheFields:
    def test_every_record_carries_all_4_fields(self):
        recs = export_finding_catalogue(_archived_entries())
        assert recs, "no records exported"
        for r in recs:
            for f in FIELDS:
                assert f in r, f"{r.get('canonical_id')} is missing {f}"

    def test_a_measured_non_cure_is_visible_in_the_export(self):
        """ANTI-VACUITY. The fields are worthless if the case never appears."""
        recs = export_finding_catalogue(_archived_entries())
        failed = [r for r in recs
                  if r["fix_efficacy_outcome"] == FIX_INEFFECTIVE]
        assert failed, (
            "this archive carries no measured non-cure, so the field this file "
            "exists to hold is untested here")
        for r in failed:
            assert r["fix_efficacy_measured"] is True
            assert r["fix_cured_its_falsifier"] is False
            assert "did NOT work" in r["fix_efficacy_meaning"]

    def test_the_tri_state_keeps_never_measured_apart_from_failed(self):
        recs = export_finding_catalogue(_archived_entries())
        states = {True: 0, False: 0, None: 0}
        for r in recs:
            states[r["fix_cured_its_falsifier"]] += 1
        assert states[None] > 0 and states[False] > 0 and states[True] > 0, (
            f"this archive does not exercise all 3 states: {states}. A boolean "
            f"would have merged 2 of them and nothing would have failed.")
        for r in recs:
            if r["fix_cured_its_falsifier"] is None:
                assert r["fix_efficacy_measured"] is False
                assert r["fix_efficacy_outcome"] not in CONCLUSIVE_OUTCOMES

    def test_every_exported_outcome_carries_its_meaning(self):
        recs = export_finding_catalogue(_archived_entries())
        bare = [r["canonical_id"] for r in recs
                if r["fix_efficacy_outcome"] and not r["fix_efficacy_meaning"]]
        assert bare == [], (
            f"an outcome reached the export with no gloss, so the record "
            f"cannot be read without a second file: {bare}")


class TestTheFieldsAreHonestOnTheAbsentCase:
    """FALSIFIERS. An entry with no probe record must not read as a pass."""

    def test_an_entry_with_no_fix_efficacy_reads_as_never_measured(self):
        recs = export_finding_catalogue({"C9001": {"status": "OPEN"}})
        r = recs[0]
        assert r["fix_efficacy_outcome"] == ""
        assert r["fix_efficacy_measured"] is False
        assert r["fix_cured_its_falsifier"] is None, (
            "an unprobed fix reads as a FAILED fix, which blames a fix nobody "
            "measured")
        assert "no fix-efficacy probe record" in r["fix_efficacy_meaning"]

    def test_a_malformed_fix_efficacy_does_not_raise_or_claim_a_verdict(self):
        for junk in ("FIX_CURES_ITS_OWN_FALSIFIER", [], 0, None):
            recs = export_finding_catalogue(
                {"C9002": {"status": "OPEN", "fix_efficacy": junk}})
            r = recs[0]
            assert r["fix_efficacy_outcome"] == "", junk
            assert r["fix_cured_its_falsifier"] is None, junk

    def test_an_unknown_outcome_string_is_reported_rather_than_glossed(self):
        recs = export_finding_catalogue(
            {"C9003": {"status": "OPEN",
                       "fix_efficacy": {"outcome": "SOMETHING_NEW"}}})
        r = recs[0]
        assert r["fix_efficacy_outcome"] == "SOMETHING_NEW"
        assert r["fix_efficacy_meaning"] == "", (
            "an outcome with no entry in the vocabulary was handed a gloss it "
            "does not have")
        assert r["fix_cured_its_falsifier"] is None

    def test_a_cure_reads_as_a_cure(self):
        recs = export_finding_catalogue(
            {"C9004": {"status": "CLOSED",
                       "fix_efficacy": {"outcome": FIX_CURES}}})
        r = recs[0]
        assert r["fix_efficacy_measured"] is True
        assert r["fix_cured_its_falsifier"] is True
        assert "it worked" in r["fix_efficacy_meaning"]


class TestWhatTheNewFieldsMakeVisible:
    def test_a_closed_finding_whose_fix_failed_is_now_findable(self):
        """The case the founder asked to be open to inspection.

        A finding can be CLOSED with `demonstrated` True -- the defect was
        shown and the finding resolved -- while the fix that resolved it was
        measured and did not cure its own falsifier. Before these fields a
        reader of the export could not see that combination at all.
        """
        recs = export_finding_catalogue(_archived_entries())
        both = [r for r in recs
                if r["fix_cured_its_falsifier"] is False
                and r["status"] in ("CLOSED", "CONFIRMED")]
        assert both, (
            "no closed-with-a-failed-fix record in this archive; if that is "
            "genuinely so, this test should name the archive that has one "
            "rather than passing vacuously")
        # Reported, not asserted as a defect: the disposition is the founder's.
        print(f"\n  CLOSED or CONFIRMED with a MEASURED NON-CURING FIX: "
              f"{len(both)} of {len(recs)}")
        for r in both[:5]:
            print(f"    {r['canonical_id']}  {r['status']}  "
                  f"demonstrated={r['demonstrated']}")
