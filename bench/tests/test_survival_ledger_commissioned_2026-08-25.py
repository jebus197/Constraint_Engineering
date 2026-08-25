"""Commissioning test for I33, the survived-falsification ledger.

WHY. On 2026-08-22 the instrument inventory measured this component as NOT
commissioned, with the note: it has a full test suite and nothing in the runner
calls it. A tested component that nothing invokes is shelved, not commissioned.
Founder ruling that day was to WIRE it rather than withdraw the claim it exists.

The wiring landed. But wired is not working, and that distinction is the one this
project keeps rediscovering — the falsifier gate was wired for months while
returning CONFIRMED for a test that only printed the word FALSIFIED. So this file
exercises the component rather than checking it is imported.

WHAT THE LEDGER IS FOR. It records that a claim was TESTED AND STOOD. Without it, a
clean review produces an ABSENCE — no findings — that is indistinguishable from a
dispatch failure that produced no findings for a quite different reason. The
denominator is the point: "forty falsifiers ran and every one fired" and "the gate
was never invoked" are opposite results that look identical in a report with no
ledger.

WHAT IS ASSERTED: it takes the verdict spread the gate really produces, writes rows
only for the verdict that means a claim survived, and renders a report section whose
emptiness is distinguishable from its absence. Its caveats are asserted too, because
a ledger of survived tests is the single most over-readable artefact in this system —
surviving a test is not proof of truth.
"""
import inspect

import pytest

from bench.evidence import SurvivedFalsificationLedger


def _record(led, finding_id, verdict, round_idx=1):
    """Drive the real interface. Signature discovered, not assumed."""
    return led.record(
        finding_id=finding_id,
        claim_under_test=f"claim behind {finding_id}",
        falsifier_code="assert True  # placeholder falsifier body",
        authored_by="SIM-A",
        runner_verdict=verdict,
        round_idx=round_idx,
        severity=0.5,
    )


class TestLedgerFunctions:
    def test_a_refuted_verdict_writes_a_row(self):
        """REFUTED means the falsifier ran and failed to break the claim: the claim
        survived. That is the one verdict that earns a row."""
        led = SurvivedFalsificationLedger(experiment="commissioning")
        out = _record(led, "C001", "REFUTED")
        assert out is not None, "a REFUTED verdict produced no ledger row"

    def test_a_confirmed_verdict_writes_no_row(self):
        """KNOWN-BAD: CONFIRMED means the claim was broken. It did NOT survive and
        must not appear in a ledger of survivals."""
        led = SurvivedFalsificationLedger(experiment="commissioning")
        out = _record(led, "C002", "CONFIRMED")
        assert out is None, (
            "CONFIRMED wrote a survival row — the ledger would report broken claims "
            "as claims that stood, which inverts its entire meaning"
        )

    def test_it_discriminates_between_the_two(self):
        """The commissioning assertion proper."""
        led = SurvivedFalsificationLedger(experiment="commissioning")
        survived = _record(led, "C003", "REFUTED")
        broken = _record(led, "C004", "CONFIRMED")
        assert (survived is None) != (broken is None), (
            "ledger answers the same way for a claim that stood and one that broke"
        )

    def test_error_and_untoolable_do_not_count_as_survival(self):
        """An instrument that crashed is not evidence in either direction. If these
        wrote rows, a run whose tooling failed would report as a run whose claims
        all stood — the reassuring-direction failure this project keeps finding."""
        led = SurvivedFalsificationLedger(experiment="commissioning")
        for verdict in ("ERROR", "UNTOOLABLE"):
            assert _record(led, f"C-{verdict}", verdict) is None, (
                f"{verdict} was recorded as a survival; equipment failure would read "
                "as corroboration"
            )

    def test_the_denominator_is_kept(self):
        """The reason the ledger exists: an empty section must be able to say WHY it
        is empty. That requires counting everything shown to it, not only survivals."""
        led = SurvivedFalsificationLedger(experiment="commissioning")
        for i, v in enumerate(["CONFIRMED", "REFUTED", "ERROR", "CONFIRMED"]):
            _record(led, f"D{i}", v)
        tally = getattr(led, "verdict_tally", None)
        assert tally, "no verdict tally kept — an empty ledger cannot explain itself"
        assert sum(dict(tally).values()) == 4, (
            f"ledger saw 4 verdicts but its tally totals {sum(dict(tally).values())}"
        )


class TestLedgerReportsHonestly:
    def test_report_section_carries_its_own_caveats(self):
        """A list of claims that survived testing is the most over-readable artefact
        in this system. The report must say so itself rather than relying on a
        reader's restraint."""
        rep = SurvivedFalsificationLedger(experiment="commissioning").report_section()
        for key in ("meaning", "not_proof_of_truth"):
            assert key in rep, f"report section omits its {key!r} caveat"
        assert rep["not_proof_of_truth"], "the not-proof-of-truth caveat is empty"

    def test_an_empty_ledger_is_distinguishable_from_an_absent_one(self):
        rep = SurvivedFalsificationLedger(experiment="commissioning").report_section()
        assert isinstance(rep, dict) and rep, (
            "an unused ledger renders as nothing, so 'never invoked' and 'invoked and "
            "found no survivals' would be indistinguishable in a report"
        )


class TestLedgerIsActuallyWiredIntoTheRunner:
    def test_the_gate_accepts_a_ledger_argument(self):
        """Pins the T03 wiring of 2026-08-22. If someone removes the parameter, the
        component silently returns to being shelved."""
        import bench.reference_runner_v2 as rr
        sig = inspect.signature(rr.apply_falsifier_verdicts)
        assert "ledger" in sig.parameters, (
            "apply_falsifier_verdicts no longer takes a ledger — I33 is shelved again"
        )

    def test_the_runner_constructs_and_attaches_one(self):
        import pathlib
        src = pathlib.Path(__file__).resolve().parents[1] / "reference_runner_v2.py"
        text = src.read_text(encoding="utf-8", errors="replace")
        assert "attach_survival_ledger" in text, "no attach point in the runner"
        assert "ledger=survival_ledger" in text, (
            "the runner constructs a ledger but does not pass it to the gate"
        )
