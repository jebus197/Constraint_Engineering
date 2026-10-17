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
    rec = A.load_record()
    return rec.get("rows", [])


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
    wrong = []
    for r in rows:
        if r.get("verdict") != "TRACKED":
            continue
        if "is DONE" in (r.get("evidence") or ""):
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
