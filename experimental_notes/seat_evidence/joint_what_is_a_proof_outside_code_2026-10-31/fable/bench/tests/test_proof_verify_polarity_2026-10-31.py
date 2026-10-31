# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_what_is_a_proof_outside_code_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3c392e4cb15cc03e9e02a0f642bd6cb6c6874e44e0882f3a3bae58915b139a1c
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Executes `bench.proof_verify` and the polarity guard it is reached by.

Every assertion here runs the real functions. No source-text assertions.
"""
import pytest

from bench.proof_verify import (
    PROOF_POLARITY,
    PROOF_VERIFIES_ARITHMETIC_NOT_RELEVANCE,
    proof_polarity_collision,
    verify_proof,
)
from bench.reference_runner_v3 import (
    SK_ADMISSIBLE,
    SK_ESCALATE,
    SK_NO_SCORE,
    SK_REJECTED,
    effective_severity,
    spec_verification_factor,
    wire_module_mirrors,
)

# A real printed proof of MET-12-REF-01's CORRECTED CM-06, computed with pint
# and uncertainties. The document quotes 0.165 per cent, which is the LINEAR sum
# of the three relative components; the root sum of squares CM-06 says it is
# using is 0.1269 per cent. Cross-checked in Wolfram Language: RSS 0.126922,
# linear 0.164694.
_CHEMISTRY_PROOF = '''
import pint
from uncertainties import ufloat
ureg = pint.UnitRegistry(); Q = ureg.Quantity
c = (Q(ufloat(0.5106, 0.0002), "g") / Q(ufloat(204.22, 0.01), "g/mol")
     / Q(ufloat(24.87, 0.03), "mL")).to("mol/L")
rel = c.magnitude.std_dev / c.magnitude.nominal_value
assert str(c.units) == "mole / liter", c.units
assert abs(rel * 100 - 0.1269) < 5e-4, rel * 100
print("PROOF HOLDS: u_c(c)/c = %.4f per cent" % (rel * 100))
'''

# The same proof with a wrong proposed figure: the model's own assertion fires.
_CHEMISTRY_PROOF_WRONG = _CHEMISTRY_PROOF.replace("0.1269", "0.1650")


def test_a_correct_chemistry_proof_is_admissible():
    r = verify_proof(_CHEMISTRY_PROOF, repo_root=".")
    assert r.tristate == SK_ADMISSIBLE, (r.tristate, r.raw_verdict, r.reason)
    # The raw run is kept, and it is the INVERTING string. This is the whole
    # point of the module: REFUTED from the sandbox means the proof HELD.
    assert r.raw_verdict == "REFUTED", r.raw_verdict
    assert PROOF_VERIFIES_ARITHMETIC_NOT_RELEVANCE in r.reason


def test_a_proof_whose_own_assertion_fires_is_rejected_not_confirmed():
    r = verify_proof(_CHEMISTRY_PROOF_WRONG, repo_root=".")
    assert r.tristate == SK_REJECTED, (r.tristate, r.raw_verdict, r.reason)
    assert r.raw_verdict == "CONFIRMED", r.raw_verdict
    assert "says nothing about the artefact" in r.reason


@pytest.mark.parametrize("empty", ["", "   ", "\n\t"])
def test_nothing_to_run_is_no_score_not_a_verdict(empty):
    r = verify_proof(empty, repo_root=".")
    assert r.tristate == SK_NO_SCORE, r


def test_a_broken_proof_escalates():
    r = verify_proof("import a_module_that_does_not_exist_anywhere\n",
                     repo_root=".")
    assert r.tristate == SK_ESCALATE, (r.tristate, r.raw_verdict)


def test_the_guard_is_reached_by_spec_verification_factor():
    class _Cfg:
        severity_spec_enabled = True

    wire_module_mirrors(_Cfg())
    held = {"severity": 0.85, "falsifier_verdict": "REFUTED",
            "verification_polarity": PROOF_POLARITY}
    failed = {"severity": 0.85, "falsifier_verdict": "CONFIRMED",
              "verification_polarity": PROOF_POLARITY}
    # Neither direction may reach an opinion.
    assert spec_verification_factor(held) == 0.5
    assert spec_verification_factor(failed) == 0.5
    # A correct proof no longer annihilates the finding.
    assert effective_severity(held) == pytest.approx(0.425)
    # And a mistaken proof no longer awards full severity.
    assert effective_severity(failed) == pytest.approx(0.425)


def test_the_default_path_is_unchanged_for_every_existing_entry():
    class _Cfg:
        severity_spec_enabled = True

    wire_module_mirrors(_Cfg())
    assert proof_polarity_collision({"falsifier_verdict": "CONFIRMED"}) is None
    assert spec_verification_factor({"falsifier_verdict": "CONFIRMED"}) == 1.0
    assert spec_verification_factor({"falsifier_verdict": "REFUTED"}) == 0.0
    assert spec_verification_factor({"falsifier_verdict": "ERROR"}) == 0.5
    assert spec_verification_factor({}) == 0.5
    # An explicit falsifier declaration is also silent.
    assert proof_polarity_collision(
        {"falsifier_verdict": "REFUTED",
         "verification_polarity": "falsifier"}) is None
    assert spec_verification_factor(
        {"falsifier_verdict": "REFUTED",
         "verification_polarity": "falsifier"}) == 0.0
