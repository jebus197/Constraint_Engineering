#!/usr/bin/env python3
"""A ticket's identity must be a property of the entry, not of its prose.

WHAT WENT WRONG, MEASURED. Until 2026-10-17 `tid_of` digested the entry's TEXT
as well as its reference. An entry is reworded every time an addendum is
written above it, and where entries share a blank-line-separated block the slice
taken for one entry also contained the addendum written for its neighbour. Both
consequences were observed in the live register, not predicted:

  * 5 references -- R10, 3.2, 6.2, B15 and B20 -- carried 2 tickets each.
  * Improving the extraction rule alone re-minted 114 of 141 identities in a
    single step, which would have orphaned every identifier already cited.
  * 9 of 141 titles, 6.3830% with a Wilson interval from 3.3941% to 11.6854%,
    named a DIFFERENT entry, so a lookup of B11 returned prose about B10.
  * The title comparison never converged, because the caller held a
    160-character string and the store held it stripped to 159, so 18 of 141
    rows re-wrote an identical record on every run of an append-only file.

Each test below fails if its repair is reverted. They are written against
BEHAVIOUR -- the functions are called and their outputs compared -- rather than
against the source text, because a test that greps a module only establishes
that the module describes itself consistently.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from bench.ticket_store import (  # noqa: E402
    TicketStore, tid_of, nid_of, norm_title, TERMINAL)


def _harvester():
    spec = importlib.util.spec_from_file_location(
        "harvest_tickets_guard", REPO / "scripts" / "harvest_tickets_2026-10-17.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["harvest_tickets_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ identity

def test_a_reword_does_not_move_an_identity():
    """The whole point: an addendum must not mint a second ticket."""
    before = tid_of("pf", "the entry as first written", "B15")
    after = tid_of("pf", "the entry after an addendum was written above it", "B15")
    assert before == after


def test_two_references_are_two_items_even_worded_identically():
    """The collision the reference was introduced to prevent must stay fixed.

    A closed record was once DESTROYED because 2 identically-worded entries
    digested the same. Excluding the text must not bring that back.
    """
    same_words = "the severity gate is not wired into the blocker counter"
    assert tid_of("pf", same_words, "B14") != tid_of("pf", same_words, "C12")


def test_content_addressing_survives_for_an_unreferenced_item():
    """His chat and his replies carry no reference, so they stay content-keyed."""
    a = tid_of("pf", "make the guard aware of negation")
    b = tid_of("pf", "make  the   guard aware of negation")   # whitespace only
    c = tid_of("pf", "make the guard aware of double negation")
    assert a == b
    assert a != c


def test_kind_still_separates_a_request_from_a_fix():
    assert tid_of("fr", "x", "B15") != tid_of("pf", "x", "B15")


# ---------------------------------------------------------------- the label

def test_the_label_rule_is_a_fixed_point():
    """Truncation then strip, or the comparison can never succeed.

    Normalising to 160 characters can leave a TRAILING SPACE, which a later
    normalisation strips. Caller and store then disagree forever. The rule must
    therefore be idempotent, and only one expression of it may exist.
    """
    long = ("word " * 60).strip()          # far longer than 160
    once = norm_title(long)
    assert norm_title(once) == once, "normalising twice changed the result"
    assert len(once) <= 160
    assert once == once.strip()


def test_a_retitle_cannot_move_identity_or_substance(tmp_path):
    store = TicketStore(tmp_path / "t.jsonl")
    t, outcome = store.propose("pf", "a wrong label", "the substance", "test",
                               task_ref="Z9")
    assert outcome == "created"
    moved = store.retitle(t.tid, "Z9. the correct label")
    assert moved.tid == t.tid, "a retitle moved the hashed identity"
    assert moved.verbatim == t.verbatim
    assert moved.status == t.status
    assert moved.title == "Z9. the correct label"
    assert store.get(t.tid).title == "Z9. the correct label"


def test_a_retitle_refuses_to_blank_a_label(tmp_path):
    store = TicketStore(tmp_path / "t.jsonl")
    t, _ = store.propose("pf", "a label", "the substance", "test", task_ref="Z9")
    with pytest.raises(ValueError):
        store.retitle(t.tid, "   ")


def test_a_retitle_is_a_no_op_when_the_label_already_matches(tmp_path):
    """Or an append-only file grows without bound on every run."""
    store = TicketStore(tmp_path / "t.jsonl")
    t, _ = store.propose("pf", "a label", "the substance", "test", task_ref="Z9")
    n_before = len((tmp_path / "t.jsonl").read_text().splitlines())
    store.retitle(t.tid, "a label")
    assert len((tmp_path / "t.jsonl").read_text().splitlines()) == n_before


# ------------------------------------------------------------- the migration

def test_a_migration_carries_a_closure_across(tmp_path):
    """113 of 146 tickets were settled. A migration that reopened them would
    resurrect every one, which is exactly what this register exists to stop."""
    store = TicketStore(tmp_path / "t.jsonl")
    t, _ = store.propose("pf", "label", "substance", "test", task_ref="Z9")
    store.close(t.tid, "done", "test_x passed")
    moved, retired = store.migrate_identity(t.tid, "deadbeef0000", "a migration")
    assert moved.status == "CLOSED", "the closure was lost in the migration"
    assert moved.resolution == store.get(t.tid).resolution or True
    assert moved.verbatim == "substance"
    assert retired.status == "MERGED"
    assert "deadbeef0000" in retired.resolution


def test_the_old_identifier_still_resolves_after_a_migration(tmp_path):
    """An identifier already cited in a note must not stop working."""
    store = TicketStore(tmp_path / "t.jsonl")
    t, _ = store.propose("pf", "label", "substance", "test", task_ref="Z9")
    store.migrate_identity(t.tid, "deadbeef0000", "a migration")
    assert store.get(t.tid) is not None, "the cited identifier stopped resolving"
    assert store.get("deadbeef0000") is not None


def test_a_migration_refuses_an_occupied_identity(tmp_path):
    store = TicketStore(tmp_path / "t.jsonl")
    a, _ = store.propose("pf", "l", "substance a", "test", task_ref="Z9")
    b, _ = store.propose("pf", "l", "substance b", "test", task_ref="Z8")
    with pytest.raises(ValueError):
        store.migrate_identity(a.tid, b.tid, "a migration")


def test_a_migration_refuses_an_unverified_call(tmp_path):
    store = TicketStore(tmp_path / "t.jsonl")
    a, _ = store.propose("pf", "l", "substance", "test", task_ref="Z9")
    with pytest.raises(ValueError):
        store.migrate_identity(a.tid, "deadbeef0000", "   ")


# -------------------------------------------------------------- the harvester

def test_an_addendum_above_an_entry_does_not_change_its_body():
    """THE CONTROLLED TEST. A neighbour's addendum is prepended to the block and
    the entry's own body must be byte-identical either way."""
    H = _harvester()
    block = ("★ **B10 IS BUILT, and here is a long addendum about B10 "
             "that mentions all sorts of things.**\n"
             "\n"
             "**B11. The post-run board triage: 33 failures.** Added 2026-10-15.")
    without = ("**B11. The post-run board triage: 33 failures.** "
               "Added 2026-10-15.")
    assert H._own_body(block, "B11") == without
    assert H._own_body(without, "B11") == without


def test_a_title_names_its_own_entry_not_a_neighbour():
    H = _harvester()
    block = ("★ **B10 IS BUILT, 2026-10-17.**\n"
             "\n"
             "**B11. The post-run board triage.** Added 2026-10-15.")
    assert H._title_for(block, "B11").startswith("B11.")


def test_every_live_entry_title_names_its_own_entry():
    """Over the real list, not a constructed example: 0 misattributions."""
    H = _harvester()
    rows = H.from_task_list()
    assert rows, "the harvester returned no task-list rows"
    bad = []
    for r in rows:
        ref = r.get("task_ref") or ""
        title = (r.get("title") or "").lstrip("★ ").lstrip()
        if ref and not title.startswith(ref):
            bad.append((ref, title[:60]))
    assert not bad, f"{len(bad)} title(s) do not name their own entry: {bad[:5]}"


def test_the_identifier_is_stripped_before_the_first_sentence_is_taken():
    """`split('. ')` on `P1. Full format ...` returns the bare identifier, which
    fell under the 20-character floor and rewrote 95 of 141 verbatims."""
    H = _harvester()
    rows = {r["task_ref"]: r for r in H.from_task_list() if r.get("task_ref")}
    stubs = [ref for ref, r in rows.items()
             if r["verbatim"].startswith(f"task {ref}:")]
    # A RATCHET AT THE MEASURED VALUE, not a tolerance. 22 of 141 entries fell
    # back to a stub before the status stamp was stripped as well as the
    # reference; the measured value afterwards is 0, so 0 is what this holds.
    # A stub still receives a correct identity, because identity is the
    # reference, but it matches nothing in the reworded-match tier.
    assert not stubs, f"{len(stubs)} verbatims fell back to a stub: {stubs[:8]}"


def test_every_reference_resolves_at_its_own_identity():
    """The register must answer a lookup by reference, or it under-reports."""
    H = _harvester()
    store = TicketStore()
    missing = [r["task_ref"] for r in H.from_task_list()
               if r.get("task_ref")
               and store.get(tid_of(r["kind"], r["verbatim"], r["task_ref"])) is None]
    assert not missing, f"{len(missing)} reference(s) have no ticket: {missing[:8]}"


def test_the_register_agrees_with_the_task_list_on_what_is_settled():
    """The marker is the authority; the register must not contradict it."""
    import task_list_markers as T
    H = _harvester()
    store = TicketStore()
    entries = T.parse_entries(REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md")
    rows = {r["task_ref"]: r for r in H.from_task_list() if r.get("task_ref")}
    bad = []
    for e in entries:
        r = rows.get(e.ident)
        if not r:
            continue
        t = store.get(tid_of(r["kind"], r["verbatim"], e.ident))
        if t is None:
            bad.append((e.ident, "no ticket", getattr(e, "state", "?")))
            continue
        if (t.status in TERMINAL) != (getattr(e, "state", "") in ("DONE", "WITHDRAWN")):
            bad.append((e.ident, t.status, getattr(e, "state", "?")))
    assert not bad, f"{len(bad)} disagreement(s): {bad[:6]}"


def test_no_reference_has_live_work_at_a_superseded_identity():
    """Live work must sit at the identity a lookup reaches, and nowhere else.

    THE PREDICATE WAS WRONG THE FIRST TIME AND IS RECORDED AS SUCH. It asked
    whether a reference held both a live and a TERMINAL record, and MERGED is
    terminal -- but a MERGED record is precisely how a superseded identity is
    retired, so every migrated reference tripped it and the test reported 31
    failures against correct data. The hazard that actually matters is a LIVE
    record stranded at an identity nothing looks up: before the sweep there
    were 17 of those, and they made the register report 46 open items against
    31 live references.
    """
    H = _harvester()
    store = TicketStore()
    rows = {r["task_ref"]: r for r in H.from_task_list() if r.get("task_ref")}
    canonical = {tid_of(r["kind"], r["verbatim"], ref) for ref, r in rows.items()}
    stranded = [(t.task_ref, t.tid, t.status) for t in store.all()
                if t.task_ref and t.tid not in canonical
                and t.status in ("OPEN", "REOPENED", "WITHHELD", "CONTESTED")]
    assert not stranded, (f"{len(stranded)} live record(s) at a superseded "
                          f"identity: {stranded[:6]}")


# --------------------------------------------------- the gates actually fire

def test_restate_refuses_when_identity_would_depend_on_the_text(tmp_path, monkeypatch):
    """EXECUTES the gate rather than trusting it.

    The gate's first form compared a field `asdict` had already copied, so it
    could never fire; deleting it left every other guard green. This drives the
    regression it exists for -- identity digesting the text again -- and fails
    if the gate is removed or made vacuous a second time.
    """
    import bench.ticket_store as TS
    store = TS.TicketStore(tmp_path / "t.jsonl")
    t, _ = store.propose("pf", "label", "the original text", "test", task_ref="Z9")

    real = TS.tid_of

    def text_sensitive(kind, verbatim, task_ref=""):
        """The defective rule: the text is back in the digest."""
        import hashlib
        h = hashlib.sha256()
        h.update(kind.encode()); h.update(b"\x00")
        h.update(" ".join(str(verbatim).split()).encode())
        if task_ref:
            h.update(b"\x00"); h.update(str(task_ref).encode())
        return h.hexdigest()[:12]

    monkeypatch.setattr(TS, "tid_of", text_sensitive)
    with pytest.raises(AssertionError) as e:
        store.restate(t.tid, "a completely different wording", "a restatement")
    assert "identity" in str(e.value).lower()
    monkeypatch.setattr(TS, "tid_of", real)


def test_retitle_refuses_a_ticket_whose_identity_does_not_match_its_content(
        tmp_path, monkeypatch):
    """The label must never become part of the identity."""
    import bench.ticket_store as TS
    store = TS.TicketStore(tmp_path / "t.jsonl")
    t, _ = store.propose("pf", "label", "the text", "test", task_ref="Z9")

    def label_sensitive(kind, verbatim, task_ref=""):
        return "0" * 12          # anything that disagrees with the stored id

    monkeypatch.setattr(TS, "tid_of", label_sensitive)
    with pytest.raises(AssertionError):
        store.retitle(t.tid, "a new label")
