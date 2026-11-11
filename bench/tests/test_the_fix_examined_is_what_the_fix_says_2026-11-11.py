#!/usr/bin/env python3
"""The tools examine what the fix makes the document SAY, not the edit markup.

★ FOUND BY A FREE PANEL SEAT IN THE JOINT ROUND OF 2026-11-11, hours after the
both-texts rule shipped, and REPRODUCED BY EXECUTION before being acted on.

THE DEFECT. The both-texts rule ran the topic's tools over the RAW
`proposed_fix`. On the live path a fix reaching the fold-back gate is ALWAYS
SEARCH/REPLACE blocks -- `_apply_back_promote` rejects `no_parseable_block`
before the gate is consulted -- so the tools reduced the MARKUP, which carries
BOTH halves of the edit. Measured on the live function, the result was exactly
INVERTED:

  * the CANONICAL CORRECTION -- a false value in SEARCH, the true one in
    REPLACE -- was REFUSED, because the tool reduced the FALSE half the fix
    exists to remove and returned an adverse verdict;
  * a DELETION OF A TRUE STATEMENT was ADMITTED, because the truth it destroys
    sat in the SEARCH half and verified.

So the repair refused correct repairs and admitted destructive ones. That is
worse than the hole it closed. `_fix_side_text` extracts the REPLACE side when
the field parses as blocks and leaves raw text alone otherwise.

★ THE SEAT'S REASONING WAS CHECKED, NOT ADOPTED. Its claim was re-derived here
by execution on the live function first; its own proposed patch sits in
`experimental_notes/seat_evidence/.../fable/` and is NOT applied, per the
standing rule that a fix goes to the human in the loop rather than being
auto-applied. What is implemented is the repair; what is credited is the find.

★ STILL OPEN AND IT IS THE FOUNDER'S, NOT CLOSED BY THIS FILE. The seat also
showed a shape that STILL admits an unexamined fix: a REPLACE side carrying an
unexamined payload PLUS a true computable rider. It argued that is structural
to any text-scoped admission, since the legitimate case differs from it only in
the SEMANTICS of the residue. Closing it needs a residue rule or an accepted
risk, and which of those is a scoping ruling for him.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))

import domain_immune as di                                     # noqa: E402

CLAIM = "the molecule 'CCO' has formula C2H6O"
FALSE = "the molecule 'CCO' has formula C3H8O"

CORRECTION = f"""<<<< SEARCH notes/thing.md
{FALSE}
====
{CLAIM}
>>>> REPLACE"""

DELETION = f"""<<<< SEARCH notes/thing.md
{CLAIM}
====
>>>> REPLACE"""


class _F:
    def __init__(self, d, fix=""):
        self.description = d
        self.proposed_fix = fix


class TestTheFixSideIsExtracted:
    def test_a_correction_yields_its_replace_side(self):
        assert di._fix_side_text(CORRECTION) == CLAIM
        assert FALSE not in di._fix_side_text(CORRECTION), (
            "the half the fix REMOVES is still being handed to the tools")

    def test_a_deletion_yields_nothing(self):
        assert di._fix_side_text(DELETION) == "", (
            "a pure deletion must leave an empty fix side so it fails closed")

    def test_plain_prose_is_left_alone(self):
        assert di._fix_side_text("correct it to: " + CLAIM) == "correct it to: " + CLAIM

    def test_empty_stays_empty(self):
        assert di._fix_side_text("") == ""
        assert di._fix_side_text("   ") == ""


class TestTheInversionIsGone:
    """★ THE PROPERTY, asserted on the live function. Both directions, because
    fixing one and breaking the other is how the defect arose."""

    def test_the_canonical_correction_admits(self):
        r = di.domain_verification_set("chemistry", _F(CLAIM, CORRECTION))
        assert r["admits"] is True, (
            f"a fix that replaces a FALSE value with the TRUE one is refused. "
            f"The tools are reducing the half being removed: {r['detail']}")

    def test_deleting_a_true_statement_is_refused(self):
        r = di.domain_verification_set("chemistry", _F(CLAIM, DELETION))
        assert r["admits"] is False, (
            f"a fix whose entire content is DELETING a true statement was "
            f"admitted, because the truth it destroys verified from the SEARCH "
            f"half: {r['detail']}")


class TestNothingTheClosureBoughtIsGivenBack:
    def test_the_original_exploit_is_still_refused(self):
        r = di.domain_verification_set("chemistry", _F(CLAIM, "delete the retry loop"))
        assert r["admits"] is False

    def test_a_prose_fix_that_verifies_still_admits(self):
        r = di.domain_verification_set(
            "chemistry", _F(CLAIM, f"correct it to: {CLAIM}"))
        assert r["admits"] is True

    def test_the_parser_is_imported_not_copied(self):
        """★ A SECOND COPY OF A GRAMMAR IS 2 DEFINITIONS OF WHAT A FIX BLOCK IS."""
        src = (ROOT / "bench" / "domain_immune.py").read_text(encoding="utf-8")
        assert "import reference_runner_v3 as _rr" in src
        assert "_rr.parse_search_replace_blocks" in src
        assert "<<<< SEARCH" not in src, (
            "the block grammar has been copied into this module; import it")

    def test_an_import_failure_degrades_rather_than_raising(self, monkeypatch):
        """A gate that crashes is worse than a gate that is conservative."""
        import builtins
        real = builtins.__import__

        def boom(name, *a, **k):
            if name == "reference_runner_v3":
                raise ImportError("simulated")
            return real(name, *a, **k)

        monkeypatch.setattr(builtins, "__import__", boom)
        assert di._fix_side_text(CORRECTION) == CORRECTION.strip(), (
            "an import failure must fall back to the raw text, not raise")
