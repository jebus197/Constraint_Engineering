"""2 live copies of the maths-routing pattern disagreed on 0.46% of findings.

Whether a finding routed to mathematical verification depended on WHICH MODULE
ASKED. Measured 2026-09-06 over 8709 distinct archived finding descriptions: the 2
copies disagreed on 40, Wilson [0.34%, 0.62%], and in 100% of those
`immune_agents` routed as MATH while `verification_utils` did not.

THIS TEST EXECUTES BOTH PATTERNS rather than comparing their source text, over the
14-item corpus below.

WHAT IT DOES NOT DO, corrected 2026-09-06 after fable caught it. An earlier version
of this docstring said agreement was enforced "by EXECUTING both over the archived
corpus". It is not: the corpus here is 14 hand-written strings chosen to cover the 7
alternatives that had diverged. The 40-of-8709 figure was real when CC1 measured it
and NOTHING COMMITTED REPRODUCED IT -- which is precisely the
`measured-rate-travels-with-its-script` violation CC1 had cited at others 4 times
that same day, committed inside a test written to enforce rigour.

The missing artefact now exists: `scripts/measure_math_pattern_divergence.py`
replays both historical forms over every distinct archived description and
reproduces 40 of 8709, 0.46%, Wilson [0.34%, 0.62%], all 40 broad-only.

AND THE ROOT CAUSE IS GONE RATHER THAN GUARDED. `immune_agents` now IMPORTS the
pattern from `verification_utils` instead of holding a second copy, so the 2 cannot
drift again -- `A is B` is literally true. This file remains as the guard against
someone re-introducing a copy, and as the record of what the divergence cost.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

CORPUS = [
    "the bound is exceeded",              # 'bound'    — only the broad form had it
    "this threshold is wrong",            # 'threshold'
    "the inequality does not hold",       # 'inequality'
    "the formula is misstated",           # 'formula'
    "the equation is inconsistent",       # 'equation'
    "log scaling is assumed",             # 'log'
    "exp growth is claimed",              # 'exp'
    "x = y + 1",                          # both
    "sqrt(2) is irrational",              # both
    "a plain english sentence about ducks",   # neither
]


def _patterns():
    vu = importlib.import_module("bench.verification_utils")
    ia = importlib.import_module("bench.immune_agents")
    return vu._MATH_PATTERN, ia._MATH_PATTERN


def test_the_two_copies_agree_on_every_corpus_item():
    a, b = _patterns()
    disagree = [t for t in CORPUS if bool(a.search(t)) != bool(b.search(t))]
    assert not disagree, f"the 2 routing patterns still disagree on: {disagree}"


def test_the_broad_alternatives_are_present_in_both():
    """The 7 that were missing. If one copy loses them again this fails."""
    a, b = _patterns()
    for text in ("the bound is exceeded", "this threshold is wrong",
                 "the inequality does not hold", "the formula is misstated",
                 "the equation is inconsistent", "log scaling", "exp growth"):
        assert a.search(text), f"verification_utils no longer routes {text!r} as maths"
        assert b.search(text), f"immune_agents no longer routes {text!r} as maths"


def test_a_non_mathematical_sentence_still_routes_nowhere():
    """Unifying on the broader form must not make the pattern match everything."""
    a, b = _patterns()
    plain = "a plain english sentence about ducks"
    assert not a.search(plain) and not b.search(plain)
