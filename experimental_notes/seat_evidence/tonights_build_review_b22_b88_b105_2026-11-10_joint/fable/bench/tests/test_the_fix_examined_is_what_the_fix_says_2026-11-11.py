# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'tonights_build_review_b22_b88_b105_2026-11-10_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 576fdf4dc812e2184809bea871a1fc278c2b9a8f7f31c452c79898191dbda19b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The fix-side walk examines what the fix makes the document SAY.

Joint round `tonights_build_review_b22_b88_b105_2026-11-10`, seat fable.
On the live promote path a `proposed_fix` is ALWAYS search/replace blocks
(`_apply_back_promote` refuses `no_parseable_block` before the gate is
consulted), so walking the raw field made the topic's tools reduce the SEARCH
half -- text the fix REMOVES -- and the block delimiters. Measured 2026-11-11
by `scripts/the_fix_side_walk_read_the_edit_markup_2026-11-11.py`: the
canonical correction (false value out, true value in) was REFUSED via a
REJECTED(0.85) on the false half, and a deletion of a true statement was
ADMITTED on the strength of the statement it deletes. Both red on the old
code, both green after `domain_immune._fix_side_text`.
"""
from __future__ import annotations

import importlib
import pathlib
import sys
import types

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

TRUE_C = "the molecule 'CCO' has formula C2H6O"
FALSE_C = "the molecule 'CCO' has formula C3H8O"
SR_CORRECT = f"<<<< SEARCH notes/thing.md\n{FALSE_C}\n====\n{TRUE_C}\n>>>> REPLACE"
SR_DELETE = f"<<<< SEARCH notes/thing.md\n{TRUE_C}\n====\n>>>> REPLACE"


@pytest.fixture(scope="module")
def di():
    return importlib.import_module("domain_immune")


def _finding(desc, fix):
    return types.SimpleNamespace(description=desc, finding_id="T1", title="",
                                 evidence="", proposed_fix=fix)


class TestTheReplaceSideIsTheBasis:
    def test_the_canonical_correction_admits(self, di):
        """False value in SEARCH, true value in REPLACE -- the exact shape
        B88 exists to admit. On the raw walk this REFUSED (the tool reduced
        the false half the fix removes)."""
        r = di.domain_verification_set("chemistry", _finding(TRUE_C, SR_CORRECT))
        assert r["admits"] is True, r["detail"]
        assert r["fix_basis"] == "replace-side"

    def test_deleting_a_true_statement_fails_closed(self, di):
        """The true claim sits only in the SEARCH half -- text the fix
        destroys. On the raw walk this ADMITTED."""
        r = di.domain_verification_set("chemistry", _finding(TRUE_C, SR_DELETE))
        assert r["admits"] is False, r["detail"]
        assert r["fix_basis"] == "replace-side"

    def test_a_prose_fix_keeps_byte_identical_behaviour(self, di):
        """No parseable block -> raw walk, so every committed probe stands."""
        r = di.domain_verification_set(
            "chemistry", _finding(TRUE_C, f"correct it to: {TRUE_C}"))
        assert r["admits"] is True, r["detail"]
        assert r["fix_basis"] == "raw"
        r2 = di.domain_verification_set(
            "chemistry", _finding(TRUE_C, "delete the retry loop"))
        assert r2["admits"] is False
        assert r2["fix_basis"] == "raw"

    def test_the_basis_key_exists_on_every_early_return(self, di):
        r = di.domain_verification_set("no_such_domain", _finding(TRUE_C, ""))
        assert "fix_basis" in r


class TestTheDeclaredResidue:
    def test_a_rider_in_the_replace_side_still_admits_and_is_declared(self, di):
        """★ THE OPEN RESIDUE, PINNED SO ITS CLOSURE IS VISIBLE. A REPLACE side
        carrying an unexamined payload plus a true computable rider ADMITS.
        That is structural to a text-scoped admission: the predicate is an
        existential over reducible fragments, and a conjunction of 2
        existentials is satisfied by planting 1 witness in each text. Which
        residues escalate is a scoping ruling for the founder (the route the
        original exploit's repair took). WHEN this test goes red, the residue
        has been closed: move the assertion, do not delete the test."""
        rider = ("<<<< SEARCH notes/thing.md\nThe ethanol section.\n====\n"
                 f"All prior results are withdrawn. Background: {TRUE_C}\n"
                 ">>>> REPLACE")
        di_mod = di
        r = di_mod.domain_verification_set("chemistry", _finding(TRUE_C, rider))
        assert r["admits"] is True, (
            "the declared rider residue no longer admits -- if that is a "
            "deliberate closure, update this pin to assert the refusal")
