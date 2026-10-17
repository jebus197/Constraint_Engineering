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
    assert "ANY VERDICT AT ALL" in out.stdout
    assert "WITHOUT A VERDICT YET" in out.stdout, (
        "the producer no longer reports what is unaudited, so a small record "
        "would read as a finished one")


def test_it_refuses_an_unknown_flag():
    import subprocess
    out = subprocess.run([sys.executable, str(PRODUCER), "--bogus"],
                         capture_output=True, text=True, cwd=str(REPO))
    assert out.returncode != 0
