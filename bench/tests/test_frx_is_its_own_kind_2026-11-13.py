"""A fix request is not a feature request, and his first use of it was invisible.

HIS RULING, 2026-11-13, verbatim: *"There is a potential collision here, and I
think it can be cleared up by adding another label to issues in the ticket
store. 'fr' to my eyes can sometimes be read as 'feature request', or 'fix
request'. What I propose going forward is that a fix request should be marked
by me as a 'frx' and a feature request should remain as 'fr'. We only need to
do this going forward. It does not need to be applied to the historical record,
providing we document the change in our docs appropriately."*

★ THE DEFECT WAS THE SUFFIX, NOT THE ALTERNATION. `fr` is a prefix of `frx`, so
the obvious worry is that a left-to-right alternation swallows the longer
token. Driven both ways it does not -- Python backtracks when the suffix fails.
What actually made his first use INVISIBLE is that `MARKER`'s suffix admitted a
colon, a closing bracket, a spaced dash or end-of-line, and he wrote `frx (`.

★ MEASURED BEFORE THE WIDENING, because adding to an accepting pattern is a
LOOSENING: over all 895 of his annotations the widened pattern changes exactly
1 verdict, 0.001117, Wilson [0.000197, 0.006302], and that 1 is his own frx
sentence. 0 false positives in 895.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
HARVEST = REPO / "scripts" / "harvest_tickets_2026-10-17.py"

#: His sentence, byte-exact. Never paraphrased inside quotation marks.
HIS_FIRST_USE = ("As I said above you should fix both. frx (as you will note "
                 "this is my first use of the fix request ticket "
                 "classification.)")


@pytest.fixture(scope="module")
def h():
    sys.path.insert(0, str(REPO / "bench"))
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("cdsfl_harvest_frx", HARVEST)
    m = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_harvest_frx"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


@pytest.fixture(scope="module")
def store():
    sys.path.insert(0, str(REPO / "bench"))
    import ticket_store
    return ticket_store


def test_frx_is_an_accepted_kind(store):
    assert "frx" in store.KINDS, (
        f"the fix-request kind is gone from the store's vocabulary: "
        f"{store.KINDS}")
    assert "fr" in store.KINDS, (
        "the feature-request kind was removed rather than joined. His ruling "
        "adds a kind; it does not replace one, and 311 historical rows are "
        "filed under fr.")


def test_his_actual_first_use_is_seen(h):
    """★ THE CASE THAT WAS INVISIBLE. Not a constructed probe -- his words."""
    assert h.marked_kind(HIS_FIRST_USE) == "frx", (
        f"his first use of frx reads as {h.marked_kind(HIS_FIRST_USE)!r}. "
        f"A ruling that creates a kind, written in that kind, must be "
        f"readable as that kind or the kind does not exist in practice.")


def test_frx_is_not_swallowed_by_fr(h):
    """The prefix worry, pinned even though it was measured as a non-issue."""
    for text in ("frx", "do it. frx", "frx:", "[frx]", "fix this. frx (note)"):
        assert h.marked_kind(text) == "frx", (
            f"{text!r} read as {h.marked_kind(text)!r}; the longer token lost "
            f"to its own prefix")


def test_fr_still_means_what_it_meant(h):
    """★ THE DISCRIMINATION HALF. Without it, a rule that made everything frx
    would pass the test above."""
    for text in ("fr", "raise fr", "a fr: thing", "please add this. fr"):
        assert h.marked_kind(text) == "fr", (
            f"{text!r} read as {h.marked_kind(text)!r}; adding frx changed "
            f"what fr means, which his ruling explicitly does not do")


def test_the_widening_admits_a_bracket_and_not_the_world(h):
    """The suffix now admits a following open bracket. It must not admit
    an arbitrary letter, or every word starting 'fr' becomes a marker."""
    assert h.marked_kind("fr (something)") == "fr"
    for text in ("frozen", "from here", "framework", "frxx", "afr"):
        assert h.marked_kind(text) is None, (
            f"{text!r} is now read as a marker ({h.marked_kind(text)!r}); the "
            f"widening admitted ordinary prose")


def test_the_historical_record_is_not_rekinded(store):
    """★ HIS RULING IS FORWARD-ONLY. Re-filing old rows would rewrite what he
    meant then from what he means now."""
    rows = REPO / "bench" / "tickets" / "tickets.jsonl"
    if not rows.is_file():
        pytest.skip("no ticket rows here")
    import json
    frx = 0
    for line in rows.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except Exception:                                      # noqa: BLE001
            continue
        if r.get("kind") == "frx":
            frx += 1
    assert frx <= 8, (
        f"{frx} rows carry the frx kind. His ruling is that it applies going "
        f"forward only; a bulk re-kind of the historical record contradicts "
        f"it in as many words.")
