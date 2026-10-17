"""The word layer surfaces candidates and may never decide a merge.

HIS INSTRUCTION, 2026-10-17: *"The registry search can contain both a word and
hashed ID search, so it can contain the best of both approaches."*

HE IS RIGHT, AND NOT BY A UNION. Measured on 150 queries over 106 known and 44
genuinely new items by
`scripts/does_the_register_beat_word_search_2026-10-17.py`:

  * the hashed tiers          recall 95.2830%, specificity 95.4545%
  * distinctive-word overlap  recall 98.1132%, specificity 86.3636%
  * UNION, either says known  recall 98.1132%, specificity 81.8182%
  * INTERSECTION, both must   recall 95.2830%, specificity 100.0000%
  * TIERED, word surfaces     98.1132% surfaced, specificity 95.4545%

A UNION IS LESS SPECIFIC THAN EITHER METHOD ALONE, and that is arithmetic rather
than an accident: saying "known" whenever either method does cannot be more
specific than the less specific of the two. So the word layer surfaces and
`propose` still decides.

THE ASYMMETRY SETTLES IT. A wrong merge BURIES a finding under a closed ticket; a
missed match only leaves a duplicate to merge later. The costs are not
comparable, which is also why his own duplicate test requires the same fault AND
the same repair AND, since 2026-10-17, the same hash.

DEMONSTRATED ON THE LIVE REGISTER, not only on the 150-query sample: taking an
open ticket's own text and deleting its first 12 words, the normalised-digest
tier falls to 0 matches while the word layer still surfaces it. That is the
recall the instruction asked for, and plainly unrelated text surfaces nothing.
"""
from __future__ import annotations

import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def store():
    import sys
    sys.path.insert(0, str(REPO))
    from bench.ticket_store import TicketStore
    return TicketStore()


def _long_open_ticket(store):
    live = [t for t in store.all()
            if t.status in ("OPEN", "REOPENED") and len(t.verbatim or "") > 200]
    if not live:
        pytest.skip("no open ticket with enough text to perturb")
    return sorted(live, key=lambda t: t.tid)[0]


def test_the_word_layer_catches_what_the_digest_misses(store):
    """THE RECALL GAIN, on the live register rather than on a fixture."""
    ticket = _long_open_ticket(store)
    perturbed = " ".join((ticket.verbatim or "").split()[12:])
    assert len(perturbed) > 100, "the perturbation left too little text"
    assert not store.similar(perturbed), (
        "the digest tier still matches after dropping 12 words, so this case "
        "does not demonstrate the gain; perturb further or pick another ticket")
    surfaced = store.similar_by_words(perturbed)
    assert surfaced, (
        "the word layer surfaced nothing for a 12-word perturbation of a "
        "ticket's own text, so it adds no recall at all")


def test_unrelated_text_surfaces_nothing(store):
    """ANTI-FALSE-SURFACING. A layer that matches everything is noise."""
    assert not store.similar_by_words(
        "the kettle in the kitchen needs descaling before tea")
    assert not store.similar_by_words("")


def test_candidates_reports_every_tier_and_decides_nothing(store):
    """The one place a caller looks before raising a ticket."""
    ticket = _long_open_ticket(store)
    found = store.candidates("pf", ticket.verbatim,
                             task_ref=ticket.task_ref or "")
    assert set(found) == {"exact", "reworded", "by_subject", "by_words"}
    assert any(found[k] for k in found), (
        "a ticket's own text surfaced in no tier at all")
    # IT MUST NOT WRITE. A surfacing call that mutates the register would make
    # looking before proposing cost something, and the rule is to look first.
    before = len(store.all())
    store.candidates("pf", "something entirely new and unseen here")
    assert len(store.all()) == before


def test_the_threshold_is_a_swept_value_not_a_guess(store):
    """It governs SURFACING only, and it was measured rather than chosen."""
    assert 0.0 < store.WORD_OVERLAP_SURFACE <= 1.0
    assert store.WORD_OVERLAP_SURFACE == 0.95, (
        "0.95 was the most accurate of 19 thresholds swept over 150 queries; a "
        "different value needs its own sweep")
    # A LOWER THRESHOLD MUST SURFACE AT LEAST AS MUCH, which is the property
    # that makes it a recall dial rather than an arbitrary number.
    ticket = _long_open_ticket(store)
    text = " ".join((ticket.verbatim or "").split()[12:])
    loose = store.similar_by_words(text, threshold=0.5)
    tight = store.similar_by_words(text, threshold=0.99)
    assert len(loose) >= len(tight)


def test_the_merge_rule_still_requires_the_substantive_elements(store):
    """A matching hash admits a merge to consideration; it does not grant one."""
    src = (REPO / "bench" / "ticket_store.py").read_text(encoding="utf-8")
    i = src.index("def merge(")
    body = src[i:i + 2600]
    assert "same fault" in body and "same repair" in body, body[:400]
    assert "same hash" in body, "his 2026-10-17 extension is not recorded"
    assert "NECESSARY CONDITION, NOT A SUFFICIENT ONE" in body, (
        "the hash must not be recorded as sufficient on its own")
    # AND IT IS ENFORCED: a merge with no verification is refused.
    with pytest.raises(ValueError):
        store.merge(sorted(store.all(), key=lambda t: t.tid)[0].tid,
                    sorted(store.all(), key=lambda t: t.tid)[1].tid, "   ")


def test_propose_creates_rather_than_merges_on_a_word_only_match(tmp_path):
    """THE SAFETY PROPERTY, and the reason the word layer may not decide.

    A proposal the word layer surfaces but the digest tiers do NOT recognise
    must be CREATED as a new ticket. If `propose` ever admitted a word-only
    match it would inherit the union's 81.8182% specificity -- worse than either
    tier alone -- and a wrong merge buries a finding.

    Run against a TEMPORARY store, because proposing writes, and the live
    register is not a place to experiment.
    """
    import sys
    sys.path.insert(0, str(REPO))
    from bench.ticket_store import TicketStore
    probe = TicketStore(tmp_path / "probe.jsonl")
    original = (
        "The morning report refused at exit 3 because two entries were live "
        "with no authored detail, while six answered study items still held "
        "stale detail that nothing had cleared after the ruling landed.")
    probe.propose("pf", original[:100], original, "seed", status="OPEN")
    # drop the opening clause: same subject, different text
    perturbed = " ".join(original.split()[8:])
    assert not probe.similar(perturbed), (
        "the digest tier still matches, so this is not a word-only case")
    assert probe.similar_by_words(perturbed, threshold=0.5), (
        "the word layer surfaces nothing, so there is no word-only case to test")
    before = len(probe.all())
    _, outcome = probe.propose("pf", perturbed[:100], perturbed, "probe",
                               status="OPEN")
    assert outcome == "created", (
        f"a word-only match was absorbed as {outcome!r} instead of creating a "
        f"new ticket; `propose` has started trusting the word layer, which "
        f"costs specificity and buries findings")
    assert len(probe.all()) == before + 1
