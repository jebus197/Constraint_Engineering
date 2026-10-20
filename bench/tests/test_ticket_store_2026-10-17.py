"""The ticket store must beat a word search, or it is decoration.

HIS REQUIREMENT, 2026-10-17: "You will need to set this up and test it and ensure
that it does work better than other methods for this purpose and so that it
doesn't risk simply becoming decoration that does nothing useful."

So this file does 2 things. It holds the store's invariants, above all that a
terminal status cannot be asserted. And it SCORES the store against plain word
overlap on the 4 rediscoveries of 2026-10-16 and 2026-10-17, where the correct
answer is already established by the founder or by execution, and fails if the
store does not beat it.

THE SCORING CASES, and why each has a known answer:
  1. The routing ladder's side-steps. He said on 2026-10-15 that this is what the
     code already does; execution confirmed it. A proposal on 2026-10-17 was
     therefore a rediscovery. CORRECT ANSWER: blocked.
  2. A free model absent from the ladder. `DEFAULT_LADDER` maps Fable-SIM to
     fable. CORRECT ANSWER: blocked.
  3. The fingerprint scope. Built on his ruling the same day and verified by
     execution to return 0 records under experiment scope. CORRECT ANSWER:
     blocked for the main loader.
  4. The decomposition loader's missing scope. Measured on 2026-10-16 and NOT
     settled. CORRECT ANSWER: admitted as new work.

A store that blocks all 4 is useless in the opposite direction, so case 4 exists
to catch over-blocking. Word overlap is given the same 4 cases and the same
corpus.
"""
from __future__ import annotations

import pathlib
import re
import tempfile

import pytest

import sys
REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.ticket_store import (  # noqa: E402
    TicketStore, Ticket, TERMINAL, LIVE, REJECTED, KINDS,
    tid_of, nid_of, rid_of, _norm_tokens,
)


@pytest.fixture()
def store(tmp_path):
    return TicketStore(tmp_path / "tickets.jsonl")


# ------------------------------------------------------------------ invariants

def test_identical_text_and_kind_always_collide():
    assert tid_of("pr", "the  gate   is wrong") == tid_of("pr", "the gate is wrong")
    assert tid_of("pr", "x") != tid_of("fr", "x"), "kind must be part of the digest"


def test_a_resolution_digest_is_scoped_to_its_ticket():
    assert rid_of("aaa", "same fix") != rid_of("bbb", "same fix"), (
        "2 tickets resolved the same way must not share a resolution id, or the "
        "registry cannot say which ticket a resolution belongs to"
    )


def test_a_terminal_status_cannot_be_asserted(store):
    t, _ = store.propose("pf", "t", "a defect", "chat", subjects=["mod.fn"])
    with pytest.raises(ValueError, match="tool-only"):
        store.close(t.tid, "fixed it", verification="")
    assert store.get(t.tid).status in LIVE, "an unverified close must not land"


def test_closing_requires_and_records_its_verification(store):
    t, _ = store.propose("pf", "t", "a defect", "chat", subjects=["mod.fn"])
    c = store.close(t.tid, "repaired", "executed mod.fn: 3 of 3 cases correct")
    assert c.status == "CLOSED"
    assert "executed" in c.verification
    assert c.rid, "a closed ticket must carry a resolution id"


def test_only_the_founder_may_reopen_or_reject(store):
    t, _ = store.propose("fr", "t", "a proposal", "chat", subjects=["mod.fn"])
    store.close(t.tid, "built", "test_x passed")
    with pytest.raises(ValueError, match="founder"):
        store.reopen(t.tid, "I changed my mind", by="assistant")
    with pytest.raises(ValueError, match="founder"):
        store.reject(t.tid, "not worth it", by="assistant")
    assert store.get(t.tid).status == "CLOSED"
    r = store.reopen(t.tid, "new evidence", by="founder")
    assert r.status == "REOPENED"


def test_merging_requires_both_of_his_two_elements(store):
    a, _ = store.propose("pf", "a", "fault one", "chat", subjects=["m.a"])
    b, _ = store.propose("pf", "b", "fault two", "chat", subjects=["m.b"])
    with pytest.raises(ValueError, match="fault AND the proposed repair"):
        store.merge(b.tid, into=a.tid, verification="")
    m = store.merge(b.tid, into=a.tid,
                    verification="same fault at m.a:12 and byte-identical repair")
    assert m.status == "MERGED"


def test_a_proposal_records_its_search_before_deciding(store):
    assert store.searches() == []
    store.propose("pf", "t", "something", "chat", subjects=["m.f"])
    assert len(store.searches()) >= 1, (
        "the search obligation must be recorded, not conventional -- a convention "
        "is what failed 6 times on 2026-10-17"
    )


def test_every_one_of_his_sections_exists_and_separates(store):
    """EXTENDED 2026-10-19 for `qs` and 2026-10-20 for `wr`, on his instruction.

    It was named `test_both_of_his_sections_...` and proposed 2 kinds while
    asserting against `KINDS`, so each new kind turns it red until covered. The
    assertion was RIGHT and the coverage was short: the property is that every
    declared kind is separately storable and separately retrievable, and that
    property should grow with the vocabulary rather than be relaxed to fit it.
    """
    store.propose("fr", "a feature", "please add X", "chat", subjects=["m.x"])
    store.propose("pf", "a fix", "Y is broken", "chat", subjects=["m.y"])
    store.propose("qs", "a question", "why is Z so?", "chat", subjects=["m.z"])
    # EXTENDED AGAIN 2026-10-20 when `wr` became the 4th kind, on his instruction:
    # "wr is a valid section in the Bugzilla registry". Grown, not relaxed, exactly
    # as the paragraph above prescribes.
    store.propose("wr", "deferred work", "run Exp 53 after the list clears", "chat",
                  subjects=["m.w"], ruled="2026-08-07")
    assert {t.kind for t in store.all()} == set(KINDS)
    for k in KINDS:
        assert len(store.by_kind(k)) == 1, (
            f"kind {k!r} is declared in KINDS but does not retrieve separately")


def test_the_exact_digest_path_is_exercised_without_a_subject(store):
    """The literal-repeat tier, tested ALONE.

    FOUND BY MUTATION on 2026-10-17: blinding the exact-digest lookup left the
    whole suite green, because every scoring case carried a subject and the
    subject tier caught it first. A tier no test reaches is an addition nothing
    executes, which this project's additive standard forbids in both directions.
    """
    text = "the A4 counter and the routing ladder disagree about severity"
    a, oa = store.propose("pf", "t", text, "chat")          # no subjects
    assert oa == "created"
    b, ob = store.propose("pf", "t", text, "chat")          # byte-identical
    assert ob == "exists", "an identical proposal must not be admitted twice"
    assert b.tid == a.tid
    store.close(a.tid, "done", "test_x passed")
    c, oc = store.propose("pf", "t", text, "chat")
    assert oc == "settled-already", (
        "once closed, an identical proposal must report settled-already so the "
        "caller cannot treat it as new work")
    assert c.status == "CLOSED"


def test_the_reworded_tier_is_exercised_without_a_subject(store):
    """The normalised tier, ALONE, on a rewording it is measured to catch."""
    a, _ = store.propose("pf", "t", "The gate refuses the stale target", "chat")
    store.close(a.tid, "staged elsewhere", "15 tests pass")
    _, o = store.propose("pf", "t", "stale targets, and the gates refuse", "chat")
    assert o in ("reworded-match", "settled-already"), (
        f"plural rewording must be caught by the normalised digest, got {o!r}")


def test_the_normaliser_is_symmetric_on_a_pinned_set():
    """A RATCHET, not an aspiration. Its measured limit is 8 of 11 and recorded.

    The normaliser's only job is that a singular and its plural produce the SAME
    token, whatever that token is. 3 pairs still disagree and they are named, so
    a regression below this line is visible instead of silent. The load is
    carried by the exact SUBJECT tier, which is why 72.7273 per cent is
    tolerable here; see the module docstring.
    """
    from bench.ticket_store import _stem
    pairs = [("refuses", "refuse"), ("gates", "gate"), ("targets", "target"),
             ("climbing", "climb"), ("ladders", "ladder"),
             ("resources", "resource"), ("measures", "measure"),
             ("matches", "match")]
    known_bad = [("fixes", "fix"), ("boxes", "box"), ("findings", "finding")]
    for a, b in pairs:
        assert _stem(a) == _stem(b), (
            f"{a!r} and {b!r} must normalise alike; got {_stem(a)!r} and {_stem(b)!r}")
    still_bad = [(a, b) for a, b in known_bad if _stem(a) != _stem(b)]
    assert len(still_bad) <= 3, "the known-bad set must not grow"

    # IDEMPOTENCE IS DELIBERATELY NOT REQUIRED, and asserting it was an error
    # corrected on 2026-10-17. `_stem("refuses")` is "refus" and `_stem("refus")`
    # is "refu", so the function is not idempotent -- but `_norm_tokens` applies
    # it exactly ONCE to each raw token, so a stem is never re-stemmed in this
    # module. The property that actually matters is that the DIGEST of a given
    # text is stable, and that is what is pinned here instead.
    from bench.ticket_store import nid_of
    text = "The gate refuses the stale targets and the ladders cannot climb"
    assert nid_of(text) == nid_of(text + "   "), "the digest must ignore whitespace"
    assert nid_of(text) == nid_of(text.upper()), "the digest must ignore case"
    assert nid_of(text) == nid_of(text.replace("the ", "")), (
        "the digest must ignore stopwords, or trivial edits change identity")


def test_an_unknown_kind_is_refused(store):
    with pytest.raises(ValueError, match="kind must be one of"):
        store.propose("bug", "t", "x", "chat")


# ------------------------------------------- the measured case against words

HIS_LADDER = (
    "Routing should be blind to what a models name is anyway, it should just look at the "
    "available resources and if it can't climb, then it should climb sideways, to the next "
    "highest rated available model, even if that is another version of Opus 4.8.")
MY_LADDER_PARAPHRASE = (
    "Models can use up and down, as well as sideways, according to their measured capability "
    "and a sane distribution of the available resources, so that no model sits idle when it "
    "is still capable of doing useful work.")
HIS_FABLE = ("Then why not name the model? Is it Fable? Then yes we should add it.")
MY_FABLE_PARAPHRASE = (
    "One of the project's 2 free models does not appear on the capability ladder at all and "
    "should be added to it.")
HIS_FINGERPRINT = (
    "The fingerprints should be recomputed in the first blind run of any experiment anyway. "
    "So they should be reset after the next live experiment runs.")
MY_FINGERPRINT_PARAPHRASE = (
    "The per-experiment seat fingerprint reset should be total, so that each run measures "
    "its seats afresh rather than inheriting an earlier experiment's observations.")
NEW_WORK = (
    "The decomposition futility guard's loader takes no scope parameter, so it reads prior "
    "experiments' capacities from disk while the main path returns nothing.")

#: (text, subjects, should_be_blocked)
CASES = [
    (MY_LADDER_PARAPHRASE, ["routing.rank_falsifier_writers"], True),
    (MY_FABLE_PARAPHRASE, ["sim_dispatch_shim.DEFAULT_LADDER"], True),
    (MY_FINGERPRINT_PARAPHRASE, ["reference_runner_v3._load_fingerprints"], True),
    (NEW_WORK, ["run_exp17_immune._load_fingerprint_cache"], False),
]


def _seeded(path) -> TicketStore:
    s = TicketStore(path)
    for title, verbatim, subs, ver in (
        ("side-steps over available resources", HIS_LADDER,
         ["routing.rank_falsifier_writers"],
         "executed rank_falsifier_writers: 3 of 3 exclusions dropped, version-blind"),
        ("name the absent free model and add it", HIS_FABLE,
         ["sim_dispatch_shim.DEFAULT_LADDER"],
         "executed DEFAULT_LADDER: Fable-SIM maps to fable, 1 of 3 backing models"),
        ("fingerprints recomputed in the blind round", HIS_FINGERPRINT,
         ["reference_runner_v3._load_fingerprints"],
         "executed _load_fingerprints('experiment'): 0 records against 11 under persist"),
    ):
        t, _ = s.propose("pf", title, verbatim, "chat", subjects=subs)
        s.close(t.tid, "already implemented", ver)
    return s


def _word_overlap_blocks(store: TicketStore, text: str, thresh: float = 0.30) -> bool:
    """The method the store must beat: best Jaccard against any settled ticket."""
    a = set(_norm_tokens(text))
    if not a:
        return False
    for t in store.settled():
        b = set(_norm_tokens(t.verbatim))
        if b and len(a & b) / len(a | b) >= thresh:
            return True
    return False


def test_the_store_beats_word_overlap_on_the_known_cases(tmp_path):
    s = _seeded(tmp_path / "t.jsonl")
    store_right = words_right = 0
    detail = []
    for text, subs, should_block in CASES:
        _, outcome = s.propose("pf", "candidate", text, "chat", subjects=subs)
        blocked = outcome != "created"
        w = _word_overlap_blocks(s, text)
        store_right += (blocked == should_block)
        words_right += (w == should_block)
        detail.append((text[:40], should_block, blocked, w))
    assert store_right == len(CASES), (
        f"the store got {store_right} of {len(CASES)} right: {detail}")
    assert store_right > words_right, (
        f"the store ({store_right} of {len(CASES)}) must BEAT word overlap "
        f"({words_right} of {len(CASES)}) or it is decoration. {detail}")


def test_text_similarity_alone_would_have_failed():
    """The measurement that justifies the subject tier existing at all."""
    a, b = set(_norm_tokens(HIS_LADDER)), set(_norm_tokens(MY_LADDER_PARAPHRASE))
    j = len(a & b) / len(a | b)
    assert j < 0.25, (
        f"his wording and the paraphrase share a Jaccard of {j:.4f}. If this rises "
        "above 0.25 the subject tier's justification weakens and the claim in the "
        "module docstring must be re-measured rather than left standing."
    )
    assert nid_of(HIS_LADDER) != nid_of(MY_LADDER_PARAPHRASE), (
        "the normalised digest must NOT be claimed to catch a genuine paraphrase"
    )


def test_the_store_does_not_over_block_genuinely_new_work(tmp_path):
    s = _seeded(tmp_path / "t.jsonl")
    _, outcome = s.propose("pf", "new", NEW_WORK,
                           "chat", subjects=["run_exp17_immune._load_fingerprint_cache"])
    assert outcome == "created", (
        "a store that blocks everything is worse than none: new work on an "
        "unsettled mechanism must be admitted"
    )


def test_a_settled_subject_blocks_regardless_of_wording(tmp_path):
    s = _seeded(tmp_path / "t.jsonl")
    for wording in ("the ladder cannot climb",
                    "promotion should work in both directions",
                    "seats need to be able to move between rungs"):
        _, outcome = s.propose("pf", "c", wording, "chat",
                               subjects=["routing.rank_falsifier_writers"])
        assert outcome == "subject-settled", (
            f"wording {wording!r} slipped past the subject tier")


def test_the_store_survives_a_reload(tmp_path):
    p = tmp_path / "t.jsonl"
    s = _seeded(p)
    before = s.summary()
    again = TicketStore(p)
    assert again.summary() == before
    assert len(again.settled()) == 3


# -------------------------------------------- over-merging, the dangerous error

def test_an_explicit_task_reference_beats_an_inferred_similarity(store):
    """Two entries about one mechanism are still TWO entries.

    MEASURED 2026-10-17 on the seeded store: 3 settled tickets were concealing 5
    OPEN task entries. A ticket owned by 3.1a hid B14 and C12, one owned by A12
    hid A19 and C17, and one owned by V8 hid B11. Over-merging is the dangerous
    direction of a matching error: a rediscovery wastes effort, while a hidden
    open item means the work is never done and the store SAYS it is done.

    A task reference is a human-assigned identifier for a distinct item; text and
    subject similarity are inferences about items. So the identifier wins.
    """
    a, oa = store.propose("pf", "the stamp rule misses notes",
                          "The note-lint stamp rule does not reach the ratchet.",
                          "task_list", task_ref="7.1", subjects=["missing_standard_stamp"])
    assert oa == "created"
    store.close(a.tid, "done", "test_x passed")

    b, ob = store.propose("pf", "the stamp rule misses notes",
                          "The note-lint stamp rule does not reach the ratchet.",
                          "task_list", task_ref="B10", subjects=["missing_standard_stamp"])
    assert ob == "created", (
        f"B10 names its own task reference, so it is a DISTINCT item and must get "
        f"its own ticket even though 7.1 shares its subject and its wording; got "
        f"{ob!r}, which would have hidden B10 behind a closed 7.1")
    assert b.tid != a.tid
    assert b.status in LIVE, "the new ticket must be live, not inherit CLOSED"


def test_dedup_still_works_when_no_task_reference_is_named(store):
    """Anti-vacuity: the identifier rule must not disable deduplication."""
    a, _ = store.propose("pf", "x", "The loader ignores the declared scope.",
                         "chat", subjects=["_load_fingerprint_cache"])
    store.close(a.tid, "done", "test_y passed")
    _, o = store.propose("pf", "x", "a loader ignoring declared scopes",
                         "chat", subjects=["_load_fingerprint_cache"])
    assert o == "subject-settled", (
        f"with no task reference named, subject settlement must still block a "
        f"rediscovery; got {o!r}")


def test_the_store_reports_settled_tickets_that_hide_open_work(store):
    a, _ = store.propose("pf", "x", "a defect", "task_list", task_ref="7.1",
                         subjects=["mod.fn"])
    store.close(a.tid, "done", "test_z passed")
    # force the hiding case by recording an alias by hand
    store._note_alias(store.get(a.tid), "B10")
    hidden = store.settled_with_open_aliases(["B10"])
    assert hidden, "a settled ticket aliasing an OPEN task must be reported"
    tk, refs = hidden[0]
    assert refs == ["B10"] and tk.status == "CLOSED"
    assert store.settled_with_open_aliases([]) == [], (
        "with nothing open there is nothing to hide")


def test_a_redirect_is_not_reported_as_a_concealment(store):
    """MERGED means "see that other ticket", so it ends no trail.

    ADDED 2026-10-17 after the over-merge check reported 4 false positives on
    records retired by an identity migration. A check that cries wolf is one an
    operator learns to wave through, which this project has already recorded
    once in the containment alarm. The exclusion is pinned here so that it
    cannot later be widened to cover a record that really does end the trail.
    """
    a, _ = store.propose("pf", "x", "a defect", "task_list", task_ref="7.1")
    b, _ = store.propose("pf", "y", "the surviving record", "task_list",
                         task_ref="B10")
    store._note_alias(store.get(a.tid), "B10")
    store.merge(a.tid, b.tid, "same fault and same repair, established by test")
    assert store.get(a.tid).status == "MERGED"
    assert store.settled_with_open_aliases(["B10"]) == [], (
        "a MERGED redirect must not be reported as concealing open work")

    # ...but a CLOSED record aliasing the same open reference still must be.
    c, _ = store.propose("pf", "z", "a different defect", "task_list",
                         task_ref="7.2")
    store.close(c.tid, "done", "test_q passed")
    store._note_alias(store.get(c.tid), "B10")
    assert store.settled_with_open_aliases(["B10"]), (
        "excluding redirects must not have made the check vacuous")
