#!/usr/bin/env python3
"""Every pattern in the panel brief validator's CHECKS can match the text it is given.

FOUND 2026-09-17 under task A4. `validate()` lowercases the brief before
matching, and 3 of the 29 patterns were written with capitals: `\\bS_k\\b`,
`\\bDuane\\b` and `\\bWilson\\b`. None could ever match, so a brief that named
only 1 of those instruments was refused on "names a mathematical instrument",
while the same brief naming gamma passed. Called, not grepped.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LABEL = "names a mathematical instrument"


@pytest.fixture(scope="module")
def pbv():
    spec = importlib.util.spec_from_file_location("pbv_patterns", ROOT / "scripts" / "panel_brief_validate.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _instrument_refused(pbv, text: str) -> bool:
    return any(p.startswith(LABEL + ":") for p in pbv.validate(text))


@pytest.mark.parametrize("word", ["Wilson", "S_k", "Duane", "gamma", "severity", "two-sided gate"])
def test_naming_any_1_instrument_satisfies_the_instrument_check(pbv, word):
    text = ("Filler sentence for length. " * 20) + f"Use the {word} as the instrument for this question."
    assert not _instrument_refused(pbv, text), f"a brief naming {word!r} was refused on the instrument check"


def test_control_naming_no_instrument_is_still_refused(pbv):
    text = ("Filler sentence for length. " * 20) + "Use your judgement."
    assert _instrument_refused(pbv, text)


def test_no_pattern_in_checks_is_unreachable_after_lowercasing(pbv):
    """Structural companion: a pattern carrying a capital letter outside an escape
    must be matched case-insensitively, or it is dead against lowercased text."""
    import re
    for label, patterns, _ in pbv.CHECKS:
        for p in patterns:
            if re.search(r"[A-Z]", re.sub(r"\\[a-zA-Z]", "", p)):
                assert re.search(p, p.replace("\\b", "").lower(), re.I), (label, p)
