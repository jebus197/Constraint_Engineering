"""A finding's description is kept whole, and any cut says so.

FOUNDER RULING 2026-08-30: "Fix it now fully. Option 1. Truncation has been the
bane of this project from the outset. If this is a new route to, or a new kind of
truncation, it should not be allowed to persist."

THE TWO CUTS, measured live on 2026-08-31 by RUNNING the parser, not reading it:

    well-formed DESCRIPTION field   900 chars in -> 900 out   (never cut)
    block with NO DESCRIPTION field 900 chars in -> 200 out   block[:200]
    wholly unstructured reply       900 chars in -> 500 out   response[:500]

Across the archive: 714 of 2,286 descriptions are exactly 200 characters and 661
exactly 500 -- 1,375 of 2,286, or 60.2%, Wilson CI [58.1%, 62.2%], sitting
exactly on a cut.

BOTH ARE FALLBACK PATHS, which is what makes them serious rather than untidy:
they fire precisely when a model's reply did NOT match the expected shape, so the
finding we understand least was the one recorded least of.

ACCEPTED CONSEQUENCE: parsing changes mid-arc, so any measure derived from
description TEXT is not comparable between Exp 40-49 and later runs. The founder
took that trade knowingly.
"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from runner_core import parse_findings, _bounded_description, _DESCRIPTION_LIMIT

HEAD = ("FINDING_ID: M_F001\nSEVERITY: 0.6\nFLAW_CLASS: 2\n"
        "ABSTRACTION_INDEX: 0.5\n")


def _desc(text):
    f = parse_findings("M", 0, text)
    return f[0].description if f else ""


class TestTheFallbacksNoLongerCut:
    def test_a_block_without_a_description_field_keeps_its_text(self):
        d = _desc(HEAD + "Y" * 900)
        assert len(d) > 500, (
            f"the block[:200] fallback is back: {len(d)} chars kept from 900"
        )

    def test_an_unstructured_reply_keeps_its_text(self):
        d = _desc("W" * 900)
        assert len(d) > 500, (
            f"the response[:500] fallback is back: {len(d)} chars kept from 900"
        )

    def test_neither_lands_on_the_old_cut_lengths(self):
        for text in (HEAD + "Y" * 900, "W" * 900):
            assert len(_desc(text)) not in (200, 500)


class TestWellFormedDescriptionsAreUntouched:
    def test_a_900_character_description_survives_whole(self):
        assert len(_desc(HEAD + "DESCRIPTION: " + "X" * 900)) == 900

    def test_a_short_description_is_unchanged(self):
        assert _desc(HEAD + "DESCRIPTION: a short one") == "a short one"


class TestACutIsDeclared:
    def test_over_the_limit_says_so(self):
        d = _desc(HEAD + "Z" * 3000)
        assert "TRUNCATED" in d, "a cut description no longer declares itself"
        assert str(_DESCRIPTION_LIMIT) in d.replace(",", "")

    def test_under_the_limit_says_nothing(self):
        assert "TRUNCATED" not in _bounded_description("short")

    def test_the_limit_matches_what_registration_keeps(self):
        """Keeping more here than registration stores would just be lost."""
        src = (pathlib.Path(__file__).resolve().parents[1]
               / "reference_runner_v2.py").read_text(encoding="utf-8")
        assert "finding.description[:2000]" in src, (
            "registration's own cap moved; _DESCRIPTION_LIMIT should follow it"
        )
        assert _DESCRIPTION_LIMIT == 2000


class TestTheHelperItself:
    @pytest.mark.parametrize("text", ["", None, "   "])
    def test_empty_inputs_do_not_crash(self, text):
        assert _bounded_description(text) == ""

    def test_exactly_at_the_limit_is_not_marked(self):
        assert "TRUNCATED" not in _bounded_description("x" * _DESCRIPTION_LIMIT)

    def test_one_over_the_limit_is_marked(self):
        assert "TRUNCATED" in _bounded_description("x" * (_DESCRIPTION_LIMIT + 1))
