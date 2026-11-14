"""An entry that asks him something must survive every gate between it and him.

★ ENTRY B189 -- the spoken report under-counting his decisions -- reported 3
entries marked as HIS appearing 0 times in the generated decisions file. Checked
2026-11-14 at the commit before that entry was written: **B81 and B103 were
already DONE and COMMITTED**, so their absence was correct and the entry was
wrong on 2 of its 3. **B175 was the 1 real case, and it was invisible through 4
INDEPENDENT gates**, each sufficient on its own:

  1. **THE ASK PATTERN.** `how_many_decisions_actually_need_him_2026-11-01.ASKS`
     requires "is his TO RULE", "so it is his" or an explicit NEEDS-HIS-RULING
     spelling. B175 says **"THE 17-MINUTE REDESIGN IS HIS, because it changes
     what a test asserts"** -- the bare possessive, in none of them.

  2. **THE SUPPRESSION FLAG, AND ITS OWN TEXT ADMITTED THE PROBLEM.** Its
     authored detail carried `no_ruling_needed` = *"The 2 writes are mine to fix
     and the seam is already prepared. Only the 17-minute redesign is his..."*.
     The generator reads that field's TRUTHINESS, never its content, so a
     nuanced reason suppressed the whole entry while saying part of it was his.
     Measured: 32 of 61 records carry a truthy flag, 25 as a boolean and 7 as
     PROSE.

  3. **THE TITLE CONVENTION.** `do_the_two_decision_surfaces_agree_2026-11-01
     .derived()` parses the entry identifier out of the rendered HEADING TEXT, so
     a title not beginning with its own code yields a garbage ident -- `'The'`
     for B175. 4 of 49 records breached it, 0.081633, Wilson [0.032203,
     0.191891]: B175, B176, B177 and B178, all written in 1 batch.

  4. **A STALE AUTHORED-DETAIL RECORD REFUSED THE WHOLE GENERATOR.** Closing
     B183 earlier the same night left its detail behind, and the generator
     correctly exited 3 rather than render a file disagreeing with the task
     list. Closing an entry means removing its authored detail too.

★ THE PATTERN REPAIR IS A COMPOSED FIX WITH THE MEASUREMENT HIS STANDARD
DEMANDS. Widening alone adds 4 entries of which 1 is a FALSE POSITIVE -- B189
itself, whose sentence DESCRIBES other entries' asks and names 4 of them, the
describing-read-as-carrying class B169 records. Excluding a sentence that names
another entry discriminates 4 of 4. Over the live task list: neither 60;
widening alone 64, precision 0.750000; exclusion alone 60, INERT; both 63,
precision 1.000000. The composed form dominates and the exclusion is no
substitute, so the composition is justified rather than merely non-conflicting.

EXECUTES the predicates and the generator's own collection path.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def decide():
    return _load("decide_guard", "scripts/how_many_decisions_actually_need_him_2026-11-01.py")


@pytest.fixture(scope="module")
def detail():
    return json.loads(DETAIL.read_text(encoding="utf-8"))


# ── gate 1: the bare possessive form ──────────────────────────────────────

@pytest.mark.parametrize("sent,want", [
    ("THE 17-MINUTE REDESIGN IS HIS, because it changes what a test asserts.", True),
    ("The move is his because the entry records his decision.", True),
    ("that question is his.", True),
    ("The mypy config decision remains his.", True),
    ("the choice is yours.", True),
])
def test_the_bare_possessive_form_is_read_as_an_ask(decide, sent, want):
    hit = bool(decide.ASKS.search(sent) or decide._BARE_POSSESSIVE_ASK.search(sent))
    assert hit is want, sent


@pytest.mark.parametrize("sent", [
    "the founder's own machine is his and nobody else's",
    "his ruling of 2026-11-08 is already recorded",
    "the credit is his for spotting it",
])
def test_ordinary_prose_about_him_is_not_an_ask(decide, sent):
    assert not decide._BARE_POSSESSIVE_ASK.search(sent), (
        f"{sent!r} was read as an ask; the bare form must require a decision "
        f"noun immediately before the possessive")


def test_a_sentence_naming_another_entry_describes_rather_than_asks(decide):
    """★ THE EXCLUSION THAT MAKES THE WIDENING SAFE, driven through
    `classify_text` rather than against the patterns.

    THE FIRST VERSION OF THIS TEST WAS WEAK AND THE MUTATION HARNESS SAID SO.
    It asserted only that the bare form MATCHED and that other entry codes were
    PRESENT, so removing the exclusion from the classifier left it green. A test
    on the pieces is not a test on the decision they make.
    """
    carrying = ("**B900. A TITLE.** THE 17-MINUTE REDESIGN IS HIS, because it "
                "changes what a test asserts.")
    describing = ("**B901. A TITLE.** 3 entries the task list itself marks as HIS "
                  "appear 0 times: B175, whose own status says the 17-minute "
                  "redesign is his; B81; and B103.")
    got_carry = decide.classify_text("OPEN", None, carrying)
    got_desc = decide.classify_text("OPEN", None, describing)
    assert got_carry["live_asks"], (
        "an entry stating the decision is his in the bare form carries no ask")
    assert not got_desc["live_asks"], (
        f"a sentence DESCRIBING other entries' asks was read as carrying one: "
        f"{got_desc['live_asks']}. That is the B169 class, and B189 had already "
        f"been reworded once for it in a different predicate.")


def test_the_bare_form_reaches_still_asks_and_not_only_the_pattern(decide):
    """★ ADDED BECAUSE THE HARNESS CAUGHT ITS ABSENCE. Disabling the classifier's
    USE of the bare form left every pattern test green, because they all asked
    the regex rather than the function the report consults."""
    mrb = _load("mrb_bare_guard", "scripts/morning_report_build_2026-10-12.py")
    import task_list_markers as tlm
    rows = {e.ident: e for e in tlm.parse_entries()}
    e = rows.get("B175")
    if e is None or (e.state or "").upper() in ("DONE", "WITHDRAWN"):
        pytest.skip("B175 is no longer live")
    assert mrb.still_asks("B175") is True, (
        "`still_asks` does not see B175's ask, so the turn counter and the "
        "whose-move-is-it producer both read it as mine")


# ── gate 2: a suppression flag must not admit that part is his ─────────────

_ADMITS = re.compile(
    r"\b(?:is|are|remains)\s+(?:his|yours)\b|\bneeds?\s+(?:his|your)\b", re.I)
#: A flag whose text says the ruling is ALREADY RECORDED is correctly suppressed.
_SPENT = re.compile(r"already recorded|he ruled it|already ruled|ruling is spent", re.I)


def test_no_suppression_flag_admits_an_unresolved_ask(detail):
    offenders = []
    for key, rec in detail.items():
        if not isinstance(rec, dict) or not rec.get("no_ruling_needed"):
            continue
        for field in ("no_ruling_needed", "_why_no_spoken_heading"):
            s = rec.get(field)
            if isinstance(s, str) and _ADMITS.search(s) and not _SPENT.search(s):
                offenders.append((key, field, s[:110]))
    assert not offenders, (
        "a record is suppressed from the decisions file while its own text says "
        "something is his:\n" + "\n".join(f"  {k} [{f}] {s}" for k, f, s in offenders))


# ── gate 3: the title must carry its own identifier ───────────────────────

def test_every_record_title_starts_with_its_own_entry_code(detail):
    """`derived()` parses the ident out of the heading text, so a title not
    starting with its code yields a garbage ident -- `'The'` for B175."""
    bad = []
    for key, rec in detail.items():
        if not (isinstance(rec, dict) and key.startswith("task:B")):
            continue
        code = key.split(":", 1)[1]
        title = rec.get("title") or ""
        if not re.match(rf"^{re.escape(code)}\b", title):
            bad.append((code, title[:70]))
    assert not bad, (
        "titles not beginning with their own entry code, which makes the "
        "surfaces-agree check parse a garbage identifier:\n"
        + "\n".join(f"  {c}: {t}" for c, t in bad))


# ── gate 4: no authored detail for an entry that is no longer live ─────────

def test_no_authored_detail_survives_its_entry_closing(detail):
    """A stale record makes the generator REFUSE outright, exit 3, so the whole
    file he reads disappears rather than one item."""
    import task_list_markers as tlm
    live = {e.ident for e in tlm.parse_entries()
            if (e.state or "").upper() not in ("DONE", "WITHDRAWN")}
    stale = [k for k in detail
             if k.startswith("task:B") and k.split(":", 1)[1] not in live]
    assert not stale, (
        f"authored detail for {len(stale)} entry/entries no longer live: {stale}. "
        f"The generator refuses rather than rendering a file that disagrees with "
        f"the task list, so this costs him the whole document.")


# ── end to end: the entry actually arrives ────────────────────────────────

def test_the_generator_collects_without_a_garbage_identifier():
    gen = _load("gen_guard", "scripts/build_decisions_file_2026-11-07.py")
    _mod, rows = gen.collect()
    assert rows, "0 decisions collected, so a pass here would be a false pass"
    idents = [(r.get("ident") or "") for r in rows]
    bad = [i for i in idents if not re.fullmatch(r"B\d{1,4}", i)]
    assert not bad, (
        f"the generator collected {bad} as identifiers; `derived()` parses the "
        f"ident out of the rendered heading, so a malformed title lands here")


def test_b175_reaches_the_decisions_file(detail):
    """★ THE REGRESSION CASE, named because it was invisible through 4 gates.

    SKIPS if B175 ever stops being live, because the assertion is about the
    gates and not about that entry existing forever.
    """
    import task_list_markers as tlm
    rows = {e.ident: e for e in tlm.parse_entries()}
    e = rows.get("B175")
    if e is None or (e.state or "").upper() in ("DONE", "WITHDRAWN"):
        pytest.skip("B175 is no longer live; the gates are covered by the tests above")
    gen = _load("gen_guard_b175", "scripts/build_decisions_file_2026-11-07.py")
    _mod, collected = gen.collect()
    assert "B175" in [(r.get("ident") or "") for r in collected], (
        "B175 asks him whether the mirrors test should assert the hook's first "
        "stage, and it has stopped reaching the file he reads")
