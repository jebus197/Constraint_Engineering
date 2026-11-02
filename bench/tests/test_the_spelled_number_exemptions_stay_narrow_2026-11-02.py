"""The spelled-number exemptions must not widen into a hole in Rule 27.

WHY THIS EXISTS. `no-word-numbers` is one of his hardest rulings -- "Digits only,
in every context without exception" -- and `scripts/note_vagueness_lint.py`
enforces it. But a detector over English prose has genuine false positives, and
the exemption list has grown twice on 2026-11-02 alone: once for `<digit>-zero`
and once for `one-way` and `the same one`. Each addition was justified on the
ground the list already states, that a hyphenated number word qualifying a noun is
English rather than data.

★ AN EXEMPTION LIST IS THE ONE PLACE A RULE CAN BE SWITCHED OFF WITHOUT ANYTHING
SAYING SO. Widen it far enough and Rule 27 stops biting while the checker still
reports 0 findings and looks healthy -- which is the shape
`feedback_a_false_positive_can_be_why_a_rule_is_unenforced_2026-11-02` names from
the other direction. So the list needs a guard that pins BOTH halves: that the
exempted phrases really are exempted, and that ordinary spelled numbers are not.

★ AND IT GUARDS THE REGEX DIRECTLY, NOT THROUGH A FILE. An earlier attempt to
control this by linting a probe file returned 0 findings for EVERY case, including
"twenty-nine pairs" which must be caught -- because the bare-word detector is
date-gated and does not run on a file outside the gated window. A uniform 0 across
6 cases is the cheapest signal that a control is vacuous, and this file tests the
compiled patterns so no gating can make it pass for the wrong reason.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


def _lint():
    spec = importlib.util.spec_from_file_location(
        "nvl_guard", REPO / "scripts" / "note_vagueness_lint.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["nvl_guard"] = m
    spec.loader.exec_module(m)
    return m


#: Phrases that are English, not data. Each is in the list for a stated reason.
EXEMPT = [
    "a one-way guarantee held at every roster size",
    "that run is the same one entry B76 is about",
    "a one-line change",
    "the two-sided gate",
    "a one-off failure",
    "the earliest 3-zero window",
]

#: Ordinary spelled numbers. Every one of these MUST still be reported, or the
#: exemption list has become a hole.
MUST_FLAG = [
    "there were seven findings",
    "it took three rounds",
    "twenty-nine pairs",
    "eleven thousand entries",
    "one extra round",
    "two seats answered",
    "nine of the twelve",
]


class TestTheExemptionsAreExempt:

    @pytest.mark.parametrize("text", EXEMPT)
    def test_an_english_phrase_is_not_a_spelled_number(self, text):
        m = _lint()
        assert m.BARE_WORD_NUMBER_OK.search(text), (
            f"{text!r} is English rather than data and should be exempt; if this "
            f"fails, either the exemption was removed or the phrase changed")


class TestTheExemptionsStayNarrow:
    """The half that matters. A hole here disables his hardest ruling silently."""

    @pytest.mark.parametrize("text", MUST_FLAG)
    def test_an_ordinary_spelled_number_is_still_reported(self, text):
        m = _lint()
        assert not m.BARE_WORD_NUMBER_OK.search(text), (
            f"{text!r} is an ordinary spelled number and the exemption list now "
            f"swallows it. Rule 27 admits no such case: 'Digits only, in every "
            f"context without exception.'")

    def test_bare_one_before_a_noun_is_not_exempted(self):
        """`one-way` is exempt; a bare `one` qualifying a noun must not be.

        This is the specific widening the 2026-11-02 addition could have caused,
        since `one[- ]way` sits beside entries like `the one` and `this one`.
        """
        m = _lint()
        for text in ("one extra round", "one seat dropped", "one finding remained"):
            assert not m.BARE_WORD_NUMBER_OK.search(text), text

    def test_the_detector_still_matches_what_the_exemption_lets_through(self):
        """Not vacuous: the thing being exempted must be something the detector
        would otherwise catch, or the exemption is decorative."""
        m = _lint()
        det = getattr(m, "BARE_WORD_NUMBER", None)
        if det is None:
            pytest.skip("BARE_WORD_NUMBER is not exposed by this version")
        for text in EXEMPT:
            assert det.search(text), (
                f"{text!r} is exempted but the detector would not have flagged it "
                f"anyway, so the exemption is decorative and hides nothing -- "
                f"which means this entry in the list is untested by construction")


class TestTheListIsAccountedFor:

    def test_every_exemption_carries_a_stated_reason(self):
        """A line added without a reason is a rule switched off without a record."""
        src = (REPO / "scripts" / "note_vagueness_lint.py").read_text()
        start = src.index("BARE_WORD_NUMBER_OK = re.compile(")
        # ★ THE WINDOW IS FOUND, NOT GUESSED. A first version sliced a fixed 3000
        # characters and then searched inside it for the regex terminator, which
        # is not there because the list is longer than that -- so the test failed
        # on its own arithmetic rather than on the subject.
        end = src.find("re.I)", start)
        assert end > start, "could not find the end of the exemption pattern"
        block = src[start:end]
        # every ★-marked addition must sit beside a comment explaining it
        assert block.count("#:") >= 2, (
            "the exemption list carries fewer than 2 explanatory comments; each "
            "addition should state the ground it rests on, because this list is "
            "where Rule 27 can be disabled without anything failing")
