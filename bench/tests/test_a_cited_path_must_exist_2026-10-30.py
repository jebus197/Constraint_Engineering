#!/usr/bin/env python3
"""A bare path citation in the master task list must name a real file.

THE GAP, AND IT IS A GAP RATHER THAN A DEFECT. B41 cited
`bench/tests/test_ladder_transport_2026-10-11.py`, a path with 0 commits in this
history, and nothing caught it.
`bench/tests/test_line_citations_resolve_2026-09-01.py` checks typed
`file.py:NNNN` citations and states that scope in its own docstring, so a
citation with no line number is outside it. It does what it says.

WHY THE BLANKET CHECK IS DELIBERATELY NOT BUILT, MEASURED BEFORE BUILDING
ANYTHING. Every tracked `.md` holds HUNDREDS of dead path citations, and the 4
largest concentrations -- 27, 24, 23 and 21 -- are `FULL_RECORD` panel
transcripts, which are VERBATIM SEAT OUTPUT. A seat citing a path that does not
exist is a record of what that seat said. `seat_evidence/` is the same. A guard
over all of them would accuse correct material, which is the 9-of-36 failure
class of 2026-10-28, so the scope is 1 document.

WHAT THE MEASUREMENT FOUND IN THAT DOCUMENT, AND WHY 2 OF THE 5 ARE NOT REPAIRED.
5 distinct dead citations. 3 are illustrative placeholders, 1 of which names its
own non-existence. The other 2 are both DELIBERATE absences:

  * `bench/capability_identity.py` sits inside a recorded lesson reading *"here
    I searched for a MODULE PATH I GUESSED ... found it absent and concluded
    nothing existed"*. The work landed in `bench/routing.py`. Correcting the
    path would destroy the sentence's whole point, so it is allowlisted. The
    first reading of this finding called it a stale citation to repair -- which
    would have edited away the lesson.
  * B41's ladder path is ANNOTATED IN PLACE rather than deleted, naming the real
    guard beside it, because point-never-prune applies to a record of an error
    as much as to data.

SO THE ALLOWLIST IS THE KNOWN SET AND ANYTHING NEW FAILS, which is
`feedback_pin_a_set_not_a_count` applied forward. Pinning 0 here is safe in a way
pinning a suspect list was not: acting on a dead citation KEEPS the count at 0,
so this cannot fire on its own success the way
`test_which_open_entries_already_have_his_ruling` did within an hour of being
written.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

PRODUCER = REPO / "scripts" / "a_cited_path_must_exist_2026-10-30.py"


def _producer():
    assert PRODUCER.is_file(), f"producer absent: {PRODUCER}"
    spec = importlib.util.spec_from_file_location("cited_path_probe", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _producer()


def _doc(text: str):
    """A throwaway document, so no test depends on the task list's contents."""
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                    encoding="utf-8")
    f.write(text)
    f.close()
    return pathlib.Path(f.name)


class TestTheCheckerDiscriminates:
    """Both directions, on synthetic documents no repair can erase."""

    def test_a_dead_citation_is_caught(self, mod):
        """POSITIVE CONTROL. Without it a 0 says nothing."""
        d = _doc("The fix went in `bench/no_such_module_abc123.py` today.\n")
        try:
            found = [x["cited"] for x in mod.dead_citations(d)]
        finally:
            d.unlink()
        assert found == ["bench/no_such_module_abc123.py"], (
            f"a citation to a file that does not exist was not reported: "
            f"{found}. Every 0 this checker prints would be uninformative.")

    def test_a_live_citation_is_not_caught(self, mod):
        d = _doc("See `scripts/task_list_markers.py` for the parser.\n")
        try:
            found = [x["cited"] for x in mod.dead_citations(d)]
        finally:
            d.unlink()
        assert found == [], f"a path that exists was reported dead: {found}"

    def test_a_citation_inside_a_verbatim_region_is_exempt(self, mod):
        """THE EXEMPTION, EXERCISED. Against today's task list it exempts 0
        citations, so it is precautionary -- and by the additive standard an
        addition nothing reaches is not additive. This is what reaches it.

        A seat's words are a RECORD. Editing a path a seat cited would falsify
        the record, which is why the exemption exists at all.
        """
        d = _doc(
            "Prose citing `bench/outside_one_zzz.py`.\n\n"
            "<!-- verbatim-begin: a seat -->\n"
            "The seat put it in `bench/inside_the_region_zzz.py` and nowhere else.\n"
            "<!-- verbatim-end -->\n\n"
            "More prose citing `bench/outside_two_zzz.py`.\n")
        try:
            found = {x["cited"] for x in mod.dead_citations(d)}
        finally:
            d.unlink()
        assert "bench/inside_the_region_zzz.py" not in found, (
            "a citation inside a verbatim region was reported, so the checker "
            "would demand edits to a record of someone else's words")
        assert found == {"bench/outside_one_zzz.py",
                         "bench/outside_two_zzz.py"}, (
            f"the exemption leaked outside the region: {found}")


class TestTheAllowlistIsHonest:
    def test_it_is_keyed_by_exact_name_and_not_by_pattern(self, mod):
        """A pattern matching `thing.py` or `x.json` would exempt a real file
        nobody decided to exempt."""
        d = _doc("A citation to `scripts/thing_but_different.py` here.\n")
        try:
            found = [x["cited"] for x in mod.dead_citations(d)]
        finally:
            d.unlink()
        assert found == ["scripts/thing_but_different.py"], (
            "a path merely RESEMBLING an allowlisted placeholder was exempted, "
            "so the allowlist is matching by pattern")

    def test_every_entry_carries_a_written_reason(self, mod):
        for path, why in mod.PLACEHOLDERS.items():
            assert isinstance(why, str) and len(why) >= 20, (
                f"{path} is allowlisted with no usable reason: {why!r}. An "
                f"allowlist without reasons becomes a place to hide findings.")

    def test_an_allowlisted_path_really_is_absent(self, mod):
        """An allowlist entry for a file that EXISTS is dead weight, and would
        silently keep exempting it if it were later deleted."""
        for path in mod.PLACEHOLDERS:
            assert not (REPO / path).exists(), (
                f"{path} is allowlisted but exists; remove the entry so the "
                f"path is checked like any other")


def test_the_task_list_has_no_unexplained_dead_citation(mod):
    """THE LIVE STATE. Pinning 0 is safe here: acting on a dead citation -- by
    repairing it or by allowlisting it with a reason -- KEEPS this at 0. It
    cannot fire on its own success."""
    dead = mod.dead_citations()
    assert dead == [], (
        f"{len(dead)} bare path citation(s) in the master task list name files "
        f"that do not exist and are neither allowlisted nor inside a verbatim "
        f"region: {[d['cited'] for d in dead]}. Either correct the citation, or "
        f"allowlist it WITH A WRITTEN REASON if the absence is deliberate.")
