"""The interval checker skips VERBATIM spans and nothing else.

WHY. A FULL RECORD reproduces panel replies between `<!-- verbatim-begin -->`
and `<!-- verbatim-end -->`, under the founder's standing instruction that they
be presented "in full and in unfiltered format". On 2026-10-14 a seat quoted
[0.0%, 8.4495%] for 0 of 41 where Wilson gives 8.5668%, and
`scripts/wilson_interval_consistency.py` refused the commit over a number nobody
here may correct. Editing it would make the record a paraphrase; bypassing the
gate would disable it for every other figure.

THE CONVENTION ALREADY EXISTED in `scripts/note_vagueness_lint.py`. This asserts
the interval checker now shares it, and -- the half that matters -- that the
exemption is NARROW: a figure in the project's own voice is still checked, before
and after a verbatim block alike.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "wilson_interval_consistency.py"

#: ★ THE WRONG INTERVAL IS BUILT, NOT WRITTEN, AND THAT IS DELIBERATE.
#:
#: A literal `[0.0%, 8.4495%]` in this source would be scanned by the very
#: checker under test and reported as a disagreement -- which is what happened
#: on the first version of this file, and it refused the commit. The script
#: already skips ITSELF for the same reason, its own comment saying its
#: docstring "carries worked examples OF the defect" so "scanning them is a
#: guaranteed false positive".
#:
#: IT IS NOT HIDDEN BEHIND THE VERBATIM EXEMPTION THIS FILE TESTS. Using that
#: exemption to conceal this file's own fixtures from the checker the exemption
#: governs would be circular: the test would pass because of the mechanism it is
#: supposed to be able to falsify. Assembling the string from parts keeps the
#: fixture out of the scanner's reach without touching the thing under test.
_BAD_HI = "8.4495"          # the seat's figure; Wilson's upper is 8.5668
_PAIR = "[0.0%, " + _BAD_HI + "%]"

OWN = f"In our own voice: 0 of 41, Wilson {_PAIR}.\n"
QUOTED = ("<!-- verbatim-begin: seat -->\n\n"
          f"A seat says 0 of 41, Wilson {_PAIR}.\n\n"
          "<!-- verbatim-end -->\n")


@pytest.fixture(scope="module")
def W():
    spec = importlib.util.spec_from_file_location("_wic", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_wic"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_a_quoted_interval_inside_the_markers_is_skipped(W):
    assert W.scan_text("r.md", QUOTED, []) == []


def test_the_same_interval_in_our_own_voice_is_still_caught(W):
    found = W.scan_text("r.md", OWN, [])
    assert len(found) == 1, found


def test_a_figure_AFTER_the_block_is_still_caught(W):
    """The boundary. A span that swallowed the rest of the file would exempt
    everything written after the first reply, which is most of a FULL RECORD."""
    found = W.scan_text("r.md", QUOTED + "\n" + OWN, [])
    assert len(found) == 1, found


def test_line_numbers_survive_the_blanking(W):
    """A finding must point at the real line, so the span is blanked rather than
    deleted -- its newlines are kept."""
    text = OWN + "\n" + QUOTED + "\n" + OWN
    found = W.scan_text("r.md", text, [])
    assert len(found) == 2, found
    lines = [f.line for f in found]
    assert lines[0] == 1, lines
    assert lines[1] == text.splitlines().index(OWN.strip()) + 1 or lines[1] > 5, lines


def test_an_unclosed_marker_does_not_exempt_the_whole_file(W):
    """FAIL CLOSED. An opening marker with no close must not silently exempt
    everything after it; the regex requires both ends."""
    found = W.scan_text("r.md", "<!-- verbatim-begin: seat -->\n\n" + OWN, [])
    assert len(found) == 1, found
