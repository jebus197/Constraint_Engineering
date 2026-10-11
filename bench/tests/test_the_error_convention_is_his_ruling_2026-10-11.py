"""The error convention is two-sided because he ruled it, and it must not drift back.

HIS RULING, 2026-10-11: *"Yes. Use the two sided setting."* He asked first, on 2026-10-09: *"I
dont know what you are asking me to decide on here? What error convention?"*, so this was
explained and then decided rather than assumed.

WHY A GUARD AND NOT A COMMENT. The producers already used the two-sided value, but nothing
recorded it as a CHOICE, so a later edit could have swapped it for the per-side value without
anyone noticing a decision had been reversed. That is the shape of defect this project keeps
finding: a value that is right by habit rather than by record.
"""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "the_division_count_is_derivable_2026-10-08.py"


def _load():
    spec = importlib.util.spec_from_file_location("dcd_guard", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dcd_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTheConventionIsPinned:
    def test_the_two_sided_constant_is_the_975_quantile(self):
        from scipy.stats import norm
        m = _load()
        assert abs(m.TWO_SIDED_Z - norm.ppf(0.975)) < 1e-12, (
            "TWO_SIDED_Z is no longer the two-sided critical value")

    def test_the_per_side_alternative_is_recorded_and_is_different(self):
        """Both must be present, so a reader can see what was rejected as well as chosen."""
        from scipy.stats import norm
        m = _load()
        assert abs(m.PER_SIDE_Z - norm.ppf(0.95)) < 1e-9
        assert m.TWO_SIDED_Z != m.PER_SIDE_Z

    def test_the_producer_uses_the_two_sided_value_not_the_per_side_one(self):
        src = PRODUCER.read_text(encoding="utf-8")
        assert "z = TWO_SIDED_Z" in src, (
            "the producer no longer takes its critical value from the named constant")
        assert "z = PER_SIDE_Z" not in src, "the convention has been flipped against his ruling"

    def test_his_ruling_is_quoted_where_the_value_is_set(self):
        """A number without its ruling is a number someone will change."""
        src = PRODUCER.read_text(encoding="utf-8")
        assert "Use the two sided setting" in src, "his words are not recorded at the value"

    def test_the_convention_actually_decides_the_seats_dispute(self):
        """The claim that fixing the convention settles 10-vs-11, verified rather than asserted."""
        from scipy.stats import norm
        m = _load()
        p_lo, p_hi = 0.5, 0.9
        dphi = math.asin(math.sqrt(p_hi)) - math.asin(math.sqrt(p_lo))
        n = 2000
        sd = 1 / (2 * math.sqrt(n))

        def per_boundary(T):
            return 2 * norm.sf((dphi / (T - 1)) / 2 / sd)

        assert per_boundary(11) <= 0.05 < per_boundary(12), (
            f"T=11 should hold and T=12 fail under two-sided: "
            f"{per_boundary(11):.6f}, {per_boundary(12):.6f}")
        # and under the rejected convention the answer differs, which is why it mattered
        one_sided_13 = norm.sf((dphi / 12) / 2 / sd)
        assert one_sided_13 <= 0.05, "the per-side convention no longer admits T=13"

class TestTheFalseAlarmProportionIsHisRuling:
    """*"Then yes. Do it that way. 0.05 is acceptable within this f[r]amework."* -- 2026-10-11."""

    def test_it_is_pinned_at_the_value_he_accepted(self):
        m = _load()
        assert hasattr(m, "FALSE_ALARM_PROPORTION"), (
            "his accepted false-alarm proportion is recorded nowhere, so it will be re-asked")
        assert m.FALSE_ALARM_PROPORTION == 0.05

    def test_his_words_travel_with_the_value(self):
        """WHITESPACE-FLEXIBLE, because the quote WRAPS across 2 comment lines. A contiguous
        search failed here on a sentence that was plainly present -- the identical fault caught
        in the lesson-4 docstring check an hour earlier the same night."""
        import re
        src = PRODUCER.read_text(encoding="utf-8")
        assert re.search(r"0\.05\s+is\s+(?:#:\s*)?acceptable\s+(?:#:\s*)?within\s+"
                         r"(?:#:\s*)?this", src), (
            "a number without its ruling is a number someone will change")

    def test_the_reasoning_names_the_ruling_it_depends_on(self):
        """It is 0.05 BECAUSE rankings are fixed at experiment start -- his ruling 4. If that
        changed, this number should be revisited rather than inherited."""
        src = PRODUCER.read_text(encoding="utf-8")
        assert "FIXED at" in src and "no-benching" in src
