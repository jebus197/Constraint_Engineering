"""A deliverable pair has 3 possible relationships and 3 different correct checks.

WHY THIS EXISTS, AND IT IS MY OWN REPEATED ERROR MADE MECHANICAL. On 2026-11-03
a pre-delivery check compared a markdown file against its text-to-speech twin,
found different hashes, and reported a delivery defect. There was none. The
protocol REQUIRES those 2 formats to differ: a text-to-speech file carries no
markdown, so the heading markers are present in 1 and absent in the other. The
predicate was wrong for that pairing, and it was the 11th error of that session
in which an instrument answered a narrower question than the one it was asked.

THE 3 RELATIONSHIPS, each with its own correct check.

  SAME FORMAT -- the repository text copy against the Desktop text copy. These
  must be BYTE-IDENTICAL, and `scripts/raise_an_entry_2026-11-02.py` already
  checks exactly that at its 6th surface. Not duplicated here.

  CONVERTED CROSS-FORMAT -- a markdown file produced from, or alongside, the
  same prose as its text twin. These must be identical ONCE HEADING MARKERS ARE
  STRIPPED. Nothing checked this, and a drift here means the file the founder
  reads is not the file that was committed. That is the gap this file closes.

  INDEPENDENTLY RENDERED -- the morning report, which has 2 renderers,
  `render_md` and `render_tts`, deliberately producing different prose for
  reading and for hearing: 364 lines against 461, differing from the title
  onward. Byte identity and markers-only are BOTH wrong for it, so it is
  excluded by name with that reason, following the convention the producer
  guards use.

ANTI-VACUITY IS THE POINT, NOT AN EXTRA. A guard over a hand-written list of
pairs passes trivially when the list is empty or when a pair is absent, so the
list is asserted non-empty, every named file must exist, and a planted
divergence must fail -- which is checked in-process rather than asserted.
"""
from __future__ import annotations

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
NOTES = REPO / "experimental_notes"
DESK = pathlib.Path.home() / "Desktop" / "CDSFL_tts"

#: Converted pairs: the markdown and the spoken copy carry the SAME prose, and
#: must differ only by heading markers.
CONVERTED = (
    "Reply_To_Your_Questions_2026-11-02",
    "Session_Self_Audit_2026-11-03",
    "Decisions_Awaiting_You_2026-11-03",
    # ADDED 2026-11-04. Both pairs below were found with a STALE spoken
    # twin: the markdown gained a section and the .txt was not
    # re-rendered, so the founder would have read aloud a copy 3.5 hours
    # behind the one he could read. Both carry 0 bold spans, 0 backticks
    # and 0 em-dashes, so markers-only is the right rule for them.
    "Decisions_Awaiting_You_2026-11-04",
    "Closing_Report_The_Period_2026-11-04",
)

#: Pairs where neither identity NOR markers-only applies, with the reason.
INDEPENDENTLY_RENDERED = {
    "Morning_Report_2026-11-03_GENERATED":
        "2 renderers, render_md and render_tts, deliberately produce different "
        "prose for reading and for hearing; 364 lines against 461",
}


def _strip_markers(s: str) -> str:
    """Normalise BOTH sides to prose before comparing them.

    Heading hashes were the only thing stripped here, which accused a correct
    pair: the spoken copy of Closing_Report_The_Period_2026-11-04 carries 0
    asterisks and 0 backticks against the markdown's 18 and 6, because the
    zero-markup rule for spoken files requires exactly that. 9 of its 161 lines
    differed, every one of them only by removed bold spans and backticks.

    THIS IS NORMALISATION, NOT DETECTION, and the difference is why the
    false-positive measurements recorded for the markdown-in-a-spoken-file
    checker do not bind here. A bare backtick fires on a chemical SMILES string
    in 226 spoken files, so a one-sided DETECTOR may not look for it; removing
    it from both sides of a comparison is symmetric and changes no verdict,
    because a SMILES string loses its backticks on both sides equally.
    """
    out = []
    for ln in s.splitlines():
        ln = re.sub(r"^#+ ", "", ln)
        ln = re.sub(r"\*\*(.+?)\*\*", r"\1", ln)   # paired span only
        ln = ln.replace("`", "")
        out.append(ln)
    return "\n".join(out)


def _pair(stem: str):
    md = NOTES / f"{stem}.md"
    txt = DESK / f"{stem}.txt"
    if not md.is_file() or not txt.is_file():
        return None, None
    return md, txt


@pytest.mark.parametrize("stem", CONVERTED)
def test_a_converted_pair_differs_only_by_heading_markers(stem):
    """The founder reads the spoken copy; the repository keeps the markdown.
    If they say different things, 1 of the 2 is wrong and nobody can tell which.
    """
    md, txt = _pair(stem)
    if md is None:
        pytest.skip(f"{stem}: one side is absent from this checkout")
    a, b = _strip_markers(md.read_text(errors="replace")), \
        _strip_markers(txt.read_text(errors="replace"))
    if a != b:
        la, lb = a.splitlines(), b.splitlines()
        first = next((i for i, (x, y) in enumerate(zip(la, lb)) if x != y), None)
        detail = (f"line {first + 1}: {la[first][:70]!r} against "
                  f"{lb[first][:70]!r}" if first is not None
                  else f"lengths {len(la)} against {len(lb)}")
        pytest.fail(f"{stem}: the markdown and the spoken copy say different "
                    f"things once heading markers are stripped. {detail}")


@pytest.mark.parametrize("stem", CONVERTED)
def test_the_spoken_copy_of_a_converted_pair_carries_no_markdown(stem):
    """A heading marker in a spoken file is read aloud as a noise."""
    _md, txt = _pair(stem)
    if txt is None:
        pytest.skip(f"{stem}: the spoken copy is absent")
    bad = [ln for ln in txt.read_text(errors="replace").splitlines()
           if ln.lstrip().startswith("#")]
    assert not bad, (
        f"{stem}: {len(bad)} line(s) in the spoken copy open with a hash, which "
        f"a reader speaks or skips awkwardly: {bad[:2]}")


class TestTheGuardCannotPassVacuously:
    def test_the_converted_list_is_not_empty(self):
        assert CONVERTED, "an empty pair list would pass every test above"

    def test_every_named_pair_exists_or_is_explained(self):
        missing = [s for s in CONVERTED if _pair(s)[0] is None]
        assert not missing, (
            f"{missing} are declared as converted pairs but one side is absent, "
            f"so the assertions above skip and prove nothing")

    def test_a_planted_divergence_IS_detected(self):
        """The control. Without this, a comparison that always returned equal
        would satisfy every assertion above."""
        a = _strip_markers("# Title\n\nbody line\n")
        b = _strip_markers("Title\n\nbody line CHANGED\n")
        assert a != b, (
            "the comparison cannot distinguish different prose, so the pair "
            "assertions above would pass whatever the files held")
        same = _strip_markers("# Title\n\nbody\n")
        assert same == _strip_markers("Title\n\nbody\n"), (
            "the comparison does not treat a heading marker as the only "
            "permitted difference, so it would reject correct pairs")

    @pytest.mark.parametrize("stem", sorted(INDEPENDENTLY_RENDERED))
    def test_an_excluded_pair_states_a_mechanical_reason(self, stem):
        why = INDEPENDENTLY_RENDERED[stem]
        assert len(why) > 20 and "render" in why, (
            f"{stem} is excluded with the unhelpful reason {why!r}; an exclusion "
            f"nobody can argue with is an exemption in disguise")

    def test_no_pair_is_in_both_lists(self):
        overlap = sorted(set(CONVERTED) & set(INDEPENDENTLY_RENDERED))
        assert not overlap, f"{overlap} are both converted and independent"
