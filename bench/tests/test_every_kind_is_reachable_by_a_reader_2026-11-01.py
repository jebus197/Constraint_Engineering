"""A kind nothing can READ is a kind nothing can raise.

THE DEFECT THIS CLOSES, FOUND 2026-11-01 WHILE ADDING HIS `stm`. The marker
vocabulary is spelled out in **4** places -- `MARKER`, `CANDIDATE_LINE` and
`CITATION` in `scripts/harvest_tickets_2026-10-17.py`, and `KINDS` in
`bench/ticket_store.py` -- and they already disagreed. `disc` is a live kind
present in NONE of the 3 regexes; it works only because it is the DEFAULT for
unmarked text, so the marker itself is never parsed.

WHAT THAT COST HIM. He proposed `stm` on 2026-11-01 and used it twice in the
same message, before it existed. Both uses were filed as `disc`, because an
unknown marker falls through to the unmarked default and neither sentence ends
in a question mark. A statement that needs ACTION recorded as something to be
talked through misroutes the work -- the same fault as the 72 annotations once
filed as proposed fixes by an unconditional `pf` default.

4 DECLARATIONS OF 1 VOCABULARY WITH NO COMPARATOR is the `execute-do-not-grep`
shape: each is individually correct and nothing notices when they diverge. This
file is the comparator, and it CALLS the readers rather than reading them.
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

from bench.ticket_store import KINDS  # noqa: E402


def _harvester():
    spec = importlib.util.spec_from_file_location(
        "H_kinds", REPO / "scripts" / "harvest_tickets_2026-10-17.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["H_kinds"] = m
    spec.loader.exec_module(m)
    return m


#: KINDS THAT ARE DELIBERATELY NOT MARKER-READABLE, each with its reason.
#: `disc` and its 2 legacy spellings are the DEFAULT for unmarked text and are
#: refused as chat markers on purpose, because the colliding sense is what the
#: token means there. `wr` is work-remaining, written by the harvester itself.
DEFAULT_ONLY = {"disc", "dis", "ds"}


@pytest.fixture(scope="module")
def H():
    return _harvester()


def test_every_kind_is_either_readable_or_declared_default_only(H):
    unreachable = [k for k in KINDS
                   if k not in DEFAULT_ONLY and H.marked_kind(k) != k]
    assert not unreachable, (
        f"{len(unreachable)} kind(s) in KINDS cannot be read by MARKER and are "
        f"not declared default-only: {unreachable}. A kind nothing can read is "
        f"a kind he cannot raise, and his marker will fall silently to the "
        f"unmarked default -- which is what happened to `stm` on 2026-11-01.")


def test_the_prefilter_is_a_superset_of_every_readable_kind(H):
    """CANDIDATE_LINE rejects cheaply on raw JSON. A kind it cannot see is a
    kind the chat half drops before anything decodes it -- the realised defect
    of 2026-10-28, where `qs` and `wr` could never be harvested at all."""
    missed = [k for k in KINDS
              if k not in DEFAULT_ONLY and not H.CANDIDATE_LINE.search(k)]
    assert not missed, f"the chat prefilter cannot see: {missed}"


def test_a_citation_of_every_readable_kind_is_recognised_as_a_citation(H):
    """Raising and citing are opposite intents. A kind whose citation form is
    unrecognised would have every REFERENCE to an existing ticket harvested as
    a new proposal."""
    missed = [k for k in KINDS
              if k not in DEFAULT_ONLY
              and not H.CITATION.search(f"{k}:bc80040e3b48")]
    assert not missed, f"citations unrecognised for: {missed}"


def test_stm_is_live_and_reads_his_two_annotations(H):
    assert "stm" in KINDS
    for sentence in ("I remember this. Yes do it as instructed. stm",
                     "Retire them. stm"):
        assert H.marked_kind(sentence) == "stm", sentence


def test_stm_does_not_fire_inside_an_ordinary_word(H):
    """ANTI-VACUITY against the collision that killed `ds` and `dis`. If the
    token matched inside a word, the measurement saying it is safe would be
    describing a different token."""
    for word in ("The system is fine.", "a stem cell", "the statement above",
                 "custom tooling", "STM32 board"):
        assert H.marked_kind(word) is None, word


def test_the_default_only_kinds_really_are_the_default(H):
    """If `disc` became marker-readable this exemption would be hiding a
    reachable kind rather than documenting an unreachable one."""
    assert H._unmarked_kind("Retire them.") == "disc"
    assert H._unmarked_kind("Is this right?") == "qs"
    for k in DEFAULT_ONLY:
        assert k in KINDS, f"{k} is exempted here but is not a kind at all"
