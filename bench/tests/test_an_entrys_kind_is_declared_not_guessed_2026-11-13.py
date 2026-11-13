"""A task-list entry's ticket kind must come from its declaration, not 2 keywords.

ENTRY B168. `from_task_list` assigned every row its kind with a single
expression: `"fr" if ("orchestrator" in title or "selection" in title) else "pf"`.
Measured over the live list that gave `fr` to 3 of 174 entries -- B20, B21 and
B147 -- chosen because 2 words appear in a title, and none of the 3 declares
itself a feature request; while the entries that DO declare it came out `pf`.

The kind is not cosmetic. His ruling of 2026-10-17 is that a feature request
stays OPEN until implemented, merged or rejected, and that only he may reject
one, so a misfiled kind changes how an entry is tracked.

★ THE PATTERN WAS MEASURED BEFORE IT WAS WRITTEN, because a coarse pattern was
wrong 3 separate times earlier the same night. 4 open entries contain the phrase
"feature request"; only 2 DECLARE it in a structured STATUS line. A free-text
search matches all 4 and would file this entry's own description of the defect as
a feature request.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
HARVEST = REPO / "scripts" / "harvest_tickets_2026-10-17.py"
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"


@pytest.fixture(scope="module")
def h():
    sys.path.insert(0, str(REPO / "bench"))
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("cdsfl_harvest", HARVEST)
    m = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_harvest"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


def _entry(ident: str) -> str:
    s = LIST.read_text()
    i = s.index(f"**{ident}.")
    return s[i:s.index(f"<!-- task: {ident}", i)]


def test_a_declared_feature_request_is_filed_as_one(h):
    """The entries that say so in a STATUS line."""
    for ident in ("B161", "B163"):
        body = _entry(ident)
        assert re.search(r"\*\*STATUS:\s*FEATURE\s+REQUEST\b", body, re.I), (
            f"{ident} no longer declares itself a feature request; this contract "
            f"needs a new fixture rather than a weaker assertion")
        assert h.task_entry_kind(body) == "fr", (
            f"{ident} declares FEATURE REQUEST in its STATUS line and was filed "
            f"as {h.task_entry_kind(body)!r}")


def test_merely_mentioning_the_phrase_is_not_declaring_it(h):
    """The boundary, and the reason the pattern is anchored to STATUS.

    B168 is the entry describing this defect: its TITLE contains the phrase. B169
    quotes his rule about feature requests in general. A free-text search files
    both as feature requests, which would be the detector accusing correct prose.
    """
    for ident in ("B168", "B169"):
        body = _entry(ident)
        assert re.search(r"FEATURE\s+REQUEST", body, re.I), (
            f"{ident} no longer mentions the phrase; the fixture is stale")
        assert h.task_entry_kind(body) == "pf", (
            f"{ident} only MENTIONS feature requests and was filed as "
            f"{h.task_entry_kind(body)!r}")


def test_two_title_keywords_no_longer_decide_anything(h):
    """The defect itself: `orchestrator` and `selection` in a title meant `fr`."""
    for ident in ("B20", "B21", "B147"):
        body = _entry(ident)
        title = body[:body.index("**", 3)] if "**" in body[3:] else body[:200]
        old = "fr" if ("orchestrator" in title.lower()
                       or "selection" in title.lower()) else "pf"
        assert old == "fr", f"{ident} no longer demonstrates the old rule"
        assert h.task_entry_kind(body, title) == "pf", (
            f"{ident} is still filed as a feature request on the strength of a "
            f"title keyword, having never declared itself one")


def test_an_explicit_marker_wins_over_the_declaration(h):
    """`marked_kind` is the project's existing declaration mechanism."""
    # ★ AN EXACT VALUE, NOT A SET. The first version asserted the kind was in
    # ("qs", "fr") -- a hedge written because I had not checked which one it
    # would be -- and mutation Q4 then removed the marker consultation entirely
    # and the test STAYED GREEN, because "fr" was in the accepted set. A hedge is
    # not a contract: it passes under exactly the change it exists to forbid.
    body = "qs: something\n**STATUS: FEATURE REQUEST** and more text here"
    assert h.marked_kind(body) == "qs", "fixture no longer carries a marker"
    assert h.task_entry_kind(body) == "qs", (
        f"the explicit marker lost to the STATUS declaration: got "
        f"{h.task_entry_kind(body)!r}. `marked_kind` is the project's existing "
        f"declaration mechanism and must win, or there are 2 of them.")
    # ...and with no marker, the declaration decides.
    assert h.task_entry_kind("**STATUS: FEATURE REQUEST** text") == "fr"


def test_the_default_is_pf_and_never_a_guess(h):
    assert h.task_entry_kind("an entry declaring nothing at all") == "pf"
    assert h.task_entry_kind("") == "pf"
    assert h.task_entry_kind("the orchestrator and the selection of a model") == "pf", (
        "the 2 old keywords still decide the kind")


def test_his_annotation_rule_is_not_applied_to_entries(h):
    """`_unmarked_kind` encodes his ruling for HIS comments, not for entries.

    A question mark means `qs` and anything else `disc` -- correct for an
    annotation he wrote, wrong for a task entry, which would make every entry a
    discussion.
    """
    assert h._unmarked_kind("does this work?") == "qs", "fixture stale"
    assert h.task_entry_kind("does this work?") == "pf", (
        "an entry ending in a question mark was treated as HIS annotation")
    # ★ BY SYNTAX TREE, NOT BY SUBSTRING. The first version of this assertion
    # read `"_unmarked_kind" not in fn` and FAILED on its own first run, because
    # the name appears in task_entry_kind's DOCSTRING -- in the sentence
    # explaining why it is deliberately not used. A substring is not a call, and
    # a textual test cannot tell a mention from an invocation. That is the same
    # shape as the retraction defect repaired the same night, where a figure
    # quoted inside its own withdrawal read as a figure still printed.
    import ast
    tree = ast.parse(HARVEST.read_text())
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == "task_entry_kind"),
              None)
    assert fn is not None, "task_entry_kind is gone"
    called = {n.func.id for n in ast.walk(fn)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "_unmarked_kind" not in called, (
        f"task_entry_kind CALLS the annotation rule, which is a different ruling "
        f"about a different kind of text. Calls found: {sorted(called)}")
    assert "marked_kind" in called, (
        f"task_entry_kind no longer consults the project's existing declaration "
        f"mechanism. Calls found: {sorted(called)}")


def test_a_cited_ticket_is_not_a_raised_one(h):
    """★ Raising a ticket and citing one are opposite intents.

    `MARKER` accepts `qs:`, which is also the form of every REFERENCE to an
    existing ticket. The first version of `task_entry_kind` called `marked_kind`
    on the raw body, and B45 -- whose text CITES a closed question as
    `[qs:6b0997d1f6b9]` -- was filed as a question. That is the same
    mention-versus-declaration defect this whole repair exists to fix, committed
    by the repair itself one level down, and caught by an existing test pinning
    that task-list rows yield only `fr` and `pf`.

    The strip is the harvester's OWN mechanism, reused rather than re-derived.
    """
    cited = "The question [qs:6b0997d1f6b9] is CLOSED on that verification."
    assert h.task_entry_kind(cited) == "pf", (
        f"a CITED ticket was read as a RAISED one: {h.task_entry_kind(cited)!r}")
    assert h.task_entry_kind("`qs: inside a code span` and prose") == "pf", (
        "a marker inside a code span was read as a declaration")
    # ...and a genuine bare marker must still be honoured, or the strip has
    # removed the capability rather than narrowing it.
    assert h.task_entry_kind("qs" + chr(10) + "some question text") == "qs", (
        "a genuine marker stopped being read; the strip removed a capability")

    # NON-VACUOUS: the live entry that caused this must still carry the citation.
    body = _entry("B45")
    assert "qs:" in body, "B45 no longer cites a question; the fixture is stale"
    assert h.task_entry_kind(body) == "pf", (
        f"B45 cites a closed question and is filed as {h.task_entry_kind(body)!r}")
