"""A cited premise is not an accusation, and must not flag a location.

THE DEFECT THIS PINS, found 2026-08-17 while repairing description truncation.

`finding_locations` is a word-boundary scan over the whole description, so it
cannot distinguish "the defect is at EN-16" from "EN-01 defines the factored
load". Under location keying a flagged location decides whether a finding counts
as new, so a finding that shows its working claims every location it cites.

WHY IT WAS INVISIBLE FOR SO LONG — the two defects were masking each other.
Descriptions were being stored truncated, which cut the premise list off the end,
so extraction produced the right answer for the wrong reason. Repairing the
truncation ALONE made extraction worse: exp49's C0037 went from {EN-16} to
{EN-01, EN-03, EN-16, EN-17, EN-20}, and the run's novelty series moved. Only
with both repaired does the series reproduce.

That is the useful lesson, and it generalises past this bug: a fix that makes a
measurement worse is not necessarily a wrong fix — it can be a right fix that has
uncovered a second defect the first one was hiding.

SCOPE IS NARROW AND WAS SET BY MEASUREMENT, NOT BY TASTE. Only `premise(s)` is
excluded. `EVIDENCE:` is the far commoner header (78 of 122 archived instances
against 35) and it introduces substantiation of the same defect at the same
place, so stripping it would delete real signal. See `_accusing_span`.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.convergence_location import (  # noqa: E402
    _accusing_span,
    finding_locations,
)

SYMS = frozenset({"EN-01", "EN-03", "EN-16", "EN-17", "EN-20"})

# Reconstructed from exp49 C0037, the finding that exposed this. Shortened, but
# the structure — an accusation naming one claim, then a premise list naming
# four more — is verbatim in shape.
C0037 = """EN-16 reports a "global bending factor of safety" for B4-01 as
`f_y / sigma_Ed = 275 / 50.78 = 5.42`. The arithmetic is dimensionally valid,
but the factor convention is wrong: it divides an unfactored nominal resistance
by a factored design-action stress.

Premises:
- EN-01 defines the factored load: `w_Ed = 1.35 x 4.20 + 1.50 x 6.00`.
- EN-03 uses design bending stress `sigma_Ed = 50.78 MPa`.
- EN-17 defines design yield: `f_yd = 275 / 1.10 = 250 MPa`.
- EN-20 gives the section modulus used throughout.
"""


class TestTheObservedExp49Case:

    def test_only_the_accused_claim_is_flagged(self):
        assert finding_locations(C0037, SYMS) == frozenset({"EN-16"})

    def test_without_the_fix_all_five_would_be_flagged(self):
        """Guards the REASON, not just the effect. If `_accusing_span` is ever
        made a no-op, the raw scan returns all five and this says so."""
        raw = {s for s in SYMS if s in C0037}
        assert raw == {"EN-01", "EN-03", "EN-16", "EN-17", "EN-20"}

    def test_the_premise_section_is_what_gets_removed(self):
        span = _accusing_span(C0037)
        assert "EN-16" in span
        assert "Premises:" not in span
        for cited in ("EN-01", "EN-03", "EN-17", "EN-20"):
            assert cited not in span


class TestTheHeaderSetIsNarrow:
    """Everything below was measured against the archive before being included or
    excluded. These tests hold that scope in place."""

    def test_evidence_is_NOT_stripped(self):
        """78 of 122 archived supporting-material headers are `EVIDENCE:`, and
        they substantiate the same defect at the same place. Stripping them would
        delete real location signal, so this must keep failing if someone widens
        the header set for symmetry."""
        text = ("EN-16 uses the wrong factor convention.\n"
                "EVIDENCE: EN-03 shows sigma_Ed applied at the same line.")
        assert finding_locations(text, SYMS) == frozenset({"EN-16", "EN-03"})

    def test_context_and_background_are_NOT_stripped(self):
        text = "EN-16 is wrong.\nBackground: EN-01 sets the load case."
        assert "EN-01" in finding_locations(text, SYMS)

    @pytest.mark.parametrize("header", [
        "Premises:", "Premise:", "PREMISES:", "**Premises:**",
        "## Premises:", "- Premises:", "> Premises -",
    ])
    def test_the_premise_header_is_recognised_in_the_shapes_models_write(self, header):
        text = f"EN-16 is wrong.\n{header}\nEN-01 defines the load."
        assert finding_locations(text, SYMS) == frozenset({"EN-16"})


class TestItCannotSilentlyEraseAFinding:

    def test_a_description_that_is_only_premises_still_yields_its_own_span(self):
        """A premise header at position 0 leaves an empty accusing span. That
        must return NO locations rather than raising — an unlocated finding is a
        state the rule already handles, an exception is not."""
        assert finding_locations("Premises:\nEN-01 defines the load.", SYMS) == frozenset()

    def test_no_premise_header_leaves_the_text_untouched(self):
        text = "EN-16 and EN-03 are both wrong for the same reason."
        assert _accusing_span(text) == text
        assert finding_locations(text, SYMS) == frozenset({"EN-16", "EN-03"})

    def test_empty_and_none_are_safe(self):
        assert _accusing_span("") == ""
        assert _accusing_span(None) == ""
        assert finding_locations(None, SYMS) == frozenset()


class TestTheArchivedSeriesStillReproduce:
    """The precondition for every convergence claim in the project. If the
    location-only replay stops reproducing a run's own recorded history, nothing
    computed from that replay means anything — including this fix's own
    justification."""

    @pytest.mark.parametrize("run", ["exp45", "exp46", "exp48", "exp49"])
    def test_close_round_is_unchanged_for_the_runs_that_did_not_move(self, run):
        from bench.tests.test_combined_identity_rule import (
            ARCHIVE, _archive_case, _symbols_for)
        from bench.convergence_location import location_only_series
        if run not in ARCHIVE:
            pytest.skip(f"{run} not in the archive table")
        ent, maxr, archived, _conv = _archive_case(run)
        assert location_only_series(ent, maxr, _symbols_for(run)) == archived
