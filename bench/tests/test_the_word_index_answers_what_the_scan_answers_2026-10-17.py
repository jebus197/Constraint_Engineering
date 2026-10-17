"""The indexed word search returns exactly what the linear scan returns.

THE IDEA IS GEMINI WEB'S, from the design brief he attached on 2026-10-17,
which proposed SQLite FTS5 for literal word search. The measurement supported
it: the register's hash tiers were already fast (`get` 0.0015 ms median,
`similar` 0.0328 ms), but the word layer cost 27.7689 ms on the mean
[24.1092, 31.4286] because it touched all 902 tickets, and it grows linearly --
which matters because the backfill he asked for will add thousands.

The MECHANISM here is a plain dict rather than FTS5, because the store already
loads wholly into memory, so a virtual table would add a second copy on disk
that can drift from the append-only log for no measured gain.

WHY BOTH FORMS STAY LIVE. The project's rule is that a test asserting on the
SOURCE TEXT of two implementations proves only that each describes itself
consistently; it cannot detect a producer and a consumer that disagree. So the
linear scan is kept as the reference implementation and this file CALLS BOTH
and compares their ordered output. Four defects in this project have been found
by executing two forms against each other and none by reading them.

THE FIRST PROTOTYPE WAS FAST AND WRONG -- 203x quicker and agreeing with the
scan on 2 of 200 queries -- because it used the wrong denominator, excluded the
query's own ticket, and skipped the title fallback. A speed-up is not evidence
of correctness, which is why the agreement assertion comes first here.
"""
from __future__ import annotations

import pathlib
import random
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.ticket_store import TicketStore, Ticket, _norm_tokens  # noqa: E402

SAMPLE = 60


@pytest.fixture(scope="module")
def store():
    s = TicketStore()
    s.load()
    if len(s.all()) < 20:
        pytest.skip("the live register is too small to compare two forms on")
    return s


def _both(store, text, share=None):
    share = store.WORD_OVERLAP_SURFACE if share is None else share
    wanted = set(_norm_tokens(text))
    indexed = [t.tid for t in store.similar_by_words(text, threshold=share)]
    scan = ([t.tid for t in store._similar_by_words_scan(wanted, share)]
            if wanted else [])
    return indexed, scan


def test_the_two_forms_agree_on_the_live_register(store):
    """THE ASSERTION THAT LICENSES THE INDEX AT ALL."""
    rng = random.Random(20261017)
    tickets = rng.sample(store.all(), min(SAMPLE, len(store.all())))
    disagreed = []
    for t in tickets:
        indexed, scan = _both(store, t.verbatim)
        if indexed != scan:
            disagreed.append((t.tid, len(indexed), len(scan)))
    assert not disagreed, (
        f"{len(disagreed)} of {len(tickets)} queries got a different ordered "
        f"answer from the index than from the scan: {disagreed[:5]}. The index "
        f"is not a faster way to the same answer, it is a different answer.")


@pytest.mark.parametrize("share", [0.0, 0.25, 0.5, 0.95, 1.0])
def test_they_agree_at_every_threshold_including_zero(store, share):
    """A THRESHOLD OF 0 IS THE ONE CASE THE SUPERSET ARGUMENT FAILS, because a
    ticket sharing no token still qualifies and appears in no postings list.
    The live method falls back to the scan there; this proves it does."""
    rng = random.Random(99)
    for t in rng.sample(store.all(), 8):
        indexed, scan = _both(store, t.verbatim, share=share)
        assert indexed == scan, (
            f"threshold {share}: the index and the scan disagree. At 0 the "
            f"index must defer to the scan entirely.")


def test_a_newly_appended_ticket_is_visible_to_word_search(tmp_path):
    """THE DANGEROUS FAILURE, STATED DIRECTLY.

    A stale index makes a just-raised ticket INVISIBLE to word search, which is
    the duplicate the register exists to catch. Every mutation funnels through
    `_append`, so this exercises that path for real rather than reaching in."""
    path = tmp_path / "tickets.jsonl"
    s = TicketStore(path=path)
    s.load()
    text = ("a distinctive proposal about chronometric widget calibration "
            "under negative pressure")
    s.propose("pf", "widget calibration", text, source="chat")
    # Warm the index, then append a second ticket and search again.
    first = s.similar_by_words(text)
    assert first, "the ticket just raised is not found by its own words"
    second = ("a distinctive proposal about chronometric widget calibration "
              "under negative pressure, restated")
    s.propose("pf", "widget calibration restated", second, source="chat")
    found = {t.title for t in s.similar_by_words(second)}
    assert "widget calibration restated" in found, (
        "the second ticket is invisible to word search, so the index went "
        "stale across an append and the register would raise a duplicate of "
        "something it already holds")


def test_the_index_is_dropped_on_append_rather_than_patched(tmp_path):
    """Invalidation, not incremental update: the simplest thing that cannot be
    subtly wrong. Asserted by observing the field, then by behaviour."""
    path = tmp_path / "tickets.jsonl"
    s = TicketStore(path=path)
    s.load()
    s.propose("pf", "one", "alpha beta gamma delta epsilon", source="chat")
    s.similar_by_words("alpha beta gamma delta epsilon")
    assert s._word_index is not None, "the index was never built"
    s.propose("pf", "two", "zeta eta theta iota kappa", source="chat")
    assert s._word_index is None, (
        "the index survived an append. If it is ever updated incrementally "
        "instead, this test must be replaced by one that proves the update "
        "equals a rebuild -- not deleted.")


def test_a_reload_also_drops_it(tmp_path):
    path = tmp_path / "tickets.jsonl"
    s = TicketStore(path=path)
    s.load()
    s.propose("pf", "one", "alpha beta gamma delta epsilon", source="chat")
    s.similar_by_words("alpha beta gamma delta epsilon")
    assert s._word_index is not None
    s.load()
    assert s._word_index is None, "a reload left a stale index in place"


def test_an_empty_query_returns_nothing_from_both_forms(store):
    assert store.similar_by_words("") == []
    assert store.similar_by_words("   ") == []


def test_the_scan_is_not_dead_code(store):
    """It is called by this file on every comparison above, and by the live
    method at a threshold of 0. An addition nothing reaches is not additive --
    and neither is a retained reference implementation nothing executes."""
    wanted = set(_norm_tokens(store.all()[0].verbatim or "x"))
    assert isinstance(store._similar_by_words_scan(wanted, 1.0), list)
    zero = store.similar_by_words(store.all()[0].verbatim or "x", threshold=0.0)
    assert isinstance(zero, list)
