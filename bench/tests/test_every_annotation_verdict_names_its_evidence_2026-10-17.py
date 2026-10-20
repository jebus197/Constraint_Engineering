"""B25: the per-annotation verdict record, and what a row may not be.

Entry C0 audited 302 of his annotations and found 20 gaps. It NAMES NO
PRODUCING SCRIPT, so its figures are a claim about evidence rather than
evidence, and its coverage cannot be mapped onto the register's annotation
tickets: the window holds 318 and C0 claimed 302, and a count cannot say WHICH
items it covered. His instruction of 2026-10-16 is to pin a set and not a
count, because a count cannot say what moved and a set catches a swap.

So the verdicts are recorded as DATA, one row per annotation, each naming the
evidence that establishes it. This file guards the properties that make such a
record worth more than the prose it replaces.

THE RULE THAT MATTERS MOST: A ROW MAY NOT BE INVENTED. Every row's text must
match an annotation the reader actually finds. Without that, the record could
drift into a list of things I believe he said, which is strictly worse than no
record at all.

AND A GAP OR A RULING DOES NOT SETTLE A TICKET. A GAP becomes a task entry and
that entry's state governs it from then on; a RULING is a question of his that
no work of mine settles. Only TRACKED, ACTED_ON and UNDECIDABLE settle, and
UNDECIDABLE settles only in the sense that this instrument cannot answer it --
which is said rather than hidden.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
PRODUCER = REPO / "scripts" / "audit_his_annotations_2026-10-17.py"


def _mod():
    spec = importlib.util.spec_from_file_location("_audit", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = _mod()


@pytest.fixture(scope="module")
def rows():
    """Rows whose anchor still exists in his folder.

    ★ `anchor_lost` EXCLUDES A ROW FROM THE RESOLUTION TESTS, 2026-10-20, and it
    is an HONEST DEMOTION rather than a repair. 12 of his annotations on
    `TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt` ceased to exist: the file is
    108 lines and the verdicts name anchors at 108, 114, 116 and 120, and the
    text of all 12 is absent from the file body as well as from his other 682
    live annotations. Microsoft Word is the agent -- a Word owner file existed
    for that document at 2026-10-20T01:08:24 and every one of his .txt files is
    CR-only cp1252, Word's Macintosh Text save, which no modern editor writes.

    THE OBVIOUS REPAIR WOULD HAVE BEEN CIRCULAR AND WAS REFUSED. Resolving these
    rows against `experimental_notes/recovered/Founder_Annotations_Recovered_
    2026-10-19.md` would check them against a file derived from those same rows,
    turning `test_no_row_is_invented` -- whose stated purpose is to stop the
    record becoming a list of things I believe he said -- into a tautology. So
    they are set aside and NOT verified, and the test below requires every one
    of them to carry its cause and a surviving copy of his words."""
    rec = A.load_record()
    return [r for r in rec.get("rows", []) if not r.get("anchor_lost")]


@pytest.fixture(scope="module")
def lost_rows():
    rec = A.load_record()
    return [r for r in rec.get("rows", []) if r.get("anchor_lost")]


def test_every_lost_anchor_names_its_cause_and_preserves_his_words(lost_rows):
    """A demotion must cost something. A row set aside from verification has to
    say WHY and has to leave his words somewhere a reader can still find them,
    or `anchor_lost` becomes a way of silencing any inconvenient row."""
    import pathlib as _pl
    repo = pathlib.Path(__file__).resolve().parents[2]
    bad = []
    for r in lost_rows:
        if not r.get("lost_cause"):
            bad.append(f"{r['anchor']}: no lost_cause recorded")
            continue
        dest = r.get("recovered_in")
        if not dest:
            bad.append(f"{r['anchor']}: no recovered_in recorded")
            continue
        f = repo / dest
        if not f.is_file():
            bad.append(f"{r['anchor']}: recovered_in names {dest}, which does not exist")
            continue
        probe = " ".join(str(r.get("text", "")).split())[:48]
        if probe and probe not in " ".join(f.read_text(encoding="utf-8").split()):
            bad.append(f"{r['anchor']}: his words are NOT in {dest}")
    assert not bad, (
        f"{len(bad)} lost-anchor row(s) are demoted without preserving his "
        f"words or naming a cause:\n  " + "\n  ".join(bad))


def test_the_lost_set_is_not_a_dumping_ground(lost_rows, rows):
    """ANTI-ABUSE. If most of the record were set aside the tests above would
    assert almost nothing, and this guard would pass loudest the day it mattered
    least. 12 of 318 is 3.7736%, Clopper-Pearson [1.9648%, 6.4989%] by
    statsmodels, scipy and Wolfram in agreement."""
    total = len(lost_rows) + len(rows)
    assert total, "no rows at all"
    assert len(lost_rows) / total <= 0.10, (
        f"{len(lost_rows)} of {total} rows are set aside as lost "
        f"({100*len(lost_rows)/total:.4f}%). Above 10% the resolution tests no "
        f"longer describe the record.")


def test_the_producer_and_the_record_both_exist():
    assert PRODUCER.is_file()
    assert A.RECORD.is_file(), "the verdict record is missing entirely"


def test_every_row_carries_a_known_verdict(rows):
    bad = [r for r in rows if r.get("verdict") not in A.VERDICTS]
    assert not bad, (
        f"{len(bad)} row(s) carry a verdict outside {A.VERDICTS}: "
        f"{[r.get('verdict') for r in bad][:4]}")


def test_every_row_names_evidence_that_is_not_empty(rows):
    """A verdict without evidence is the prose C0 left behind, in JSON."""
    silent = [r for r in rows if not (r.get("evidence") or "").strip()]
    assert not silent, (
        f"{len(silent)} row(s) carry a verdict and no evidence: "
        f"{[r.get('text', '')[:40] for r in silent][:3]}")


def test_every_row_also_says_why(rows):
    thin = [r for r in rows if len((r.get("why") or "").split()) < 5]
    assert not thin, (
        f"{len(thin)} row(s) give no reason a reader could check: "
        f"{[r.get('text', '')[:40] for r in thin][:3]}")


def test_no_row_is_invented(rows):
    """THE RULE THAT MATTERS MOST. A row whose text matches no annotation would
    make the record a list of things I believe he said."""
    if not rows:
        pytest.skip("the record is empty; nothing to verify yet")
    try:
        reader = A._reader()
        live = {" ".join(a["text"].split()) for a in reader.annotations()}
    except Exception as exc:                                   # noqa: BLE001
        pytest.skip(f"his Responses folder is not readable here: {exc}")
    invented = [r for r in rows
                if " ".join((r.get("text") or "").split()) not in live]
    assert not invented, (
        f"{len(invented)} row(s) quote text that matches no annotation the "
        f"reader finds: {[r.get('text', '')[:50] for r in invented][:3]}")


def test_a_gap_or_a_ruling_never_settles_a_ticket():
    """EXECUTED against the module's own constant, so the 2 cannot drift."""
    assert "GAP" not in A.SETTLING, (
        "a GAP settles a ticket, but a gap is unfinished work: it becomes a "
        "task entry and that entry's state governs it")
    assert "RULING" not in A.SETTLING, (
        "a RULING settles a ticket, but nothing I do settles a question of his")
    assert set(A.SETTLING) <= set(A.VERDICTS)
    assert "TRACKED" in A.SETTLING and "ACTED_ON" in A.SETTLING


def test_the_coverage_figure_is_reported_against_the_window_not_the_record(rows):
    """A record of 3 rows must not read as complete because all 3 are sound.
    The denominator is the window, so the figure stays honest while small."""
    import subprocess
    out = subprocess.run([sys.executable, str(PRODUCER)], capture_output=True,
                         text=True, cwd=str(REPO))
    if out.returncode != 0:
        pytest.skip("the reader is unavailable in this checkout")
    #: THE LABEL CHANGED WHEN THE FIGURE DID. It used to read "ANY VERDICT AT
    #: ALL" and compare counts; it now reads "ANNOTATIONS WITH A VERDICT" and
    #: intersects sets, which is a different claim and says so.
    assert "ANNOTATIONS WITH A VERDICT" in out.stdout
    assert "WITHOUT A VERDICT YET" in out.stdout, (
        "the producer no longer reports what is unaudited, so a small record "
        "would read as a finished one")


def test_it_refuses_an_unknown_flag():
    import subprocess
    out = subprocess.run([sys.executable, str(PRODUCER), "--bogus"],
                         capture_output=True, text=True, cwd=str(REPO))
    assert out.returncode != 0


def test_a_tracked_row_whose_entry_is_open_has_not_settled_its_ticket(rows):
    """THE PROPERTY, CHECKED AGAINST THE LIVE REGISTER rather than against the
    close path's source. A TRACKED verdict says an entry GOVERNS the
    annotation; it does not say the entry is finished. Settling a ticket
    governed by an OPEN entry would record an instruction of his as handled
    while the work is still outstanding.

    Mutation on 2026-10-17 showed 8 rows would have settled wrongly if the
    condition were dropped, and nothing asserted it -- so this does."""
    if not rows:
        pytest.skip("the record is empty")
    from bench.ticket_store import TicketStore
    store = TicketStore()
    store.load()

    def key(f, text):
        return (str(f).split("#")[0], " ".join(str(text).split()).lower())

    unconfirmed = {key(t.anchor, t.verbatim or t.title)
                   for t in store.unconfirmed()}

    # ★ THE ESCAPE NOW READS THE LIVE MARKER, NOT THE ROW'S PROSE (2026-10-20).
    # It was `if "is DONE" in r["evidence"]`, a match against the sentence the
    # row was written with. A row recorded on 2026-10-17 says "entry C4 is OPEN"
    # because that was true then; C4 is now DONE | COMMITTED, and the string
    # does not move when the entry does. Measured: all 27 rows this guard was
    # refusing name entries that have since finished -- C4, C18, B28 and B27 are
    # DONE and B26 is WITHDRAWN -- so 27 of 27 were FALSE POSITIVES, and the
    # guard was reading a description of the state instead of the state. That is
    # the shape `execute-do-not-grep` names, inside a guard whose whole job is to
    # compare the record against the live register.
    import re as _re
    import sys as _sys
    _sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
    import task_list_markers as _tlm                             # noqa: PLC0415
    _entries = {e.ident: e for e in _tlm.parse_entries(
        pathlib.Path(__file__).resolve().parents[2]
        / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md")}
    _FINISHED = {"DONE", "WITHDRAWN", "DEFERRED"}

    def _its_entry_is_finished(row) -> bool:
        # PLURAL AND LISTS TOO. The first form of this read `entry X` only, and
        # missed "entries A10, A26 and C14 are DONE" entirely -- 1 of the 2 rows
        # still refused after the live-marker fix was a miss of exactly that
        # shape. Identifiers are harvested from the whole clause instead.
        ev = row.get("evidence") or ""
        idents = []
        for clause in _re.findall(
                r"entr(?:y|ies)\s+((?:[A-Z]?\d+[A-Za-z0-9.]*[,\s]*(?:and\s+)?)+)", ev):
            idents += _re.findall(r"[A-Z]?\d+[A-Za-z0-9.]*", clause)
        for ident in idents:
            e = _entries.get(ident)
            if e is not None and e.state in _FINISHED:
                return True
        return False

    wrong = []
    for r in rows:
        if r.get("verdict") != "TRACKED":
            continue
        if _its_entry_is_finished(r):
            continue
        if key(r["file"], r["text"]) not in unconfirmed:
            wrong.append(r["text"][:60])
    assert not wrong, (
        f"{len(wrong)} annotation(s) are recorded as TRACKED by an entry that "
        f"is NOT done, and their tickets have been settled anyway: {wrong[:3]}. "
        f"That records an instruction of his as handled while the work is "
        f"outstanding.")


def test_no_two_rows_share_an_anchor(rows):
    """A COLLAPSED ROW IS A LOST VERDICT, and this was nearly one.

    The record was first keyed on the file plus a hash of his words, and 37 of
    his annotations across 12 files share their exact text with a sibling in
    the SAME file: "Do it." appears twice in one report with different
    referents, and "Already ruled above." 3 times in another. Two such rows
    would have collapsed into 1 and the loss would have been invisible. The
    anchor now carries the line index."""
    if not rows:
        pytest.skip("the record is empty")
    seen = {}
    for r in rows:
        seen.setdefault(r["anchor"], []).append(r["text"][:40])
    dupes = {k: v for k, v in seen.items() if len(v) > 1}
    assert not dupes, (
        f"{len(dupes)} anchor(s) carry more than 1 row, so a verdict has been "
        f"collapsed into another: {list(dupes.items())[:2]}")


def test_every_anchor_resolves_to_exactly_one_annotation(rows):
    """An anchor that resolves to 2 annotations cannot say which it judged, and
    one that resolves to none is an invented row by another name."""
    if not rows:
        pytest.skip("the record is empty")
    try:
        reader = A._reader()
        ann = reader.annotations()
    except Exception as exc:                                   # noqa: BLE001
        pytest.skip(f"his Responses folder is not readable here: {exc}")
    by_anchor = {}
    for a in ann:
        by_anchor.setdefault(f"{a['file']}#{a.get('line_index')}", []).append(a)
    wrong = []
    for r in rows:
        hits = by_anchor.get(r["anchor"], [])
        if len(hits) != 1:
            wrong.append((r["anchor"], len(hits)))
    assert not wrong, (
        f"{len(wrong)} anchor(s) do not resolve to exactly 1 annotation: "
        f"{wrong[:4]}")


def test_coverage_is_a_set_intersection_and_not_a_count_ratio(rows):
    """THE ERROR THIS CATCHES HAPPENED, and it happened in this very producer.

    On 2026-10-17 the report said "318 of 318 = 100.0000%" and "WITHOUT A
    VERDICT YET: 18" in the same breath. Two rules about one question: the
    figure compared len(rows) to len(annotations), while the missing list
    matched on raw text. A count ratio reports 100% for 318 rows that miss 18
    annotations and duplicate 18 others, and his own instruction is to pin a
    SET, not a count, because a count cannot say what moved and a set catches
    a swap.

    Both now use the anchor, and this asserts the property rather than the
    figure: every row must point at a real annotation and every annotation in
    the window must have a row, so the 2 sets are equal."""
    if not rows:
        pytest.skip("the record is empty")
    try:
        ann = [a for a in A._reader().annotations()
               if str(a.get("date", "")) >= A.WINDOW_FROM]
    except Exception as exc:                                   # noqa: BLE001
        pytest.skip(f"his Responses folder is not readable here: {exc}")
    want = {f"{a['file']}#{a.get('line_index')}" for a in ann}
    have = {r["anchor"] for r in rows}
    orphans = sorted(have - want)
    uncovered = sorted(want - have)
    assert not orphans, (
        f"{len(orphans)} row(s) point at no annotation in the window: "
        f"{orphans[:4]}. A row that matches nothing inflates any count ratio "
        f"while covering nothing.")
    assert not uncovered, (
        f"{len(uncovered)} annotation(s) in the window have no row: "
        f"{uncovered[:4]}. A count ratio would have hidden this behind an "
        f"equal number of orphan rows.")


def test_every_verdict_class_is_actually_used(rows):
    """An unreachable class is a distinction that decides nothing. All 5 are
    used: 90 TRACKED, 84 ACTED_ON, 72 RULING, 59 NOTED, 13 UNDECIDABLE."""
    if len(rows) < 50:
        pytest.skip("too few rows to expect every class")
    used = {r["verdict"] for r in rows}
    unused = set(A.VERDICTS) - used - {"GAP"}
    assert not unused, (
        f"verdict class(es) {sorted(unused)} are declared and never used. GAP "
        f"is exempt because a gap becomes a task entry and the row is then "
        f"re-verdicted as TRACKED, so an empty GAP set is the healthy state.")


def test_the_finished_entry_escape_is_not_a_blanket_pass():
    """ANTI-VACUITY FOR THE ESCAPE ITSELF, added 2026-10-20 after a mutation.

    Replacing `if _its_entry_is_finished(r)` with `if True` left the whole file
    GREEN, because no live row currently sits in the state the escape exists to
    refuse. So the guard above could not distinguish a working escape from one
    that passes everything, and the escape is the half that was just rewritten.

    This exercises the predicate directly against constructed rows, so it holds
    whatever the live record happens to contain."""
    import re
    import sys as _sys
    repo = pathlib.Path(__file__).resolve().parents[2]
    _sys.path.insert(0, str(repo / "scripts"))
    import task_list_markers as tlm                              # noqa: PLC0415
    entries = {e.ident: e for e in tlm.parse_entries(
        repo / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md")}
    FINISHED = {"DONE", "WITHDRAWN", "DEFERRED"}

    def finished(evidence: str) -> bool:
        idents = []
        for clause in re.findall(
                r"entr(?:y|ies)\s+((?:[A-Z]?\d+[A-Za-z0-9.]*[,\s]*(?:and\s+)?)+)",
                evidence):
            idents += re.findall(r"[A-Z]?\d+[A-Za-z0-9.]*", clause)
        return any(entries.get(i) and entries[i].state in FINISHED for i in idents)

    open_ids = [i for i, e in entries.items() if e.state == "OPEN"]
    done_ids = [i for i, e in entries.items() if e.state == "DONE"]
    assert open_ids and done_ids, "need both an open and a done entry to test this"

    assert not finished(f"entry {open_ids[0]} is OPEN; the work is outstanding"), (
        "the escape fired for an entry that is OPEN, so it is a blanket pass and "
        "the settlement guard asserts nothing")
    assert finished(f"entry {done_ids[0]} is DONE"), (
        "the escape did not fire for a finished entry, so every finished row "
        "would be reported as a wrongly-settled ticket")
    assert finished(
        f"entries {done_ids[0]}, {done_ids[1]} and {done_ids[2]} are DONE"), (
        "the plural, comma-separated form is not matched; this is the exact "
        "miss that left 1 row refused on 2026-10-20")
    assert not finished("bench/some_file.py and a note, with no entry named"), (
        "evidence naming no entry at all was treated as finished")
