"""Task C1: the commissioning measurement the channel's promotion waits on.

HIS INSTRUCTION, 2026-10-02: *"Also implement this and test it on the upcoming
simulated runs."* His reply to the position that the claim channel's promotion
into the scoring equations *"waits on a commissioning run measuring how often
it is wrong against known ground truth"*.

THE TEST HALF WAS DONE AND THE MEASURE HALF WAS NOT. `bench/claim_ledger.py`
carries `informative_only = True` and its header says the ledger is promoted
"only after a commissioning run measures its error". The channel ran in both
free runs of 2026-10-15 -- 22 claims, 19 decidable, 3 routed -- so it was
exercised; its error was never measured.

WHAT "ITS ERROR" CAN MEAN, which decides what this file asserts.
`claim_from_entry` does NOT judge whether a claim is true. It TRANSCRIBES the
falsifier path: `decidable` is whether a falsifier exists, `verdict` is the
falsifier's own verdict when that verdict is one of the decided five, and
`routed_to` records where an undecidable claim went. So the channel's own error
is TRANSCRIPTION error, and the end-to-end accuracy it inherits belongs to the
falsifier path. Crediting one to the other would blame the wrong mechanism.

MEASURED, by scripts/commission_the_claim_channel_2026-10-17.py:
  * the falsifier path discriminates BOTH WAYS on 5 of 5 documents --
    CONFIRMED on the pristine text where the false claim is planted, REFUTED on
    the corrected text -- 100.0000%, Wilson [56.5518%, 100.0000%];
  * the channel transcribes 58 of 58 verdicts exactly, 100.0000%, Wilson
    [93.7882%, 100.0000%], so its transcription error is bounded below about
    6.2% at 95%. The first version of that measurement used 1 claim per
    document, n=10, and bounded the error only below about 28% -- not a figure
    worth gating a promotion on, which is why it uses all 29 tagged claims;
  * all 4 routing properties hold.

PROMOTION IS STILL NOT DONE, AND DELIBERATELY. The channel is not wired into
sigma, S_k or R_k, and NO DOCUMENT SPECIFIES HOW it would enter them -- as a
weight, a multiplier, a gate or a term. Clearing `informative_only` without
that form would not promote the channel; it would invent a model term. This
project has one near-miss of exactly that shape on record: a proposal to
replace the model-derived severity with a rubric that had already measured as
agreeing no better than chance (kappa = -0.0227, Fisher p = 0.78). The form is
his, and the measurement is what his gate asked for.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "commission_the_claim_channel_2026-10-17.py"
for p in (REPO, REPO / "bench" / "tests" / "fixtures" / "stem"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from bench.claim_ledger import (ClaimLedger, claim_from_entry, UNVERIFIED,  # noqa: E402
                                ROUTE_HIL, ROUTE_VERIFY_CURRENT)


def _entry(**kw):
    base = {"canonical_id": "C-1", "description": "a claim",
            "source_ref": "anchor", "falsifier_code": "print(1)",
            "falsifier_verdict": "CONFIRMED",
            "finding_category": "computation", "severity": 0.5,
            "source_model": "fixture"}
    base.update(kw)
    return base


def test_the_producer_exists():
    assert PRODUCER.is_file(), "the commissioning measurement has no script"


def test_the_ground_truth_corpus_is_present_and_the_right_size():
    import stem_fixtures as SF
    assert len(SF.FIXTURES) == 5
    total = sum(len(f.claims) for f in SF.FIXTURES)
    assert total == 29, (
        f"the corpus holds {total} tagged claims, not 29. Every figure derived "
        f"from it needs re-deriving, including the Wilson bound quoted in this "
        f"file's docstring.")


@pytest.mark.parametrize("verdict", ["CONFIRMED", "REFUTED", "ERROR",
                                     "UNTOOLABLE", "INTEGRITY_VIOLATION"])
def test_a_decided_verdict_is_transcribed_unchanged(verdict):
    """TRANSCRIPTION FIDELITY, the figure his gate asked for, asserted per
    verdict rather than in aggregate so a single mangled one cannot hide."""
    c = claim_from_entry("X", _entry(falsifier_verdict=verdict))
    assert c.verdict == verdict, (
        f"a {verdict} verdict came out of the channel as {c.verdict!r}; the "
        f"channel is editing the falsifier path's conclusion, not recording it")


def test_an_unknown_verdict_becomes_UNVERIFIED_rather_than_passing_through():
    """The other direction: the channel must not launder an unrecognised string
    into the record as though the falsifier had said it."""
    c = claim_from_entry("X", _entry(falsifier_verdict="PROBABLY_FINE"))
    assert c.verdict == UNVERIFIED


def test_a_claim_with_no_falsifier_is_routed_and_not_decided():
    c = claim_from_entry("X", _entry(falsifier_code="",
                                     falsifier_verdict=""))
    assert c.decidable is False
    assert c.verdict == UNVERIFIED
    assert c.routed_to == ROUTE_HIL


def test_a_state_claim_routes_to_verify_current_instead_of_a_human():
    c = claim_from_entry("X", _entry(falsifier_code="", falsifier_verdict="",
                                     finding_category="state"))
    assert c.routed_to == ROUTE_VERIFY_CURRENT


def test_the_channel_is_still_informative_only_and_that_is_the_honest_state():
    """THE ASSERTION MOST LIKELY TO BE MISREAD, so it says why.

    This does NOT assert that the channel should stay unpromoted for ever. It
    asserts that it must not be promoted WITHOUT a specified form, because
    clearing the flag alone changes nothing in sigma, S_k or R_k -- it merely
    stops the code saying it is unwired. If the flag is ever cleared, the same
    commit must wire the channel into a named term and this test must be
    re-derived to check THAT wiring, not deleted."""
    assert ClaimLedger.informative_only is True, (
        "`informative_only` has been cleared. If the channel is now wired into "
        "the scoring equations, name the term and the document that specifies "
        "it, and replace this test with one that checks the wiring. If it is "
        "not wired, clearing the flag made the code describe itself falsely.")


def test_the_promotion_gate_is_recorded_where_a_reader_will_look():
    """The gate is a claim about the code's state, so it lives in the code."""
    src = (REPO / "bench" / "claim_ledger.py").read_text(
        encoding="utf-8", errors="replace")
    assert "commissioning" in src.lower(), (
        "the module no longer records that its promotion waits on a "
        "commissioning measurement, so the gate exists only in a note")


def test_the_aggregate_reaches_all_three_of_its_states():
    """ALL 3 REACHED, which is what makes 3 states worth having over 2.

    An earlier version of this test asserted that adding an undecidable claim
    to a decided ledger CHANGES the aggregate. That was wrong about the code
    and the code was right: `CLAIM_ADDRESSABLE` means, in the module's own
    words, "At least 1 claim in this target is decidable by computation", so a
    mixed ledger is still claim-addressable. The aggregate is not a mixedness
    measure and does not claim to be. What matters is that none of its 3
    states is unreachable -- an unreachable state is a distinction that
    decides nothing."""
    from bench.claim_ledger import (CLAIM_ADDRESSABLE, ROUTED_ONLY,
                                    NO_DECIDABLE_CLAIMS, AGGREGATE_STATES,
                                    AGGREGATE_MEANINGS)

    empty = ClaimLedger(target="t")
    assert empty.aggregate() == NO_DECIDABLE_CLAIMS

    routed = ClaimLedger(target="t")
    routed.add(claim_from_entry("R", _entry(falsifier_code="",
                                            falsifier_verdict="")))
    assert routed.aggregate() == ROUTED_ONLY

    decided = ClaimLedger(target="t")
    decided.add(claim_from_entry("A", _entry()))
    assert decided.aggregate() == CLAIM_ADDRESSABLE
    #: And a MIXED ledger stays addressable, which is the documented meaning
    #: rather than an accident.
    decided.add(claim_from_entry("B", _entry(canonical_id="B",
                                             falsifier_code="",
                                             falsifier_verdict="")))
    assert decided.aggregate() == CLAIM_ADDRESSABLE
    assert len(decided.decidable()) == 1 and len(decided.routed()) == 1, (
        "the mixed ledger no longer holds 1 of each, so this is not testing a "
        "mixed state at all")
    #: EVERY STATE CARRIES ITS MEANING INLINE, because one exported record must
    #: be readable without a second file.
    assert set(AGGREGATE_STATES) == set(AGGREGATE_MEANINGS)
    assert all(AGGREGATE_MEANINGS[s].strip() for s in AGGREGATE_STATES)


def test_no_claim_is_ever_discarded():
    """`discarded` must always be empty: a claim that is neither decidable nor
    routed has fallen out of the record entirely."""
    led = ClaimLedger(target="t")
    for n, kw in enumerate(({}, {"falsifier_code": "", "falsifier_verdict": ""},
                            {"finding_category": "state",
                             "falsifier_code": "", "falsifier_verdict": ""})):
        led.add(claim_from_entry(f"D{n}", _entry(canonical_id=f"D{n}", **kw)))
    assert led.discarded() == [], (
        f"{len(led.discarded())} claim(s) are neither decidable nor routed, so "
        f"they exist in the ledger and in no category")
