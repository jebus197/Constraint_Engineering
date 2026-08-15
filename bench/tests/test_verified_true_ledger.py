"""Regression tests for the survived-falsification ledger (2026-08-08).

The gap this ledger closes: the harness had NO positive record that a claim was
tested and stood. Grepping the runner for ``verified_true`` / ``confirmed_true``
/ ``claim_stands`` returned nothing, so a perfect run of the zero-plant control
— a target document with no planted defects — produced an ABSENCE, which is
indistinguishable from a dispatch failure or a document nobody read.

What is pinned here:

  * A clean-exit (REFUTED) falsifier WRITES a row.
  * A firing (CONFIRMED) falsifier writes NOTHING.
  * An ERRORing falsifier writes NOTHING and confirms NOTHING — an error is not
    evidence in either direction. Same for UNTOOLABLE.
  * An un-fed ledger says NEVER_INVOKED rather than serenely reporting zero
    survivals. Those two states are opposite in meaning and this suite refuses
    to let them share a rendering.
  * The ledger never touches the two-sided convergence gate.
  * The wording can never be read as "proven true".

The end-to-end tests drive the REAL ``reverify_falsifier`` sandbox, so the
verdicts under test are produced by the same code path a live run uses rather
than by hand-written strings. Offline: the falsifier snippets run in a
subprocess and make no network calls.
"""
from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from bench.evidence import (
    KNOWN_VERDICTS,
    LEDGER_CRITICAL_SEVERITY,
    MISSING_CLAIM_SENTINEL,
    SURVIVAL_MEANING,
    SurvivedFalsificationLedger,
    SurvivedTest,
)
from bench.falsifier_verify import reverify_falsifier


# A falsifier for a claim that is TRUE: it probes for the alleged defect,
# does not find it, and exits cleanly. This is the zero-plant control shape.
TRUE_CLAIM_FALSIFIER = (
    "vals = [1, 2, 3]\n"
    "if sum(vals) != 6:\n"
    "    raise AssertionError('sum is wrong')\n"
    "print('probe found no defect')\n"
)

# A falsifier for a claim that is FALSE: the defect is real and it fires.
REAL_DEFECT_FALSIFIER = "assert 2 + 2 == 5, 'arithmetic defect demonstrated'\n"

# A falsifier that is BROKEN — crashes for an unrelated reason.
BROKEN_FALSIFIER = "import module_that_does_not_exist_xyz\n"

# A falsifier that reaches for the material that decides the answer. The
# integrity gate refuses it BEFORE execution, so it is never run and resolves
# the finding in neither direction. This is the fifth thing reverify_falsifier
# can return and the ledger must route it, not raise on it.
KEY_READING_FALSIFIER = (
    "import json\n"
    "key = json.load(open('answer_key.json'))\n"
    "assert key['claims']['CH-13']['truth'] is False\n"
)


def _ledger(**kw):
    return SurvivedFalsificationLedger(experiment=kw.pop("experiment", "test_exp"))


def _record(ledger, **kw):
    """Record with sane defaults so each test states only what it varies."""
    args = dict(
        finding_id="C0042",
        claim_under_test="Section 3 asserts the decay constant is 0.30",
        falsifier_code=TRUE_CLAIM_FALSIFIER,
        authored_by="CC2-SIM",
        runner_verdict="REFUTED",
        round_idx=4,
        severity=0.5,
    )
    args.update(kw)
    return ledger.record(**args)


# ── The three P-pass obligations, against the REAL sandbox ───────────────────

def test_clean_falsifier_writes_an_entry_end_to_end():
    """A falsifier that runs clean is recorded as the claim surviving that test."""
    verdict = reverify_falsifier(TRUE_CLAIM_FALSIFIER)
    assert verdict == "REFUTED", "precondition: this falsifier must exit clean"

    led = _ledger()
    row = _record(led, runner_verdict=verdict)

    assert isinstance(row, SurvivedTest)
    assert len(led) == 1
    assert led.standing() == [row]
    # The row carries everything the founder asked for: the claim, the
    # falsifier, the model that wrote it, the runner's verdict, and the round.
    assert row.claim_under_test == "Section 3 asserts the decay constant is 0.30"
    assert row.falsifier_code == TRUE_CLAIM_FALSIFIER
    assert row.authored_by == "CC2-SIM"
    assert row.runner_verdict == "REFUTED"
    assert row.round_idx == 4
    assert row.still_standing is True
    assert row.malformed is False


def test_firing_falsifier_writes_nothing_end_to_end():
    """A falsifier that demonstrates the defect writes no survival row."""
    verdict = reverify_falsifier(REAL_DEFECT_FALSIFIER)
    assert verdict == "CONFIRMED", "precondition: this falsifier must fire"

    led = _ledger()
    row = _record(led, falsifier_code=REAL_DEFECT_FALSIFIER, runner_verdict=verdict)

    assert row is None
    assert led.entries == []
    assert led.standing() == []
    # But the attempt IS counted — the ledger knows it was working.
    assert led.observations == 1
    assert led.verdict_tally["CONFIRMED"] == 1


def test_errored_falsifier_is_evidence_in_neither_direction_end_to_end():
    """An ERROR produces no survival row AND no confirmation."""
    verdict = reverify_falsifier(BROKEN_FALSIFIER)
    assert verdict == "ERROR", "precondition: a broken falsifier must ERROR"

    led = _ledger()
    row = _record(led, falsifier_code=BROKEN_FALSIFIER, runner_verdict=verdict)

    assert row is None
    assert led.entries == []
    # Not a survival...
    assert led.standing() == []
    # ...and not a demonstration either: it must not overturn anything, and a
    # later genuine survival of the same finding must be born standing.
    later = _record(led, round_idx=5)
    assert later is not None and later.still_standing is True
    assert led.overturned() == []
    assert led.verdict_tally["ERROR"] == 1
    assert led.verdict_tally["CONFIRMED"] == 0


def test_untoolable_writes_nothing_and_confirms_nothing():
    """No falsifier means nothing was tested — same standing as an ERROR."""
    assert reverify_falsifier("") == "UNTOOLABLE"

    led = _ledger()
    row = led.record(
        finding_id="C0100",
        claim_under_test="a claim nobody wrote a falsifier for",
        falsifier_code="",
        authored_by="Gemini-SIM",
        runner_verdict="UNTOOLABLE",
        round_idx=2,
    )
    assert row is None
    assert led.entries == []
    assert led.observations == 1
    assert led.verdict_tally["UNTOOLABLE"] == 1


def test_a_refused_falsifier_is_never_a_survival_end_to_end():
    """A falsifier refused by the integrity gate never ran, so nothing stands.

    ADDED 2026-08-08 after an adversarial pass reproduced the failure: the
    ledger's vocabulary was four literals while ``reverify_falsifier`` emits
    five, so the wiring this module prescribes would have raised ValueError
    inside the round loop the first time a falsifier reached for the scoring
    key — killing the run at precisely the moment the integrity gate did its
    job, and blaming a wiring fault that did not exist.

    The routing is the load-bearing half: a refusal must sit with ERROR and
    UNTOOLABLE, never with REFUTED. A key-reading falsifier recorded as a
    survival would enter "this claim was tested and stood" for a test the
    harness deliberately refused to run.
    """
    verdict = reverify_falsifier(KEY_READING_FALSIFIER)
    assert verdict == "INTEGRITY_VIOLATION", (
        "precondition: the integrity gate must refuse a falsifier that opens "
        "the answer key")

    led = _ledger()
    row = _record(led, falsifier_code=KEY_READING_FALSIFIER,
                  runner_verdict=verdict, severity=0.9)

    assert row is None, "a refused falsifier is not a survival"
    assert led.entries == []
    assert led.standing() == []
    # ...but it IS counted, or the denominator hides a compromised measurement.
    assert led.observations == 1
    assert led.verdict_tally["INTEGRITY_VIOLATION"] == 1
    # ...and it confirms nothing: a genuine later survival is born standing.
    later = _record(led, round_idx=6)
    assert later.still_standing is True

    section = led.report_section()
    assert section["rows_recorded"] == 1
    joined = " ".join(section["alarms"])
    assert "INTEGRITY VIOLATIONS" in joined, "a refusal must never be quiet"
    assert "compromised measurement" in joined
    assert "INTEGRITY_VIOLATION" in section["verdict_semantics"]


def test_the_refusal_literal_matches_the_re_verifiers_own_constant():
    """The duplicated literal is pinned to its source, like the threshold is."""
    from bench.falsifier_verify import INTEGRITY_VIOLATION

    from bench.evidence import VERDICT_INTEGRITY_VIOLATION

    assert VERDICT_INTEGRITY_VIOLATION == INTEGRITY_VIOLATION
    assert INTEGRITY_VIOLATION in KNOWN_VERDICTS


# ── The governing failure mode: an absence must not render as a success ──────

def test_never_invoked_is_not_reported_as_zero_survivals():
    """The gap this ledger closes must not be recreated one level up.

    An un-fed ledger reporting a serene "0 claims survived" would be exactly
    the absence-as-result problem the ledger exists to remove.
    """
    led = _ledger()
    section = led.report_section()

    assert section["status"] == "NEVER_INVOKED"
    assert section["falsifier_verdicts_observed"] == 0
    assert section["alarms"], "an un-fed ledger must raise an alarm, not stay quiet"
    joined = " ".join(section["alarms"])
    assert "NEVER INVOKED" in joined
    assert "WIRING FAULT" in joined


def test_ran_but_nothing_survived_is_distinguishable_from_never_invoked():
    """"40 falsifiers fired" and "nothing was measured" are opposite results."""
    led = _ledger()
    for i in range(3):
        _record(led, finding_id=f"C{i:04d}",
                falsifier_code=REAL_DEFECT_FALSIFIER, runner_verdict="CONFIRMED")

    section = led.report_section()
    assert section["status"] == "ACTIVE"
    assert section["rows_recorded"] == 0
    assert section["falsifier_verdicts_observed"] == 3
    joined = " ".join(section["alarms"])
    assert "NO SURVIVALS" in joined
    assert "NEVER INVOKED" not in joined


def test_unknown_verdict_raises_rather_than_being_silently_dropped():
    """A dropped verdict corrupts the denominator silently — the house defect."""
    led = _ledger()
    for bad in ("PASSED", "ok", "TRUE", "VERIFIED"):
        with pytest.raises(ValueError, match="unrecognised verdict"):
            _record(led, runner_verdict=bad)
    assert led.observations == 0, "a rejected verdict must not be tallied"


def test_empty_verdict_names_the_likely_miswiring():
    """`falsifier_verdict` defaults to "" on findings the gate never re-ran."""
    led = _ledger()
    with pytest.raises(ValueError) as exc:
        _record(led, runner_verdict="")
    assert "denominator" in str(exc.value)


def test_refuted_with_no_falsifier_is_an_impossible_pairing_and_raises():
    """reverify_falsifier returns UNTOOLABLE when there is nothing to run, so a
    REFUTED with empty code means the caller crossed its arguments. Recording it
    would enter 'a claim survived a test' where no test exists."""
    led = _ledger()
    with pytest.raises(ValueError, match="REFUTED with no falsifier"):
        _record(led, falsifier_code="   ")
    assert led.entries == []


def test_missing_claim_text_is_recorded_with_a_sentinel_not_raised():
    """Model output can be malformed; that must not kill a live run.

    But nor may it render as a well-formed survival — the row confesses.
    """
    led = _ledger()
    row = _record(led, claim_under_test="")

    assert row is not None, "dropping it would under-count survivals silently"
    assert row.malformed is True
    assert row.claim_under_test == MISSING_CLAIM_SENTINEL
    section = led.report_section()
    assert section["malformed_rows"] == 1
    assert any("MALFORMED ROWS" in a for a in section["alarms"])


# ── Supersession: a stale clean row is a confident wrong answer ──────────────

def test_a_later_demonstration_overturns_an_earlier_survival():
    """Round 2's weak falsifier cleared it; round 7's good one fired.

    The survival row is retained (it is historically true that the round-2
    falsifier did not fire) but the claim no longer stands, and the overturn is
    alarmed — it is direct evidence a falsifier in this run was too weak.
    """
    led = _ledger()
    row = _record(led, round_idx=2)
    assert row.still_standing is True

    led.record(
        finding_id="C0042",
        claim_under_test="Section 3 asserts the decay constant is 0.30",
        falsifier_code=REAL_DEFECT_FALSIFIER,
        authored_by="Codex-SIM",
        runner_verdict="CONFIRMED",
        round_idx=7,
    )

    assert row.still_standing is False
    assert row.overturned_at_round == 7
    assert led.standing() == []
    assert led.overturned() == [row]
    assert led.entries == [row], "the historical row must never be deleted"
    assert led.distinct_claims_standing() == []
    assert any("OVERTURNED" in a for a in led.report_section()["alarms"])


def test_a_survival_after_a_demonstration_is_born_overturned():
    """The known false-REFUTED shape: a broken falsifier exiting 0 on a finding
    already demonstrated to be a real defect. It must not read as new evidence
    that the claim stands."""
    led = _ledger()
    _record(led, falsifier_code=REAL_DEFECT_FALSIFIER,
            runner_verdict="CONFIRMED", round_idx=3)
    row = _record(led, round_idx=9)

    assert row.still_standing is False
    assert row.overturned_at_round == 3
    assert led.standing() == []


def test_overturn_is_keyed_per_finding_and_does_not_leak():
    led = _ledger()
    a = _record(led, finding_id="C0001", round_idx=1)
    b = _record(led, finding_id="C0002", round_idx=1)
    led.record(finding_id="C0001", claim_under_test="x",
               falsifier_code=REAL_DEFECT_FALSIFIER, authored_by="m",
               runner_verdict="CONFIRMED", round_idx=5)

    assert a.still_standing is False
    assert b.still_standing is True
    assert led.distinct_claims_standing() == ["C0002"]


# ── Wording: no reader may take this for proof ───────────────────────────────

def test_no_field_or_key_claims_the_thing_was_proven():
    """The ledger's own vocabulary must not overstate the evidence.

    Checked on KEY NAMES and row FIELD NAMES only — the prose caveats
    legitimately contain phrases like "verified true" in order to forbid them.
    """
    forbidden = ("verified_true", "confirmed_true", "proven", "proof_that",
                 "validated", "claim_is_true", "correct")
    led = _ledger()
    _record(led)
    section = led.report_section()

    for key in section:
        assert not any(f in key.lower() for f in forbidden), \
            f"report key {key!r} overstates the evidence"
    for key in section["rows"][0]:
        assert not any(f in key.lower() for f in forbidden), \
            f"row field {key!r} overstates the evidence"


def test_the_caveat_travels_with_the_numbers():
    """A consumer reading only the JSON must not get a count without the caveat."""
    led = _ledger()
    _record(led)
    section = led.report_section()

    assert section["meaning"] == SURVIVAL_MEANING
    assert section["not_proof_of_truth"] is True
    assert "NOT proof the claim is true" in section["meaning"]
    assert "not a demonstration of absence" in section["meaning"]
    # It survives serialisation into the run report.
    assert "NOT proof the claim is true" in json.dumps(section)


def test_the_ledgers_own_blind_spot_is_stated_in_the_report():
    """A falsifier can be valid, runnable code and still test nothing.

    The discrimination control catches the case where such a falsifier FIRES for
    an unrelated reason. The mirror case — going QUIET for an unrelated reason —
    is this ledger's blind spot and it cannot detect it, so it must say so where
    the numbers are read rather than leave it implicit.
    """
    from bench.evidence import DISCRIMINATION_LIMITATION

    led = _ledger()
    row = _record(led)
    section = led.report_section()

    assert section["discrimination_limitation"] == DISCRIMINATION_LIMITATION
    assert "does NOT establish" in section["discrimination_limitation"]
    # The escape hatch the limitation points to must actually be there: the full
    # falsifier text and its digest, on every row, for inspection.
    assert section["rows"][0]["falsifier_code"] == row.falsifier_code
    assert section["rows"][0]["falsifier_sha256"].startswith("sha256:")


def test_critical_severity_survivals_are_flagged_as_weak_evidence():
    """Exp 42 measured 2 of 3 clean-exit criticals to be FALSE. A critical row
    is a prompt for human review, not a clearance."""
    led = _ledger()
    weak = _record(led, finding_id="C0001", severity=0.9)
    ordinary = _record(led, finding_id="C0002", severity=0.4)

    assert weak.is_critical is True
    assert ordinary.is_critical is False
    assert led.weak_evidence() == [weak]
    section = led.report_section()
    assert section["weak_evidence_standing_rows"] == 1
    joined = " ".join(section["alarms"])
    assert "WEAK EVIDENCE" in joined
    assert "2 of 3" in joined


def test_the_weak_evidence_band_is_inclusive_at_the_threshold():
    """Severity exactly 0.7 IS critical, matching the runner's ``>=``.

    ADDED 2026-08-08: a mutation flipping the ledger's ``>=`` to ``>`` survived
    the suite, because the existing cases probe 0.9 and 0.4 and never the line
    itself. Under that mutation a survival at exactly the threshold — a real
    critical, and the band where 2 of 3 clean exits were measured false — would
    silently lose its WEAK EVIDENCE alarm.
    """
    from bench.reference_runner_v2 import CRITICAL_SEVERITY_THRESHOLD

    led = _ledger()
    on_line = _record(led, finding_id="C0001", severity=CRITICAL_SEVERITY_THRESHOLD)
    just_under = _record(led, finding_id="C0002",
                         severity=CRITICAL_SEVERITY_THRESHOLD - 0.01)

    assert on_line.is_critical is True, "the threshold is inclusive in the runner"
    assert just_under.is_critical is False
    assert led.weak_evidence() == [on_line]
    assert any("WEAK EVIDENCE" in a for a in led.report_section()["alarms"])


def test_critical_threshold_matches_the_runner():
    """evidence.py stays a leaf module, so the threshold is duplicated rather
    than imported. This pins the duplicate against drift."""
    from bench.reference_runner_v2 import CRITICAL_SEVERITY_THRESHOLD

    assert LEDGER_CRITICAL_SEVERITY == CRITICAL_SEVERITY_THRESHOLD


# ── Isolation from the convergence gate ──────────────────────────────────────

def test_the_convergence_gate_does_not_reference_the_ledger():
    """The founder was explicit: this must not block the convergence gate.

    Scoped to the gate function itself, so wiring `record()` elsewhere in the
    runner (the intended integration) does not falsely trip this test.
    """
    from bench.reference_runner_v2 import _check_gamma_alt_convergence

    src = inspect.getsource(_check_gamma_alt_convergence)
    for token in ("SurvivedFalsificationLedger", "survived_falsification",
                  "SurvivedTest", "ledger"):
        assert token not in src, (
            f"the two-sided gate references {token!r} — the survived-"
            f"falsification ledger must never be a convergence input"
        )


def test_report_section_exposes_nothing_the_gate_consumes():
    """No key here collides with a gate input, so a future wiring cannot feed
    the gate from this section by accident."""
    from bench.reference_runner_v2 import _check_gamma_alt_convergence

    gate_inputs = set(
        inspect.signature(_check_gamma_alt_convergence).parameters
    )
    led = _ledger()
    _record(led)
    assert gate_inputs.isdisjoint(set(led.report_section()))


def test_recording_does_not_mutate_its_inputs():
    """A mutation of a finding dict could perturb downstream gate arithmetic."""
    finding = {
        "canonical_id": "C0042",
        "description": "Section 3 asserts the decay constant is 0.30",
        "falsifier_code": TRUE_CLAIM_FALSIFIER,
        "source_model": "DeepSeek-SIM",
        "falsifier_verdict": "REFUTED",
        "severity": 0.8,
        "status": "OPEN",
    }
    before = copy.deepcopy(finding)

    led = _ledger()
    led.record(
        finding_id=finding["canonical_id"],
        claim_under_test=finding["description"],
        falsifier_code=finding["falsifier_code"],
        authored_by=finding["source_model"],
        runner_verdict=finding["falsifier_verdict"],
        round_idx=4,
        severity=finding["severity"],
    )
    assert finding == before


def test_ledger_has_no_blocking_or_gating_api():
    """Nothing on the ledger looks like something a gate would call."""
    banned = ("block", "gate", "converge", "veto", "halt", "pass_condition")
    for name in dir(SurvivedFalsificationLedger):
        if name.startswith("_"):
            continue
        assert not any(b in name.lower() for b in banned), \
            f"{name!r} reads like a gate input; the ledger records, it does not gate"


# ── Queryability and integrity ───────────────────────────────────────────────

def test_the_ledger_is_queryable_on_every_recorded_dimension():
    led = _ledger()
    a = _record(led, finding_id="C0001", authored_by="CC2-SIM", round_idx=1)
    b = _record(led, finding_id="C0002", authored_by="Gemini-SIM", round_idx=1)
    c = _record(led, finding_id="C0003", authored_by="CC2-SIM", round_idx=2)

    assert led.by_finding("C0002") == [b]
    assert led.by_round(1) == [a, b]
    assert led.by_model("CC2-SIM") == [a, c]
    assert led.distinct_claims_standing() == ["C0001", "C0002", "C0003"]


def test_row_digest_identifies_the_falsifier_that_actually_ran():
    led = _ledger()
    row = _record(led)
    expected = hashlib.sha256(TRUE_CLAIM_FALSIFIER.encode("utf-8")).hexdigest()

    assert row.falsifier_sha256 == "sha256:" + expected
    assert row.to_dict()["falsifier_sha256"] == "sha256:" + expected


def test_entries_property_cannot_be_used_to_mutate_the_ledger():
    led = _ledger()
    _record(led)
    led.entries.clear()
    assert len(led) == 1


def test_recorded_timestamp_is_named_for_what_it_measures():
    """A stamp that records the save rather than the event is a known failure
    mode here. The field is `recorded_at_utc` and must not be read as the
    falsifier's execution time."""
    fields = {f for f in SurvivedTest.__dataclass_fields__}
    assert "recorded_at_utc" in fields
    assert not any(f in fields for f in ("tested_at", "last_updated", "timestamp"))
    led = _ledger()
    assert _record(led).recorded_at_utc


@pytest.mark.parametrize("bad_round", [-1, "3", 2.5, True, None])
def test_bad_round_index_raises(bad_round):
    led = _ledger()
    with pytest.raises(ValueError, match="round_idx"):
        _record(led, round_idx=bad_round)


def test_missing_finding_id_raises():
    led = _ledger()
    with pytest.raises(ValueError, match="finding_id is required"):
        _record(led, finding_id="  ")


def test_known_verdicts_match_the_reverifier_behaviour():
    """The ledger's accepted vocabulary must be exactly what the runner's
    re-execution primitive can actually return.

    Checked by RUNNING the re-verifier over one input of each shape rather than
    by reading its docstring — a prose contract can drift from the code, and it
    is the code the ledger is fed from.
    """
    produced = {
        reverify_falsifier(TRUE_CLAIM_FALSIFIER),
        reverify_falsifier(REAL_DEFECT_FALSIFIER),
        reverify_falsifier(BROKEN_FALSIFIER),
        reverify_falsifier(""),
        # The fifth shape. Omitting it is how this guard came to pass while the
        # drift it exists to catch was live in the tree: four probes can only
        # ever observe four literals, so a guard built from four probes asserts
        # its own blind spot. Every ADDITIONAL return path of reverify_falsifier
        # needs a probe here or this test is decorative.
        reverify_falsifier(KEY_READING_FALSIFIER),
    }
    assert produced == {"REFUTED", "CONFIRMED", "ERROR", "UNTOOLABLE",
                        "INTEGRITY_VIOLATION"}
    assert produced == set(KNOWN_VERDICTS), (
        "the ledger accepts a different vocabulary than the re-verifier emits; "
        "one of them has drifted"
    )
    # Every verdict the re-verifier can emit must be routable without raising.
    for verdict in produced:
        SurvivedFalsificationLedger().record(
            finding_id="C0001", claim_under_test="c",
            falsifier_code=TRUE_CLAIM_FALSIFIER, authored_by="m",
            runner_verdict=verdict, round_idx=0,
        )


def test_a_row_is_one_test_not_one_claim():
    """The runner re-runs every open finding's falsifier EVERY ROUND, so one
    claim surviving five rounds writes five rows. A headline count of claims
    must come from `standing_claims`, never from `standing_rows` — this is the
    most likely way a reader would over-state the result."""
    led = _ledger()
    for rnd in range(1, 6):
        _record(led, finding_id="C0042", round_idx=rnd)

    section = led.report_section()
    assert section["standing_rows"] == 5
    assert section["standing_claims"] == 1
    assert section["distinct_claims_standing"] == ["C0042"]
    assert "not one claim" in section["rows_note"]


def test_zero_plant_control_produces_a_body_of_evidence_not_an_absence():
    """The experiment this ledger was built for.

    Every claim in the target is true, so every falsifier runs clean. Under the
    old design the run produced nothing. It now produces a queryable positive
    record — while still not claiming any of it is proven.
    """
    led = SurvivedFalsificationLedger(experiment="exp53_zero_plant")
    for i in range(12):
        verdict = reverify_falsifier(TRUE_CLAIM_FALSIFIER)
        led.record(
            finding_id=f"C{i:04d}",
            claim_under_test=f"claim {i} of the zero-plant control document",
            falsifier_code=TRUE_CLAIM_FALSIFIER,
            authored_by=["CC2-SIM", "Codex-SIM", "Gemini-SIM"][i % 3],
            runner_verdict=verdict,
            round_idx=1 + i // 4,
            severity=0.5,
        )

    section = led.report_section()
    assert section["status"] == "ACTIVE"
    assert section["standing_rows"] == 12
    assert len(section["distinct_claims_standing"]) == 12
    assert section["overturned_rows"] == 0
    assert section["malformed_rows"] == 0
    # Nothing is wrong, so the only alarms permitted are none at all.
    assert section["alarms"] == []
    # And the result is still not a proof.
    assert section["not_proof_of_truth"] is True
