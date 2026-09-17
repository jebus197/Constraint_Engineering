"""Task A12: "the ruling, 28 of 28 replies" is a COUNT, not a reference to item 28.

THE DEFECT, the A25 false-hit class inside the A12 instrument. `account()`
matches `\\bruling[*_\\x60\\s]*28\\b` anywhere outside the A12 block, and the P3
entry's sentence "under the ruling 28 of 28 = 100.0000%" satisfies it -- so
item 28 was reported CARRIED by the list when its only true accounting is A12's
own DECLARED EXCLUDED sentence. The headline 0/15 did not move, but the guard
could no longer fire for item 28: delete A12's declaration of it and the
comparator would still answer CARRIED. A guard that cannot fire is the defect
this project keeps re-finding, here in the instrument built for A12.

THE FIX IS A LOOKAHEAD ON THE PROPORTION FORM ONLY: `ruling N of M` (N, M
numbers) is a count phrase; `ruling N of the tracker` is still a reference.

EVERYTHING HERE CALLS account() -- nothing retypes its pattern.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ruled_items_are_accounted_2026-09-11.py"


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("ruled_a12fx", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ruled_a12fx"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTheCountPhraseDoesNotCarry:
    def test_item_28_is_declared_not_carried(self, m):
        """THE LIVE INSTANCE. The list's only mention of 28 outside A12 is the
        P3 proportion "under the ruling 28 of 28"; A12's entry says 28 is a
        study-programme item NOT carried here, and the entry is right."""
        block, rest = m._a12_block()
        assert m.account(28, block, rest) == "DECLARED EXCLUDED"

    def test_a_proportion_after_ruling_is_not_a_reference(self, m):
        rest = "under the ruling 99 of 99 seat replies recorded a tool call"
        assert m.account(99, "item 99 is declared excluded here", rest) == \
            "DECLARED EXCLUDED"

    def test_the_same_for_item(self, m):
        rest = "for item 99 of 120 in the inventory sweep"
        assert m.account(99, "item 99 is declared excluded here", rest) == \
            "DECLARED EXCLUDED"


class TestRealReferencesStillCarry:
    def test_item_46_is_still_carried(self, m):
        """POSITIVE CONTROL over the live list: `item 46` at its real site."""
        block, rest = m._a12_block()
        assert m.account(46, block, rest) == "CARRIED"

    def test_ruling_followed_by_prose_still_matches(self, m):
        assert m.account(43, "", "the disposition of ruling 43 of the tracker") \
            == "CARRIED"

    def test_deleting_the_declaration_is_now_loud(self, m):
        """THE PROPERTY THE FIX BUYS: with the false hit gone, removing A12's
        declaration of 28 must read UNACCOUNTED rather than CARRIED."""
        _block, rest = m._a12_block()
        assert m.account(28, "", rest) == "UNACCOUNTED"
