# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'what_is_a_proof_outside_code_b22_2026-10-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 026f2a0deacc1ec3f4c5439db9ad825cca0cc2a6726271373380b3d1e0ba8a32
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Step 4 for a PRINTED PROOF, and the polarity guard that keeps it out of severity.

WHAT THIS ADDS, AND WHY IT ADDS NO NEW VERDICT VOCABULARY.

The panel brief of 2026-10-30 asks for a harness step that re-verifies a model's
printed proof with the same tools the model used. Measured by execution before
anything was written here, four things were already true:

  1. `falsifier_verify.reverify_falsifier` ALREADY re-runs a model-authored
     script in a confined sandbox and decides the verdict itself. Executed
     against all five prose fixtures in `bench/tests/fixtures/stem/`, it
     returned CONFIRMED 5/5 on the pristine documents (structural SM-08,
     statistics ST-05, metrology CM-06, algorithms AL-03, numerical NA-05). So
     step 4 is not missing for the FINDING side, on prose, in five fields.

  2. `immune_agents._specialist_b_cell_dispatch` ALREADY runs the real STEM
     tools -- sympy, z3, pint, astropy, rdkit, Bio.Seq, statsmodels -- in a
     tools-equipped child interpreter, and is live in the current runner. But
     its input is `tf.extracted_claim`, a regex-scraped substring of a
     finding's `description`. It never reads the model's derivation and never
     reads the model's tool output, so it is a first-pass verification of a
     claim rather than a re-verification of a proof.

  3. `compute_sk` returns `NO_SCORE` on a prose target -- executed against
     `bench/tests/fixtures/stem/docs/MET-12-REF-01.md`: tristate `NO_SCORE`,
     sk 0.0, reason "S_k is defined over Python source". So the measure that
     decides whether a proposed REPAIR is admissible is silent exactly where a
     printed proof arrives. That is the hole.

  4. Routing a proof through the finding-side channel INVERTS it. A correct
     printed proof of MET-12's corrected CM-06 (0.1269 per cent, computed with
     pint + uncertainties, cross-checked in Wolfram Language) exits cleanly, so
     `reverify_falsifier` returns REFUTED, `spec_verification_factor` returns
     0.0 and `effective_severity` returns 0.0 against an asserted 0.85. A
     CORRECT proof annihilates the finding. The inverse is worse: a proof whose
     own arithmetic slips raises AssertionError, reads CONFIRMED, and scores the
     finding at FULL severity on the strength of the model's own mistake.

THE DERIVATION. A falsifier and a proof are the same artefact under opposite
terminal conventions. Re-runnability forces any such script to (i) open the
artefact by path, (ii) compute with installed tools, (iii) terminate with a
machine-readable outcome that depends on comparing (i) against (ii). A falsifier
adopts `failure => the defect is real`; a proof adopts `clean exit => the
asserted result holds`. They differ in one bit. So no new sandbox and no new
runner is needed -- only a declared polarity, and a landing place whose polarity
already matches.

That landing place exists. A proof is a REPAIR-side object, so its outcome
belongs in the S_k tristate, whose polarity is already `clean => good`:

    the proof's assertions all held   -> SK_ADMISSIBLE
    the proof's own assertions failed -> SK_REJECTED
    nothing supplied to re-run        -> SK_NO_SCORE
    untrusted run / integrity fault   -> SK_ESCALATE

Four cases, four pre-existing members, correct polarity, nothing coined. The
project's rule that an unverifiable claim escalates rather than being guessed at
is carried by `SK_ESCALATE`, which already means exactly that.

WHAT THIS DOES NOT DO, STATED PLAINLY. `verify_proof` decides whether the
model's own computation holds. It does NOT decide that the computation answers
the question the artefact asked. A proof can be internally correct and
substantively irrelevant, and this module cannot tell the difference -- see
`PROOF_VERIFIES_ARITHMETIC_NOT_RELEVANCE`, which is why `SK_ADMISSIBLE` from
here is repair-side evidence only and never on its own a finding verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from bench.falsifier_verify import reverify_falsifier
from bench.reference_runner_v3 import (
    SK_ADMISSIBLE,
    SK_ESCALATE,
    SK_NO_SCORE,
    SK_REJECTED,
)

#: The terminal convention a re-runnable verification script was written under.
#: `FALSIFIER_POLARITY` is the pre-existing default and the only one
#: `reverify_falsifier`'s own verdict strings may be read under.
FALSIFIER_POLARITY = "falsifier"
PROOF_POLARITY = "proof"

#: The boundary of what tool execution establishes. Carried on every ADMISSIBLE
#: result rather than living only in this module's prose, so the limitation
#: travels with the measurement.
PROOF_VERIFIES_ARITHMETIC_NOT_RELEVANCE = (
    "tool execution establishes that the proof's computation holds, not that "
    "the computation answers the question the artefact asked"
)


@dataclass(frozen=True)
class ProofResult:
    """A step-4 outcome, in the S_k tristate, with the raw run it came from."""

    tristate: str
    raw_verdict: str
    reason: str


def verify_proof(
    proof_code: str,
    repo_root: Optional[str] = None,
    timeout: int = 60,
    cwd: Optional[str] = None,
) -> ProofResult:
    """Re-run a printed proof and return an S_k-side tristate.

    The run itself is delegated to `reverify_falsifier`, deliberately and
    without modification, so every integrity control already built around that
    function applies here unchanged: the pre-run source scan for key material,
    the runtime audit-hook observer, the Wolfram refusal and the
    scratch-directory confinement. This function contributes the polarity
    normalisation and nothing else.
    """
    if not proof_code or not proof_code.strip():
        return ProofResult(
            SK_NO_SCORE, "UNTOOLABLE",
            "no proof was supplied, so there is nothing to re-run")

    raw = reverify_falsifier(proof_code, repo_root=repo_root,
                             timeout=timeout, cwd=cwd)

    if raw == "REFUTED":
        # Clean exit under proof polarity: every assertion the proof made held.
        return ProofResult(
            SK_ADMISSIBLE, raw,
            "the proof ran to a clean exit, so its own assertions held; "
            + PROOF_VERIFIES_ARITHMETIC_NOT_RELEVANCE)
    if raw == "CONFIRMED":
        # AssertionError / FALSIFIED under proof polarity: the model's OWN
        # proposed result does not hold. That is a rejected repair, and it is
        # NOT evidence that the artefact's claim is defective.
        return ProofResult(
            SK_REJECTED, raw,
            "the proof's own assertions failed, so the proposed result does "
            "not hold; this says nothing about the artefact's claim")
    if raw == "UNTOOLABLE":
        return ProofResult(
            SK_NO_SCORE, raw,
            "nothing was re-run, so no opinion was formed")
    # "ERROR" and INTEGRITY_VIOLATION both mean the run cannot be trusted to
    # decide. SK_ESCALATE already carries exactly that action.
    return ProofResult(
        SK_ESCALATE, raw,
        f"the re-run returned {raw}, which cannot decide the proposed result")


def proof_polarity_collision(entry: dict) -> Optional[str]:
    """Why this entry's verdict must not be read as a finding verdict, or None.

    Returns a reason string when the entry declares proof polarity, because a
    proof-polarity outcome carries no finding-side information and the strings
    `reverify_falsifier` returns under it collide with the finding vocabulary in
    the INVERTING direction. Returns None otherwise, which is every entry
    written before this module existed -- so the guard is silent on the whole
    existing archive.
    """
    declared = str(entry.get("verification_polarity") or "").strip().lower()
    if declared == PROOF_POLARITY:
        return (
            "this entry's verdict was produced under proof polarity, where a "
            "clean exit means the proof HELD; read as a falsifier verdict it "
            "would score 0.0 for a correct proof and 1.0 for a mistaken one")
    return None
