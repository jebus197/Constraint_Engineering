# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'what_is_a_proof_outside_code_b22_2026-10-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1b4470b2401a52f6c13f5c6601f39925d65e07284d2f04665d997e666ecb8466
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A verified STEM proof is carried by the EXISTING verdict vocabulary.

WHAT THIS PINS (panel seat, brief `what_is_a_proof_outside_code`, 2026-10-31)
-----------------------------------------------------------------------------
The brief asserted "Step 4 [harness re-verification of a model's printed
proof] is the one that does not exist yet" and asked whether a verified proof
needs its own verdict. Both halves were decided by execution against this
repository, and this file pins the answers so they cannot drift unremarked:

  1. STEP 4 EXISTS. ``falsifier_verify.reverify_falsifier`` independently
     re-runs a model-authored tool artefact against a non-code STEM target
     and the RUNNER mints the verdict. Exercised here end to end on the
     metrology fixture (import-free falsifier, chemistry/uncertainty content):
     pristine document -> CONFIRMED; document carrying the correct fix ->
     REFUTED. The solution-direction half is ``fix_efficacy.probe`` (applies
     the fix, re-runs the finding's own falsifier, reports FIX_CURES /
     FIX_INEFFECTIVE), wired at reference_runner_v3's close path.

  2. A PRINTED PROOF ENTERS IN DEFECT POLARITY, NOT AS A NEW TOKEN. A proof
     whose success is a clean exit ("NOT FALSIFIED" + returncode 0) is read
     by ``_read_verdict`` as REFUTED -- "the defect was not demonstrated" --
     which is exactly the verdict a sound solution's falsifier must produce
     against the patched artefact. No ``VERIFIED`` token is needed, and none
     may be minted casually: ``spec_verification_factor`` maps every token it
     does not know to 0.5, so an UNDECLARED proof token would silently halve
     effective severity instead of being honoured. That mapping is pinned
     below; anyone extending the verdict vocabulary must extend the factor in
     the same change or this file fails.

  3. TOOL-UNDECIDABLE ALREADY HAS NAMES. UNTOOLABLE (nothing to run) and
     ERROR (the instrument could not look) both map to factor 0.5, and the
     runner's gate escalates them (equipment failure -> UNCONFIRMED -> HIL,
     founder ruling 2026-08-22). No new outcome is required.

Everything here is offline and fast: the metrology falsifier imports nothing
and only reads text; the proof snippet is stdlib ``math``.
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
if str(_root / "bench") not in sys.path:
    sys.path.insert(0, str(_root / "bench"))

from bench.falsifier_verify import reverify_falsifier  # noqa: E402
from bench.reference_runner_v3 import (  # noqa: E402
    _estimate_gamma,
    spec_verification_factor,
)
from bench.tests.fixtures.stem.stem_fixtures import load  # noqa: E402

#: A printed proof in proof polarity: it computes the value with a tool,
#: asserts its own claim, and exits cleanly on success. The claim is the
#: metrology fixture's TRUE combined relative standard uncertainty (RSS of
#: the three components in CM-04), so the proof verifies.
_VERIFIED_PROOF = (
    "import math\n"
    "rss = math.sqrt(0.0392**2 + 0.0049**2 + 0.1206**2)\n"
    "assert abs(rss - 0.1269) < 5e-5, f'proof fails: {rss}'\n"
    "print('NOT FALSIFIED: combined u_r =', round(rss, 6))\n"
)


class TestStepFourExistsAndDecides:
    """The harness independently re-runs a model's tool artefact on a
    non-code STEM target. This is the brief's step 4, executing today."""

    def test_the_false_claim_is_confirmed_on_the_pristine_document(self, tmp_path):
        f = load("metrology")
        copy = tmp_path / f.doc_name
        copy.write_text(f.document, encoding="utf-8")
        assert reverify_falsifier(f.falsifier(copy)) == "CONFIRMED"

    def test_the_correct_fix_flips_the_verdict_to_refuted(self, tmp_path):
        f = load("metrology")
        copy = tmp_path / f.doc_name
        copy.write_text(f.apply(f.correct_fix), encoding="utf-8")
        assert reverify_falsifier(f.falsifier(copy)) == "REFUTED"


class TestAVerifiedProofNeedsNoNewVerdict:
    """A proof that verifies maps onto the existing vocabulary: REFUTED in
    defect polarity. A new token is not only unnecessary -- minted without
    extending ``spec_verification_factor`` it would be silently halved."""

    def test_a_verified_proof_reads_as_refuted(self):
        assert reverify_falsifier(_VERIFIED_PROOF) == "REFUTED"

    def test_a_failed_proof_reads_as_confirmed(self):
        broken = _VERIFIED_PROOF.replace("0.1269", "0.1650")  # the false claim
        assert reverify_falsifier(broken) == "CONFIRMED"

    def test_an_undeclared_proof_token_is_read_as_unresolved(self):
        """Pin: every token the factor does not know -> 0.5. This is the
        guard that makes 'no new verdict vocabulary' enforceable -- a change
        that mints VERIFIED must extend the factor in the same change."""
        e = {"severity": 0.8}
        assert spec_verification_factor({**e, "falsifier_verdict": "CONFIRMED"}) == 1.0
        assert spec_verification_factor({**e, "falsifier_verdict": "REFUTED"}) == 0.0
        for undecided in ("VERIFIED", "PROOF_VERIFIED", "UNTOOLABLE",
                          "ERROR", "INTEGRITY_VIOLATION", None):
            assert spec_verification_factor(
                {**e, "falsifier_verdict": undecided}) == 0.5, undecided


class TestGammaMovesOnlyThroughSettledNovelty:
    """A proof-bearing step 4 affects convergence by SETTLING claims, so
    settled criticals stop re-arriving as novel. The decay fit sees that;
    it does not see proofs directly."""

    def test_tool_settled_rounds_flatten_the_curve(self):
        assert _estimate_gamma([5, 3, 1, 0, 0, 0]) >= 0.30

    def test_never_settled_rounds_do_not(self):
        assert _estimate_gamma([5, 5, 5, 5, 5, 5]) < 0.30
