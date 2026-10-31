# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'what_is_a_proof_outside_code_b22_2026-10-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2a870892c6f09d42c069b2a951fd1a710f9e9b2287bb48e9e0eb964bc410959f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""FALSIFIER: a proof-polarity verdict inverts `spec_verification_factor`.

Imports the REAL target module. Raises AssertionError -- and prints FALSIFIED --
if and only if the defect is present: a verdict produced under proof polarity is
read as a finding verdict, so a clean exit (the proof HELD) scores V=0.0 and
annihilates the finding, while a fired assertion (the proof did NOT hold) scores
V=1.0 and awards full severity on the strength of the model's own mistake.

Exits cleanly if the polarity guard is in place.
"""
import sys
sys.path.insert(0, __file__.rsplit("/bench/", 1)[0])

from bench.reference_runner_v3 import (  # the REAL target, not a copy
    effective_severity,
    spec_verification_factor,
    wire_module_mirrors,
)


class _Cfg:
    severity_spec_enabled = True


wire_module_mirrors(_Cfg())

ASSERTED = 0.85

# A model printed a CORRECT proof. Under proof polarity a clean exit means the
# proof HELD; `reverify_falsifier` returns the string "REFUTED" for a clean exit.
held = {"severity": ASSERTED, "falsifier_verdict": "REFUTED",
        "verification_polarity": "proof"}
# A model printed a proof whose own assertion fired, i.e. its proposed result
# does NOT hold. `reverify_falsifier` returns "CONFIRMED" for a fired assertion.
failed = {"severity": ASSERTED, "falsifier_verdict": "CONFIRMED",
          "verification_polarity": "proof"}

v_held = spec_verification_factor(held)
v_failed = spec_verification_factor(failed)
s_held = effective_severity(held)
s_failed = effective_severity(failed)

bad = []
if v_held == 0.0:
    bad.append(f"a proof that HELD scored V={v_held} and annihilated the "
               f"finding: effective_severity {ASSERTED} -> {s_held}")
if v_failed == 1.0:
    bad.append(f"a proof that did NOT hold scored V={v_failed} and took full "
               f"severity: effective_severity {ASSERTED} -> {s_failed}")
if v_held < v_failed:
    bad.append(f"the ordering is inverted: V(proof held)={v_held} < "
               f"V(proof failed)={v_failed}")

if bad:
    print("FALSIFIED")
    for line in bad:
        print("  " + line)
    raise AssertionError("proof-polarity verdict inverts spec_verification_factor: "
                         + "; ".join(bad))

print("NOT FALSIFIED: proof polarity is not read as a finding verdict "
      f"(V held={v_held}, V failed={v_failed}, both the no-opinion value)")
