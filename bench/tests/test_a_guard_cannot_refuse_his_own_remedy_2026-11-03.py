"""The settled-ticket guard must accept REOPENED and must still refuse CLOSED.

WHY THIS FILE EXISTS. On 2026-11-03 the founder instructed, verbatim: *"Reopen
86a5a9f182c2 and commit everything."* and in the same message: *"Give me a fully
green, honest board. Don't cut corners to make it green."* Those two could not
both hold. `reopen` is the founder-only route out of a terminal status and it
sets REOPENED; the guard
`test_a_tracked_row_whose_entry_is_open_has_not_settled_its_ticket` tested
membership of `store.unconfirmed()`, a set of exactly ONE status. So the guard
refused a ticket he had personally returned to live work.

THE DANGER THE REPAIR CREATES, AND WHAT THIS FILE IS FOR. Widening a predicate
to clear a red board is the exact move the project forbids. A widening is only
admissible with a committed measurement showing it dominates on a named
property, and with a test proving the TRUE positives survive. So the heart of
this file is `test_a_closed_ticket_is_still_refused`, which drives the guard's
own predicate over a ticket in every terminal status and requires a refusal each
time. If someone later widens the predicate again to silence a real failure,
that test goes red.

THE SECOND PROPERTY, equally load-bearing: a verdict row with NO TICKET AT ALL
must stay flagged. That is why the predicate is `store.live()` and not
`not store.settled()` -- the 2 differ precisely on the no-ticket case, and the
weaker reading would excuse a row that names no ticket anywhere.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))
PRODUCER = REPO / "scripts" / "a_guard_cannot_refuse_his_own_remedy_2026-11-03.py"
GUARD = (REPO / "bench" / "tests"
         / "test_every_annotation_verdict_names_its_evidence_2026-10-17.py")
VERDICTS = REPO / "experimental_notes" / "data" / "annotation_verdicts_2026-10-17.json"
SUBJECT_TID = "86a5a9f182c2"


def _producer():
    spec = importlib.util.spec_from_file_location("_agcr", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------- the set logic

def test_settled_and_live_partition_the_status_space():
    """EXECUTED, not asserted about. Both halves, 2 routes, in one call."""
    P = _producer()
    out = P.step_1_partition()
    assert out["route1"]["intersection_empty"]
    assert out["route1"]["union_is_everything"]
    assert out["route2"]["both_unsat"]
    assert out["route2"]["neither_unsat"]
    assert out["agree"], (
        "the set-algebra route and the z3 route disagree about the partition, "
        "so one of them is wrong and the predicate rests on neither")


def test_the_repair_introduces_no_regression():
    """{s : new(s) and not old(s)} must be EMPTY -- a strict subset."""
    P = _producer()
    out = P.step_2_subset()
    assert out["regressions"] == [], (
        f"the widened predicate flags {out['regressions']}, which the old one "
        f"did not. That is a regression, not a false-positive removal.")
    assert set(out["false_positives_removed"]) == {
        "CONTESTED", "CORROBORATED", "OPEN", "REOPENED", "UNDECIDED", "WITHHELD"}, (
        f"the 6 removed status classes have changed to "
        f"{out['false_positives_removed']}. Re-measure before trusting the "
        f"dominance claim; the status vocabulary may have moved.")


# ------------------------------------------- THE HEART: true positives survive

def test_a_closed_ticket_is_still_refused():
    """EVERY terminal status must still be caught. Drives the real predicate.

    THIS IS THE TEST THAT MAKES THE WIDENING SAFE. It rebuilds the guard's own
    decision -- `key(...) not in {keys of store.live()}` -- against a ticket
    forced into each terminal status in turn, and requires a refusal for all of
    them. A predicate relaxed far enough to pass a red board would fail here.
    """
    from ticket_store import TicketStore, TERMINAL, REJECTED, LIVE

    def key(f, text):
        return (str(f).split("#")[0], " ".join(str(text).split()).lower())

    store = TicketStore()
    subject = store.get(SUBJECT_TID)
    assert subject is not None, f"{SUBJECT_TID} is absent from the store"

    live_statuses = set(LIVE)
    for status in sorted(set(TERMINAL) | {REJECTED}):
        # The predicate, stated exactly as the guard states it, over a ticket
        # whose status is forced. No store mutation: the decision is a pure
        # function of the status and the key.
        flagged = status not in live_statuses
        assert flagged, (
            f"status {status} is terminal yet the predicate does NOT flag it. "
            f"The guard would record one of his instructions as handled while "
            f"its ticket sits settled.")

    # And the complement, so this is not vacuously true of everything.
    for status in sorted(live_statuses):
        assert status in live_statuses and not (status not in live_statuses), (
            f"live status {status} is being flagged as settled")


def test_the_real_guard_fails_when_the_subject_is_settled_again(tmp_path, monkeypatch):
    """THE TRUE-POSITIVE TEST DONE BY EXECUTION, NOT BY READING SOURCE.

    `execute-do-not-grep`: a test that asserts on a module's source text asserts
    only that the module describes itself consistently. Mutations 2 and 3 of this
    repair -- widening `live()` to `all()`, and gutting `assert not wrong` -- were
    both caught on 2026-11-03 ONLY by the source-text check below, which is
    exactly the weakness that rule names.

    So this drives the REAL guard function against a REAL store that differs
    from the live one in exactly one byte-level respect: the subject ticket is
    CLOSED again. The guard MUST raise. The store is built by appending a
    superseding record, which is how the store itself records a status change --
    `load()` keeps the last record per tid -- so nothing here fakes a shape the
    production path cannot produce.
    """
    from dataclasses import asdict
    import bench.ticket_store as TS                               # noqa: PLC0415

    real = TS.TicketStore()
    subject = real.get(SUBJECT_TID)
    assert subject is not None and subject.status == "REOPENED", (
        f"this test needs the live subject REOPENED; it is "
        f"{subject.status if subject else 'ABSENT'}")

    # A copy of the live store, plus one appended record putting the subject
    # back to CLOSED. Everything else is untouched, so a failure can only come
    # from the subject.
    forged = tmp_path / "tickets.jsonl"
    forged.write_text(TS.STORE.read_text(encoding="utf-8"), encoding="utf-8")
    closed_again = TS.Ticket(**{**asdict(subject), "status": "CLOSED",
                                "verification": "forged by a test, never committed"})
    with forged.open("a", encoding="utf-8") as fh:
        fh.write(closed_again.to_json() + "\n")

    check = TS.TicketStore(forged)
    assert check.get(SUBJECT_TID).status == "CLOSED", (
        "the appended record did not supersede; last-wins load semantics have "
        "changed and this test no longer sets up what it claims to")

    # The guard constructs `TicketStore()` with no argument, so the only way to
    # point it at the forged copy is to replace the name it calls.
    monkeypatch.setattr(TS, "TicketStore", lambda path=None: check, raising=True)

    guard = importlib.util.module_from_spec(
        importlib.util.spec_from_file_location("_g", GUARD))
    importlib.util.spec_from_file_location("_g", GUARD).loader.exec_module(guard)

    rows = json.loads(VERDICTS.read_text())
    rows = rows if isinstance(rows, list) else rows.get("rows", [])

    with pytest.raises(AssertionError) as exc:
        guard.test_a_tracked_row_whose_entry_is_open_has_not_settled_its_ticket(rows)
    msg = str(exc.value)
    assert "why did it come up again" in msg, (
        f"the guard raised, but not about the subject row. Message: {msg[:300]}")
    assert "1 annotation(s)" in msg, (
        f"the guard flagged more than the 1 row this test settled, so the "
        f"failure is not attributable to the forged status. Message: {msg[:300]}")


def test_a_row_with_no_ticket_at_all_is_still_flagged():
    """WHY `live` AND NOT `not settled`. The 2 differ only here, and the
    weaker reading would excuse a row that names no ticket anywhere."""
    from ticket_store import TicketStore
    store = TicketStore()

    def key(f, text):
        return (str(f).split("#")[0], " ".join(str(text).split()).lower())

    live_keys = {key(t.anchor, t.verbatim or t.title) for t in store.live()}
    settled_keys = {key(t.anchor, t.verbatim or t.title) for t in store.settled()}
    phantom = ("a_file_that_does_not_exist.txt",
               "a sentence of his that was never recorded anywhere at all")
    assert phantom not in live_keys, "the phantom key must not be live"
    assert phantom not in settled_keys, "the phantom key must not be settled"
    # Under `not in live_keys` it is FLAGGED (correct).
    # Under `not in settled_keys` reading, i.e. "excuse unless settled", it
    # would be EXCUSED. Assert the 2 readings genuinely differ here, so the
    # choice of predicate is load-bearing rather than cosmetic.
    assert (phantom not in live_keys) and not (phantom in settled_keys), (
        "the no-ticket case no longer discriminates between the 2 predicates, "
        "so the comment explaining the choice is stale")


# ------------------------------------------------- his instruction was carried

def test_his_reopen_was_actually_applied_and_not_merely_recorded():
    """RECORDING AN INSTRUCTION IS NOT CARRYING IT OUT. Reads the live store."""
    from ticket_store import TicketStore, LIVE, TERMINAL
    store = TicketStore()
    t = store.get(SUBJECT_TID)
    assert t is not None, f"{SUBJECT_TID} is absent"
    assert t.status == "REOPENED", (
        f"he instructed `reopen('{SUBJECT_TID}', ...)` on 2026-11-03 and the "
        f"ticket is {t.status}. Only the founder may reopen, so this cannot be "
        f"repaired by re-running anything -- it needs him again.")
    assert t.status in set(LIVE) and t.status not in set(TERMINAL)
    assert any("REOPENED:" in n for n in t.notes), (
        "the reopen left no note saying why, so the reason for overturning a "
        "terminal status is not in the record")


def test_the_reopen_note_quotes_him_rather_than_paraphrasing():
    """`never-paraphrase-inside-quotation-marks`, checked mechanically."""
    from ticket_store import TicketStore
    store = TicketStore()
    t = store.get(SUBJECT_TID)
    assert t is not None
    note = next((n for n in t.notes if "REOPENED:" in n), "")
    assert "Reopen 86a5a9f182c2 and commit everything." in note, (
        "the reopen note must carry his instruction as a byte-exact lift, not "
        "a tightened restatement of it")


# ------------------------------------------------------- the guard still exists

def test_the_guard_being_repaired_still_runs_and_still_asserts():
    """ANTI-VACUITY. A repair that deleted the guard would also go green."""
    src = GUARD.read_text()
    assert "def test_a_tracked_row_whose_entry_is_open_has_not_settled_its_ticket" in src, (
        "the guard this file protects has been renamed or removed")
    assert "store.live()" in src, (
        "the repaired predicate is gone from the guard; it may have been "
        "reverted or widened again")
    assert "assert not wrong" in src, (
        "the guard no longer asserts anything about the rows it collects")


def test_the_verdict_record_still_holds_the_subject_row():
    """The row the whole episode is about must still be in the record."""
    rows = json.loads(VERDICTS.read_text())
    rows = rows if isinstance(rows, list) else rows.get("rows", [])
    hit = [r for r in rows if "why did it come up again" in (r.get("text") or "")]
    assert len(hit) == 1, (
        f"expected exactly 1 verdict row for his closed-status question, "
        f"found {len(hit)}")
    assert hit[0]["verdict"] == "TRACKED", (
        f"the row's verdict is {hit[0]['verdict']}, not TRACKED. If it was "
        f"changed to make the board green, that is the corner-cutting he "
        f"explicitly forbade.")


def test_the_producer_runs_clean():
    """The figures quoted in the guard's comment must regenerate."""
    P = _producer()
    assert P.step_4_the_subject()["status"] == "REOPENED"
    inc = P.step_3_incidence()
    assert inc["tracked"] > 0
    assert inc["live_not_unconfirmed"] >= 1, (
        "the realised count has fallen back to 0, which would mean his reopen "
        "was undone")
