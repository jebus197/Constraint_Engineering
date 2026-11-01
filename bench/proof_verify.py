"""Step 4 for a PRINTED PROOF, and the polarity guard that keeps it out of severity.

FOLDED BACK 2026-11-01 ON HIS RULING, verbatim: *"Fix it and fold it back as you
suggest."* Written by panel seat `fable` in the joint round of 2026-10-31 and
preserved under `experimental_notes/seat_evidence/`; tested under analysis, the
5-step cycle and the tools before folding, as his standing rule requires, where
it passed 7 of 8 with a 95 per cent interval of 0.529112 to 0.977583.

THE 1 FAILURE IS FIXED HERE AND IT IS NAMED RATHER THAN QUIETLY PATCHED. A proof
with NO ASSERTION AT ALL exits cleanly, and a clean exit is exactly what grants
admissibility under proof polarity -- so a model could print 1 harmless line and
have its repair admitted. The seat's own empty-string guard catches the empty
string and not `print("ok")`.

WHY A NARROW PREDICATE RATHER THAN THE EXISTING ONE. `reference_runner_v3` has
`_runnable`, which accepts an `Import` or `ImportFrom` as evidence that a block
is real code. That is right for deciding whether a fenced block is a candidate
falsifier and WRONG here: a proof that only imports something has asserted
nothing, and under proof polarity its clean exit would be read as every
assertion holding. So this module requires an `Assert` or a `Raise`, and says
why, rather than reusing a predicate written for a different question.

ADDITIVE, AND IT ONLY NARROWS. Nothing admissible for a stated reason becomes
inadmissible; the single behaviour change is that a proof asserting nothing is
now UNTOOLABLE rather than ADMISSIBLE, which is the correct reading of an
artefact that made no claim. SIMPLEST SUFFICIENT: 1 predicate and 1 branch. NO
COMPOSABILITY CLAIM: no second repair was measured against it.

THE SEAT'S OWN REASONING FOLLOWS, UNEDITED.

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


def asserts_something(code: str) -> bool:
    """Does this proof make a checkable claim at all?

    AN `Assert` OR A `Raise`, AND DELIBERATELY NOT AN IMPORT. The runner's
    `_runnable` accepts an import because it is deciding whether a fenced block
    is code worth running; this decides whether a CLEAN EXIT means anything, and
    a proof that only imports has claimed nothing. Unparseable text asserts
    nothing, which is the safe direction: it becomes UNTOOLABLE rather than
    admissible.
    """
    import ast as _a
    if not code or not code.strip():
        return False
    try:
        tree = _a.parse(code)
    except Exception:  # noqa: BLE001 -- SyntaxError and friends: not code
        return False
    for node in _a.walk(tree):
        if isinstance(node, (_a.Assert, _a.Raise)):
            return True
        if (isinstance(node, _a.Constant) and isinstance(node.value, str)
                and "FALSIFIED" in node.value):
            return True
    return False


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
        # ★ A CLEAN EXIT IS ONLY EVIDENCE IF THE PROOF ASSERTED SOMETHING.
        # Added 2026-11-01 when this module was folded back. An assertion-free
        # proof exits cleanly, and a clean exit is what grants admissibility,
        # so `print("ok")` would have admitted a repair. The sentence this
        # branch writes -- "its own assertions held" -- is VACUOUSLY TRUE of a
        # proof with no assertions, which is what makes it dangerous.
        if not asserts_something(proof_code):
            return ProofResult(
                SK_NO_SCORE, "UNTOOLABLE",
                "the proof ran cleanly but asserts nothing, so there is no "
                "claim whose holding could be evidence")
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
