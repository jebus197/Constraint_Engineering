"""The proof verifier is in the tree, and a proof that asserts nothing is refused.

HIS RULING, 2026-11-01, verbatim: *"Fix it and fold it back as you suggest."*
Taken from the copy preserved under panel seat `fable` in the joint round of
2026-10-31; authored by seat `cc2` in the blind round of 2026-10-30 -- see the
correction in `bench/proof_verify.py`. Tested under
analysis, the 5-step cycle and the tools before folding as his standing rule
requires, where it passed 7 of 8.

THE 1 FAILURE, AND WHY IT MATTERED. Under PROOF polarity a clean exit is what
grants admissibility — the opposite of falsifier polarity, where a clean exit
means the defect is absent. So a proof with NO ASSERTION AT ALL exits cleanly and
was reported ADMISSIBLE: a model could print 1 harmless line and have its repair
admitted. The seat's own guard caught the empty string and not `print("ok")`.

THE SENTENCE IS WHAT GIVES IT AWAY. The branch writes "its own assertions held",
which is VACUOUSLY TRUE of a proof with no assertions. A verdict whose
justification is vacuously true is the shape this project keeps meeting.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench import proof_verify as PV  # noqa: E402


class TestItIsInTheTreeAtAll:
    def test_the_module_is_importable_from_the_real_package(self):
        """It lived only in a sandbox until 2026-11-01. The allowlist entry
        recording it as deliberately absent is removed, so the citation check
        now holds the path like any other."""
        assert pathlib.Path(PV.__file__).resolve().is_relative_to(REPO / "bench")

    def test_it_declares_both_polarities_and_they_differ(self):
        assert PV.FALSIFIER_POLARITY != PV.PROOF_POLARITY

    def test_the_boundary_of_what_execution_establishes_travels_with_it(self):
        """The limitation is carried on the result, not left in prose."""
        assert "not that" in PV.PROOF_VERIFIES_ARITHMETIC_NOT_RELEVANCE


class TestAProofMustAssertSomething:
    @pytest.mark.parametrize("code,expected", [
        ("assert 1 + 1 == 2", True),
        ("raise SystemExit(1)", True),
        ('print("FALSIFIED")', True),
        ('print("ok")', False),
        ("import bench.routing", False),
        ("", False),
        ("   \n  ", False),
        ("def f(:", False),
    ])
    def test_the_predicate(self, code, expected):
        assert PV.asserts_something(code) is expected, code

    def test_an_import_alone_is_NOT_enough_and_that_is_deliberate(self):
        """The runner's `_runnable` accepts an import, because it decides
        whether a fenced block is code worth running. This decides whether a
        CLEAN EXIT means anything, and a proof that only imports has claimed
        nothing. Reusing the wrong predicate would have reintroduced the hole."""
        assert not PV.asserts_something("from bench.routing import ladder")

    def test_unparseable_text_fails_closed(self):
        """The safe direction: it becomes untoolable rather than admissible."""
        assert not PV.asserts_something("this is not python at all (")


class TestTheHoleIsClosedAtTheDecisionPoint:
    def test_an_assertionless_proof_is_not_admissible(self, monkeypatch):
        """THE DEFECT ITSELF, driven through `verify_proof`. The underlying
        re-run is stubbed to its CLEAN-EXIT verdict, because the point is not
        whether the sandbox works — it does — but what this module concludes
        from a clean exit."""
        monkeypatch.setattr(PV, "reverify_falsifier",
                            lambda *a, **k: "REFUTED")
        r = PV.verify_proof('print("ok")')
        assert r.tristate == PV.SK_NO_SCORE, r
        assert "asserts nothing" in r.reason

    def test_a_real_proof_IS_admissible(self, monkeypatch):
        """ANTI-VACUITY. If the fix refused everything the test above would
        pass for the wrong reason and the module would be useless."""
        monkeypatch.setattr(PV, "reverify_falsifier",
                            lambda *a, **k: "REFUTED")
        r = PV.verify_proof("assert 2 ** 10 == 1024")
        assert r.tristate == PV.SK_ADMISSIBLE, r

    def test_a_failing_proof_is_rejected_not_treated_as_a_finding(self, monkeypatch):
        """The polarity guard, which is the module's whole reason for existing:
        a proof whose own assertions fail says nothing about the artefact."""
        monkeypatch.setattr(PV, "reverify_falsifier",
                            lambda *a, **k: "CONFIRMED")
        r = PV.verify_proof("assert 1 == 2")
        assert r.tristate == PV.SK_REJECTED, r
        assert "says nothing about the artefact" in r.reason

    def test_an_untrustworthy_run_escalates_rather_than_deciding(self, monkeypatch):
        monkeypatch.setattr(PV, "reverify_falsifier", lambda *a, **k: "ERROR")
        r = PV.verify_proof("assert True")
        assert r.tristate == PV.SK_ESCALATE, r

    def test_an_empty_proof_is_still_refused(self, monkeypatch):
        """The seat's original guard, kept rather than replaced."""
        monkeypatch.setattr(PV, "reverify_falsifier", lambda *a, **k: "REFUTED")
        assert PV.verify_proof("").tristate == PV.SK_NO_SCORE
